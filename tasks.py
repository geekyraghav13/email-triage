from typing import Dict, List, Any
from models import Action


# Task definitions with action schemas and requirements
TASKS: Dict[str, Dict[str, Any]] = {
    "easy": {
        "id": "easy",
        "name": "Email Classification",
        "description": "Classify 10 clear-cut emails into the correct categories. Only classification action is required.",
        "difficulty": "easy",
        "email_count": 10,
        "time_limit": 10,  # steps
        "allowed_actions": ["classify"],
        "required_fields": {
            "classify": ["action_type", "category"]
        },
        "objective": "Correctly classify each email into one of the predefined categories",
        "grading_criteria": "Exact match on category. Score = correct classifications / total emails",
        "expected_baseline_score": 0.90,
        "action_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["classify"],
                    "description": "Must be 'classify'"
                },
                "category": {
                    "type": "string",
                    "enum": ["bug_report", "feature_request", "billing", "general_inquiry", "spam", "feedback"],
                    "description": "The category to assign to the email"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Optional: Explanation for the classification"
                }
            },
            "required": ["action_type", "category"]
        }
    },

    "medium": {
        "id": "medium",
        "name": "Priority Triage",
        "description": "Classify AND prioritize 15 emails with some ambiguous cases. Both classification and prioritization required.",
        "difficulty": "medium",
        "email_count": 15,
        "time_limit": 15,  # steps
        "allowed_actions": ["classify", "prioritize"],
        "required_fields": {
            "classify": ["action_type", "category"],
            "prioritize": ["action_type", "category", "priority"]
        },
        "objective": "Correctly classify and prioritize emails, handling ambiguous cases with good judgment",
        "grading_criteria": "50% category accuracy + 30% priority accuracy + 20% processing order (urgent emails first)",
        "expected_baseline_score": 0.70,
        "action_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["classify", "prioritize"],
                    "description": "Use 'prioritize' to set both category and priority"
                },
                "category": {
                    "type": "string",
                    "enum": ["bug_report", "feature_request", "billing", "general_inquiry", "spam", "escalation", "feedback"],
                    "description": "The category to assign to the email"
                },
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "medium", "low"],
                    "description": "The priority level (required when action_type is 'prioritize')"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Optional: Explanation for the classification and prioritization"
                }
            },
            "required": ["action_type", "category"]
        }
    },

    "hard": {
        "id": "hard",
        "name": "Full Triage & Response",
        "description": "Classify, prioritize, and compose appropriate replies for 20 emails including multi-turn threads. All action types available.",
        "difficulty": "hard",
        "email_count": 20,
        "time_limit": 20,  # steps
        "allowed_actions": ["classify", "prioritize", "reply", "escalate", "archive", "skip"],
        "required_fields": {
            "classify": ["action_type", "category"],
            "prioritize": ["action_type", "category", "priority"],
            "reply": ["action_type", "category", "priority", "reply_text"],
            "escalate": ["action_type", "category", "priority", "escalate_to"],
            "archive": ["action_type"],
            "skip": ["action_type"]
        },
        "objective": "Perform full email triage including composing contextual replies and escalating when appropriate",
        "grading_criteria": "25% category + 15% priority + 35% reply quality + 15% escalation decisions + 10% efficiency",
        "expected_baseline_score": 0.50,
        "action_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "enum": ["classify", "prioritize", "reply", "escalate", "archive", "skip"],
                    "description": "The type of action to take"
                },
                "category": {
                    "type": "string",
                    "enum": ["bug_report", "feature_request", "billing", "general_inquiry", "spam", "escalation", "feedback"],
                    "description": "The category (required for classify, prioritize, reply, escalate)"
                },
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "medium", "low"],
                    "description": "The priority level (required for prioritize, reply, escalate)"
                },
                "reply_text": {
                    "type": "string",
                    "description": "The reply message to send (required for 'reply' action)"
                },
                "escalate_to": {
                    "type": "string",
                    "enum": ["manager", "legal", "billing_specialist", "technical_lead", "executive"],
                    "description": "Who to escalate to (required for 'escalate' action)"
                },
                "reasoning": {
                    "type": "string",
                    "description": "Optional but recommended: Explanation for the action"
                }
            },
            "required": ["action_type"]
        }
    }
}


def get_task(task_id: str) -> Dict[str, Any]:
    """Get task definition by ID."""
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id: {task_id}. Available tasks: {list(TASKS.keys())}")
    return TASKS[task_id]


def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all task definitions."""
    return list(TASKS.values())


def validate_action(action: Action, task_id: str) -> tuple[bool, str]:
    """
    Validate that an action is allowed and properly formed for the given task.

    Returns: (is_valid, error_message)
    """
    task = get_task(task_id)

    # Check if action type is allowed
    if action.action_type not in task["allowed_actions"]:
        return False, f"Action '{action.action_type}' not allowed for task '{task_id}'. Allowed: {task['allowed_actions']}"

    # Check required fields for this action type
    required = task["required_fields"].get(action.action_type, [])

    for field in required:
        value = getattr(action, field, None)
        if value is None:
            return False, f"Field '{field}' is required for action '{action.action_type}' in task '{task_id}'"

    # Specific validations
    if action.action_type == "reply" and action.reply_text:
        if len(action.reply_text.strip()) < 10:
            return False, "Reply text must be at least 10 characters"

    if action.action_type == "escalate" and not action.escalate_to:
        return False, "Must specify who to escalate to"

    return True, ""


def get_task_summary(task_id: str) -> str:
    """Get a human-readable summary of a task."""
    task = get_task(task_id)
    return f"""
Task: {task['name']} ({task['difficulty']})
Description: {task['description']}
Emails: {task['email_count']}
Time Limit: {task['time_limit']} steps
Allowed Actions: {', '.join(task['allowed_actions'])}
Objective: {task['objective']}
Grading: {task['grading_criteria']}
Expected Baseline Score: {task['expected_baseline_score']}
"""

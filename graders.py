from typing import List, Dict, Any
from models import Action, EmailCategory, EmailPriority


def grade_episode(
    task_id: str,
    actions: List[Dict[str, Any]],
    ground_truths: List[Dict[str, Any]],
    step_rewards: List[float]
) -> Dict[str, Any]:
    """
    Grade a completed episode.

    CRITICAL: Must be deterministic - same actions produce same score.

    Args:
        task_id: The task ID
        actions: List of action dictionaries taken during episode
        ground_truths: List of ground truth dictionaries for each email
        step_rewards: List of step-wise rewards

    Returns:
        Dictionary with 'score' (0.0-1.0), 'breakdown', and 'feedback'
    """
    if task_id == "easy":
        return _grade_easy(actions, ground_truths, step_rewards)
    elif task_id == "medium":
        return _grade_medium(actions, ground_truths, step_rewards)
    elif task_id == "hard":
        return _grade_hard(actions, ground_truths, step_rewards)
    else:
        raise ValueError(f"Unknown task_id: {task_id}")


def _grade_easy(
    actions: List[Dict[str, Any]],
    ground_truths: List[Dict[str, Any]],
    step_rewards: List[float]
) -> Dict[str, Any]:
    """
    Grade easy task: Email Classification.

    Grading: Exact match on category. Score = correct / total
    """
    if not actions or not ground_truths:
        return {
            "score": 0.0,
            "breakdown": {"correct": 0, "total": 0},
            "feedback": "No actions or ground truths provided"
        }

    correct = 0
    total = min(len(actions), len(ground_truths))

    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        action_category = action.get("category")
        gt_category = gt.get("category")

        # Handle enum string comparison
        if isinstance(gt_category, EmailCategory):
            gt_category = gt_category.value
        if isinstance(action_category, EmailCategory):
            action_category = action_category.value

        if action_category == gt_category:
            correct += 1

    score = correct / total if total > 0 else 0.0

    return {
        "score": score,
        "breakdown": {
            "correct": correct,
            "total": total,
            "accuracy": score
        },
        "feedback": f"Classified {correct}/{total} emails correctly ({score*100:.1f}% accuracy)"
    }


def _grade_medium(
    actions: List[Dict[str, Any]],
    ground_truths: List[Dict[str, Any]],
    step_rewards: List[float]
) -> Dict[str, Any]:
    """
    Grade medium task: Priority Triage.

    Grading:
    - 50% weight on category accuracy
    - 30% weight on priority accuracy
    - 20% weight on processing order (urgent emails first)
    """
    if not actions or not ground_truths:
        return {
            "score": 0.0,
            "breakdown": {},
            "feedback": "No actions or ground truths provided"
        }

    total = min(len(actions), len(ground_truths))

    # Category accuracy
    category_correct = 0
    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        action_category = action.get("category")
        gt_category = gt.get("category")

        if isinstance(gt_category, EmailCategory):
            gt_category = gt_category.value
        if isinstance(action_category, EmailCategory):
            action_category = action_category.value

        if action_category == gt_category:
            category_correct += 1

    category_accuracy = category_correct / total if total > 0 else 0.0

    # Priority accuracy
    priority_correct = 0
    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        action_priority = action.get("priority")
        gt_priority = gt.get("priority")

        if isinstance(gt_priority, EmailPriority):
            gt_priority = gt_priority.value
        if isinstance(action_priority, EmailPriority):
            action_priority = action_priority.value

        if action_priority == gt_priority:
            priority_correct += 1

    priority_accuracy = priority_correct / total if total > 0 else 0.0

    # Order efficiency: Check if urgent/high priority emails were processed earlier
    order_score = _compute_order_efficiency(actions, ground_truths)

    # Weighted score
    score = (
        category_accuracy * 0.5 +
        priority_accuracy * 0.3 +
        order_score * 0.2
    )

    return {
        "score": score,
        "breakdown": {
            "category_accuracy": category_accuracy,
            "category_correct": category_correct,
            "priority_accuracy": priority_accuracy,
            "priority_correct": priority_correct,
            "order_efficiency": order_score,
            "total": total
        },
        "feedback": f"Category: {category_accuracy*100:.1f}%, Priority: {priority_accuracy*100:.1f}%, Order: {order_score*100:.1f}%"
    }


def _grade_hard(
    actions: List[Dict[str, Any]],
    ground_truths: List[Dict[str, Any]],
    step_rewards: List[float]
) -> Dict[str, Any]:
    """
    Grade hard task: Full Triage & Response.

    Grading:
    - 25% category accuracy
    - 15% priority accuracy
    - 35% reply quality (when reply action used)
    - 15% escalation decisions (escalate when needed, reply when appropriate)
    - 10% efficiency (use appropriate action types)
    """
    if not actions or not ground_truths:
        return {
            "score": 0.0,
            "breakdown": {},
            "feedback": "No actions or ground truths provided"
        }

    total = min(len(actions), len(ground_truths))

    # Category accuracy (25%)
    category_correct = 0
    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        action_category = action.get("category")
        gt_category = gt.get("category")

        if isinstance(gt_category, EmailCategory):
            gt_category = gt_category.value
        if isinstance(action_category, EmailCategory):
            action_category = action_category.value

        if action_category == gt_category:
            category_correct += 1

    category_accuracy = category_correct / total if total > 0 else 0.0

    # Priority accuracy (15%)
    priority_correct = 0
    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        action_priority = action.get("priority")
        gt_priority = gt.get("priority")

        if isinstance(gt_priority, EmailPriority):
            gt_priority = gt_priority.value
        if isinstance(action_priority, EmailPriority):
            action_priority = action_priority.value

        if action_priority == gt_priority:
            priority_correct += 1

    priority_accuracy = priority_correct / total if total > 0 else 0.0

    # Reply quality (35%)
    reply_quality_score = _compute_reply_quality_score(actions, ground_truths)

    # Escalation decisions (15%)
    escalation_score = _compute_escalation_score(actions, ground_truths)

    # Efficiency (10%)
    efficiency_score = _compute_efficiency_score(actions, ground_truths)

    # Weighted score
    score = (
        category_accuracy * 0.25 +
        priority_accuracy * 0.15 +
        reply_quality_score * 0.35 +
        escalation_score * 0.15 +
        efficiency_score * 0.10
    )

    return {
        "score": score,
        "breakdown": {
            "category_accuracy": category_accuracy,
            "category_correct": category_correct,
            "priority_accuracy": priority_accuracy,
            "priority_correct": priority_correct,
            "reply_quality": reply_quality_score,
            "escalation_decisions": escalation_score,
            "efficiency": efficiency_score,
            "total": total
        },
        "feedback": f"Category: {category_accuracy*100:.1f}%, Priority: {priority_accuracy*100:.1f}%, Reply: {reply_quality_score*100:.1f}%, Escalation: {escalation_score*100:.1f}%, Efficiency: {efficiency_score*100:.1f}%"
    }


def _compute_order_efficiency(actions: List[Dict], ground_truths: List[Dict]) -> float:
    """
    Compute how well the agent prioritized urgent/high priority emails.
    Higher priority emails should be processed earlier.
    """
    priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}

    # Create list of (step_number, priority_value)
    processing_order = []
    for i, gt in enumerate(ground_truths):
        gt_priority = gt.get("priority")
        if isinstance(gt_priority, EmailPriority):
            gt_priority = gt_priority.value

        priority_val = priority_order.get(gt_priority, 0)
        processing_order.append((i, priority_val))

    if not processing_order:
        return 0.0

    # Ideal order: Sort by priority descending
    ideal_order = sorted(processing_order, key=lambda x: x[1], reverse=True)

    # Compute correlation between actual and ideal
    # Simple metric: Count how many high priority items were in first half
    total = len(processing_order)
    first_half = total // 2

    high_priority_in_first_half = 0
    total_high_priority = 0

    for i, (step, priority_val) in enumerate(processing_order):
        if priority_val >= 3:  # High or Urgent
            total_high_priority += 1
            if i < first_half:
                high_priority_in_first_half += 1

    if total_high_priority == 0:
        return 1.0  # No high priority emails, order doesn't matter

    score = high_priority_in_first_half / total_high_priority
    return score


def _compute_reply_quality_score(actions: List[Dict], ground_truths: List[Dict]) -> float:
    """
    Compute average reply quality for reply actions.
    Uses deterministic keyword checks.
    """
    from rewards import _evaluate_reply_quality

    reply_scores = []

    for i, action in enumerate(actions):
        if action.get("action_type") == "reply":
            reply_text = action.get("reply_text", "")
            if reply_text and i < len(ground_truths):
                gt = ground_truths[i]
                gt_category = gt.get("category")
                if isinstance(gt_category, str):
                    try:
                        gt_category = EmailCategory(gt_category)
                    except ValueError:
                        gt_category = EmailCategory.GENERAL_INQUIRY

                quality = _evaluate_reply_quality(reply_text, gt_category)
                reply_scores.append(quality)

    if not reply_scores:
        return 0.5  # Neutral score if no replies (not required for all emails)

    return sum(reply_scores) / len(reply_scores)


def _compute_escalation_score(actions: List[Dict], ground_truths: List[Dict]) -> float:
    """
    Compute escalation decision accuracy.
    Should escalate when required, and not escalate otherwise.
    """
    correct_decisions = 0
    total = min(len(actions), len(ground_truths))

    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        requires_escalation = gt.get("requires_escalation", False)
        action_type = action.get("action_type")

        if requires_escalation and action_type == "escalate":
            correct_decisions += 1
        elif not requires_escalation and action_type != "escalate":
            correct_decisions += 1
        # Else: Wrong decision

    return correct_decisions / total if total > 0 else 0.0


def _compute_efficiency_score(actions: List[Dict], ground_truths: List[Dict]) -> float:
    """
    Compute efficiency: Using appropriate action types.
    - Spam should be archived
    - Escalation category should be escalated
    - Others should get replies or prioritization
    """
    appropriate_actions = 0
    total = min(len(actions), len(ground_truths))

    for i in range(total):
        action = actions[i]
        gt = ground_truths[i]

        action_type = action.get("action_type")
        gt_category = gt.get("category")

        if isinstance(gt_category, EmailCategory):
            gt_category = gt_category.value

        # Check if action type is appropriate
        if gt_category == "spam" and action_type == "archive":
            appropriate_actions += 1
        elif gt_category == "escalation" and action_type == "escalate":
            appropriate_actions += 1
        elif gt_category not in ["spam", "escalation"] and action_type in ["reply", "prioritize", "classify"]:
            appropriate_actions += 1
        elif action_type == "skip":
            # Skip is never ideal but don't penalize too heavily
            appropriate_actions += 0.3
        # Else: Inappropriate action

    return appropriate_actions / total if total > 0 else 0.0

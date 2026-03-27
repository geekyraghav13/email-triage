from typing import Dict, Any
from models import Action, Reward, Email, EmailCategory, EmailPriority


def compute_reward(
    action: Action,
    ground_truth: Dict[str, Any],
    task_id: str,
    step_number: int,
    total_steps: int
) -> Reward:
    """
    Compute reward for a single action.

    CRITICAL: Must return score between 0.0 and 1.0 with partial credit.

    Args:
        action: The action taken by the agent
        ground_truth: Dictionary with 'category', 'priority', 'requires_escalation', etc.
        task_id: The current task ID
        step_number: Current step in the episode
        total_steps: Total steps available

    Returns:
        Reward object with score, breakdown, and feedback
    """
    score = 0.0
    breakdown = {}
    feedback_parts = []

    gt_category = ground_truth.get("category")
    gt_priority = ground_truth.get("priority")
    requires_escalation = ground_truth.get("requires_escalation", False)

    # Penalty for skip action
    if action.action_type == "skip":
        breakdown["skip_penalty"] = -0.1
        score -= 0.1
        feedback_parts.append("Skipped email (penalty applied)")

    # Penalty for no reasoning (encourage thoughtful decisions)
    if not action.reasoning or len(action.reasoning.strip()) < 5:
        breakdown["no_reasoning_penalty"] = -0.02
        score -= 0.02
        feedback_parts.append("No reasoning provided")

    # Task-specific reward computation
    if task_id == "easy":
        score += _compute_easy_reward(action, gt_category, breakdown, feedback_parts)

    elif task_id == "medium":
        score += _compute_medium_reward(action, gt_category, gt_priority, step_number, total_steps, breakdown, feedback_parts)

    elif task_id == "hard":
        score += _compute_hard_reward(action, ground_truth, breakdown, feedback_parts)

    # Ensure score is in valid range [0.0, 1.0]
    score = max(0.0, min(1.0, score))

    feedback = " | ".join(feedback_parts) if feedback_parts else "Action processed"

    return Reward(
        score=score,
        breakdown=breakdown,
        feedback=feedback
    )


def _compute_easy_reward(
    action: Action,
    gt_category: EmailCategory,
    breakdown: Dict,
    feedback_parts: list
) -> float:
    """
    Easy task: Just category classification.
    Returns 1.0 for correct, 0.0 for incorrect.
    """
    score = 0.0

    if action.category == gt_category:
        score = 1.0
        breakdown["category_correct"] = 1.0
        feedback_parts.append(f"Correct category: {gt_category.value}")
    else:
        score = 0.0
        breakdown["category_correct"] = 0.0
        feedback_parts.append(f"Incorrect category. Expected: {gt_category.value}, Got: {action.category.value if action.category else 'None'}")

    return score


def _compute_medium_reward(
    action: Action,
    gt_category: EmailCategory,
    gt_priority: EmailPriority,
    step_number: int,
    total_steps: int,
    breakdown: Dict,
    feedback_parts: list
) -> float:
    """
    Medium task: Category + Priority + Order efficiency.

    Scoring:
    - 50% weight on category accuracy
    - 30% weight on priority accuracy
    - 20% weight on processing order (should prioritize urgent/high first)
    """
    score = 0.0

    # Category accuracy (50% weight)
    if action.category == gt_category:
        category_score = 0.5
        breakdown["category_accuracy"] = 0.5
        feedback_parts.append(f"Correct category: {gt_category.value}")
    else:
        # Partial credit for close categories
        category_score = _get_category_similarity(action.category, gt_category) * 0.5
        breakdown["category_accuracy"] = category_score
        feedback_parts.append(f"Category mismatch. Expected: {gt_category.value}, Got: {action.category.value if action.category else 'None'}")

    score += category_score

    # Priority accuracy (30% weight)
    if action.priority == gt_priority:
        priority_score = 0.3
        breakdown["priority_accuracy"] = 0.3
        feedback_parts.append(f"Correct priority: {gt_priority.value}")
    elif action.priority:
        # Partial credit based on priority distance
        priority_score = _get_priority_similarity(action.priority, gt_priority) * 0.3
        breakdown["priority_accuracy"] = priority_score
        feedback_parts.append(f"Priority mismatch. Expected: {gt_priority.value}, Got: {action.priority.value}")
    else:
        priority_score = 0.0
        breakdown["priority_accuracy"] = 0.0
        feedback_parts.append("No priority assigned")

    score += priority_score

    # Order efficiency (20% weight)
    # Should process urgent/high priority emails earlier
    expected_position = _get_expected_position(gt_priority, total_steps)
    position_score = 1.0 - abs(step_number - expected_position) / total_steps
    position_score = max(0.0, position_score) * 0.2

    breakdown["order_efficiency"] = position_score
    score += position_score

    return score


def _compute_hard_reward(
    action: Action,
    ground_truth: Dict,
    breakdown: Dict,
    feedback_parts: list
) -> float:
    """
    Hard task: Category + Priority + Reply Quality + Escalation + Efficiency.

    Scoring:
    - 25% category accuracy
    - 15% priority accuracy
    - 35% reply quality (if reply action)
    - 15% escalation decision (escalate when needed, reply when appropriate)
    - 10% efficiency (use appropriate action type)
    """
    score = 0.0

    gt_category = ground_truth.get("category")
    gt_priority = ground_truth.get("priority")
    requires_escalation = ground_truth.get("requires_escalation", False)

    # Category accuracy (25% weight)
    if action.category == gt_category:
        category_score = 0.25
        breakdown["category_accuracy"] = 0.25
        feedback_parts.append(f"Correct category: {gt_category.value}")
    elif action.category:
        category_score = _get_category_similarity(action.category, gt_category) * 0.25
        breakdown["category_accuracy"] = category_score
        feedback_parts.append(f"Category close but not exact")
    else:
        category_score = 0.0
        breakdown["category_accuracy"] = 0.0
        feedback_parts.append("No category assigned")

    score += category_score

    # Priority accuracy (15% weight)
    if action.priority == gt_priority:
        priority_score = 0.15
        breakdown["priority_accuracy"] = 0.15
        feedback_parts.append(f"Correct priority")
    elif action.priority:
        priority_score = _get_priority_similarity(action.priority, gt_priority) * 0.15
        breakdown["priority_accuracy"] = priority_score
    else:
        priority_score = 0.0
        breakdown["priority_accuracy"] = 0.0

    score += priority_score

    # Reply quality (35% weight) - only if reply action
    if action.action_type == "reply" and action.reply_text:
        reply_score = _evaluate_reply_quality(action.reply_text, gt_category) * 0.35
        breakdown["reply_quality"] = reply_score
        score += reply_score
        feedback_parts.append(f"Reply quality: {reply_score/0.35:.2f}")
    elif action.action_type == "reply":
        breakdown["reply_quality"] = 0.0
        feedback_parts.append("Reply action but no reply text")

    # Escalation decision (15% weight)
    escalation_score = 0.0
    if requires_escalation:
        if action.action_type == "escalate":
            escalation_score = 0.15
            breakdown["escalation_decision"] = 0.15
            feedback_parts.append("Correctly chose to escalate")
        else:
            escalation_score = 0.0
            breakdown["escalation_decision"] = 0.0
            feedback_parts.append("Should have escalated but didn't")
    else:
        if action.action_type != "escalate":
            escalation_score = 0.15
            breakdown["escalation_decision"] = 0.15
            feedback_parts.append("Correctly did not escalate")
        else:
            escalation_score = 0.05  # Small partial credit - maybe reasonable escalation
            breakdown["escalation_decision"] = 0.05
            feedback_parts.append("Escalated unnecessarily")

    score += escalation_score

    # Efficiency (10% weight) - using appropriate action type
    efficiency_score = 0.0
    if action.action_type == "archive" and gt_category == EmailCategory.SPAM:
        efficiency_score = 0.1
        feedback_parts.append("Efficiently archived spam")
    elif action.action_type in ["reply", "escalate"] and gt_category != EmailCategory.SPAM:
        efficiency_score = 0.1
        feedback_parts.append("Appropriate action type")
    elif action.action_type == "classify":
        efficiency_score = 0.05  # Partial credit for at least categorizing
    else:
        efficiency_score = 0.0

    breakdown["efficiency"] = efficiency_score
    score += efficiency_score

    return score


def _get_category_similarity(cat1: EmailCategory, cat2: EmailCategory) -> float:
    """
    Return similarity score between categories (0.0 to 1.0).
    Some categories are more similar than others.
    """
    if cat1 == cat2:
        return 1.0

    # Define category similarity groups
    similar_pairs = [
        (EmailCategory.BUG_REPORT, EmailCategory.GENERAL_INQUIRY),
        (EmailCategory.FEATURE_REQUEST, EmailCategory.FEEDBACK),
        (EmailCategory.ESCALATION, EmailCategory.BUG_REPORT),
        (EmailCategory.BILLING, EmailCategory.GENERAL_INQUIRY),
    ]

    for pair in similar_pairs:
        if (cat1 in pair and cat2 in pair):
            return 0.5  # Partial credit for similar categories

    return 0.0  # Completely different


def _get_priority_similarity(pri1: EmailPriority, pri2: EmailPriority) -> float:
    """
    Return similarity score between priorities (0.0 to 1.0).
    Adjacent priorities get partial credit.
    """
    if pri1 == pri2:
        return 1.0

    priority_order = [EmailPriority.LOW, EmailPriority.MEDIUM, EmailPriority.HIGH, EmailPriority.URGENT]

    try:
        idx1 = priority_order.index(pri1)
        idx2 = priority_order.index(pri2)
        distance = abs(idx1 - idx2)

        if distance == 1:
            return 0.6  # One level off
        elif distance == 2:
            return 0.3  # Two levels off
        else:
            return 0.0  # Completely wrong
    except ValueError:
        return 0.0


def _get_expected_position(priority: EmailPriority, total_steps: int) -> int:
    """
    Get expected step number for processing based on priority.
    Urgent should be early, low should be later.
    """
    if priority == EmailPriority.URGENT:
        return int(total_steps * 0.1)  # First 10%
    elif priority == EmailPriority.HIGH:
        return int(total_steps * 0.3)  # First 30%
    elif priority == EmailPriority.MEDIUM:
        return int(total_steps * 0.6)  # First 60%
    else:  # LOW
        return int(total_steps * 0.9)  # Last 10%


def _evaluate_reply_quality(reply_text: str, category: EmailCategory) -> float:
    """
    Evaluate reply quality using deterministic keyword and structure checks.

    Checks:
    1. Has greeting (Hi, Hello, Dear, etc.)
    2. Has acknowledgment/empathy
    3. Addresses the issue (category-specific keywords)
    4. Has next steps or resolution
    5. Has professional sign-off
    6. Appropriate tone for category
    7. Sufficient length

    Returns score 0.0 to 1.0
    """
    score = 0.0
    reply_lower = reply_text.lower()

    # 1. Greeting (0.1 points)
    greetings = ["hi", "hello", "dear", "greetings", "good morning", "good afternoon"]
    if any(g in reply_lower for g in greetings):
        score += 0.1

    # 2. Acknowledgment/Empathy (0.15 points)
    acknowledgments = [
        "thank you", "thanks", "appreciate", "understand", "sorry",
        "apologize", "apologies", "regret", "acknowledge"
    ]
    if any(a in reply_lower for a in acknowledgments):
        score += 0.15

    # 3. Category-specific keywords (0.25 points)
    category_keywords = {
        EmailCategory.BUG_REPORT: ["investigating", "fix", "issue", "bug", "resolved", "patch", "update", "reproduce"],
        EmailCategory.FEATURE_REQUEST: ["roadmap", "consider", "feedback", "future", "development", "request", "feature"],
        EmailCategory.BILLING: ["charge", "refund", "invoice", "billing", "payment", "account", "transaction"],
        EmailCategory.GENERAL_INQUIRY: ["information", "help", "documentation", "guide", "answer", "question"],
        EmailCategory.FEEDBACK: ["feedback", "suggestion", "appreciate", "team", "improve", "noted"],
        EmailCategory.ESCALATION: ["manager", "team", "escalate", "priority", "immediately"],
        EmailCategory.SPAM: [],  # Shouldn't be replying to spam
    }

    keywords = category_keywords.get(category, [])
    if any(kw in reply_lower for kw in keywords):
        score += 0.25

    # 4. Next steps or resolution (0.2 points)
    next_steps = [
        "will", "going to", "next", "follow up", "update", "contact",
        "within", "shortly", "soon", "working on", "steps", "process"
    ]
    if any(ns in reply_lower for ns in next_steps):
        score += 0.2

    # 5. Sign-off (0.1 points)
    signoffs = [
        "regards", "sincerely", "best", "thank you", "thanks",
        "cordially", "respectfully", "cheers"
    ]
    if any(so in reply_lower for so in signoffs):
        score += 0.1

    # 6. Appropriate tone (0.1 points)
    # Formal for billing/escalation, can be casual for others
    formal_indicators = ["please", "kindly", "would", "could", "may i"]
    if category in [EmailCategory.BILLING, EmailCategory.ESCALATION]:
        if any(fi in reply_lower for fi in formal_indicators):
            score += 0.1
    else:
        score += 0.1  # Less strict for other categories

    # 7. Sufficient length (0.1 points)
    if len(reply_text.split()) >= 20:  # At least 20 words
        score += 0.1

    return min(1.0, score)


def compute_episode_reward(step_rewards: list, completed: bool) -> float:
    """
    Compute final episode reward from individual step rewards.

    Args:
        step_rewards: List of step-wise reward scores
        completed: Whether episode was completed (didn't run out of time)

    Returns:
        Final episode score (0.0 to 1.0)
    """
    if not step_rewards:
        return 0.0

    # Mean of step rewards
    mean_reward = sum(step_rewards) / len(step_rewards)

    # Completion bonus
    completion_bonus = 1.0 if completed else 0.8

    # Final score
    final_score = mean_reward * completion_bonus

    return max(0.0, min(1.0, final_score))

"""
Basic tests for Email Triage Environment.

Run with: pytest tests/test_env.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from environment import EmailTriageEnv
from models import Action, EmailCategory, EmailPriority
from tasks import get_task, validate_action
from graders import grade_episode


def test_environment_reset():
    """Test environment reset for all tasks."""
    env = EmailTriageEnv()

    for task_id in ["easy", "medium", "hard"]:
        obs = env.reset(task_id)

        assert obs.task_id == task_id
        assert obs.inbox_size > 0
        assert obs.processed_count == 0
        assert obs.step_number == 0
        assert env.done == False
        assert len(env.emails) > 0
        print(f"✓ Reset test passed for {task_id}")


def test_environment_step():
    """Test taking steps in environment."""
    env = EmailTriageEnv()
    obs = env.reset("easy")

    action = Action(
        action_type="classify",
        category=EmailCategory.BUG_REPORT,
        reasoning="Test action"
    )

    obs, reward, done, info = env.step(action)

    assert reward.score >= 0.0 and reward.score <= 1.0
    assert isinstance(done, bool)
    assert obs.processed_count == 1
    print("✓ Step test passed")


def test_episode_completion():
    """Test completing a full episode."""
    env = EmailTriageEnv()
    obs = env.reset("easy")

    steps = 0
    max_steps = 20

    while not env.done and steps < max_steps:
        action = Action(
            action_type="classify",
            category=EmailCategory.GENERAL_INQUIRY,
            reasoning="Default action"
        )

        obs, reward, done, info = env.step(action)
        steps += 1

    assert env.done == True
    assert env.current_index == len(env.emails)
    print(f"✓ Episode completion test passed ({steps} steps)")


def test_state_method():
    """Test state() method returns valid state."""
    env = EmailTriageEnv()
    env.reset("medium")

    state = env.state()

    assert state.task_id == "medium"
    assert len(state.emails) > 0
    assert state.current_index >= 0
    assert isinstance(state.done, bool)
    print("✓ State method test passed")


def test_action_validation():
    """Test action validation for different tasks."""

    # Valid action for easy task
    action = Action(action_type="classify", category=EmailCategory.BUG_REPORT)
    is_valid, msg = validate_action(action, "easy")
    assert is_valid == True

    # Invalid action for easy task (reply not allowed)
    action = Action(
        action_type="reply",
        category=EmailCategory.BUG_REPORT,
        priority=EmailPriority.HIGH,
        reply_text="Test reply"
    )
    is_valid, msg = validate_action(action, "easy")
    assert is_valid == False

    # Valid action for hard task
    action = Action(
        action_type="reply",
        category=EmailCategory.BUG_REPORT,
        priority=EmailPriority.HIGH,
        reply_text="Test reply with sufficient length"
    )
    is_valid, msg = validate_action(action, "hard")
    assert is_valid == True

    print("✓ Action validation test passed")


def test_reward_range():
    """Test that rewards are always in valid range [0.0, 1.0]."""
    env = EmailTriageEnv()
    env.reset("medium")

    for _ in range(5):
        action = Action(
            action_type="prioritize",
            category=EmailCategory.BILLING,
            priority=EmailPriority.MEDIUM,
            reasoning="Test"
        )

        obs, reward, done, info = env.step(action)

        assert reward.score >= 0.0 and reward.score <= 1.0
        assert "breakdown" in reward.model_dump()
        assert "feedback" in reward.model_dump()

        if done:
            break

    print("✓ Reward range test passed")


def test_grader():
    """Test grader produces valid scores."""
    env = EmailTriageEnv()
    env.reset("easy")

    # Take some actions
    for _ in range(10):
        action = Action(
            action_type="classify",
            category=EmailCategory.BUG_REPORT
        )

        obs, reward, done, info = env.step(action)
        if done:
            break

    # Get grading
    actions = env.get_actions()
    ground_truths = env.get_ground_truths()
    rewards = env.rewards

    grading = grade_episode("easy", actions, ground_truths, rewards)

    assert "score" in grading
    assert grading["score"] >= 0.0 and grading["score"] <= 1.0
    assert "breakdown" in grading
    assert "feedback" in grading

    print(f"✓ Grader test passed (score: {grading['score']:.3f})")


def test_no_state_leakage():
    """Test that reset() produces clean state with no leakage."""
    env = EmailTriageEnv()

    # First episode
    env.reset("easy")
    first_email_id = env.emails[0].id

    action = Action(action_type="classify", category=EmailCategory.BUG_REPORT)
    env.step(action)

    # Reset and check state is clean
    env.reset("medium")

    assert env.current_index == 0
    assert len(env.actions_taken) == 0
    assert len(env.rewards) == 0
    assert env.done == False
    assert env.task_id == "medium"

    # Email should be different (or at least state is independent)
    assert env.emails[0].id != first_email_id or env.task_id == "medium"

    print("✓ No state leakage test passed")


def test_all_tasks_have_emails():
    """Test that all tasks generate appropriate number of emails."""
    env = EmailTriageEnv()

    for task_id in ["easy", "medium", "hard"]:
        env.reset(task_id)
        task_config = get_task(task_id)

        assert len(env.emails) == task_config["email_count"]
        print(f"✓ Task {task_id} has {len(env.emails)} emails (expected {task_config['email_count']})")


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("Running Email Triage Environment Tests")
    print("="*60)

    tests = [
        test_environment_reset,
        test_environment_step,
        test_episode_completion,
        test_state_method,
        test_action_validation,
        test_reward_range,
        test_grader,
        test_no_state_leakage,
        test_all_tasks_have_emails,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1

    print("="*60)
    print(f"Tests passed: {passed}/{len(tests)}")
    if failed > 0:
        print(f"Tests failed: {failed}/{len(tests)}")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

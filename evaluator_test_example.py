#!/usr/bin/env python3
"""
Example test script that evaluators might run
This demonstrates how they'll validate your environment
"""

import requests
import json

BASE_URL = "https://geekyraghav13-openenv-email-triage.hf.space"

def test_endpoint_availability():
    """Test 1: All endpoints must be accessible"""
    print("=" * 60)
    print("TEST 1: Endpoint Availability")
    print("=" * 60)

    tests = [
        ("GET", "/", "Root metadata"),
        ("GET", "/health", "Health check"),
        ("GET", "/tasks", "Task definitions"),
        ("GET", "/state", "Environment state"),
        ("GET", "/baseline", "Baseline info"),
    ]

    for method, endpoint, description in tests:
        response = requests.get(f"{BASE_URL}{endpoint}")
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        print(f"{status} - {description}: {response.status_code}")

    print()

def test_reset_all_tasks():
    """Test 2: Reset must work for all 3 tasks"""
    print("=" * 60)
    print("TEST 2: Reset for All Tasks")
    print("=" * 60)

    for task_id in ["easy", "medium", "hard"]:
        response = requests.post(
            f"{BASE_URL}/reset",
            json={"task_id": task_id}
        )

        if response.status_code == 200:
            data = response.json()
            has_obs = "observation" in data
            status = "✅ PASS" if has_obs else "❌ FAIL"
            print(f"{status} - Task '{task_id}': {response.status_code} | Has observation: {has_obs}")
        else:
            print(f"❌ FAIL - Task '{task_id}': {response.status_code}")

    print()

def test_reward_range():
    """Test 3: Rewards must be 0.0-1.0 with partial credit"""
    print("=" * 60)
    print("TEST 3: Reward Function (Partial Credit)")
    print("=" * 60)

    # Reset environment
    requests.post(f"{BASE_URL}/reset", json={"task_id": "easy"})

    # Test correct classification
    response = requests.post(
        f"{BASE_URL}/step",
        json={"action": {
            "action_type": "classify",
            "category": "bug_report",
            "reasoning": "Test correct classification"
        }}
    )

    if response.status_code == 200:
        reward1 = response.json()["reward"]["score"]
        print(f"Reward for action 1: {reward1}")

        # Test incorrect classification (should get 0.0, not negative)
        response = requests.post(
            f"{BASE_URL}/step",
            json={"action": {
                "action_type": "classify",
                "category": "spam"  # likely wrong
            }}
        )

        reward2 = response.json()["reward"]["score"]
        print(f"Reward for action 2: {reward2}")

        # Validate range
        valid_range = 0.0 <= reward1 <= 1.0 and 0.0 <= reward2 <= 1.0
        partial_credit = reward1 != reward2  # Not all same (shows granularity)

        if valid_range:
            print("✅ PASS - Rewards in valid range [0.0, 1.0]")
        else:
            print("❌ FAIL - Rewards outside valid range")

        if partial_credit:
            print("✅ PASS - Partial credit demonstrated (not binary)")
        else:
            print("⚠️  WARNING - All rewards same (may be binary)")

    print()

def test_complete_episode():
    """Test 4: Run complete episode and get grader score"""
    print("=" * 60)
    print("TEST 4: Complete Episode")
    print("=" * 60)

    # Reset
    response = requests.post(f"{BASE_URL}/reset", json={"task_id": "easy"})
    print(f"Reset: {response.status_code}")

    # Take 10 actions
    step_count = 0
    done = False

    while not done and step_count < 10:
        response = requests.post(
            f"{BASE_URL}/step",
            json={"action": {
                "action_type": "classify",
                "category": "general_inquiry",
                "reasoning": "Test step"
            }}
        )

        if response.status_code == 200:
            result = response.json()
            done = result.get("done", False)
            step_count += 1
            print(f"  Step {step_count}: Reward={result['reward']['score']:.3f} | Done={done}")

    # Get grader score
    response = requests.post(f"{BASE_URL}/grader")

    if response.status_code == 200:
        score = response.json().get("score", -1)
        print(f"\n✅ Episode completed!")
        print(f"✅ Final grader score: {score:.3f}")

        if 0.0 <= score <= 1.0:
            print("✅ PASS - Grader score in valid range")
        else:
            print("❌ FAIL - Grader score outside [0.0, 1.0]")
    else:
        print(f"❌ FAIL - Grader endpoint: {response.status_code}")

    print()

def test_deterministic_grading():
    """Test 5: Same actions should give same rewards (deterministic)"""
    print("=" * 60)
    print("TEST 5: Deterministic Grading")
    print("=" * 60)

    rewards = []

    for run in range(2):
        # Reset
        requests.post(f"{BASE_URL}/reset", json={"task_id": "easy"})

        # Take same action
        response = requests.post(
            f"{BASE_URL}/step",
            json={"action": {
                "action_type": "classify",
                "category": "bug_report",
                "reasoning": "Same action test"
            }}
        )

        reward = response.json()["reward"]["score"]
        rewards.append(reward)
        print(f"  Run {run + 1}: Reward = {reward}")

    if rewards[0] == rewards[1]:
        print("✅ PASS - Grading is deterministic")
    else:
        print("❌ FAIL - Grading is non-deterministic")

    print()

def main():
    """Run all evaluator tests"""
    print("\n" + "=" * 60)
    print("EVALUATOR TEST SUITE")
    print(f"Testing: {BASE_URL}")
    print("=" * 60 + "\n")

    try:
        test_endpoint_availability()
        test_reset_all_tasks()
        test_reward_range()
        test_complete_episode()
        test_deterministic_grading()

        print("=" * 60)
        print("ALL EVALUATOR TESTS COMPLETED")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

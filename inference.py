#!/usr/bin/env python3
"""
Baseline inference script for Email Triage environment.

Uses OpenAI API to run against all 3 tasks and report scores.

Usage:
    export OPENAI_API_KEY=your-key-here
    python baseline.py
"""

import os
import sys
import json
import requests
from typing import Dict, Any
from openai import OpenAI


# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:7860")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = "gpt-4o-mini"  # Using GPT-4 mini for cost-effectiveness


def check_openai_key():
    """Verify OpenAI API key is set."""
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Usage: export OPENAI_API_KEY=your-key-here")
        sys.exit(1)


def create_system_prompt(task_id: str) -> str:
    """Create system prompt explaining the task to the model."""

    base_prompt = """You are an AI email triage assistant. Your job is to process emails from an inbox by classifying them, prioritizing them, and taking appropriate actions.

You will be shown emails one at a time. For each email, you must respond with a JSON action.

Email Categories:
- bug_report: Technical issues and bugs
- feature_request: Requests for new features
- billing: Payment and subscription issues
- general_inquiry: General questions
- spam: Unwanted/unsolicited emails
- escalation: Issues requiring management attention
- feedback: User feedback and suggestions

Priority Levels:
- urgent: Immediate attention required
- high: Important, address soon
- medium: Normal priority
- low: Can wait

Action Types:
- classify: Just categorize the email
- prioritize: Categorize AND set priority
- reply: Send a response (requires category, priority, and reply_text)
- escalate: Forward to appropriate person (requires category, priority, and escalate_to)
- archive: File away (typically for spam)
- skip: Skip this email (not recommended, incurs penalty)

Escalation Targets: manager, legal, billing_specialist, technical_lead, executive

You must respond with ONLY a valid JSON object matching this structure:
{
    "action_type": "classify|prioritize|reply|escalate|archive|skip",
    "category": "category_name",
    "priority": "priority_level",
    "reply_text": "your reply text here",
    "escalate_to": "escalation_target",
    "reasoning": "brief explanation of your decision"
}

"""

    if task_id == "easy":
        task_prompt = """
TASK: Email Classification (Easy)
Your goal is to correctly classify 10 emails. Use action_type "classify" and provide the category.
Focus on accuracy - each email has a clear category.
"""
    elif task_id == "medium":
        task_prompt = """
TASK: Priority Triage (Medium)
Your goal is to classify AND prioritize 15 emails. Use action_type "prioritize" and provide both category and priority.
Some emails may be ambiguous - use your judgment.
Process urgent/high priority emails first for better efficiency score.
"""
    else:  # hard
        task_prompt = """
TASK: Full Triage & Response (Hard)
Your goal is to fully process 20 emails including multi-turn threads.
- For spam: use "archive"
- For escalations: use "escalate" with appropriate escalate_to
- For others: use "reply" with a professional, helpful response

When replying, include:
1. Greeting (Hi, Hello, Dear)
2. Acknowledgment/empathy (Thank you, I understand, etc.)
3. Address the issue with relevant keywords
4. Next steps or resolution
5. Professional sign-off (Best regards, etc.)

Pay attention to the "context" field which shows previous messages in a thread.
"""

    return base_prompt + task_prompt


def parse_model_response(response_text: str) -> Dict[str, Any]:
    """Parse model response into action dictionary."""
    try:
        # Try to extract JSON from response
        response_text = response_text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()

        action = json.loads(response_text)
        return action

    except json.JSONDecodeError as e:
        print(f"Failed to parse model response: {e}")
        print(f"Response was: {response_text}")
        # Return a safe default
        return {
            "action_type": "skip",
            "reasoning": "Failed to parse model response"
        }


def format_observation(obs: Dict[str, Any]) -> str:
    """Format observation as a prompt for the model."""
    email = obs["current_email"]

    prompt = f"""
EMAIL #{obs['processed_count'] + 1} of {obs['inbox_size']}
Time remaining: {obs['time_remaining']} steps

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}
Has attachment: {email['has_attachment']}
"""

    if obs.get("context"):
        prompt += f"\n--- THREAD CONTEXT ---\n{obs['context']}\n--- END CONTEXT ---\n"

    prompt += "\nProvide your action as JSON:"

    return prompt


def run_task(client: OpenAI, task_id: str) -> Dict[str, Any]:
    """Run baseline on a single task."""

    print(f"\n{'='*60}")
    print(f"Running task: {task_id}")
    print(f"{'='*60}")

    # Reset environment
    response = requests.post(
        f"{API_BASE_URL}/reset",
        json={"task_id": task_id}
    )

    if response.status_code != 200:
        print(f"Failed to reset: {response.text}")
        return {"error": "Failed to reset"}

    system_prompt = create_system_prompt(task_id)

    step = 0
    done = False

    while not done:
        step += 1

        # Get current observation from reset response (first step) or step response
        if step == 1:
            observation = response.json()["observation"]
        else:
            observation = step_response["observation"]

        print(f"\nStep {step}: Processing email from {observation['current_email']['sender']}")

        # Format prompt
        user_prompt = format_observation(observation)

        # Call OpenAI API
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            response_text = completion.choices[0].message.content

            # Parse action
            action = parse_model_response(response_text)

            print(f"  Action: {action.get('action_type')} - {action.get('category', 'N/A')}")

            # Send action to environment
            step_response = requests.post(
                f"{API_BASE_URL}/step",
                json={"action": action}
            ).json()

            done = step_response["done"]

            reward = step_response["reward"]["score"]
            print(f"  Reward: {reward:.3f}")

        except Exception as e:
            print(f"Error during step {step}: {e}")
            break

    # Get grader score
    print(f"\nEpisode complete. Getting grader score...")

    grader_response = requests.post(f"{API_BASE_URL}/grader")

    if grader_response.status_code != 200:
        print(f"Failed to get grader score: {grader_response.text}")
        return {"error": "Failed to get grader score"}

    grader_result = grader_response.json()

    return grader_result


def main():
    """Run baseline on all tasks."""

    print("="*60)
    print("Email Triage Baseline Evaluation")
    print("="*60)

    # Check API key
    check_openai_key()

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Check if API is running
    try:
        health = requests.get(f"{API_BASE_URL}/health")
        if health.status_code != 200:
            print(f"ERROR: API not responding at {API_BASE_URL}")
            print("Please start the API server first:")
            print("  uvicorn app:app --host 0.0.0.0 --port 7860")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"ERROR: Cannot connect to API at {API_BASE_URL}")
        print("Please start the API server first:")
        print("  uvicorn app:app --host 0.0.0.0 --port 7860")
        sys.exit(1)

    print(f"API: {API_BASE_URL}")
    print(f"Model: {MODEL}")
    print()

    # Run all tasks
    tasks = ["easy", "medium", "hard"]
    results = {}

    for task_id in tasks:
        result = run_task(client, task_id)
        results[task_id] = result

    # Print summary
    print("\n" + "="*60)
    print("BASELINE RESULTS")
    print("="*60)

    for task_id in tasks:
        result = results[task_id]
        if "error" in result:
            print(f"Task: {task_id:8s} | Error: {result['error']}")
        else:
            score = result["score"]
            print(f"Task: {task_id:8s} | Score: {score:.3f} ({score*100:.1f}%)")

    print("="*60)
    print("\nBreakdowns:")
    for task_id in tasks:
        result = results[task_id]
        if "error" not in result:
            print(f"\n{task_id.upper()}:")
            print(f"  {result['feedback']}")
            print(f"  Breakdown: {json.dumps(result['breakdown'], indent=4)}")


if __name__ == "__main__":
    main()

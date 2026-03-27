# For Evaluators

This document provides quick testing instructions for the Email Triage OpenEnv environment.

## Quick Start

**Live API:** https://geekyraghav13-openenv-email-triage.hf.space

### 1. Health Check
```bash
curl https://geekyraghav13-openenv-email-triage.hf.space/health
```

### 2. Get All Tasks
```bash
curl https://geekyraghav13-openenv-email-triage.hf.space/tasks
```

### 3. Run Complete Episode
```bash
# Reset
curl -X POST https://geekyraghav13-openenv-email-triage.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy"}'

# Take action
curl -X POST https://geekyraghav13-openenv-email-triage.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"action_type": "classify", "category": "bug_report", "reasoning": "Test"}}'

# Get score (after 10 steps)
curl -X POST https://geekyraghav13-openenv-email-triage.hf.space/grader
```

## Automated Testing

Run the comprehensive test suite:

```bash
python3 evaluator_test_example.py
```

This tests:
- ✅ All 8 endpoints
- ✅ All 3 tasks (easy, medium, hard)
- ✅ Reward function (0.0-1.0 range)
- ✅ Partial credit (not binary)
- ✅ Deterministic grading
- ✅ Complete episode workflow

## Expected Results

- **Easy task baseline:** 0.85-0.95
- **Medium task baseline:** 0.60-0.75
- **Hard task baseline:** 0.40-0.60

## Key Features

- ✅ 59 email templates across 7 categories
- ✅ 3 difficulty levels with progressive complexity
- ✅ Multi-turn email threads (hard task)
- ✅ Deterministic keyword-based grading
- ✅ Partial credit reward shaping
- ✅ Full OpenEnv specification compliance

## Architecture

```
Agent → Step (classify/prioritize/reply/escalate/archive/skip)
       ↓
    Observation (email + context)
       ↓
    Reward (0.0-1.0 with partial credit)
       ↓
    Grader (deterministic scoring)
```

## Contact

For questions or issues, see the README.md documentation.

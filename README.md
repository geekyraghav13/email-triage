---
title: Email Triage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
tags:
  - openenv
  - email
  - triage
  - reinforcement-learning
  - nlp
---

# Email Triage OpenEnv Environment

## Overview

Email Triage is a production-grade OpenEnv environment that simulates real-world email management tasks. Unlike toy environments or games, this represents a genuine task that humans perform daily: triaging incoming emails by classifying them, prioritizing responses, and taking appropriate action.

This environment is designed for training and evaluating AI agents on a practical, high-utility task with clear real-world applications. The environment supports three difficulty levels with progressive complexity, from basic classification to full triage including contextual reply generation and escalation decisions.

The environment provides rich reward shaping with partial credit, making it suitable for reinforcement learning research while maintaining deterministic grading for fair evaluation.

## Environment Description

The Email Triage environment simulates an inbox management system where an AI agent processes emails sequentially. Each episode presents a series of emails that the agent must handle appropriately.

**Key Features:**
- **Realistic email scenarios**: Synthetic emails across 7 categories (bug reports, feature requests, billing, inquiries, spam, escalations, feedback)
- **Multi-turn threads**: Hard difficulty includes email conversations with context from previous messages
- **Ambiguous cases**: Medium and hard tasks include emails that require judgment and interpretation
- **Partial credit rewards**: Granular reward function (0.0-1.0) that provides signal for partial correctness
- **Progressive difficulty**: Three tasks ranging from simple classification to full triage with replies
- **Deterministic grading**: Same actions always produce the same score

## Action Space

The agent can take the following actions:

| Action Type | Description | Required Fields | When to Use |
|------------|-------------|-----------------|-------------|
| `classify` | Categorize the email | `action_type`, `category` | Basic classification (easy task) |
| `prioritize` | Categorize and set priority | `action_type`, `category`, `priority` | Triage workflow (medium task) |
| `reply` | Send a response | `action_type`, `category`, `priority`, `reply_text` | When email needs a response (hard task) |
| `escalate` | Forward to specialist | `action_type`, `category`, `priority`, `escalate_to` | Issues requiring expert attention (hard task) |
| `archive` | File away email | `action_type` | Spam or resolved issues (hard task) |
| `skip` | Skip processing | `action_type` | Not recommended (penalty applied) |

**Categories:**
- `bug_report` - Technical issues and bugs
- `feature_request` - Requests for new functionality
- `billing` - Payment and subscription issues
- `general_inquiry` - General questions and support
- `spam` - Unwanted/unsolicited emails
- `escalation` - Issues requiring management attention
- `feedback` - User feedback and suggestions

**Priority Levels:**
- `urgent` - Immediate attention required
- `high` - Important, address soon
- `medium` - Normal priority
- `low` - Can wait

**Escalation Targets:**
- `manager` - Team manager
- `legal` - Legal department
- `billing_specialist` - Billing team
- `technical_lead` - Technical specialist
- `executive` - Executive team

**Optional Fields:**
- `reasoning` - Explanation for the decision (recommended, small penalty if omitted)

## Observation Space

Each observation contains:

| Field | Type | Description |
|-------|------|-------------|
| `current_email` | Email | The email being processed |
| `inbox_size` | int | Total emails in episode |
| `processed_count` | int | Number of emails already processed |
| `time_remaining` | int | Steps remaining before episode ends |
| `context` | str \| null | Thread context for multi-turn conversations (hard task only) |
| `task_id` | str | Current task identifier |
| `step_number` | int | Current step in episode |

**Email Object:**
| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique email identifier |
| `sender` | str | Email sender address |
| `subject` | str | Email subject line |
| `body` | str | Email body text |
| `timestamp` | str | When email was sent |
| `has_attachment` | bool | Whether email has attachments |
| `thread_id` | str \| null | Thread identifier for multi-turn conversations |
| `reply_to` | str \| null | Previous email being replied to |

## Tasks

### Task 1: Email Classification (Easy)

**Objective:** Classify 10 clear-cut emails into the correct categories.

**Details:**
- Email count: 10
- Time limit: 10 steps
- Allowed actions: `classify`
- Email types: Clear, unambiguous emails evenly distributed across categories (no escalations)

**Grading Criteria:**
- Exact match on category
- Score = correct classifications / total emails
- Expected baseline score: 0.85-0.95

**Strategy:**
- Focus on accuracy over speed
- Each email has clear indicators of its category
- No escalations or spam in this task

### Task 2: Priority Triage (Medium)

**Objective:** Classify AND prioritize 15 emails, including some ambiguous cases, with time pressure.

**Details:**
- Email count: 15
- Time limit: 15 steps
- Allowed actions: `classify`, `prioritize`
- Email types: Mix of clear and ambiguous emails requiring judgment

**Grading Criteria:**
- 50% weight on category accuracy
- 30% weight on priority accuracy
- 20% weight on processing order (urgent/high priority emails should be processed first)
- Expected baseline score: 0.60-0.75

**Strategy:**
- Use `prioritize` action to set both category and priority
- Process urgent/high priority emails earlier for better order efficiency score
- Some emails may have conflicting signals - use reasoning field to explain decisions

### Task 3: Full Triage & Response (Hard)

**Objective:** Classify, prioritize, and compose appropriate replies for 20 emails including multi-turn threads.

**Details:**
- Email count: 20
- Time limit: 20 steps
- Allowed actions: ALL (`classify`, `prioritize`, `reply`, `escalate`, `archive`, `skip`)
- Email types: Mix of single emails and multi-turn threads, some require escalation

**Grading Criteria:**
- 25% category accuracy
- 15% priority accuracy
- 35% reply quality (semantic elements + structure)
- 15% escalation decisions (escalate when needed, reply when appropriate)
- 10% efficiency (use appropriate action types)
- Expected baseline score: 0.40-0.60

**Strategy:**
- Archive spam emails using `archive` action
- Escalate emails marked as escalations or requiring specialist attention
- For replies, include:
  - Greeting (Hi, Hello, Dear)
  - Acknowledgment/empathy (Thank you, I understand, etc.)
  - Category-specific keywords addressing the issue
  - Next steps or resolution
  - Professional sign-off (Best regards, etc.)
- Read `context` field for multi-turn threads to understand conversation history
- Use appropriate action types: archive for spam, escalate for escalations, reply for others

## Reward Function

The reward function provides granular feedback with partial credit.

**Components:**

1. **Accuracy Component** (varies by task)
   - Category correctness: 1.0 for exact match, 0.5 for similar categories, 0.0 otherwise
   - Priority correctness: 1.0 for exact match, 0.6 for one level off, 0.3 for two levels off

2. **Quality Component** (hard task only)
   - Reply quality score (0.0-1.0) based on:
     - Presence of greeting (0.1)
     - Acknowledgment/empathy (0.15)
     - Category-specific keywords (0.25)
     - Next steps/resolution (0.2)
     - Professional sign-off (0.1)
     - Appropriate tone (0.1)
     - Sufficient length (0.1)

3. **Efficiency Component**
   - Order efficiency (medium/hard): Higher priority emails processed earlier
   - Action type appropriateness (hard): Using correct action for email type

4. **Penalties**
   - Skip action: -0.1
   - No reasoning provided: -0.02

**Per-step reward:** Weighted sum of components minus penalties (clamped to [0.0, 1.0])

**Episode reward:** Mean of per-step rewards × completion bonus (1.0 if completed, 0.8 otherwise)

**Key principle:** Rewards are NEVER binary. Partial correctness earns partial reward.

## Setup & Usage

### Local Development

#### Build and run with Docker:

```bash
cd openenv-email-triage

# Build the Docker image
docker build -t email-triage .

# Run the container
docker run -p 7860:7860 email-triage
```

The API will be available at `http://localhost:7860`

#### Run without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Running Baseline

The baseline script uses OpenAI's API to run an agent against all three tasks.

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=your-key-here

# Ensure the API server is running (in another terminal)
uvicorn app:app --host 0.0.0.0 --port 7860

# Run baseline
python baseline.py
```

The baseline will:
1. Connect to the running API server
2. Run GPT-4 mini against all three tasks
3. Print per-step rewards and final scores
4. Display detailed breakdowns

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Environment metadata (HF Spaces ping) |
| GET | `/health` | Health check |
| POST | `/reset` | Reset environment with task ID |
| POST | `/step` | Execute action, get observation/reward |
| GET | `/state` | Get full environment state |
| GET | `/tasks` | Get all task definitions |
| POST | `/grader` | Get final score for completed episode |
| GET | `/baseline` | Baseline information |

### Example Usage

```python
import requests

# Reset for easy task
response = requests.post("http://localhost:7860/reset", json={"task_id": "easy"})
observation = response.json()["observation"]

# Take action
action = {
    "action_type": "classify",
    "category": "bug_report",
    "reasoning": "Email describes a crash on startup"
}

response = requests.post("http://localhost:7860/step", json={"action": action})
result = response.json()

print(f"Reward: {result['reward']['score']}")
print(f"Done: {result['done']}")

# After episode completes
grader_response = requests.post("http://localhost:7860/grader")
final_score = grader_response.json()["score"]
print(f"Final Score: {final_score}")
```

## Baseline Scores

Baseline scores using GPT-4 mini (expected ranges):

| Task | Expected Score | Notes |
|------|----------------|-------|
| Easy | 0.85-0.95 | Strong performance on clear classification |
| Medium | 0.60-0.75 | Moderate performance, struggles with ambiguous cases |
| Hard | 0.40-0.60 | Challenging, reply quality and context handling are difficult |

**Note:** Actual scores may vary based on model version and prompt engineering.

## Technical Details

### Pydantic Models

All data structures use Pydantic v2 for type safety:

- `Email` - Email object with metadata
- `Observation` - What the agent sees at each step
- `Action` - Agent's decision and parameters
- `Reward` - Score with breakdown and feedback
- `EnvironmentState` - Complete internal state

### State Management

- **Clean reset:** `reset()` produces completely fresh state with no leakage between episodes
- **Deterministic:** Same random seed produces same email sequence
- **Episode boundaries:** Episodes terminate when all emails processed or time limit reached
- **Action history:** All actions stored for grading

### Grader Internals

Graders are deterministic and use:

1. **Exact matching** for categories and priorities
2. **Keyword-based scoring** for reply quality (no LLM evaluation)
3. **Structural checks** for required reply elements
4. **Order correlation** for efficiency metrics

Same sequence of actions ALWAYS produces the same score.

### Data Generation

- 50+ email templates across all categories
- Synthetic data only (no real emails)
- Procedural generation with controlled randomness
- Templates include:
  - Clear-cut examples for easy task
  - Ambiguous cases for medium/hard tasks
  - Multi-turn threads with context
  - Edge cases (spam disguised as urgent, etc.)

## Deployment to Hugging Face Spaces

1. Create new HF Space (Docker type)
2. Tag with `openenv`
3. Push repository:
```bash
git init
git add .
git commit -m "Initial commit: Email Triage OpenEnv"
git remote add origin https://huggingface.co/spaces/USERNAME/openenv-email-triage
git push -u origin main
```

4. HF Spaces will automatically build and deploy
5. Verify deployment by accessing the Space URL

**Important:** The root endpoint `/` returns 200 status for HF Spaces health checks.

## License

MIT

## Contributing

Contributions welcome! Areas for enhancement:

- Additional email categories
- More sophisticated reply quality metrics
- Multi-agent collaboration scenarios
- Real-time difficulty adjustment
- Integration with actual email APIs (with privacy controls)

## Citation

If you use this environment in research, please cite:

```
@misc{email-triage-openenv,
  title={Email Triage: An OpenEnv Environment for Real-World Task Simulation},
  author={OpenEnv Contributors},
  year={2024},
  url={https://github.com/openenv/email-triage}
}
```

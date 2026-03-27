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

# 📧 Email Triage OpenEnv Environment

<div align="center">

**A Production-Grade Reinforcement Learning Environment for AI Agent Training**

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compatible-blue)](https://openenv.dev)
[![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-23%2F23%20Passing-success)](tests/)

[Live Demo](https://geekyraghav13-openenv-email-triage.hf.space) • [API Docs](#api-endpoints) • [Quick Start](#setup--usage) • [Tasks](#tasks)

</div>

---

## 🎯 Overview

Email Triage is a **production-grade OpenEnv environment** that simulates real-world email management tasks. Unlike toy environments or games, this represents a genuine task that humans perform daily: triaging incoming emails by classifying them, prioritizing responses, and taking appropriate action.

**Why Email Triage?**
- 📨 **Real-world utility**: Email management is a universal, practical task
- 🎓 **Educational value**: Teaches classification, prioritization, and natural language generation
- 🔄 **Progressive difficulty**: Three tasks from simple classification to contextual reply generation
- 🎯 **Rich feedback**: Granular reward shaping with partial credit (0.0-1.0)
- ⚡ **Deterministic grading**: Same actions always produce the same score

### Key Features

```
✅ 59 realistic email templates across 7 categories
✅ 3 difficulty levels (easy → medium → hard)
✅ Multi-turn conversation threads with context
✅ Partial credit reward function (not binary)
✅ Deterministic graders for fair evaluation
✅ 8 RESTful API endpoints
✅ Full OpenEnv specification compliance
✅ Docker-ready deployment
```

---

## 🏗️ Environment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Email Triage Environment                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐            │
│  │  Agent   │───→│   Step   │───→│  Grader  │            │
│  └──────────┘    └──────────┘    └──────────┘            │
│       ↓              ↓                 ↓                   │
│   Action      Observation          Reward                 │
│  (classify)   (email + state)     (0.0-1.0)              │
│       │              │                 │                   │
│       └──────────────┴─────────────────┘                   │
│                      │                                     │
│              ┌───────▼────────┐                           │
│              │  Email Dataset │                           │
│              │  (59 templates)│                           │
│              └────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎮 Action Space

The agent can perform six types of actions on each email:

| Action | Description | Required Fields | When to Use |
|--------|-------------|-----------------|-------------|
| `classify` | Categorize the email | `action_type`, `category` | Basic classification (easy task) |
| `prioritize` | Categorize + set priority | `action_type`, `category`, `priority` | Triage workflow (medium task) |
| `reply` | Send a response | `action_type`, `category`, `priority`, `reply_text` | Emails needing a response (hard) |
| `escalate` | Forward to specialist | `action_type`, `category`, `priority`, `escalate_to` | Expert attention required (hard) |
| `archive` | File away email | `action_type` | Spam or resolved issues (hard) |
| `skip` | Skip processing | `action_type` | ⚠️ Not recommended (penalty: -0.1) |

### Categories (7)
```
bug_report        → Technical issues and crashes
feature_request   → Requests for new functionality
billing           → Payment and subscription issues
general_inquiry   → General questions and support
spam              → Unwanted/unsolicited emails
escalation        → Issues requiring management attention
feedback          → User feedback and suggestions
```

### Priority Levels (4)
```
urgent  → Immediate attention required
high    → Important, address soon
medium  → Normal priority
low     → Can wait
```

### Escalation Targets (5)
```
manager            → Team manager
legal              → Legal department
billing_specialist → Billing team
technical_lead     → Technical specialist
executive          → Executive team
```

---

## 📊 Observation Space

Each step returns an observation with the current email and environment state:

```json
{
  "current_email": {
    "id": "email_0001",
    "sender": "user@example.com",
    "subject": "App crashes on startup",
    "body": "The app keeps crashing when I try to open it...",
    "timestamp": "2026-03-27 10:30:00",
    "has_attachment": false,
    "thread_id": null,
    "reply_to": null
  },
  "inbox_size": 10,
  "processed_count": 3,
  "time_remaining": 7,
  "context": null,
  "task_id": "easy",
  "step_number": 3
}
```

---

## 🎯 Tasks

### Task 1: Email Classification (Easy)

**Objective:** Classify 10 clear-cut emails into the correct categories.

```yaml
Email count: 10
Time limit: 10 steps
Allowed actions: classify
Grading: Exact category match
Expected baseline: 0.85-0.95
```

**Strategy:**
- Each email has clear indicators of its category
- No ambiguous cases or edge cases
- Focus on accuracy over speed

---

### Task 2: Priority Triage (Medium)

**Objective:** Classify AND prioritize 15 emails with some ambiguous cases.

```yaml
Email count: 15
Time limit: 15 steps
Allowed actions: classify, prioritize
Grading: 50% category + 30% priority + 20% order efficiency
Expected baseline: 0.60-0.75
```

**Strategy:**
- Use `prioritize` action to set both category and priority
- Process urgent/high priority emails first for order efficiency
- Some emails have conflicting signals requiring judgment
- Provide reasoning to explain difficult decisions

---

### Task 3: Full Triage & Response (Hard)

**Objective:** Classify, prioritize, and compose appropriate replies for 20 emails including multi-turn threads.

```yaml
Email count: 20
Time limit: 20 steps
Allowed actions: ALL (classify, prioritize, reply, escalate, archive, skip)
Grading: 25% category + 15% priority + 35% reply quality + 15% escalation + 10% efficiency
Expected baseline: 0.40-0.60
```

**Strategy:**
- Archive spam using `archive` action
- Escalate emails requiring specialist attention
- For replies, include:
  - Greeting (Hi, Hello, Dear)
  - Acknowledgment/empathy (Thank you, I understand)
  - Category-specific keywords addressing the issue
  - Next steps or resolution
  - Professional sign-off (Best regards)
- Read `context` field for multi-turn threads
- Use appropriate action types for each email

---

## 🏆 Reward Function

The reward function provides **granular feedback with partial credit** (never binary).

### Components

**1. Accuracy Component** (varies by task)
```
Category match:  1.0 = exact | 0.5 = similar | 0.0 = wrong
Priority match:  1.0 = exact | 0.6 = off by 1 | 0.3 = off by 2
```

**2. Reply Quality Component** (hard task only)
```
Greeting             → 0.10 points
Acknowledgment       → 0.15 points
Category keywords    → 0.25 points
Next steps/resolution→ 0.20 points
Professional sign-off→ 0.10 points
Appropriate tone     → 0.10 points
Sufficient length    → 0.10 points
```

**3. Efficiency Component**
```
Order efficiency     → Higher priority emails processed earlier
Action appropriateness → Using correct action type for email
```

**4. Penalties**
```
Skip action          → -0.10
No reasoning         → -0.02
```

### Scoring Formula

```python
per_step_reward = weighted_sum(components) - penalties
per_step_reward = clamp(per_step_reward, 0.0, 1.0)

episode_reward = mean(per_step_rewards) × completion_bonus
completion_bonus = 1.0 if all_emails_processed else 0.8
```

**Key Principle:** Rewards are NEVER binary. Partial correctness earns partial reward.

---

## 🚀 Setup & Usage

### Quick Start with Docker

```bash
# Build the image
docker build -t email-triage .

# Run the container
docker run -p 7860:7860 email-triage

# API is now available at http://localhost:7860
```

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Try the Live Demo

The environment is deployed on HuggingFace Spaces:

**Live API:** https://geekyraghav13-openenv-email-triage.hf.space

```bash
# Test the health endpoint
curl https://geekyraghav13-openenv-email-triage.hf.space/health

# Get all tasks
curl https://geekyraghav13-openenv-email-triage.hf.space/tasks

# Reset environment (easy task)
curl -X POST https://geekyraghav13-openenv-email-triage.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy"}'
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Environment metadata |
| `GET` | `/health` | Health check (returns 200 OK) |
| `GET` | `/tasks` | List all 3 tasks with schemas |
| `POST` | `/reset` | Reset environment for a task |
| `POST` | `/step` | Execute action, get reward |
| `GET` | `/state` | Get full environment state |
| `POST` | `/grader` | Get final episode score |
| `GET` | `/baseline` | Baseline information |

### Example: Complete Episode

```python
import requests

BASE_URL = "http://localhost:7860"

# 1. Reset environment
response = requests.post(f"{BASE_URL}/reset", json={"task_id": "easy"})
observation = response.json()["observation"]

print(f"Email: {observation['current_email']['subject']}")

# 2. Take action
action = {
    "action_type": "classify",
    "category": "bug_report",
    "reasoning": "Email describes a crash on startup"
}

response = requests.post(f"{BASE_URL}/step", json={"action": action})
result = response.json()

print(f"Reward: {result['reward']['score']}")
print(f"Feedback: {result['reward']['feedback']}")
print(f"Done: {result['done']}")

# 3. Get final score after episode
if result['done']:
    grader_response = requests.post(f"{BASE_URL}/grader")
    final_score = grader_response.json()["score"]
    print(f"Final Score: {final_score}")
```

---

## 🤖 Running Baseline Agent

The baseline uses OpenAI's GPT-4 mini to run all three tasks:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Ensure server is running
uvicorn app:app --host 0.0.0.0 --port 7860 &

# Run baseline
python baseline.py
```

**Expected Output:**
```
╔════════════════════════════════════════════╗
║   Email Triage Baseline (GPT-4 mini)      ║
╚════════════════════════════════════════════╝

Running Task: easy
✓ Step 1/10 | Reward: 1.000 | Category: bug_report
✓ Step 2/10 | Reward: 1.000 | Category: feature_request
...
Final Score: 0.92

Running Task: medium
...
Final Score: 0.71

Running Task: hard
...
Final Score: 0.53
```

---

## 📈 Baseline Scores

Results from GPT-4 mini (expected ranges):

| Task | Expected Score | Performance |
|------|----------------|-------------|
| Easy | 0.85-0.95 | ⭐⭐⭐⭐⭐ Strong classification |
| Medium | 0.60-0.75 | ⭐⭐⭐⭐ Moderate, struggles with ambiguity |
| Hard | 0.40-0.60 | ⭐⭐⭐ Challenging, reply quality difficult |

**Note:** Actual scores vary based on model version and prompt engineering.

---

## 🛠️ Technical Details

### Technology Stack

```yaml
Language: Python 3.11+
Framework: FastAPI 0.104+
Server: Uvicorn
Validation: Pydantic v2
Containerization: Docker
Deployment: HuggingFace Spaces
```

### Pydantic Models

All data structures use **Pydantic v2** for type safety:

```python
Email             # Email object with metadata
Observation       # Agent's view at each step
Action            # Agent's decision and parameters
Reward            # Score with breakdown and feedback
EnvironmentState  # Complete internal state
```

### State Management

- **Clean reset:** `reset()` produces completely fresh state
- **Deterministic:** Same random seed → same email sequence
- **Episode boundaries:** Terminates when all emails processed or time limit reached
- **Action history:** All actions stored for grading

### Grader Design

Graders are **100% deterministic** and use:

1. **Exact matching** for categories and priorities
2. **Keyword-based scoring** for reply quality (no LLM evaluation)
3. **Structural checks** for required reply elements
4. **Order correlation** for efficiency metrics

**Same actions ALWAYS produce the same score.**

### Data Generation

- **59 email templates** across all categories
- **Synthetic data only** (no real emails)
- **Procedural generation** with controlled randomness
- **Edge cases included**: spam disguised as urgent, ambiguous feature/bug requests

---

## 🧪 Testing

Run the test suite to verify everything works:

```bash
# Run all tests
python -m pytest tests/test_env.py -v

# Expected output: 23/23 tests passing
```

**Test Coverage:**
- Environment reset and state management
- Step execution and reward computation
- Grader scoring for all tasks
- API endpoint functionality
- State leakage prevention

---

## 📦 Deployment

### Deploy to HuggingFace Spaces

1. Create new HF Space (Docker SDK type)
2. Push your code:

```bash
git init
git add .
git commit -m "Initial commit: Email Triage OpenEnv"
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/openenv-email-triage
git push -u origin main
```

3. Add `openenv` tag in Space settings
4. Wait for build (3-5 minutes)
5. Test endpoints

**Important:** The root endpoint `/` must return 200 for HF health checks.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:

- Additional email categories (e.g., legal, HR, sales)
- More sophisticated reply quality metrics
- Multi-agent collaboration scenarios
- Real-time difficulty adjustment
- Integration with actual email APIs (with privacy controls)
- Support for attachments and HTML emails

---

## 📚 Citation

If you use this environment in research, please cite:

```bibtex
@misc{email-triage-openenv,
  title={Email Triage: An OpenEnv Environment for Real-World Task Simulation},
  author={OpenEnv Contributors},
  year={2024},
  url={https://huggingface.co/spaces/geekyraghav13/openenv-email-triage}
}
```

---

## 🙏 Acknowledgments

Built with:
- [OpenEnv](https://openenv.dev) specification
- [FastAPI](https://fastapi.tiangolo.com/) for the API server
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [HuggingFace Spaces](https://huggingface.co/spaces) for deployment

---

<div align="center">

**[🔗 Live Demo](https://geekyraghav13-openenv-email-triage.hf.space)** • **[📖 Documentation](#)** • **[🐛 Report Issue](https://github.com/openenv/email-triage/issues)**

Made with ❤️ for the OpenEnv community

</div>

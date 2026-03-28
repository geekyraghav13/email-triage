from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import sys
import json

from environment import EmailTriageEnv
from models import Action, Observation, Reward, EnvironmentState
from tasks import get_all_tasks, get_task
from graders import grade_episode


# FastAPI app
app = FastAPI(
    title="Email Triage OpenEnv Environment",
    description="AI agent environment for email triage - classify, prioritize, and respond to emails",
    version="1.0.0"
)


# Global environment instance
# In production, you'd want session management
env = EmailTriageEnv()


# Request/Response models
class ResetRequest(BaseModel):
    task_id: str = "easy"


class ResetResponse(BaseModel):
    observation: Observation
    message: str


class StepRequest(BaseModel):
    action: Action


class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Dict[str, Any]


class GraderResponse(BaseModel):
    score: float
    breakdown: Dict[str, Any]
    feedback: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - returns environment metadata.
    CRITICAL: HF Spaces automated ping hits this - MUST return 200.
    """
    return {
        "name": "email-triage",
        "version": "1.0.0",
        "description": "AI agent environment for email triage - classify, prioritize, and respond to emails",
        "status": "ok",
        "endpoints": {
            "reset": "/reset",
            "step": "/step",
            "state": "/state",
            "tasks": "/tasks",
            "grader": "/grader",
            "baseline": "/baseline",
            "health": "/health"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "message": "Email Triage Environment is running"}


@app.post("/reset")
async def reset(request: Request):
    """
    Reset environment to initial state for given task.

    Args:
        request: HTTP request (body is optional, defaults to "easy" task)

    Returns:
        Observation and message
    """
    try:
        # Try to parse body, default to easy if no body or parsing fails
        task_id = "easy"
        try:
            body_bytes = await request.body()
            if body_bytes:
                body = json.loads(body_bytes)
                if isinstance(body, dict) and "task_id" in body:
                    task_id = body["task_id"]
        except:
            # If body parsing fails, just use default
            pass

        # Validate task_id
        valid_tasks = ["easy", "medium", "hard"]
        if task_id not in valid_tasks:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid task_id: {task_id}. Must be one of: {valid_tasks}"
            )

        # Reset environment
        observation = env.reset(task_id=task_id)

        return {
            "observation": observation.model_dump() if hasattr(observation, 'model_dump') else observation,
            "message": f"Environment reset for task: {task_id}"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/step")
async def step(request: StepRequest) -> StepResponse:
    """
    Execute action and return (observation, reward, done, info).

    Args:
        request: StepRequest with action

    Returns:
        StepResponse with observation, reward, done, info
    """
    try:
        observation, reward, done, info = env.step(request.action)

        return StepResponse(
            observation=observation,
            reward=reward,
            done=done,
            info=info
        )

    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/state")
async def state() -> EnvironmentState:
    """
    Return current environment state.

    Returns:
        EnvironmentState with all internal state
    """
    try:
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/tasks")
async def tasks():
    """
    Get all task definitions with action schemas.

    Returns:
        List of task definitions
    """
    try:
        all_tasks = get_all_tasks()
        return {
            "tasks": all_tasks,
            "count": len(all_tasks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/grader")
async def grader() -> GraderResponse:
    """
    Return grader score for completed episode.

    Returns:
        GraderResponse with score, breakdown, and feedback
    """
    try:
        if not env.done:
            raise HTTPException(
                status_code=400,
                detail="Episode not complete. Cannot grade unfinished episode."
            )

        # Get data for grading
        actions = env.get_actions()
        ground_truths = env.get_ground_truths()
        rewards = env.rewards

        # Grade episode
        grading_result = grade_episode(
            task_id=env.task_id,
            actions=actions,
            ground_truths=ground_truths,
            step_rewards=rewards
        )

        return GraderResponse(
            score=grading_result["score"],
            breakdown=grading_result["breakdown"],
            feedback=grading_result["feedback"]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/baseline")
async def baseline():
    """
    Trigger baseline inference and return scores.

    NOTE: This endpoint triggers the baseline script.
    In a real deployment, this would be handled separately.
    For now, it returns a message to run baseline.py manually.
    """
    return {
        "message": "To run baseline, execute: python baseline.py",
        "note": "Baseline script requires OPENAI_API_KEY environment variable",
        "expected_scores": {
            "easy": 0.90,
            "medium": 0.70,
            "hard": 0.50
        }
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "detail": f"The endpoint {request.url.path} does not exist",
            "available_endpoints": [
                "/", "/health", "/reset", "/step", "/state", "/tasks", "/grader", "/baseline"
            ]
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )


# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on app startup."""
    print("=" * 60)
    print("Email Triage OpenEnv Environment")
    print("=" * 60)
    print("Version: 1.0.0")
    print("Status: Running")
    print("=" * 60)
    print("\nAvailable endpoints:")
    print("  GET  /           - Root (environment metadata)")
    print("  GET  /health     - Health check")
    print("  POST /reset      - Reset environment")
    print("  POST /step       - Execute action")
    print("  GET  /state      - Get current state")
    print("  GET  /tasks      - Get task definitions")
    print("  POST /grader     - Get grader score")
    print("  GET  /baseline   - Baseline info")
    print("=" * 60)


def main():
    """Main entry point for the server."""
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

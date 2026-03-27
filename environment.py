from typing import Tuple, Dict, Any, List, Optional
from models import Observation, Action, Reward, Email, EnvironmentState
from data.emails import generate_task_emails
from tasks import get_task, validate_action
from rewards import compute_reward
import copy


class EmailTriageEnv:
    """
    Email Triage Environment.

    Simulates email triage workflow where an agent must classify, prioritize,
    and respond to emails.
    """

    def __init__(self):
        """Initialize environment."""
        self.task_id: str = "easy"
        self.emails: List[Email] = []
        self.ground_truths: List[Dict[str, Any]] = []
        self.current_index: int = 0
        self.actions_taken: List[Dict[str, Any]] = []
        self.rewards: List[float] = []
        self.reward_objects: List[Reward] = []
        self.done: bool = False
        self.total_reward: float = 0.0
        self.step_count: int = 0

    def reset(self, task_id: str = "easy") -> Observation:
        """
        Reset environment to initial state for given task.

        CRITICAL: Must produce completely clean state. No leakage between episodes.

        Args:
            task_id: Task to load ("easy", "medium", or "hard")

        Returns:
            Initial observation
        """
        # Validate task
        task = get_task(task_id)

        # Clean reset - no state leakage
        self.task_id = task_id
        self.current_index = 0
        self.actions_taken = []
        self.rewards = []
        self.reward_objects = []
        self.done = False
        self.total_reward = 0.0
        self.step_count = 0

        # Generate emails for this task
        email_data = generate_task_emails(task_id, task["email_count"])

        self.emails = []
        self.ground_truths = []

        for email, gt_category, gt_priority, metadata in email_data:
            self.emails.append(email)
            self.ground_truths.append({
                "category": gt_category,
                "priority": gt_priority,
                "requires_escalation": metadata.get("requires_escalation", False),
                "context": metadata.get("context", None),
                "difficulty": metadata.get("difficulty", "easy")
            })

        # Return first observation
        return self._get_observation()

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Execute action and return (observation, reward, done, info).

        Args:
            action: Action to execute

        Returns:
            Tuple of (observation, reward, done, info)
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start new episode.")

        # Validate action
        is_valid, error_msg = validate_action(action, self.task_id)
        if not is_valid:
            # Return penalty for invalid action
            reward = Reward(
                score=0.0,
                breakdown={"invalid_action": -0.1},
                feedback=f"Invalid action: {error_msg}"
            )
            info = {
                "error": error_msg,
                "valid": False
            }
            return self._get_observation(), reward, self.done, info

        # Store action
        action_dict = action.model_dump()
        self.actions_taken.append(action_dict)

        # Get ground truth for current email
        gt = self.ground_truths[self.current_index]

        # Compute reward
        task = get_task(self.task_id)
        reward = compute_reward(
            action=action,
            ground_truth=gt,
            task_id=self.task_id,
            step_number=self.step_count,
            total_steps=task["email_count"]
        )

        self.rewards.append(reward.score)
        self.reward_objects.append(reward)
        self.total_reward += reward.score
        self.step_count += 1

        # Move to next email
        self.current_index += 1

        # Check if done
        if self.current_index >= len(self.emails):
            self.done = True

        # Check time limit
        task_time_limit = task.get("time_limit", len(self.emails))
        if self.step_count >= task_time_limit:
            self.done = True

        # Get next observation (or current if done)
        observation = self._get_observation()

        info = {
            "valid": True,
            "step": self.step_count,
            "emails_remaining": len(self.emails) - self.current_index,
            "total_reward": self.total_reward,
            "average_reward": self.total_reward / self.step_count if self.step_count > 0 else 0.0
        }

        return observation, reward, self.done, info

    def state(self) -> EnvironmentState:
        """
        Return full current state.

        Returns:
            EnvironmentState with all internal state
        """
        return EnvironmentState(
            task_id=self.task_id,
            emails=self.emails,
            current_index=self.current_index,
            actions_taken=self.actions_taken,
            scores=self.rewards,
            done=self.done,
            total_reward=self.total_reward
        )

    def _get_observation(self) -> Observation:
        """
        Get current observation.

        Returns:
            Observation for current state
        """
        # If done, return last email seen
        if self.current_index >= len(self.emails):
            current_email = self.emails[-1] if self.emails else Email(
                id="done",
                sender="system",
                subject="Episode Complete",
                body="All emails processed.",
                timestamp="",
                has_attachment=False
            )
            time_remaining = 0
            context = None
        else:
            current_email = self.emails[self.current_index]
            gt = self.ground_truths[self.current_index]
            context = gt.get("context", None)

            task = get_task(self.task_id)
            time_remaining = task["time_limit"] - self.step_count

        return Observation(
            current_email=current_email,
            inbox_size=len(self.emails),
            processed_count=self.current_index,
            time_remaining=max(0, time_remaining),
            context=context,
            task_id=self.task_id,
            step_number=self.step_count
        )

    def get_ground_truths(self) -> List[Dict[str, Any]]:
        """
        Get ground truth labels for all emails.
        Used by graders.

        Returns:
            List of ground truth dictionaries
        """
        return copy.deepcopy(self.ground_truths)

    def get_actions(self) -> List[Dict[str, Any]]:
        """
        Get all actions taken in current episode.

        Returns:
            List of action dictionaries
        """
        return copy.deepcopy(self.actions_taken)

    def get_episode_summary(self) -> Dict[str, Any]:
        """
        Get summary of completed episode.

        Returns:
            Dictionary with episode statistics
        """
        return {
            "task_id": self.task_id,
            "emails_processed": self.current_index,
            "total_emails": len(self.emails),
            "steps_taken": self.step_count,
            "total_reward": self.total_reward,
            "average_reward": self.total_reward / self.step_count if self.step_count > 0 else 0.0,
            "done": self.done,
            "completion_rate": self.current_index / len(self.emails) if self.emails else 0.0
        }

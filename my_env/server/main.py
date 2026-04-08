from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict, List
from .logger import setup_logger

logger = setup_logger("openenv_api")


# === Data Models ===


class Observation(BaseModel):
    """Environment observation state"""
    tasks: List[Dict[str, Any]] = []
    total_tasks: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0


class ResetResponse(BaseModel):
    """Response from /reset endpoint"""
    observation: Observation
    reward: float = 0.0
    done: bool = False


class StepResponse(BaseModel):
    """Response from /step endpoint"""
    observation: Observation
    reward: float
    done: bool


class StateResponse(BaseModel):
    """Response from /state endpoint"""
    observation: Observation


class ActionInput(BaseModel):
    """Action input from client"""
    action: Any


# === Environment ===


class TaskEnvironment:
    """Simple task management environment for OpenEnv compliance"""

    def __init__(self):
        self.tasks: List[Dict[str, Any]] = []
        self.task_id_counter = 1
        self.episode_steps = 0
        self.max_steps = 100
        self.reset()

    def reset(self) -> Observation:
        """Reset environment to initial state"""
        self.tasks = []
        self.task_id_counter = 1
        self.episode_steps = 0
        logger.info("Environment reset")
        return self._get_observation()

    def step(self, action: Dict[str, Any]) -> tuple[Observation, float, bool]:
        """Execute action and return observation, reward, done"""
        self.episode_steps += 1
        reward = 0.0
        done = False

        try:
            action_type = action.get("type", "unknown")

            if action_type == "create_task":
                text = action.get("text", "Untitled Task")
                priority = action.get("priority", "medium")
                if priority not in ["low", "medium", "high"]:
                    priority = "medium"
                new_task = {
                    "id": self.task_id_counter,
                    "text": text,
                    "priority": priority,
                    "status": "pending",
                }
                self.tasks.append(new_task)
                self.task_id_counter += 1
                reward = 1.0
                logger.info(f"Task created: {new_task}")

            elif action_type == "complete_task":
                task_id = action.get("id")
                for task in self.tasks:
                    if task["id"] == task_id:
                        task["status"] = "completed"
                        reward = 2.0
                        logger.info(f"Task completed: {task_id}")
                        break

            elif action_type == "delete_task":
                task_id = action.get("id")
                self.tasks = [t for t in self.tasks if t["id"] != task_id]
                reward = 0.5
                logger.info(f"Task deleted: {task_id}")

            elif action_type == "list_tasks":
                reward = 0.1
                logger.info("Tasks listed")

            else:
                logger.warning(f"Unknown action type: {action_type}")
                reward = -0.1

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            reward = -1.0

        # Episode ends after max steps or if all tasks completed
        done = self.episode_steps >= self.max_steps or (
            len(self.tasks) > 0 and all(t["status"] == "completed" for t in self.tasks)
        )

        return self._get_observation(), reward, done

    def get_state(self) -> Observation:
        """Get current environment state"""
        return self._get_observation()

    def _get_observation(self) -> Observation:
        """Generate observation from current state"""
        pending = sum(1 for t in self.tasks if t["status"] == "pending")
        completed = sum(1 for t in self.tasks if t["status"] == "completed")
        return Observation(
            tasks=self.tasks,
            total_tasks=len(self.tasks),
            pending_tasks=pending,
            completed_tasks=completed,
        )


# === FastAPI Application ===

env = TaskEnvironment()

app = FastAPI(title="OpenEnv Task Manager")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === OpenEnv Compliance Endpoints ===


@app.post("/reset")
def reset():
    """Reset the environment and return initial observation"""
    try:
        observation = env.reset()
        
        # Return plain dict for maximum JSON compatibility
        return {
            "observation": {
                "tasks": observation.tasks if hasattr(observation, "tasks") else [],
                "total_tasks": observation.total_tasks if hasattr(observation, "total_tasks") else 0,
                "pending_tasks": observation.pending_tasks if hasattr(observation, "pending_tasks") else 0,
                "completed_tasks": observation.completed_tasks if hasattr(observation, "completed_tasks") else 0,
            },
            "reward": float(0.0),
            "done": bool(False),
        }
    except Exception as e:
        logger.error(f"Reset failed: {e}", exc_info=True)
        # Return safe default response on any error
        return {
            "observation": {
                "tasks": [],
                "total_tasks": 0,
                "pending_tasks": 0,
                "completed_tasks": 0,
            },
            "reward": float(0.0),
            "done": bool(False),
        }


@app.post("/step")
def step(action_input: ActionInput):
    """Execute one step of the environment"""
    try:
        action_dict = action_input.action if isinstance(action_input.action, dict) else {"type": "unknown"}
        observation, reward, done = env.step(action_dict)
        
        # Return plain dict for maximum JSON compatibility
        return {
            "observation": {
                "tasks": observation.tasks if hasattr(observation, "tasks") else [],
                "total_tasks": observation.total_tasks if hasattr(observation, "total_tasks") else 0,
                "pending_tasks": observation.pending_tasks if hasattr(observation, "pending_tasks") else 0,
                "completed_tasks": observation.completed_tasks if hasattr(observation, "completed_tasks") else 0,
            },
            "reward": float(reward),
            "done": bool(done),
        }
    except Exception as e:
        logger.error(f"Step failed: {e}", exc_info=True)
        current_state = env.get_state()
        return {
            "observation": {
                "tasks": current_state.tasks if hasattr(current_state, "tasks") else [],
                "total_tasks": current_state.total_tasks if hasattr(current_state, "total_tasks") else 0,
                "pending_tasks": current_state.pending_tasks if hasattr(current_state, "pending_tasks") else 0,
                "completed_tasks": current_state.completed_tasks if hasattr(current_state, "completed_tasks") else 0,
            },
            "reward": float(-1.0),
            "done": bool(False),
        }


@app.get("/state")
def get_state():
    """Get current environment state"""
    try:
        observation = env.get_state()
        
        # Return plain dict for maximum JSON compatibility
        return {
            "observation": {
                "tasks": observation.tasks if hasattr(observation, "tasks") else [],
                "total_tasks": observation.total_tasks if hasattr(observation, "total_tasks") else 0,
                "pending_tasks": observation.pending_tasks if hasattr(observation, "pending_tasks") else 0,
                "completed_tasks": observation.completed_tasks if hasattr(observation, "completed_tasks") else 0,
            }
        }
    except Exception as e:
        logger.error(f"State retrieval failed: {e}", exc_info=True)
        return {
            "observation": {
                "tasks": [],
                "total_tasks": 0,
                "pending_tasks": 0,
                "completed_tasks": 0,
            }
        }


# === Health Check ===


@app.get("/health")
def health() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}

"""FastAPI backend with Gym-style reset/step/state endpoints."""

from __future__ import annotations

import logging
from threading import Lock
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .my_env_environment import MyEnvironment

try:
    from models import MyAction
except ModuleNotFoundError:  # pragma: no cover
    from my_env.models import MyAction


app = FastAPI(title="OpenEnv-Compatible Backend")
_env = MyEnvironment()
_env_lock = Lock()
_logger = logging.getLogger("openenv.api")
if not _logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

_DEFAULT_OBSERVATION: dict[str, Any] = {
    "echoed_message": "My Env environment ready!",
    "message_length": 0,
    "done": False,
    "reward": 0.0,
    "metadata": {},
}
_DEFAULT_STATE: dict[str, Any] = {
    "episode_id": "bootstrap",
    "step_count": 0,
}


class StepActionRequest(BaseModel):
    message: str = Field(..., description="Action message to send to the environment")


def _to_dict(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    return dict(obj)


def _step_payload(observation_obj: Any) -> dict[str, Any]:
    observation = _to_dict(observation_obj)
    reward = float(observation.get("reward") or 0.0)
    done = bool(observation.get("done", False))
    return {
        "observation": observation,
        "reward": reward,
        "done": done,
    }


def _success_response(data: dict[str, Any]) -> dict[str, Any]:
    return {"success": True, "error": None, "data": data, **data}


def _error_response(error_message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = data or {}
    return {"success": False, "error": error_message, "data": payload, **payload}


@app.post("/reset")
def reset_environment() -> dict[str, Any]:
    """
    Hard-reset environment state and return initial observation.
    Always returns a stable JSON shape and never raises uncaught errors.
    """
    global _env
    with _env_lock:
        try:
            # Recreate env instance for a true clean reset between episodes.
            _env = MyEnvironment()
            payload = _step_payload(_env.reset())
            state = _to_dict(_env.state)
            _logger.info("Environment reset completed.")
            return _success_response(
                {
                    "observation": payload["observation"],
                    "reward": payload["reward"],
                    "done": payload["done"],
                    "state": state,
                }
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            _logger.exception("Environment reset failed.")
            return _error_response(
                error,
                {
                    "observation": dict(_DEFAULT_OBSERVATION),
                    "reward": 0.0,
                    "done": True,
                    "state": dict(_DEFAULT_STATE),
                },
            )


@app.post("/step")
def step_environment(action: StepActionRequest) -> dict[str, Any]:
    """
    Apply one action step and return observation, reward, and done.
    """
    with _env_lock:
        try:
            payload = _step_payload(_env.step(MyAction(message=action.message)))
            state = _to_dict(_env.state)
            return _success_response(
                {
                    "observation": payload["observation"],
                    "reward": payload["reward"],
                    "done": payload["done"],
                    "state": state,
                }
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            _logger.exception("Environment step failed.")
            return _error_response(
                error,
                {
                    "observation": dict(_DEFAULT_OBSERVATION),
                    "reward": 0.0,
                    "done": True,
                    "state": dict(_DEFAULT_STATE),
                },
            )


@app.get("/state")
def get_state() -> dict[str, Any]:
    """
    Return current environment state.
    """
    with _env_lock:
        try:
            state = _to_dict(_env.state)
            return _success_response({"state": state})
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            _logger.exception("Environment state fetch failed.")
            return _error_response(error, {"state": dict(_DEFAULT_STATE)})


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()

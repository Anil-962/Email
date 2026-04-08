"""
OpenEnv Inference Client

Provides a simple interface to interact with the OpenEnv backend API.
"""

import requests
from typing import Any, Dict, Optional

BASE_URL = "http://localhost:7860"


class OpenEnvClient:
    """Client for communicating with OpenEnv backend"""

    def __init__(self, base_url: str = BASE_URL):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the OpenEnv backend (default: http://localhost:7860)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def reset(self) -> Dict[str, Any]:
        """
        Reset the environment to initial state.

        Returns:
            dict with keys: observation, reward, done
        """
        try:
            response = self.session.post(f"{self.base_url}/reset")
            response.raise_for_status()
            data = response.json()

            # Ensure all required keys exist
            return {
                "observation": data.get("observation", {}),
                "reward": float(data.get("reward", 0.0)),
                "done": bool(data.get("done", False)),
            }
        except requests.exceptions.RequestException as e:
            print(f"Error calling /reset: {e}")
            # Return safe default on error
            return {
                "observation": {},
                "reward": 0.0,
                "done": False,
            }

    def step(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one step of the environment with the given action.

        Args:
            action: Action dict to execute

        Returns:
            dict with keys: observation, reward, done
        """
        try:
            payload = {"action": action}
            response = self.session.post(
                f"{self.base_url}/step",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            # Ensure all required keys exist
            return {
                "observation": data.get("observation", {}),
                "reward": float(data.get("reward", 0.0)),
                "done": bool(data.get("done", False)),
            }
        except requests.exceptions.RequestException as e:
            print(f"Error calling /step: {e}")
            # Return safe default on error
            return {
                "observation": {},
                "reward": -1.0,
                "done": False,
            }

    def get_state(self) -> Dict[str, Any]:
        """
        Get the current environment state.

        Returns:
            dict with key: observation
        """
        try:
            response = self.session.get(f"{self.base_url}/state")
            response.raise_for_status()
            data = response.json()

            # Ensure observation key exists
            return {
                "observation": data.get("observation", {}),
            }
        except requests.exceptions.RequestException as e:
            print(f"Error calling /state: {e}")
            # Return safe default on error
            return {
                "observation": {},
            }

    def health_check(self) -> bool:
        """
        Check if backend is healthy.

        Returns:
            True if backend responds, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def close(self) -> None:
        """Close the session"""
        self.session.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Module-level convenience functions


def reset() -> Dict[str, Any]:
    """Reset the environment"""
    client = OpenEnvClient()
    try:
        return client.reset()
    finally:
        client.close()


def step(action: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one step with the given action"""
    client = OpenEnvClient()
    try:
        return client.step(action)
    finally:
        client.close()


def get_state() -> Dict[str, Any]:
    """Get current environment state"""
    client = OpenEnvClient()
    try:
        return client.get_state()
    finally:
        client.close()


if __name__ == "__main__":
    # Example usage
    print("OpenEnv Inference Client")
    print("=" * 50)

    # Create client
    with OpenEnvClient() as client:
        # Check health
        print(f"Backend health: {client.health_check()}")
        print()

        # Reset environment
        print("Calling /reset...")
        reset_resp = client.reset()
        print(f"Reset response: {reset_resp}")
        print()

        # Get state
        print("Calling /state...")
        state_resp = client.get_state()
        print(f"State response: {state_resp}")
        print()

        # Create a task
        print("Creating a task...")
        action = {
            "type": "create_task",
            "text": "Example task",
            "priority": "high",
        }
        step_resp = client.step(action)
        print(f"Step response: {step_resp}")
        print()

        # Complete the task
        if step_resp.get("observation", {}).get("tasks"):
            task_id = step_resp["observation"]["tasks"][0]["id"]
            print(f"Completing task {task_id}...")
            action = {
                "type": "complete_task",
                "id": task_id,
            }
            step_resp = client.step(action)
            print(f"Step response: {step_resp}")

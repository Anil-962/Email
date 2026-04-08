#!/usr/bin/env python3
"""
Baseline inference script for OpenEnv submission checks.

MANDATORY STDOUT FORMAT:
[START] task=<task_name> env=<benchmark> model=<model_name>
[STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
[END] success=<true|false> steps=<n> score=<score> rewards=<r1,r2,...,rn>
"""

from __future__ import annotations

import json
import os
from typing import Any, List, Optional

from openai import OpenAI

from my_env.client import MyEnv
from my_env.models import MyAction

API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
API_KEY = (
    os.environ.get("HF_TOKEN")
    or os.environ.get("API_KEY")
    or os.environ.get("OPENAI_API_KEY")
    or ""
)

ENV_URL = os.environ.get("ENV_URL", "http://127.0.0.1:8000")
BENCHMARK = "my-env-openenv"
MAX_STEPS_PER_TASK = 3

TASKS = [
    {"name": "easy_echo"},
    {"name": "medium_echo"},
    {"name": "hard_echo"},
]


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    safe_action = action.replace("\n", " ").replace("\r", " ").strip()
    if len(safe_action) > 120:
        safe_action = safe_action[:120]
    err = "null" if not error else error.replace("\n", " ").replace("\r", " ")
    print(
        f"[STEP] step={step} action={safe_action} reward={reward:.2f} done={str(done).lower()} error={err}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{value:.2f}" for value in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def make_openai_client() -> Optional[OpenAI]:
    if not API_KEY:
        return None
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def suggest_message(
    llm_client: Optional[OpenAI],
    task_name: str,
    step_num: int,
    last_observation: str,
) -> str:
    fallback = f"{task_name} step {step_num}: {last_observation or 'hello'}"
    if llm_client is None:
        return fallback

    try:
        prompt = (
            "Return one short action message for an echo environment. "
            "Keep it under 12 words and plain text.\n"
            f"Task: {task_name}\n"
            f"Step: {step_num}\n"
            f"Last observation: {last_observation or 'none'}"
        )
        response = llm_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You generate concise action messages."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        content = (response.choices[0].message.content or "").strip()
        return content or fallback
    except Exception:
        return fallback


def compute_score(success: bool, rewards: List[float]) -> float:
    if not success:
        return 0.0
    if not rewards:
        return 0.0
    avg_reward = sum(rewards) / len(rewards)
    # Normalize to 0..1 for checker-friendly scoring.
    return max(0.0, min(1.0, avg_reward / 10.0))


def run_task(task_name: str, llm_client: Optional[OpenAI]) -> dict[str, Any]:
    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    rewards: List[float] = []
    steps_taken = 0
    success = True
    last_observation = ""

    try:
        with MyEnv(base_url=ENV_URL).sync() as env:
            reset_result = env.reset()
            last_observation = getattr(reset_result.observation, "echoed_message", "") or ""

            for step_num in range(1, MAX_STEPS_PER_TASK + 1):
                action_text = suggest_message(llm_client, task_name, step_num, last_observation)
                try:
                    result = env.step(MyAction(message=action_text))
                    reward = float(result.reward or 0.0)
                    done = bool(result.done)
                    rewards.append(reward)
                    steps_taken = step_num
                    log_step(step_num, action_text, reward, done, None)
                    last_observation = getattr(result.observation, "echoed_message", "") or ""
                    if done:
                        break
                except Exception as exc:
                    steps_taken = step_num
                    success = False
                    log_step(step_num, action_text, 0.0, True, str(exc))
                    break
    except Exception as exc:
        success = False
        log_step(0, "connect", 0.0, True, str(exc))

    score = compute_score(success, rewards)
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {
        "task": task_name,
        "success": success,
        "steps": steps_taken,
        "score": score,
        "rewards": rewards,
    }


def main() -> None:
    llm_client = make_openai_client()
    results = [run_task(task["name"], llm_client) for task in TASKS]

    summary = {
        "benchmark": BENCHMARK,
        "env_url": ENV_URL,
        "model": MODEL_NAME,
        "average_score": (sum(item["score"] for item in results) / len(results)) if results else 0.0,
        "results": results,
    }
    with open("inference_results.json", "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)


if __name__ == "__main__":
    main()

from __future__ import annotations

import os


STEP_PROVIDER = "step"
STEP_MODEL = "step-3.7-flash"
STEP_BASE_URL = "https://api.stepfun.com/step_plan/v1"


def get_step_base_url() -> str:
    """Return the configured Step base URL or the Step Plan default."""
    return os.getenv("STEP_BASE_URL", STEP_BASE_URL).strip() or STEP_BASE_URL


def get_connection_test_model(provider_name: str | None) -> str:
    """Return a model that the selected OpenAI-compatible provider supports."""
    test_models = {
        "siliconflow": "Qwen/Qwen2.5-7B-Instruct",
        "zhipu": "glm-4",
        STEP_PROVIDER: STEP_MODEL,
    }
    return test_models.get(str(provider_name or "").lower(), "gpt-3.5-turbo")

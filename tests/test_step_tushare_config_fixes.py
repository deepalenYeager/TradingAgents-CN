import asyncio
import importlib.util
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_module(name: str, relative_path: str):
    module_path = PROJECT_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_step_defaults_are_consistent():
    defaults = _load_module(
        "step_defaults", "tradingagents/config/step_defaults.py"
    )

    assert defaults.STEP_PROVIDER == "step"
    assert defaults.STEP_MODEL == "step-3.7-flash"
    assert defaults.STEP_BASE_URL == "https://api.stepfun.com/step_plan/v1"


def test_step_connection_test_uses_step_model():
    defaults = _load_module(
        "step_defaults", "tradingagents/config/step_defaults.py"
    )

    assert defaults.get_connection_test_model("step") == "step-3.7-flash"
    assert defaults.get_connection_test_model("zhipu") == "glm-4"
    assert defaults.get_connection_test_model("unknown") == "gpt-3.5-turbo"


def test_step_base_url_can_be_overridden(monkeypatch):
    defaults = _load_module(
        "step_defaults", "tradingagents/config/step_defaults.py"
    )

    monkeypatch.setenv("STEP_BASE_URL", " https://step.example.test/v1/ ")
    assert defaults.get_step_base_url() == "https://step.example.test/v1/"


def test_tushare_custom_url_is_applied_when_enabled():
    tushare_url = _load_module(
        "tushare_url",
        "tradingagents/tushare_utils.py",
    )

    class FakeDataApi:
        _DataApi__http_url = "http://api.tushare.pro"

    api = FakeDataApi()

    assert tushare_url.apply_tushare_api_url(
        api, " https://proxy.example.test/ ", True
    )
    assert api._DataApi__http_url == "https://proxy.example.test/"


def test_tushare_custom_url_is_ignored_when_disabled_or_empty():
    tushare_url = _load_module(
        "tushare_url",
        "tradingagents/tushare_utils.py",
    )

    class FakeDataApi:
        _DataApi__http_url = "http://api.tushare.pro"

    disabled_api = FakeDataApi()
    empty_api = FakeDataApi()

    assert not tushare_url.apply_tushare_api_url(
        disabled_api, "https://proxy.example.test", False
    )
    assert not tushare_url.apply_tushare_api_url(empty_api, "  ", True)
    assert disabled_api._DataApi__http_url == "http://api.tushare.pro"
    assert empty_api._DataApi__http_url == "http://api.tushare.pro"


def test_env_example_requires_both_tushare_custom_url_settings():
    env_example = (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "TUSHARE_USE_CUSTOM_URL=true" in env_example
    assert "TUSHARE_API_URL=https://" in env_example
    assert "请勿同时设置 TUSHARE_API_URL" not in env_example


def test_runtime_model_fallbacks_do_not_revert_to_qwen():
    fallback_files = [
        "app/models/analysis.py",
        "app/core/unified_config.py",
        "app/services/analysis_service.py",
    ]

    for relative_path in fallback_files:
        source = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
        assert '"qwen-turbo"' not in source
        assert '"qwen-max"' not in source


def test_web_analysis_validates_the_selected_provider_key():
    source = (PROJECT_ROOT / "web/utils/analysis_runner.py").read_text(
        encoding="utf-8"
    )

    assert "env_key_for_provider(llm_provider)" in source
    assert 'raise ValueError("DASHSCOPE_API_KEY 环境变量未设置")' not in source


def test_main_default_config_enables_step(monkeypatch):
    from app.services.config_service import ConfigService

    class NoSaveConfigService(ConfigService):
        async def save_system_config(self, config):
            return True

    config = asyncio.run(NoSaveConfigService()._create_default_config())
    enabled_models = [model for model in config.llm_configs if model.enabled]

    assert config.default_llm == "step-3.7-flash"
    assert [(model.provider, model.model_name) for model in enabled_models] == [
        ("step", "step-3.7-flash")
    ]


def test_step_connection_request_uses_step_model(monkeypatch):
    from app.services.config_service import ConfigService
    import requests

    captured = {}

    class FakeResponse:
        status_code = 200
        text = ""

        @staticmethod
        def json():
            return {"choices": [{"message": {"content": "OK"}}]}

    def fake_post(url, json, headers, timeout):
        captured.update(url=url, json=json, headers=headers, timeout=timeout)
        return FakeResponse()

    monkeypatch.setattr(requests, "post", fake_post)

    result = ConfigService()._test_openai_compatible_api(
        "test-key",
        "阶跃星辰",
        "https://api.stepfun.com/step_plan/v1",
        "step",
    )

    assert result["success"] is True
    assert captured["url"].endswith("/step_plan/v1/chat/completions")
    assert captured["json"]["model"] == "step-3.7-flash"


def test_tushare_config_test_uses_custom_url(monkeypatch):
    from app.models.config import DataSourceConfig, DataSourceType
    from app.services.config_service import ConfigService
    import tushare as ts

    class FakeDataApi:
        _DataApi__http_url = "http://api.tushare.pro"

        def trade_cal(self, **kwargs):
            return pd.DataFrame([{"is_open": 0}])

    api = FakeDataApi()
    monkeypatch.setattr(ts, "set_token", lambda token: None)
    monkeypatch.setattr(ts, "pro_api", lambda: api)
    monkeypatch.setenv("TUSHARE_USE_CUSTOM_URL", "true")
    monkeypatch.setenv("TUSHARE_API_URL", "https://proxy.example.test")

    result = asyncio.run(
        ConfigService().test_data_source_config(
            DataSourceConfig(
                name="Tushare",
                type=DataSourceType.TUSHARE,
                api_key="complete-test-token",
            )
        )
    )

    assert result["success"] is True
    assert api._DataApi__http_url == "https://proxy.example.test"

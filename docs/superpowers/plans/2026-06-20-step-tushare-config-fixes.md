# Step and Tushare Configuration Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Step the consistent new-install fallback model and make Step and Tushare connection tests use their configured endpoints correctly.

**Architecture:** Keep the existing configuration layers, but align their fallback values and isolate Tushare SDK URL mutation in a lightweight helper shared by runtime and configuration-test paths. Preserve stored user settings and database records.

**Tech Stack:** Python, Pydantic, pytest, Tushare SDK, requests

---

### Task 1: Add Regression Tests

**Files:**
- Create: `tests/test_step_tushare_config_fixes.py`

- [ ] **Step 1: Test Step defaults and connection-test model selection**

Assert that default configuration sources use `step-3.7-flash`, and that the OpenAI-compatible test-model selector returns it for provider `step`.

- [ ] **Step 2: Test Tushare custom URL application**

Use a fake SDK API object and assert that enabled, non-empty custom URLs update `_DataApi__http_url`, while disabled configuration leaves it unchanged.

- [ ] **Step 3: Test example configuration documentation**

Assert that `.env.example` instructs users to set both `TUSHARE_USE_CUSTOM_URL` and `TUSHARE_API_URL`, without the contradictory prohibition.

- [ ] **Step 4: Run the tests and verify expected failures**

Run: `pytest -q tests/test_step_tushare_config_fixes.py`

Expected: failures for the missing shared helper, old fallback values, and old Step test model.

### Task 2: Align Step Defaults and Test Requests

**Files:**
- Modify: `app/services/config_service.py`
- Modify: `tradingagents/config/config_manager.py`
- Modify: `web/modules/config_management.py`

- [ ] **Step 1: Add Step to the main default system configuration**

Create an enabled `LLMConfig` for `ModelProvider.STEP` using model `step-3.7-flash` and the Step Plan base URL, then set `default_llm` to that model.

- [ ] **Step 2: Align legacy and Web fallback settings**

Change only missing-settings fallbacks from `dashscope/qwen-turbo` to `step/step-3.7-flash`; do not modify loaded settings files.

- [ ] **Step 3: Select the correct Step connection-test model**

Add a small provider-to-test-model selector and use `step-3.7-flash` for `step`, preserving existing special cases.

- [ ] **Step 4: Run focused tests**

Run: `pytest -q tests/test_step_tushare_config_fixes.py -k step`

Expected: all Step-focused tests pass.

### Task 3: Share Tushare Custom URL Handling

**Files:**
- Create: `tradingagents/tushare_utils.py`
- Modify: `tradingagents/dataflows/providers/china/tushare.py`
- Modify: `app/services/config_service.py`
- Modify: `.env.example`

- [ ] **Step 1: Add the lightweight URL helper**

Implement `apply_tushare_api_url(api_obj, api_url, enabled)` to trim the URL, return `False` when disabled or empty, set `_DataApi__http_url` otherwise, and return `True`.

- [ ] **Step 2: Use the helper in the runtime provider**

Replace direct private-field mutation with the shared helper and retain the existing success log.

- [ ] **Step 3: Use the helper in the configuration connection test**

After `ts.pro_api()`, load `TUSHARE_USE_CUSTOM_URL` and `TUSHARE_API_URL` from settings and apply the same helper before `trade_cal`.

- [ ] **Step 4: Correct `.env.example`**

Document that both variables must be set and that the custom service must accept the configured token source.

- [ ] **Step 5: Run focused tests**

Run: `pytest -q tests/test_step_tushare_config_fixes.py -k tushare`

Expected: all Tushare-focused tests pass.

### Task 4: Verify and Publish

**Files:**
- Verify all modified files

- [ ] **Step 1: Run the complete regression test file**

Run: `pytest -q tests/test_step_tushare_config_fixes.py`

Expected: all tests pass.

- [ ] **Step 2: Run syntax and diff checks**

Run: `python -m compileall -q app tradingagents web`

Run: `git diff --check`

Expected: both commands exit successfully.

- [ ] **Step 3: Commit implementation**

Stage only the plan, tests, and implementation files, then commit with `fix: align Step and Tushare configuration`.

- [ ] **Step 4: Push main**

Run: `git push origin main` and report the exact remote result.

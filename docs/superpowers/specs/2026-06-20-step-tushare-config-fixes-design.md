# Step and Tushare Configuration Fixes

## Scope

Repair the configuration inconsistencies identified in commits `192b894` and
`2abfb1b` without restructuring the configuration system or overwriting stored
user choices.

## Design

- Use `step`, `step-3.7-flash`, and
  `https://api.stepfun.com/step_plan/v1` consistently for newly created and
  fallback model settings.
- Make the Step provider connection test send `step-3.7-flash` instead of the
  generic `gpt-3.5-turbo` test model.
- Apply the configured Tushare custom URL to both the runtime provider and the
  configuration service's connection test.
- Keep Tushare URL application in a small shared helper so SDK private-field
  access is isolated and validated in one place.
- Correct `.env.example` so the documented variables match runtime behavior.

## Compatibility

Existing database configurations and existing `settings.json` files remain
unchanged. The new defaults apply only when configuration is absent or a code
path needs a fallback.

## Verification

Regression tests will assert default configuration values, Step connection-test
payload selection, Tushare custom URL application, and example configuration
text. Existing focused configuration tests and syntax checks will also run.

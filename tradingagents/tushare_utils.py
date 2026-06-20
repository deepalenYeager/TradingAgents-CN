from __future__ import annotations


def apply_tushare_api_url(api_obj, api_url: str | None, enabled: bool) -> bool:
    """Apply an optional custom HTTP endpoint to a Tushare SDK API object."""
    custom_url = str(api_url or "").strip()
    if not enabled or not custom_url:
        return False

    api_obj._DataApi__http_url = custom_url
    return True

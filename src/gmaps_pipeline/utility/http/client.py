import time
import requests
from requests.exceptions import RequestException

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def http_request(
    method: str,
    url: str,
    *,
    headers: dict | None = None,
    params: dict | None = None,
    json: dict | None = None,
    data: dict | None = None,
    retries: int = 3,
    base_delay: float = 1.0,
    timeout: int = 15,
) -> dict:
    """
    Perform an HTTP request with retry and exponential backoff.

    Supports JSON bodies, query parameters, and form data, making it suitable
    for a wide range of APIs (e.g., Google Places, LocationIQ).

    Retries are applied to transient failures (HTTP 429, 5xx, and network errors).
    Non-retryable errors (e.g., 4xx except 429) raise immediately.

    Args:
        method: HTTP method (e.g., "GET", "POST").
        url: Full endpoint URL.
        headers: Optional HTTP headers.
        params: Query string parameters (for GET-style APIs).
        json: JSON request body.
        data: Form-encoded request body.
        retries: Number of retry attempts.
        base_delay: Initial delay for exponential backoff.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response as a dictionary.

    Raises:
        RuntimeError: On non-retryable errors or exhausted retries.
        RequestException: On network-related failures after retries.
    """
    last_error = None

    for attempt in range(1, retries + 1):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                timeout=timeout,
            )

            # Success
            if response.ok:
                try:
                    data_out = response.json()
                except ValueError:
                    raise RuntimeError("Response is not valid JSON")

                # Catch API-level errors (common in some providers)
                if isinstance(data_out, dict) and "error" in data_out:
                    raise RuntimeError(data_out["error"])

                return data_out

            # Non-retryable error
            if response.status_code not in RETRYABLE_STATUS_CODES:
                raise RuntimeError(
                    f"{method} {url} failed ({response.status_code}): {response.text}"
                )

            last_error = RuntimeError(response.text)

        except RequestException as e:
            last_error = e

        # Backoff before retry
        if attempt < retries:
            sleep = base_delay * (2 ** (attempt - 1))
            time.sleep(sleep)

    raise RuntimeError(
        f"{method} {url} failed after {retries} retries") from last_error


def rate_limited_call(func, delay_time: int | float = 0.2, *args, **kwargs):
    # 0.2 == 5 requests per second
    result = func(*args, **kwargs)
    time.sleep(delay_time)
    return result

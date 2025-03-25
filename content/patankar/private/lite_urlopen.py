"""
lite_urlopen
============

This module provides a universal `urlopen` function that works seamlessly in both standard CPython
and browser-based Python environments such as **JupyterLite** or **Pyodide**.

It transparently detects whether it's running in a single-threaded WebAssembly kernel (JupyterLite)
and, if so, uses JavaScript's `XMLHttpRequest` to perform HTTP requests **synchronously**, bypassing
the lack of native `urllib.request.urlopen` support and the absence of async I/O.

Features:
---------
- Drop-in replacement for `urllib.request.urlopen`
- Supports both `GET` and `POST` methods
- Compatible with `PubChemPy` and similar libraries expecting a file-like `.read()` interface
- Properly raises `HTTPError` on non-2xx responses
- Returns a `FakeHTTPResponse` object mimicking the standard HTTP response stream

Limitations:
------------
- Only basic request headers are supported (no cookie or advanced session handling)
- Only synchronous access is supported (suitable for simple API calls and static resources)
- Binary responses (e.g. PNG images) are not auto-decoded and must be handled from `.read()` result

Example:
--------
```python
from lite_urlopen import urlopen
from urllib.error import HTTPError

try:
    response = urlopen("https://example.com/api", data=b"key=value")
    print(response.read().decode())
except HTTPError as e:
    print(f"HTTP error: {e.code}")
"""

import sys            # For platform detection (_LITE_)
import io             # For BytesIO (used in FakeHTTPResponse)
from urllib.parse import urlencode   # For encoding POST data
from urllib.error import HTTPError   # To simulate and raise proper errors


_LITE_ = sys.platform == 'emscripten' or "pyodide" in sys.modules

# Fallback default headers
_DEFAULT_HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

class FakeHTTPResponse(io.BytesIO):
    def __init__(self, body, status=200, headers=None, url=None):
        self.status = status
        self.headers = headers or {}
        self.url = url
        super().__init__(body.encode("utf-8") if isinstance(body, str) else body)

    def read(self, *args, **kwargs):
        self.seek(0)
        return super().read(*args, **kwargs)

    def getcode(self):
        return self.status

    def info(self):
        return self.headers

    def geturl(self):
        return self.url


def urlopen(url, data=None, headers=None):
    """
    Replacement for urllib.request.urlopen that works in JupyterLite using JavaScript's XMLHttpRequest.

    Parameters:
        url (str): The target URL.
        data (bytes or None): POST body as bytes, or None for GET.
        headers (dict): Optional HTTP headers.

    Returns:
        FakeHTTPResponse: file-like object with read() method returning response content.

    Raises:
        HTTPError: if the status code is not in 200–299.
    """
    if not _LITE_:
        from urllib.request import urlopen as std_urlopen
        return std_urlopen(url, data=data)

    import js             # Access to JavaScript APIs (e.g., XMLHttpRequest)
    headers = headers or _DEFAULT_HEADERS.copy()

    # Detect whether this is a POST or GET
    is_post = data is not None
    if isinstance(data, bytes):
        data = data.decode("utf-8")

    # Set up XMLHttpRequest
    xhr = js.XMLHttpRequest.new()
    xhr.open("POST" if is_post else "GET", url, False)  # synchronous

    for key, value in headers.items():
        xhr.setRequestHeader(key, value)

    xhr.send(data if is_post else None)

    status = xhr.status
    response_text = xhr.responseText

    if status < 200 or status >= 300:
        raise HTTPError(url, status, f"HTTP Error {status}", hdrs=None, fp=None)

    return FakeHTTPResponse(response_text, status=status, headers={}, url=url)
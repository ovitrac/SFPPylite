"""
    This code was an attempt to wrap async calls in a single-thread Pyodide environment completely asynchronous
    The solution was not kept.
    Pubchempy uses js.XMLHttpRequest() fullly synchronous even if it is depreciated today.
"""


import os
import time
import sys
import json
import asyncio
from datetime import datetime, UTC

_LITE_ = sys.platform == "emscripten" or "pyodide" in sys.modules

# Main trampoline function to run async code and sync-wait for result via file.
def sync_async_to_file(
    async_fn,
    args=(),
    kwargs=None,
    output_dir="/drive/utils/async",
    timeout=10,
    ext=".json",
    decode_json=False,
    cleanup=True,
    debugmode=False
):
    """
    Launch an async function that writes its result to a file,
    then wait synchronously until the file appears and return its content.

    Parameters:
        async_fn: async function to call
        args: positional arguments to pass
        kwargs: keyword arguments to pass
        output_dir: where to save the result file (must be writable)
        timeout: how many seconds to wait
        ext: extension of the result file (default: .json)
        decode_json: if True, decode the returned content with json.loads
        cleanup: if True, delete the output file after reading
        debugmode: if True, log events to /drive/utils/async/debug.log

    Returns:
        bytes or dict: the raw or decoded contents of the result file
    """
    kwargs = kwargs or {}
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    output_file = os.path.join(output_dir, f"{timestamp}{ext}")

    def log(msg):
        if debugmode:
            with open(os.path.join(output_dir, "debug.log"), "a") as f:
                f.write(msg + "\n")
        print(msg, flush=True)

    log(f"▶️ Starting sync_async_to_file: {args}, output_file={output_file}")

    if _LITE_:
        async def _runner():
            log("⏳ Scheduling async function...")
            await async_fn(*args, output_file=output_file, **kwargs)
            log("✅ Async function completed.")

        async def _trampoline():
            asyncio.ensure_future(_runner())
            await asyncio.sleep(0)  # yield to browser event loop immediately

        # Schedule the trampoline
        asyncio.ensure_future(_trampoline())

        loop = asyncio.get_event_loop()
        # Give the event loop a small head start to schedule the async task:
        loop.run_until_complete(asyncio.sleep(0.1))
        t0 = time.time()
        while not os.path.exists(output_file):
            if time.time() - t0 > timeout:
                log("⏰ Timeout expired while waiting for file.")
                raise TimeoutError(f"Timeout waiting for async result file: {output_file}")
            loop.run_until_complete(asyncio.sleep(0.1))

        log(f"📁 File found: {output_file}")
        with open(output_file, "rb") as f:
            content = f.read()

        if cleanup:
            try:
                os.remove(output_file)
                log(f"🧹 Cleaned up file: {output_file}")
            except Exception as e:
                log(f"⚠️ Could not delete file: {e}")

        return json.loads(content) if decode_json else content

    else:
        async def _runner_native():
            await async_fn(*args, output_file=output_file, **kwargs)

        asyncio.run(_runner_native())

        with open(output_file, "rb") as f:
            content = f.read()

        if cleanup:
            try:
                os.remove(output_file)
            except Exception:
                pass

        return json.loads(content) if decode_json else content
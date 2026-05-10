## 2025-05-07 - Stack Trace Leakage in Exception Handling
**Vulnerability:** The application was catching exceptions during initialization and directly printing `traceback.format_exc()` to the console.
**Learning:** This exposes internal file paths, dependency structures, and application state to the user interface, which is an information disclosure risk. Wait, it is good to log it to an internal log file using `logging.error(..., exc_info=True)`, but we should not print it directly to the user interface.
**Prevention:** Always fail securely by catching exceptions and returning or rendering generic, user-friendly error messages while logging the actual stack trace to internal, secure logs.

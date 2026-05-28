## 2024-05-18 - [Error Message Leakage]
**Vulnerability:** Raw exception messages were printed to user output, potentially leaking sensitive system information such as paths or OS details.
**Learning:** It is crucial to hide raw exception messages from users, providing only generic feedback, while logging the actual exception details securely for maintainers.
**Prevention:** Always use a logging module to track exact errors, and display sanitized messages to end users.

## 2024-05-20 - [Broad Exception Catching]
**Vulnerability:** Catching the base `Exception` class in file saving logic could mask unexpected errors (e.g., `KeyboardInterrupt`, memory issues, or logic bugs) and lead to unpredictable program state.
**Learning:** Catching specific exceptions (like `OSError` for file I/O) is essential for robust error handling and security, as it avoids swallowing unrelated system or logic failures.
**Prevention:** Always catch the most specific exceptions possible for a given operation.

## 2025-02-14 - Prevent Information Exposure in Exception Handling
**Vulnerability:** Raw exception strings (e.g. `except ValueError as e: print(f"...{e}")`) were directly exposed to end users via CLI output.
**Learning:** Returning or printing exact system exceptions to the user UI interface can unintentionally leak sensitive system paths, execution states, or dependency logic details.
**Prevention:** Catch the exception, securely log the detailed information using `logging.error(f"...{e}")` for internal monitoring, and display a safe, generalized error message to the end user.

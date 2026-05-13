
## 2024-05-18 - Discovering Accessibility Power in Textual TUIs
**Learning:** Textual TUI applications inherently lack standard web-like hover affordances for accessibility, making complex panels like the Chorderizer dashboard potentially difficult to parse for screen reader users or new users. However, we discovered that `tooltip` attributes are a powerful, universally supported prop across Textual interactive widgets (`Select`, `RadioSet`, `Button`, `DataTable`), providing vital contextual guidance.
**Action:** Always leverage `tooltip` attributes on interactive elements in TUI dashboard layouts to provide inline assistance, especially for domain-specific controls (like musical theory selections) where the UI layout must remain compact.
## 2024-05-18 - Destructive Action Protection in Textual TUIs
**Learning:** Terminal User Interfaces (TUIs) can suffer from accidental key presses, especially for destructive actions like clearing a list. Relying purely on single keystrokes without confirmation can lead to data loss and frustration.
**Action:** Implemented a pattern for double-tap confirmation using a state variable (`self.clear_requested_at`) and the `time` module. If the user presses the action key within a specific timeframe (e.g., 2 seconds), the action executes; otherwise, a warning notification and log message prompt them to confirm. This pattern is easily reusable for other destructive TUI actions.

## 2024-05-18 - Handling Silent Failures in TUI Actions
**Learning:** When a user initiates an action (like adding an item) but hasn't met the prerequisites (like selecting the item first), failing silently creates a poor user experience. Users need immediate, clear feedback on what went wrong and how to fix it.
**Action:** Added explicit checks for prerequisites before executing actions. If the check fails, present a clear, actionable warning message using both the application's logging mechanism (`self.log_status`) and the TUI framework's notification system (`self.notify`).

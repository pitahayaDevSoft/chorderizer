
## 2024-05-18 - Discovering Accessibility Power in Textual TUIs
**Learning:** Textual TUI applications inherently lack standard web-like hover affordances for accessibility, making complex panels like the Chorderizer dashboard potentially difficult to parse for screen reader users or new users. However, we discovered that `tooltip` attributes are a powerful, universally supported prop across Textual interactive widgets (`Select`, `RadioSet`, `Button`, `DataTable`), providing vital contextual guidance.
**Action:** Always leverage `tooltip` attributes on interactive elements in TUI dashboard layouts to provide inline assistance, especially for domain-specific controls (like musical theory selections) where the UI layout must remain compact.
## 2024-05-12 - Destructive Action Confirmation in TUI
**Learning:** Terminal User Interfaces (TUIs) can be prone to accidental keystrokes. Important destructive actions, such as clearing user data (like the chord progression list), should implement confirmation mechanisms. A simple double-press within a short time frame (e.g., 2 seconds) provides safety without disrupting keyboard-driven workflows.
**Action:** When implementing destructive keyboard shortcuts in TUI apps, check if there's a mechanism to confirm the action (like tracking the time since the last press of the same key) to prevent accidental data loss.

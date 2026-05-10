
## 2024-05-18 - Discovering Accessibility Power in Textual TUIs
**Learning:** Textual TUI applications inherently lack standard web-like hover affordances for accessibility, making complex panels like the Chorderizer dashboard potentially difficult to parse for screen reader users or new users. However, we discovered that `tooltip` attributes are a powerful, universally supported prop across Textual interactive widgets (`Select`, `RadioSet`, `Button`, `DataTable`), providing vital contextual guidance.
**Action:** Always leverage `tooltip` attributes on interactive elements in TUI dashboard layouts to provide inline assistance, especially for domain-specific controls (like musical theory selections) where the UI layout must remain compact.
## 2024-05-18 - Chorderizer Textual TUI Tooltips and Confirmations
**Learning:** Adding standard UX micro-interactions like tooltips, notifications, and double-press confirmations works seamlessly in terminal applications built with Textual, significantly improving discoverability and preventing destructive actions (e.g. clearing progression buffers) without cluttering the UI.
**Action:** Always verify if destructive TUI commands have a safeguard or confirmation mechanism, and utilize Textual's built-in `.tooltip` properties on components to provide context when space is limited.

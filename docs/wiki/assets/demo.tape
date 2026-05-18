# VHS tape script for Chorderizer PRO Demo
Output demo.gif

Set Shell "pwsh"
Set FontSize 16
Set Width 1600
Set Height 900
Set Padding 30
Set Theme "Catppuccin Mocha"

# Start the app
Type ".venv\Scripts\python.exe -m chorderizer.chorderizer"
Enter
Sleep 4s

# Select Tonic
Tab 2
Sleep 500ms
Type "j"
Sleep 500ms
Enter
Sleep 1s

# Select Scale (Dorian)
Tab
Type "jjjj" 
Sleep 500ms
Enter
Sleep 1s

# Toggle Extensions (7ths)
Tab
Type "jj"
Type " "
Sleep 1s

# Chord Selection
Tab 8
Sleep 800ms
Type "j"
Sleep 500ms
Type "a"
Sleep 800ms
Type "j"
Type "a"
Sleep 800ms
Type "j"
Type "a"
Sleep 1.5s

# Manual
Type "h"
Sleep 3s
Type "escape"
Sleep 1s

# Export
Type "e"
Sleep 2s

# Exit
Type "q"
Sleep 1s

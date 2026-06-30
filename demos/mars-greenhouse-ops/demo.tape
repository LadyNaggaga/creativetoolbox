# vhs script for a clean, repeatable GIF of the magic moment.
# https://github.com/charmbracelet/vhs  ->  vhs demo.tape
Output assets/demo.gif
Set FontFamily "JetBrains Mono"
Set FontSize 18
Set Width 1100
Set Height 640
Set Theme { "background": "#D6D6D4", "foreground": "#1A1A1A" }
Type "make demo"
Enter
Sleep 6s

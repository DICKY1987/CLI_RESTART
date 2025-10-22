# Desktop Shortcut - CLI_SYSTEM

## ✅ Shortcut Created Successfully

A desktop shortcut named **"CLI_SYSTEM"** has been created on your desktop.

### Shortcut Details

- **Name**: CLI_SYSTEM
- **Location**: `C:\Users\Richard Wilks\Desktop\CLI_SYSTEM.lnk`
- **Target**: `python.exe -m gui_terminal.main`
- **Working Directory**: `C:\Users\Richard Wilks\CLI_RESTART`
- **Description**: CLI Orchestrator - Professional Workflow Management

### How to Use

1. **Double-click** the "CLI_SYSTEM" icon on your desktop
2. The CLI Orchestrator GUI will launch
3. Start browsing and executing workflows!

### Manual Creation (If Needed)

If you need to recreate the shortcut:

```bash
# Run the batch file
cd CLI_RESTART
scripts\create_desktop_shortcut.cmd

# Or run PowerShell script directly
powershell -ExecutionPolicy Bypass -File scripts\create_desktop_shortcut.ps1
```

### Customization

You can customize the shortcut by:
1. Right-click the shortcut → Properties
2. Modify:
   - Target path
   - Working directory
   - Icon (if you have a custom .ico file)
   - Run options (minimized, maximized, normal)

### Icon

Currently using the default Python icon. To use a custom icon:

1. Place your `.ico` file at: `CLI_RESTART\docs\gui\cli_system.ico`
2. Run the shortcut creation script again
3. The new icon will be applied

### Troubleshooting

**Shortcut doesn't launch GUI:**
1. Ensure PyQt6 is installed: `pip install PyQt6`
2. Verify Python path is correct in shortcut properties
3. Try launching manually: `cd CLI_RESTART && python -m gui_terminal.main`

**Python not found:**
- Update the shortcut target to point to your Python installation
- Default location: `C:\Program Files\Python312\python.exe`

**Working directory error:**
- Ensure the working directory in shortcut properties points to: `C:\Users\Richard Wilks\CLI_RESTART`

## Quick Launch Alternatives

### Start Menu (Optional)

Create a Start Menu entry:
```powershell
# Copy shortcut to Start Menu
Copy-Item "$env:USERPROFILE\Desktop\CLI_SYSTEM.lnk" "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\"
```

### Taskbar Pin (Optional)

1. Locate "CLI_SYSTEM" on desktop
2. Right-click → "Pin to taskbar"
3. Access from taskbar anytime!

### Command Line Launch

You can always launch from command line:
```bash
# From anywhere
cli-orchestrator-gui

# Or directly with Python
python -m gui_terminal.main
```

## Scripts Provided

1. **create_desktop_shortcut.ps1** - PowerShell script
2. **create_desktop_shortcut.cmd** - Batch file wrapper

Both scripts create the same shortcut and can be run anytime to recreate it.

---

**Enjoy your CLI Orchestrator GUI!** 🚀

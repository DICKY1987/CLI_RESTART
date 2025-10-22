from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback import error handling
    yaml = None

try:
    from gui_terminal.plugins.manager import PluginManager
    from gui_terminal.security.policy_manager import PolicyManager
except Exception:
    PolicyManager = None  # type: ignore
    PluginManager = None  # type: ignore


def load_default_config() -> dict:
    cfg_path = Path(__file__).resolve().parents[2] / "config" / "default_config.yaml"
    try:
        if yaml is None:
            return {}
        with cfg_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def main(argv: list[str] | None = None) -> int:
    """Minimal entry for the GUI Terminal scaffold.

    - If PyQt6 is available, print a notice about forthcoming GUI initialization.
    - If PyQt6 is not installed, remain headless and exit gracefully.
    - Always parse default configuration to validate file presence.
    """
    _ = load_default_config()
    # Instantiate policy manager to validate security config presence
    if PolicyManager is not None:
        try:
            pm = PolicyManager()
            ok, reason = pm.command_allowed("echo hello")
            _ = (ok, reason)
        except Exception:
            pass

    # Initialize plugins if configured
    cfg = _
    try:
        if PluginManager is not None and cfg:
            plug_cfg = cfg.get("plugins") or {}
            if plug_cfg.get("enabled"):
                dirs = plug_cfg.get("plugin_directories", []) or []
                pmgr = PluginManager(dirs)
                for rec in pmgr.discover():
                    pmgr.load(rec)
                pmgr.activate_all({"mode": "headless", "version": "0.1.0"})
    except Exception:
        # Non-fatal if plugin subsystem fails at this stage
        pass

    try:
        # Import lazily so this module works without GUI deps installed.
        from PyQt6 import QtWidgets  # type: ignore

        from gui_terminal.ui.main_window_modern import ModernMainWindow

        app = QtWidgets.QApplication([])
        app.setApplicationName("CLI Orchestrator")
        app.setOrganizationName("CLI Orchestrator Team")

        win = ModernMainWindow(_)
        win.show()
        return app.exec()

    except ImportError as e:
        print(
            "[gui_terminal] Running in headless mode (PyQt6 not available). "
            "Install PyQt6 to use the GUI: pip install cli-orchestrator[gui]"
        )
        print(f"Error: {e}")
    except Exception as e:
        print(f"[gui_terminal] GUI initialization failed: {e}")
        import traceback
        traceback.print_exc()

    return 0


if __name__ == "__main__":  # pragma: no cover - manual invocation path
    raise SystemExit(main(sys.argv[1:]))

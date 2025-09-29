"""
EAFIX CLI Commands Package
Contains all command modules for the trading system CLI
"""

from .analysis import app as analysis_app
from .guardian import app as guardian_app
from .setup import app as setup_app
from .system import app as system_app
from .trading import app as trading_app

__all__ = ["trading_app", "guardian_app", "system_app", "analysis_app", "setup_app"]

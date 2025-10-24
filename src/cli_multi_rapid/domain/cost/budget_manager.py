from __future__ import annotations

from datetime import date
from typing import Any, Optional

from .models import BudgetLimit


class BudgetManager:
    """Budget enforcement logic and limit checks."""

    def check_limits(
        self,
        get_daily_usage: callable,
        budget: Optional[BudgetLimit] = None,
        tokens_to_spend: int = 0,
    ) -> dict[str, Any]:
        if budget is None:
            budget = BudgetLimit()

        daily_usage = get_daily_usage(date.today())
        current_tokens = daily_usage.get("total_tokens", 0)
        current_cost = daily_usage.get("total_cost", 0.0)

        projected_tokens = current_tokens + tokens_to_spend
        projected_cost = current_cost + (tokens_to_spend * 0.00001)

        return {
            "within_daily_token_limit": projected_tokens <= budget.daily_token_limit,
            "within_daily_cost_limit": projected_cost <= budget.daily_cost_limit,
            "within_workflow_limit": tokens_to_spend <= budget.per_workflow_limit,
            "current_tokens": current_tokens,
            "current_cost": current_cost,
            "projected_tokens": projected_tokens,
            "projected_cost": projected_cost,
            "daily_token_limit": budget.daily_token_limit,
            "daily_cost_limit": budget.daily_cost_limit,
            "workflow_limit": budget.per_workflow_limit,
            "warn_if_over": projected_cost >= (budget.daily_cost_limit * budget.warn_threshold),
        }


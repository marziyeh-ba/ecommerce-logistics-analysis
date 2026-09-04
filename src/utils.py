"""Reusable helpers for the Olist delivery-performance analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve


def calculate_delivery_delay(
    dataframe: pd.DataFrame,
    actual_column: str,
    estimated_column: str,
) -> pd.Series:
    """Return calendar-day delay; positive values indicate a late delivery."""

    actual = pd.to_datetime(dataframe[actual_column], errors="coerce")
    estimated = pd.to_datetime(dataframe[estimated_column], errors="coerce")
    return (actual - estimated).dt.days


def summarise_performance(
    dataframe: pd.DataFrame,
    group_column: str,
    minimum_orders: int = 1,
) -> pd.DataFrame:
    """Build a consistent order, delivery, review, and revenue scorecard."""

    summary = (
        dataframe.groupby(group_column, dropna=False)
        .agg(
            order_count=("order_id", "count"),
            on_time_rate=("on_time", "mean"),
            avg_delay_days=("delivery_delay_days", "mean"),
            avg_review=("review_score", "mean"),
            total_revenue=("total_revenue", "sum"),
        )
        .query("order_count >= @minimum_orders")
        .reset_index()
    )

    summary["on_time_rate"] = (summary["on_time_rate"] * 100).round(1)
    summary["avg_delay_days"] = summary["avg_delay_days"].round(2)
    summary["avg_review"] = summary["avg_review"].round(2)
    return summary


def best_f1_threshold(y_true: pd.Series, probabilities: np.ndarray) -> dict[str, float]:
    """Select a classification threshold on validation data by maximum F1."""

    precision, recall, thresholds = precision_recall_curve(y_true, probabilities)
    if len(thresholds) == 0:
        return {"threshold": 0.5, "precision": 0.0, "recall": 0.0, "f1": 0.0}

    precision = precision[:-1]
    recall = recall[:-1]
    denominator = precision + recall
    f1 = np.divide(
        2 * precision * recall,
        denominator,
        out=np.zeros_like(denominator),
        where=denominator > 0,
    )
    best_index = int(np.nanargmax(f1))
    return {
        "threshold": float(thresholds[best_index]),
        "precision": float(precision[best_index]),
        "recall": float(recall[best_index]),
        "f1": float(f1[best_index]),
    }

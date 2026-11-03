from typing import Any

import numpy as np


def calculate_metrics(
    y_true: np.ndarray, preds: np.ndarray, drop_na: bool = True
) -> dict[str, Any]:
    residuals = preds - y_true

    if drop_na:
        residuals = residuals[~np.isnan(residuals)]

    sse = (residuals**2).sum()
    mse = (residuals**2).mean()

    return {
        "sse": sse,
        "mse": mse,
        "rmse": np.sqrt(mse),
        "residual_std": residuals.std(),
        "residual_mean": residuals.mean(),
    }

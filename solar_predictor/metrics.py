from typing import Any

import numpy as np


def calculate_metrics(
    y_true: np.ndarray, preds: np.ndarray, drop_na: bool = True
) -> dict[str, Any]:
    residuals = preds - y_true

    if drop_na:
        residuals = residuals[~np.isnan(residuals)]

    mean_squared_error = (residuals**2).mean()

    return {"mse": mean_squared_error, "rmse": np.sqrt(mean_squared_error)}

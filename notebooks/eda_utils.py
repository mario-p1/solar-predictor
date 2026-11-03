import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def line_with_slider(
    df: pd.DataFrame, window: pd.DateOffset, x: str | None = None, **kwargs
):
    fig = px.line(df, x=x, **kwargs)
    end = df.index.max() if x is None else df[x].max()
    fig.update_layout(
        xaxis={
            "rangeslider": {
                "visible": True,
                "thickness": 0.08,
            },
            "range": [end - window, end],
        },
    )
    return fig


def plot_with_residuals(
    actual: pd.Series, predicted: pd.Series, window: pd.DateOffset, title: str = ""
):
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.7, 0.3]
    )
    fig.add_trace(
        go.Scatter(x=actual.index, y=actual, name=actual.name, line_color="lightgray"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=predicted.index, y=predicted, name=predicted.name, line_color="red"
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=actual.index, y=actual - predicted, name="residuals", marker_color="red"
        ),
        row=2,
        col=1,
    )

    end = actual.index.max()
    fig.update_xaxes(range=[end - window, end])
    fig.update_xaxes(rangeslider={"visible": True, "thickness": 0.05}, row=2, col=1)
    fig.update_yaxes(title_text="residuals", row=2, col=1)
    fig.update_layout(title=title, height=800)
    return fig


def plot_decomposition(
    trend: pd.Series,
    seasonal: pd.Series,
    resid: pd.Series,
    window: pd.DateOffset,
    title: str = "",
):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03)
    fig.add_trace(
        go.Scatter(x=trend.index, y=trend, name="trend", line_color="red"),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=seasonal.index, y=seasonal, name="seasonal", line_color="red"),
        row=2,
        col=1,
    )
    fig.add_trace(
        go.Bar(x=resid.index, y=resid, name="residuals", marker_color="red"),
        row=3,
        col=1,
    )

    end = trend.index.max()
    fig.update_xaxes(range=[end - window, end])
    fig.update_xaxes(rangeslider={"visible": True, "thickness": 0.05}, row=3, col=1)
    for row, name in enumerate(("trend", "seasonal", "residuals"), start=1):
        fig.update_yaxes(title_text=name, row=row, col=1)
    fig.update_layout(title=title, height=800, showlegend=False)
    return fig

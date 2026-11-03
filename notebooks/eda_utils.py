import pandas as pd
import plotly.express as px


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

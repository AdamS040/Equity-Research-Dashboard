import plotly.graph_objects as go

def plot_equity_curve(eq_curve):
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=eq_curve["Portfolio"], name="Portfolio"))
    if "Benchmark" in eq_curve.columns:
        fig.add_trace(go.Scatter(y=eq_curve["Benchmark"], name="Benchmark"))
    fig.update_layout(title="Backtest Equity Curve", xaxis_title="Time", yaxis_title="Growth")
    return fig
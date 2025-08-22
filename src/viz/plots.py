import matplotlib.pyplot as plt

def plot_equity_curve(equity_curve, title="Portfolio Equity Curve"):
    plt.figure(figsize=(10,5))
    plt.plot(equity_curve, label="Portfolio")
    plt.title(title)
    plt.xlabel("Date")
    plt.ylabel("Equity")
    plt.legend()
    plt.grid(True)
    plt.show()

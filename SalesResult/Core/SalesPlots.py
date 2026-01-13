from matplotlib.figure import Figure
import pandas as pd

class SalesPlots:
    """
    Manages the rendering of financial visualizations onto a provided Matplotlib Figure.
    """

    def __init__(self, figure: Figure):
        """
        Args:
            figure (Figure): The canvas instance where plots will be drawn.
        """
        self.figure = figure

    def draw(self, data: pd.Series, chart_type: str, title_suffix: str, color: str, rotate_x: int):
        """
        Orchestrates the plotting process: clears the canvas and renders the requested chart.

        Args:
            data (pd.Series): The dataset to visualize (Index = Labels, Values = Numeric).
            chart_type (str): Visualization mode. Supported: "Pie Chart", "Bar Chart".
            title_suffix (str): Text appended to the chart title for context (e.g., "by Country").
            color (str): Hex code or color name (applies to Bar Chart).
            rotate_x (int): Degree of rotation for x-axis labels (applies to Bar Chart).
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if chart_type == "Pie Chart":
            self._draw_pie(ax, data, title_suffix)
        elif chart_type == "Bar Chart":
            self._draw_bar(ax, data, title_suffix, color, rotate_x)
        
        self.figure.tight_layout()

    def _draw_pie(self, ax, data, title_suffix):
        """Internal helper to render a percentage-based pie chart."""
        ax.pie(data, labels=data.index, autopct='%1.1f%%', startangle=140)
        ax.set_title(f"Revenue Share {title_suffix}")

    def _draw_bar(self, ax, data, title_suffix, color, rotate_x):
        """Internal helper to render a value-based bar chart with annotations."""
        bars = ax.bar(data.index, data.values, color=color)
        
        ax.set_title(f"Revenue Amount {title_suffix}")
        ax.set_ylabel("Revenue ($)")
        ax.ticklabel_format(style='plain', axis='y')
        ax.tick_params(axis='x', rotation=rotate_x)
        
        # Annotate bars with currency values
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'${height:,.0f}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
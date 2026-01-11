import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Assumes Core modules are in the python path
from Core.SalesAnalyzer import SalesAnalyzer
from Core.SalesPlots import SalesPlots
from Core.XlsxExport import XlsxExport

class DashboardView(tk.Frame):
    """
    The main visualization container representing the interactive dashboard.

    This class manages the UI layout, event binding for dropdowns/buttons, 
    and coordinates the flow between data analysis and plotting components.
    """

    def __init__(self, parent):
        """
        Initializes the dashboard layout and instantiates helper logic classes.

        Args:
            parent (tk.Widget): The parent container (usually root or another Frame).
        """
        super().__init__(parent)
        
        # Core logic components
        self.analyzer = SalesAnalyzer()
        self.plotter = SalesPlots(Figure(figsize=(6, 5), dpi=100))
        self.xlsx_export = XlsxExport()
        
        # State containers
        self.current_df = None
        self.current_chart_data = None

        # UI Initialization
        self.top_panel = tk.Frame(self, bg="#f0f0f0", height=50)
        self.top_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        self.lbl_revenue = tk.Label(self.top_panel, text="Total Revenue: $0", font=("Arial", 12, "bold"), bg="#f0f0f0")
        self.lbl_revenue.pack(side=tk.LEFT, padx=10)

        # View Selection (Category/Country/Age)
        tk.Label(self.top_panel, text="Group by:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(20, 5))
        self.data_view_var = tk.StringVar(value="Category")
        self.combo_data = ttk.Combobox(self.top_panel, textvariable=self.data_view_var, state="readonly", width=12)
        self.combo_data['values'] = ("Category", "Country", "Age Group")
        self.combo_data.pack(side=tk.LEFT)
        self.combo_data.bind("<<ComboboxSelected>>", self.refresh_chart)

        # Chart Type Selection (Pie/Bar)
        tk.Label(self.top_panel, text="Chart Type:", bg="#f0f0f0").pack(side=tk.LEFT, padx=(10, 5))
        self.chart_type_var = tk.StringVar(value="Pie Chart")
        self.combo_chart = ttk.Combobox(self.top_panel, textvariable=self.chart_type_var, state="readonly", width=12)
        self.combo_chart['values'] = ("Pie Chart", "Bar Chart")
        self.combo_chart.pack(side=tk.LEFT)
        self.combo_chart.bind("<<ComboboxSelected>>", self.refresh_chart)

        # Export Button
        self.btn_export = tk.Button(self.top_panel, text="Export to Excel", command=self.export_click, bg="#4CAF50", fg="white")
        self.btn_export.pack(side=tk.RIGHT, padx=10)

        # Matplotlib Canvas embedding
        self.canvas = FigureCanvasTkAgg(self.plotter.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def render(self, df):
        """
        Loads a new dataset into the dashboard and triggers the initial render.

        Args:
            df (pd.DataFrame): The raw sales data to visualize.
        """
        self.current_df = df
        total_rev = self.analyzer.calculate_total_revenue(df)
        self.lbl_revenue.config(text=f"Total Revenue: ${total_rev:,.0f}")
        self.draw_plot()

    def refresh_chart(self, event=None):
        """
        Callback for UI dropdown changes. Re-renders the chart if data is present.

        Args:
            event: The tkinter event object (unused but required for bind compatibility).
        """
        if self.current_df is not None:
            self.draw_plot()

    def draw_plot(self):
        """
        Orchestrates the data aggregation and visualization based on current UI state.

        Determines:
        1. Aggregation logic (by Category, Country, or Age).
        2. Visualization parameters (colors, labels, chart type).
        3. Updates the internal `current_chart_data` state for export purposes.
        """
        view_mode = self.data_view_var.get()
        chart_type = self.chart_type_var.get()
        
        # Configuration mapping based on selected view
        if view_mode == "Category":
            data = self.analyzer.get_category_share(self.current_df)
            title_suffix = "by Product Category"
            color = 'skyblue'
            rotate_x = 45
            
        elif view_mode == "Country":
            data = self.analyzer.get_country_share(self.current_df)
            title_suffix = "by Country"
            color = '#4CAF50'
            rotate_x = 45

        elif view_mode == "Age Group":
            data = self.analyzer.get_age_group_share(self.current_df)
            title_suffix = "by Age Group"
            color = '#FF9800'
            rotate_x = 0
            
            if data.empty:
                tk.messagebox.showwarning("No Data", "Column 'Customer_Age' not found!")
                return

        # Update state and delegate drawing
        self.current_chart_data = data
        self.plotter.draw(data, chart_type, title_suffix, color, rotate_x)
        self.canvas.draw()

    def export_click(self):
        """
        Opens a file dialog to save the currently visible aggregation to Excel.
        
        Shows a success/error message box upon completion.
        """
        if self.current_chart_data is None or self.current_chart_data.empty:
            tk.messagebox.showwarning("Export", "No data available to export.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Analysis"
        )

        if file_path:
            success, message = self.xlsx_export.save(self.current_chart_data, file_path)
            
            if success:
                tk.messagebox.showinfo("Success", message)
            else:
                tk.messagebox.showerror("Error", f"Failed to save file:\n{message}")
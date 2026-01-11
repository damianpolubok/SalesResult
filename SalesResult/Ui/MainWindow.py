import tkinter as tk
from tkinter import ttk
from Ui.HomeView import HomeView
from Ui.DashboardView import DashboardView

class MainWindow(tk.Tk):
    """
    The root application controller that manages the primary window lifecycle and navigation.

    This class orchestrates the initialization of child views (Home, Dashboard) and 
    implements the 'Mediator' pattern to handle data propagation between tabs.
    """

    def __init__(self):
        """
        Initializes the main window geometry, navigation tabs, and child views.
        """
        super().__init__()
        self.title("SalesResult")
        self.geometry("1000x600")

        # Container for tabbed navigation
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill='both')

        # Initialize Views
        # Note: on_data_ready is injected into HomeView as a callback
        self.home_view = HomeView(self.tabs, self.on_data_ready)
        self.dashboard_view = DashboardView(self.tabs)

        # Register views with the navigation controller
        self.tabs.add(self.home_view, text="Home & Data")
        self.tabs.add(self.dashboard_view, text="Sales Analysis")

    def on_data_ready(self, df):
        """
        Callback triggered when data is successfully imported in the HomeView.

        This method bridges the gap between views by:
        1. Passing the new dataset to the DashboardView for rendering.
        2. Automatically switching the active tab to the analysis view.

        Args:
            df (pd.DataFrame): The validated dataset ready for analysis.
        """
        self.dashboard_view.render(df)
        self.tabs.select(1)
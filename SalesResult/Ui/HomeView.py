import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Core.CsvImport import CsvImport

class HomeView(tk.Frame):
    """
    The primary entry point for data ingestion. 
    
    This view handles file selection, format validation, and provides a 
    tabular preview of the raw dataset using a distinct visual style.
    """

    def __init__(self, parent, on_data_loaded_callback):
        """
        Initializes the import interface and grid layout.

        Args:
            parent (tk.Widget): The parent container (Notebook or Window).
            on_data_loaded_callback (callable): A function to invoke when data is successfully 
                                                loaded (signature: f(df: pd.DataFrame)).
        """
        super().__init__(parent)
        self.on_data_loaded = on_data_loaded_callback
        self.full_data = None
        
        self.configure_styles()
        
        main_frame = tk.Frame(self, bg="#f5f5f5")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Section
        header_frame = tk.Frame(main_frame, bg="#f5f5f5")
        header_frame.pack(fill=tk.X, pady=(20, 10), padx=20)

        lbl_title = tk.Label(
            header_frame, 
            text="Sales Data Dashboard", 
            font=("Segoe UI", 24, "bold"),
            bg="#f5f5f5", fg="#333"
        )
        lbl_title.pack(side=tk.TOP)

        lbl_subtitle = tk.Label(
            header_frame, 
            text="Import your CSV file to generate charts and analyze revenue.",
            font=("Segoe UI", 11),
            bg="#f5f5f5", fg="#666"
        )
        lbl_subtitle.pack(side=tk.TOP, pady=5)

        # Controls Section
        controls_frame = tk.Frame(main_frame, bg="#f5f5f5")
        controls_frame.pack(pady=10)

        self.btn_import = ttk.Button(
            controls_frame, 
            text="Import CSV Data", 
            command=self.import_click,
            style="Accent.TButton"
        )
        self.btn_import.pack(side=tk.LEFT, padx=(0, 20), ipadx=10, ipady=5)

        lbl_rows = tk.Label(controls_frame, text="Show rows:", bg="#f5f5f5", font=("Segoe UI", 10))
        lbl_rows.pack(side=tk.LEFT, padx=(0, 5))

        self.row_limit_var = tk.StringVar(value="100")
        self.combo_rows = ttk.Combobox(
            controls_frame, 
            textvariable=self.row_limit_var, 
            state="readonly", 
            width=10,
            values=["10", "100", "All"]
        )
        self.combo_rows.pack(side=tk.LEFT)
        self.combo_rows.bind("<<ComboboxSelected>>", self.on_row_limit_change)

        # Data Table (Treeview) Section
        table_frame = tk.Frame(main_frame, bg="white", bd=1, relief=tk.SOLID)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        scroll_y = ttk.Scrollbar(table_frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(
            table_frame, 
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set,
            style="Custom.Treeview"
        )
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.lbl_status = tk.Label(main_frame, text="Ready to load data...", bg="#f5f5f5", fg="#888", anchor="w")
        self.lbl_status.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=5)

    def configure_styles(self):
        """
        Sets up the 'clam' theme and defines custom styles for Buttons and Treeview headers.
        """
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"))
        
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=5)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

    def import_click(self):
        """
        Triggers the system file dialog for CSV selection.
        
        Upon success:
        1. Loads data via CsvImport.
        2. Updates the UI status.
        3. Populates the preview table.
        4. Invokes the application-wide data callback.
        """
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            try:
                self.lbl_status.config(text="Loading data...")
                self.update_idletasks() 
                
                df = CsvImport().load(path)
                self.full_data = df
                
                self.refresh_table_view()
                self.on_data_loaded(df)
                
                rows_count = len(df)
                self.lbl_status.config(text=f"Successfully loaded {rows_count} rows from {path}")
                
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to load CSV:\n{str(e)}")
                self.lbl_status.config(text="Error loading data.")

    def on_row_limit_change(self, event=None):
        """Callback for the row limit dropdown. Triggers a table refresh."""
        if self.full_data is not None:
            self.refresh_table_view()

    def refresh_table_view(self):
        """
        Slices the dataset based on the user's selected row limit to optimize rendering performance.
        """
        limit_str = self.row_limit_var.get()
        
        if limit_str == "All":
            data_to_show = self.full_data
        else:
            limit = int(limit_str)
            data_to_show = self.full_data.head(limit)
            
        self.update_grid(data_to_show)

    def update_grid(self, df):
        """
        Dynamically rebuilds the Treeview columns and rows based on the provided DataFrame structure.
        
        Args:
            df (pd.DataFrame): The subset of data to render in the grid.
        """
        self.tree.delete(*self.tree.get_children())
        
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        
        for col in df.columns:
            self.tree.heading(col, text=col, anchor=tk.W)
            self.tree.column(col, width=120, minwidth=100, anchor=tk.W)
        
        # Zebra striping logic
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f0f8ff') 

        for i, row in enumerate(df.to_numpy()):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=list(row), tags=(tag,))
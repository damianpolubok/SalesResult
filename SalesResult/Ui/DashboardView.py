import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Warstwa logiki (Core) – zakładamy, że jest w PYTHONPATH
from Core.SalesAnalyzer import SalesAnalyzer
from Core.SalesPlots import SalesPlots
from Core.XlsxExport import XlsxExport


class DashboardView(tk.Frame):
    """
    Widok analityczny (dashboard):
    - KPI (Total Revenue),
    - wybór “Group by” i typu wykresu,
    - render wykresu (Matplotlib),
    - eksport aktualnej agregacji do Excela.

    UI jest zrobione w stylu “karty + toolbar” i przycisk export jest wyłączony,
    dopóki nie ma danych.
    """

    # ===================== Kolory / motyw =====================
    BG_APP = "#f6f7fb"
    BG_CARD = "#ffffff"
    BORDER = "#e6e8ef"
    TEXT = "#1f2937"
    MUTED = "#6b7280"

    PRIMARY = "#2563eb"   # niebieski - główna akcja
    SUCCESS = "#16a34a"   # zielony
    WARNING = "#f59e0b"   # pomarańcz

    # ===================== Fonty =====================
    FONT_H1 = ("Segoe UI", 14, "bold")
    FONT_H2 = ("Segoe UI", 11, "bold")
    FONT_BODY = ("Segoe UI", 10)
    FONT_KPI = ("Segoe UI", 18, "bold")

    def __init__(self, parent):
        super().__init__(parent, bg=self.BG_APP)

        # -------------------- Komponenty logiki --------------------
        # analyzer: liczenie KPI + agregacje (Category/Country/Age)
        self.analyzer = SalesAnalyzer()

        # plotter: rysuje wykres na figurze Matplotlib
        self.plotter = SalesPlots(Figure(figsize=(7, 5), dpi=100))

        # exporter: zapis do Excel
        self.xlsx_export = XlsxExport()

        # -------------------- Stan widoku --------------------
        self.current_df = None            # aktualny DataFrame z danymi
        self.current_chart_data = None    # aktualna agregacja (do exportu)

        # Konfigurujemy style + budujemy UI
        self._configure_styles()
        self._build_ui()

        # Stan startowy: brak danych -> export disabled + “empty state”
        self._set_export_enabled(False)
        self._show_empty_state(True)

    # ====================================================================
    #                               STYLE
    # ====================================================================

    def _configure_styles(self) -> None:
        """
        Konfiguracja stylów TTK dla comboboxów i przycisków.
        """
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # -------------------- Combobox --------------------
        style.configure("Pro.TCombobox", font=self.FONT_BODY, padding=(6, 4))

        # -------------------- Primary button --------------------
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 6),
        )
        style.map(
            "Primary.TButton",
            foreground=[("disabled", "#9ca3af")],  # tekst gdy przycisk disabled
        )

        # (opcjonalnie) Ghost button – na przyszłość, jeśli dodasz np. “Reset”
        style.configure(
            "Ghost.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 6),
        )

        # Notebook – na wypadek gdyby styl był potrzebny w tym widoku
        style.configure("TNotebook", background=self.BG_APP, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 8), font=("Segoe UI", 10, "bold"))

    # ====================================================================
    #                               UI BUILD
    # ====================================================================

    def _build_ui(self) -> None:
        """
        Buduje layout dashboardu:
        1) Toolbar (KPI + filtry + eksport),
        2) Karta z wykresem (Matplotlib),
        3) Empty state, gdy brak danych.
        """
        # Główny kontener z paddingiem
        self.container = tk.Frame(self, bg=self.BG_APP)
        self.container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # ===================== Toolbar card =====================
        self.toolbar_card = tk.Frame(
            self.container,
            bg=self.BG_CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        self.toolbar_card.pack(fill=tk.X, pady=(0, 12))

        self.toolbar = tk.Frame(self.toolbar_card, bg=self.BG_CARD)
        self.toolbar.pack(fill=tk.X, padx=12, pady=12)

        # -------------------- KPI card (po lewej) --------------------
        self.kpi = tk.Frame(self.toolbar, bg="#f3f4f6", highlightthickness=0)
        self.kpi.pack(side=tk.LEFT, padx=(0, 12), pady=0)

        self.lbl_kpi_title = tk.Label(
            self.kpi,
            text="Total Revenue",
            font=self.FONT_BODY,
            bg="#f3f4f6",
            fg=self.MUTED,
        )
        self.lbl_kpi_title.pack(anchor="w", padx=12, pady=(10, 0))

        self.lbl_revenue = tk.Label(
            self.kpi,
            text="$0",
            font=self.FONT_KPI,
            bg="#f3f4f6",
            fg=self.TEXT,
        )
        self.lbl_revenue.pack(anchor="w", padx=12, pady=(0, 10))

        # -------------------- Controls (środek) --------------------
        controls = tk.Frame(self.toolbar, bg=self.BG_CARD)
        controls.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Wybór grupowania
        grp = tk.Frame(controls, bg=self.BG_CARD)
        grp.pack(side=tk.LEFT, padx=(0, 14))

        tk.Label(grp, text="Group by", font=self.FONT_BODY, bg=self.BG_CARD, fg=self.MUTED).pack(anchor="w")

        self.data_view_var = tk.StringVar(value="Category")
        self.combo_data = ttk.Combobox(
            grp,
            textvariable=self.data_view_var,
            state="readonly",
            width=18,
            values=("Category", "Country", "Age Group"),
            style="Pro.TCombobox",
        )
        self.combo_data.pack(anchor="w", pady=(4, 0))
        self.combo_data.bind("<<ComboboxSelected>>", self.refresh_chart)

        # Wybór typu wykresu
        ch = tk.Frame(controls, bg=self.BG_CARD)
        ch.pack(side=tk.LEFT, padx=(0, 14))

        tk.Label(ch, text="Chart type", font=self.FONT_BODY, bg=self.BG_CARD, fg=self.MUTED).pack(anchor="w")

        self.chart_type_var = tk.StringVar(value="Pie Chart")
        self.combo_chart = ttk.Combobox(
            ch,
            textvariable=self.chart_type_var,
            state="readonly",
            width=18,
            values=("Pie Chart", "Bar Chart"),
            style="Pro.TCombobox",
        )
        self.combo_chart.pack(anchor="w", pady=(4, 0))
        self.combo_chart.bind("<<ComboboxSelected>>", self.refresh_chart)

        # -------------------- Actions (po prawej) --------------------
        actions = tk.Frame(self.toolbar, bg=self.BG_CARD)
        actions.pack(side=tk.RIGHT)

        # Przycisk exportu (na starcie disabled)
        self.btn_export = ttk.Button(
            actions,
            text="⬇ Export to Excel",
            command=self.export_click,
            style="Primary.TButton",
        )
        self.btn_export.pack(side=tk.RIGHT, padx=(8, 0))

        # ===================== Plot card =====================
        self.plot_card = tk.Frame(
            self.container,
            bg=self.BG_CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        self.plot_card.pack(fill=tk.BOTH, expand=True)

        # Tytuł sekcji wykresu
        self.plot_title = tk.Label(
            self.plot_card,
            text="Sales Analysis",
            font=self.FONT_H1,
            bg=self.BG_CARD,
            fg=self.TEXT,
        )
        self.plot_title.pack(anchor="w", padx=12, pady=(12, 6))

        # Kontener na canvas Matplotlib
        self.canvas_host = tk.Frame(self.plot_card, bg=self.BG_CARD)
        self.canvas_host.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        # -------------------- Empty state (gdy brak danych) --------------------
        self.empty_state = tk.Frame(self.canvas_host, bg=self.BG_CARD)
        self.empty_state.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.empty_state,
            text="No data yet",
            font=self.FONT_H1,
            bg=self.BG_CARD,
            fg=self.TEXT,
        ).pack(pady=(0, 6))

        tk.Label(
            self.empty_state,
            text="Import a CSV in the Home tab to generate charts.",
            font=self.FONT_BODY,
            bg=self.BG_CARD,
            fg=self.MUTED,
        ).pack()

        # -------------------- Matplotlib embed --------------------
        # Dopasowujemy tło figury do karty (estetyka)
        try:
            self.plotter.figure.patch.set_facecolor(self.BG_CARD)
        except Exception:
            pass

        self.canvas = FigureCanvasTkAgg(self.plotter.figure, self.canvas_host)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # ====================================================================
    #                              PUBLIC API
    # ====================================================================

    def render(self, df):
        """
        Publiczna metoda wywoływana z MainWindow po imporcie danych.
        Ustawia:
        - current_df,
        - KPI (total revenue),
        - rysuje wykres.
        """
        self.current_df = df

        # Liczymy przychód łączny (KPI)
        total_rev = self.analyzer.calculate_total_revenue(df)
        self.lbl_revenue.config(text=f"${total_rev:,.0f}")

        # Ukrywamy “empty state”, bo mamy dane
        self._show_empty_state(False)

        # Rysujemy wykres zgodnie z aktualnymi ustawieniami comboboxów
        self.draw_plot()

    # ====================================================================
    #                              INTERNALS
    # ====================================================================

    def refresh_chart(self, event=None):
        """
        Callback od comboboxów:
        po zmianie “Group by” lub “Chart type” odświeżamy wykres.
        """
        if self.current_df is not None:
            self.draw_plot()

    def _set_export_enabled(self, enabled: bool) -> None:
        """
        Włącza/wyłącza przycisk eksportu:
        - disabled, jeśli brak danych do eksportu,
        - normal, jeśli mamy poprawną agregację.
        """
        state = "normal" if enabled else "disabled"
        try:
            self.btn_export.configure(state=state)
        except Exception:
            pass

    def _show_empty_state(self, show: bool) -> None:
        """
        Pokazuje/ukrywa ekran “No data yet” w obszarze wykresu.
        """
        if show:
            self.empty_state.lift()
            self.empty_state.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.empty_state.place_forget()

    def draw_plot(self):
        """
        Główna metoda “renderowania wykresu”:
        1) wybiera agregację (Category / Country / Age Group),
        2) ustawia parametry rysowania (kolor, obrót etykiet),
        3) aktualizuje stan current_chart_data (do exportu),
        4) deleguje rysowanie do SalesPlots.draw(...)
        """
        view_mode = self.data_view_var.get()
        chart_type = self.chart_type_var.get()

        # Jeśli nie mamy danych, nie renderujemy nic
        if self.current_df is None:
            self._set_export_enabled(False)
            self._show_empty_state(True)
            return

        # -------------------- Wybór agregacji --------------------
        if view_mode == "Category":
            data = self.analyzer.get_category_share(self.current_df)
            title_suffix = "by Product Category"
            color = "#60a5fa"  # delikatny niebieski
            rotate_x = 45

        elif view_mode == "Country":
            data = self.analyzer.get_country_share(self.current_df)
            title_suffix = "by Country"
            color = "#22c55e"  # delikatny zielony
            rotate_x = 45

        else:  # "Age Group"
            data = self.analyzer.get_age_group_share(self.current_df)
            title_suffix = "by Age Group"
            color = "#fb923c"  # delikatny pomarańcz
            rotate_x = 0

            # Jeśli brak danych (np. brak kolumny Customer_Age) – komunikat i brak exportu
            if data is None or getattr(data, "empty", True):
                messagebox.showwarning("No Data", "Column 'Customer_Age' not found or empty.")
                self.current_chart_data = None
                self._set_export_enabled(False)
                return

        # Jeśli agregacja jest pusta – pokaż empty state i zablokuj export
        if data is None or getattr(data, "empty", True):
            self.current_chart_data = None
            self._set_export_enabled(False)
            self._show_empty_state(True)
            return

        # -------------------- Aktualizacja UI --------------------
        self.plot_title.config(text=f"Sales Analysis {title_suffix}")

        # Zapisujemy aktualną agregację do exportu
        self.current_chart_data = data

        # Skoro mamy dane → export dostępny + ukrywamy empty state
        self._set_export_enabled(True)
        self._show_empty_state(False)

        # -------------------- Rysowanie wykresu --------------------
        # Tu delegujemy logikę rysowania do klasy SalesPlots
        self.plotter.draw(data, chart_type, title_suffix, color, rotate_x)

        # Odświeżamy canvas w Tkinter
        self.canvas.draw()

    def export_click(self):
        """
        Obsługa eksportu:
        - zapisuje aktualną agregację (current_chart_data) do pliku .xlsx
        - jeśli brak danych -> ostrzeżenie
        """
        if self.current_chart_data is None or getattr(self.current_chart_data, "empty", True):
            messagebox.showwarning("Export", "No data available to export.")
            return

        # Okno wyboru ścieżki do zapisu
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Analysis",
        )

        if not file_path:
            return

        # Zapis przez warstwę Core (XlsxExport)
        success, message = self.xlsx_export.save(self.current_chart_data, file_path)

        # Komunikat po zapisie
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", f"Failed to save file:\n{message}")

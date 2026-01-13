import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont

from Core.CsvImport import CsvImport


class HomeView(tk.Frame):
    """
    Widok startowy aplikacji:
    - import danych z pliku CSV,
    - podgląd danych w tabeli (Treeview),
    - wybór liczby wyświetlanych wierszy,
    - pasek statusu (informacje o postępie / błędach).
    """

    # ===================== Kolory / motyw aplikacji =====================
    BG_APP = "#f6f7fb"     # tło całej aplikacji (jasne, nowoczesne)
    BG_CARD = "#ffffff"    # tło kart/paneli
    BORDER = "#e6e8ef"     # kolor obramowań (delikatny)
    TEXT = "#1f2937"       # kolor głównego tekstu
    MUTED = "#6b7280"      # kolor tekstu pomocniczego
    PRIMARY = "#2563eb"    # kolor główny (np. akcje)

    # ===================== Fonty =====================
    FONT_TITLE = ("Segoe UI", 22, "bold")
    FONT_SUB = ("Segoe UI", 11)
    FONT_BODY = ("Segoe UI", 10)
    FONT_BODY_B = ("Segoe UI", 10, "bold")

    def __init__(self, parent, on_data_loaded_callback):
        """
        Args:
            parent: Kontener nadrzędny (np. Notebook lub Frame)
            on_data_loaded_callback: callback wywoływany po wczytaniu danych (df)
        """
        super().__init__(parent, bg=self.BG_APP)

        # Callback do przekazania danych dalej (np. do Dashboardu)
        self.on_data_loaded = on_data_loaded_callback

        # Przechowujemy pełny DataFrame po imporcie
        self.full_data = None

        # Konfigurujemy style TTK (ładniejszy wygląd)
        self._configure_styles()

        # Budujemy całe UI
        self._build_ui()

        # Stan początkowy (status + “pusty ekran” w tabeli)
        self._set_status("Ready to load data...", kind="info")
        self._show_table_empty_state(True)

    # ====================================================================
    #                               STYLE
    # ====================================================================

    def _configure_styles(self) -> None:
        """
        Definiuje wygląd kontrolek ttk:
        - przyciski,
        - combobox,
        - tabela (Treeview) + nagłówki,
        - kolory zaznaczenia.
        """
        style = ttk.Style()

        # 'clam' jest zwykle najładniejszy i najbardziej przewidywalny
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # -------------------- Przyciski --------------------
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))
        style.configure("Ghost.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 7))

        # Kolor tekstu gdy przycisk jest wyłączony
        style.map("Primary.TButton", foreground=[("disabled", "#9ca3af")])

        # -------------------- Combobox --------------------
        style.configure("Pro.TCombobox", font=self.FONT_BODY, padding=(6, 4))

        # -------------------- Treeview (tabela) --------------------
        style.configure(
            "Pro.Treeview",
            font=self.FONT_BODY,
            rowheight=26,
            background="#ffffff",
            fieldbackground="#ffffff",
            borderwidth=0,
        )

        style.configure(
            "Pro.Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            padding=(8, 6),
            relief="flat",
        )

        # Kolory zaznaczenia wiersza
        style.map(
            "Pro.Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#111827")],
        )

        # -------------------- Notebook (jeśli HomeView jest w zakładkach) --------------------
        style.configure("TNotebook", background=self.BG_APP, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 8), font=("Segoe UI", 10, "bold"))

    # ====================================================================
    #                               UI BUILD
    # ====================================================================

    def _build_ui(self) -> None:
        """
        Buduje widok:
        1) Nagłówek (karta z tytułem),
        2) Panel sterowania (Import + liczba wierszy),
        3) Karta z tabelą + scrollbary,
        4) Pasek statusu na dole.
        """
        # Główny kontener z paddingiem
        self.container = tk.Frame(self, bg=self.BG_APP)
        self.container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # ===================== Header card =====================
        header_card = tk.Frame(
            self.container,
            bg=self.BG_CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        header_card.pack(fill=tk.X, pady=(0, 12))

        header = tk.Frame(header_card, bg=self.BG_CARD)
        header.pack(fill=tk.X, padx=14, pady=14)

        tk.Label(
            header,
            text="Sales Data Dashboard",
            font=self.FONT_TITLE,
            bg=self.BG_CARD,
            fg=self.TEXT,
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Import a CSV file to preview raw data, generate charts and analyze revenue.",
            font=self.FONT_SUB,
            bg=self.BG_CARD,
            fg=self.MUTED,
        ).pack(anchor="w", pady=(6, 0))

        # ===================== Controls card =====================
        controls_card = tk.Frame(
            self.container,
            bg=self.BG_CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        controls_card.pack(fill=tk.X, pady=(0, 12))

        controls = tk.Frame(controls_card, bg=self.BG_CARD)
        controls.pack(fill=tk.X, padx=14, pady=12)

        # Przycisk importu CSV
        self.btn_import = ttk.Button(
            controls,
            text="📄 Import CSV",
            command=self.import_click,
            style="Primary.TButton",
        )
        self.btn_import.pack(side=tk.LEFT)

        # Odstęp wizualny
        tk.Frame(controls, bg=self.BG_CARD, width=18).pack(side=tk.LEFT)

        # Wybór liczby wierszy do wyświetlenia (dla wydajności)
        tk.Label(
            controls,
            text="Show rows:",
            bg=self.BG_CARD,
            fg=self.MUTED,
            font=self.FONT_BODY,
        ).pack(side=tk.LEFT)

        self.row_limit_var = tk.StringVar(value="100")
        self.combo_rows = ttk.Combobox(
            controls,
            textvariable=self.row_limit_var,
            state="readonly",
            width=10,
            values=["10", "100", "1000", "All"],
            style="Pro.TCombobox",
        )
        self.combo_rows.pack(side=tk.LEFT, padx=(8, 0))
        self.combo_rows.bind("<<ComboboxSelected>>", self.on_row_limit_change)

        # ===================== Table card =====================
        self.table_card = tk.Frame(
            self.container,
            bg=self.BG_CARD,
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        self.table_card.pack(fill=tk.BOTH, expand=True)

        # Nagłówek sekcji tabeli
        table_header = tk.Frame(self.table_card, bg=self.BG_CARD)
        table_header.pack(fill=tk.X, padx=14, pady=(12, 6))

        tk.Label(
            table_header,
            text="Data preview",
            font=("Segoe UI", 12, "bold"),
            bg=self.BG_CARD,
            fg=self.TEXT,
        ).pack(side=tk.LEFT)

        # Informacja typu "Showing 100 of 5000 rows"
        self.lbl_rows_info = tk.Label(
            table_header,
            text="",
            font=self.FONT_BODY,
            bg=self.BG_CARD,
            fg=self.MUTED,
        )
        self.lbl_rows_info.pack(side=tk.RIGHT)

        # -------------------- Table frame --------------------
        # UWAGA: tutaj używamy grid (a nie pack) aby scrollbary działały poprawnie przy zmianie rozmiaru okna.
        table_frame = tk.Frame(self.table_card, bg=self.BG_CARD)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 12))

        # Treeview ma zająć całe dostępne miejsce, scrollbary mają się “dokleić” do krawędzi.
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Scrollbary (pionowy i poziomy)
        self.scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        self.scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

        # Treeview (tabela)
        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=self.scroll_y.set,
            xscrollcommand=self.scroll_x.set,
            style="Pro.Treeview",
        )

        # Layout przez grid:
        # - Treeview: row=0 col=0 (rozciąga się)
        # - Scroll pionowy: row=0 col=1
        # - Scroll poziomy: row=1 col=0
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        # Podpinamy “sterowanie” scrollbary → tabela
        self.scroll_y.config(command=self.tree.yview)
        self.scroll_x.config(command=self.tree.xview)

        # ===================== Empty state overlay =====================
        # Pokazywany gdy brak danych.
        self.table_empty = tk.Frame(table_frame, bg=self.BG_CARD)
        self.table_empty.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.table_empty,
            text="No data loaded",
            font=("Segoe UI", 14, "bold"),
            bg=self.BG_CARD,
            fg=self.TEXT,
        ).pack(pady=(0, 6))

        tk.Label(
            self.table_empty,
            text="Click “Import CSV” to load a dataset and preview rows here.",
            font=self.FONT_BODY,
            bg=self.BG_CARD,
            fg=self.MUTED,
        ).pack()

        # ===================== Status bar =====================
        self.status_bar = tk.Frame(
            self.container,
            bg="#eef2ff",
            highlightbackground=self.BORDER,
            highlightthickness=1,
        )
        self.status_bar.pack(fill=tk.X, pady=(12, 0))

        self.lbl_status = tk.Label(
            self.status_bar,
            text="",
            bg="#eef2ff",
            fg=self.TEXT,
            font=self.FONT_BODY,
            anchor="w",
        )
        self.lbl_status.pack(fill=tk.X, padx=12, pady=8)

    # ====================================================================
    #                              UX HELPERS
    # ====================================================================

    def _set_status(self, text: str, kind: str = "info") -> None:
        """
        Ustawia komunikat w pasku statusu na dole.

        kind:
          - info  (neutralny)
          - ok    (sukces)
          - warn  (ostrzeżenie)
          - err   (błąd)
        """
        bg_map = {
            "info": "#eef2ff",
            "ok": "#ecfdf5",
            "warn": "#fffbeb",
            "err": "#fef2f2",
        }
        fg_map = {
            "info": self.TEXT,
            "ok": "#065f46",
            "warn": "#92400e",
            "err": "#991b1b",
        }
        icon_map = {
            "info": "ℹ ",
            "ok": "✅ ",
            "warn": "⚠ ",
            "err": "⛔ ",
        }

        bg = bg_map.get(kind, "#eef2ff")
        fg = fg_map.get(kind, self.TEXT)
        icon = icon_map.get(kind, "")

        self.status_bar.config(bg=bg)
        self.lbl_status.config(text=f"{icon}{text}", bg=bg, fg=fg)

    def _show_table_empty_state(self, show: bool) -> None:
        """
        Pokazuje/ukrywa ekran “No data loaded” nad tabelą.
        """
        if show:
            self.table_empty.lift()
            self.table_empty.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.table_empty.place_forget()

    # ====================================================================
    #                               ACTIONS
    # ====================================================================

    def import_click(self):
        """
        1) Otwiera okno wyboru pliku CSV,
        2) Ładuje dane przez CsvImport(),
        3) Aktualizuje tabelę,
        4) Wywołuje callback (przekazanie df do innych widoków).
        """
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        try:
            # Blokujemy przycisk, żeby user nie kliknął 2x
            self.btn_import.configure(state="disabled")

            # Status + odświeżenie UI (żeby komunikat się pokazał od razu)
            self._set_status("Loading data...", kind="info")
            self.update_idletasks()

            # Import danych
            df = CsvImport().load(path)
            self.full_data = df

            # Odśwież tabelę
            self.refresh_table_view()

            # Przekaż dane do reszty aplikacji (np. Dashboard)
            self.on_data_loaded(df)

            # Komunikat o sukcesie
            rows_count = len(df)
            self._set_status(f"Loaded {rows_count:,} rows from {path}", kind="ok")

        except Exception as e:
            # Błąd importu
            messagebox.showerror("Import Error", f"Failed to load CSV:\n{str(e)}")
            self._set_status("Error loading data.", kind="err")

        finally:
            # Zawsze odblokuj przycisk na końcu
            self.btn_import.configure(state="normal")

    def on_row_limit_change(self, event=None):
        """
        Zmiana liczby wierszy do podglądu.
        W przypadku "All" ostrzegamy przy dużym zbiorze (żeby nie zamrozić UI).
        """
        if self.full_data is None:
            return

        if self.row_limit_var.get() == "All":
            n = len(self.full_data)

            # Ostrzeżenie, bo renderowanie tysięcy wierszy w Treeview może przyciąć aplikację
            if n > 5000:
                res = messagebox.askyesno(
                    "Large dataset",
                    f"You are about to render ALL rows ({n:,}).\n"
                    "This may freeze the UI.\n\nContinue?",
                )
                if not res:
                    self.row_limit_var.set("1000" if n > 1000 else "100")
                    return

        self.refresh_table_view()

    def refresh_table_view(self):
        """
        Wyświetla wybraną liczbę wierszy:
        - 10 / 100 / 1000 = head(limit),
        - All = wszystkie wiersze.
        """
        if self.full_data is None:
            self._show_table_empty_state(True)
            return

        limit_str = self.row_limit_var.get()

        if limit_str == "All":
            data_to_show = self.full_data
        else:
            limit = int(limit_str)
            data_to_show = self.full_data.head(limit)

        self.update_grid(data_to_show)

        # Aktualizujemy label z informacją ile pokazujemy
        total = len(self.full_data)
        shown = len(data_to_show)
        self.lbl_rows_info.config(text=f"Showing {shown:,} of {total:,} rows")

    def update_grid(self, df):
        """
        Przebudowuje tabelę:
        - ustawia kolumny na podstawie df.columns,
        - wstawia wiersze,
        - ustawia zebra-striping,
        - automatycznie dobiera szerokości kolumn (na podstawie nagłówka i próbki wierszy).

        Uwaga:
        stretch=False w kolumnach jest celowe -> gdy okno jest mniejsze niż tabela,
        poziomy scrollbar działa poprawnie (kolumny nie “ściskają się” na siłę).
        """
        # Czyścimy poprzednią zawartość tabeli
        self.tree.delete(*self.tree.get_children())

        # Ustawiamy kolumny
        cols = list(df.columns)
        self.tree["columns"] = cols
        self.tree["show"] = "headings"

        # Zebra striping (naprzemienne tła wierszy)
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("evenrow", background="#f3f4f6")

        # Wyliczamy sensowną szerokość kolumn na podstawie fontu
        font = tkfont.Font(family="Segoe UI", size=10)
        sample_rows = df.head(30).to_numpy()  # próbka do szacowania szerokości

        for col_i, col in enumerate(cols):
            header_w = font.measure(str(col)) + 24
            cell_w = header_w

            # bierzemy max szerokość z próbki wierszy
            for r in sample_rows:
                try:
                    cell_w = max(cell_w, font.measure(str(r[col_i])) + 24)
                except Exception:
                    pass

            # ograniczamy, żeby kolumny nie były absurdalnie szerokie
            cell_w = min(max(cell_w, 110), 420)

            self.tree.heading(col, text=col, anchor=tk.W)

            # stretch=False -> poziomy scrollbar jest “prawdziwy” i działa przy małym oknie
            self.tree.column(col, width=cell_w, minwidth=90, anchor=tk.W, stretch=False)

        # Wstawiamy wiersze do tabeli
        for i, row in enumerate(df.to_numpy()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree.insert("", "end", values=list(row), tags=(tag,))

        # Pokaż/ukryj empty state
        self._show_table_empty_state(len(df) == 0)

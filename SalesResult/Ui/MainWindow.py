import tkinter as tk
from tkinter import ttk

from Ui.HomeView import HomeView
from Ui.DashboardView import DashboardView


class MainWindow(tk.Tk):
    """
    Główne okno aplikacji (kontroler/root).
    Odpowiada za:
    - konfigurację okna,
    - motyw i style globalne (Notebook),
    - nawigację zakładkami (Home / Dashboard),
    - przekazanie danych z HomeView do DashboardView.
    """

    # Kolor tła aplikacji (spójny z resztą widoków)
    BG_APP = "#f6f7fb"

    def __init__(self):
        super().__init__()

        # -------------------- Ustawienia okna --------------------
        self.title("SalesResult")
        self.configure(bg=self.BG_APP)

        # Rozmiar startowy + minimalny, żeby UI się nie “rozjeżdżało”
        self.geometry("1100x700")
        self.minsize(980, 620)

        # -------------------- Style globalne (ttk) --------------------
        self._configure_styles()

        # -------------------- Notebook (zakładki) --------------------
        # Notebook jest kontenerem na zakładki aplikacji
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(expand=True, fill="both", padx=10, pady=10)

        # -------------------- Widoki --------------------
        # HomeView dostaje callback, żeby po imporcie CSV powiadomić MainWindow o nowych danych
        self.home_view = HomeView(self.tabs, self.on_data_ready)

        # DashboardView renderuje wykresy i KPI
        self.dashboard_view = DashboardView(self.tabs)

        # Rejestracja zakładek
        self.tabs.add(self.home_view, text="Home & Data")
        self.tabs.add(self.dashboard_view, text="Sales Analysis")

    def _configure_styles(self) -> None:
        """
        Konfiguruje wygląd zakładek (Notebook):
        - kolory tła,
        - padding,
        - fonty,
        - inny kolor tła dla aktywnej zakładki.
        """
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Tło całego Notebooka
        style.configure("TNotebook", background=self.BG_APP, borderwidth=0)

        # Wygląd pojedynczych zakładek
        style.configure(
            "TNotebook.Tab",
            padding=(14, 10),
            font=("Segoe UI", 10, "bold"),
        )

        # Mapowanie tła: aktywna zakładka biała, nieaktywna lekko niebieska
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#ffffff"), ("!selected", "#eef2ff")],
        )

    def on_data_ready(self, df):
        """
        Callback wywołany przez HomeView po udanym imporcie danych.
        Robimy tu dwie rzeczy:
        1) Przekazujemy DataFrame do DashboardView (render KPI + wykres),
        2) Automatycznie przełączamy użytkownika na zakładkę analizy.
        """
        self.dashboard_view.render(df)
        self.tabs.select(1)  # indeks 1 = druga zakładka (Sales Analysis)

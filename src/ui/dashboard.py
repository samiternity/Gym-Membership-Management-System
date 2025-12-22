import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter
import datetime
from ..styles import *
from ..analytics import Analytics

class Dashboard:
    def __init__(self, parent_frame, data_manager):
        self.parent_frame = parent_frame
        self.data_manager = data_manager
        self.analytics = Analytics(data_manager)
        
        self.setup_ui()

    def setup_ui(self):
        # Grid configuration - 2 rows of stats, 2 rows of graphs
        self.parent_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.parent_frame.grid_rowconfigure(0, weight=0)  # Stats row 1
        self.parent_frame.grid_rowconfigure(1, weight=0)  # Stats row 2
        self.parent_frame.grid_rowconfigure(2, weight=1)  # Graphs row 1
        self.parent_frame.grid_rowconfigure(3, weight=1)  # Graphs row 2

        # Load Basic Stats
        total_members = len(self.data_manager.members_db)
        pending_payments = len([p for p in self.data_manager.payments_log if p['status'] == 'Unpaid'])
        # Filter check-ins to today only
        today = datetime.date.today().isoformat()
        active_check_ins = 0
        for a in self.data_manager.attendance_log:
            if a.get('check_out_time') is None:
                check_in_time = a.get('check_in_time')
                if check_in_time:
                    try:
                        # Parse the check-in date
                        check_in_date = check_in_time.split('T')[0] if 'T' in check_in_time else check_in_time.split(' ')[0]
                        if check_in_date == today:
                            active_check_ins += 1
                    except (ValueError, IndexError):
                        pass
        frozen_memberships = len([m for m in self.data_manager.membership_history if m.get('status') == 'Frozen'])

        # Load Analytics Stats
        # Load Analytics Stats
        retention_rate = self.analytics.calculate_retention_rate()
        at_risk_members = self.analytics.get_at_risk_members(30)
        at_risk_count = len(at_risk_members)

        # Row 1: Basic Stats
        self.create_stat_card("Total Members", total_members, 0, 0)
        self.create_stat_card("Pending Payments", pending_payments, 0, 1, 
                            text_color=DANGER_COLOR if pending_payments > 0 else TEXT_COLOR)
        self.create_stat_card("Active Check-ins", active_check_ins, 0, 2, 
                            text_color=SUCCESS_COLOR if active_check_ins > 0 else TEXT_COLOR)
        self.create_stat_card("Frozen Memberships", frozen_memberships, 0, 3,
                            text_color=ACCENT_COLOR if frozen_memberships > 0 else TEXT_COLOR)

        # Row 2: Analytics Stats
        self.create_stat_card(f"Retention Rate", f"{retention_rate}%", 1, 0,
                            text_color=SUCCESS_COLOR if retention_rate >= 70 else DANGER_COLOR)
        
        self.create_stat_card("Expiring Soon", at_risk_count, 1, 1,
                            text_color=DANGER_COLOR if at_risk_count > 0 else TEXT_COLOR)

        # Row 3: Graphs
        self.create_revenue_forecast_graph(2, 0)
        self.create_retention_trend_graph(2, 2)

        # Row 4: More Graphs
        self.create_historical_revenue_graph(3, 0)
        self.create_peak_hours_graph(3, 2)

    def create_stat_card(self, title, value, row, col, text_color=TEXT_COLOR):
        card = ctk.CTkFrame(self.parent_frame, fg_color=SIDEBAR_COLOR)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        title_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"), 
                                text_color=TEXT_SECONDARY_COLOR)
        title_lbl.pack(pady=(10, 0))
        
        value_lbl = ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=28, weight="bold"), 
                                text_color=text_color)
        value_lbl.pack(pady=(0, 10))

    def create_revenue_forecast_graph(self, row, col):
        """Creates revenue prediction graph."""
        predictions = self.analytics.predict_revenue(6)
        confidence = self.analytics.calculate_confidence_interval()
        
        # Create Figure
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=CONTENT_COLOR)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CONTENT_COLOR)
        
        if predictions['months']:
            x = range(len(predictions['months']))
            ax.bar(x, predictions['predicted'], color=PRIMARY_COLOR, alpha=0.7, label='Predicted')
            ax.set_xticks(x)
            ax.set_xticklabels(predictions['months'], rotation=45, ha='right')
            ax.legend(facecolor=SIDEBAR_COLOR, edgecolor=TEXT_SECONDARY_COLOR)
        else:
            ax.text(0.5, 0.5, "Insufficient Data", ha='center', va='center', 
                   color=TEXT_SECONDARY_COLOR)
        
        title = f"Revenue Forecast (Confidence: {confidence['confidence']}%)"
        ax.set_title(title, color=TEXT_COLOR, fontsize=12)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        ax.set_ylabel("Revenue (PKR)", color=TEXT_COLOR)
        ax.tick_params(axis='x', colors=TEXT_SECONDARY_COLOR)
        ax.tick_params(axis='y', colors=TEXT_SECONDARY_COLOR)
        ax.spines['bottom'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['top'].set_color(CONTENT_COLOR)
        ax.spines['left'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['right'].set_color(CONTENT_COLOR)
        
        fig.tight_layout()

        # Embed in Tkinter
        graph_frame = ctk.CTkFrame(self.parent_frame, fg_color=CONTENT_COLOR)
        graph_frame.grid(row=row, column=col, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_retention_trend_graph(self, row, col):
        """Creates retention rate trend graph."""
        trend = self.analytics.get_retention_trend(6)
        
        # Create Figure
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=CONTENT_COLOR)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CONTENT_COLOR)
        
        if trend['months']:
            ax.plot(trend['months'], trend['rates'], color=SUCCESS_COLOR, 
                   marker='o', linewidth=2, markersize=6)
            ax.fill_between(range(len(trend['months'])), trend['rates'], 
                           color=SUCCESS_COLOR, alpha=0.2)
            ax.axhline(y=70, color=DANGER_COLOR, linestyle='--', alpha=0.5, label='Target (70%)')
            ax.legend(facecolor=SIDEBAR_COLOR, edgecolor=TEXT_SECONDARY_COLOR)
        else:
            ax.text(0.5, 0.5, "Insufficient Data", ha='center', va='center', 
                   color=TEXT_SECONDARY_COLOR)
        
        ax.set_title("Retention Rate Trend", color=TEXT_COLOR, fontsize=12)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        ax.set_ylabel("Retention Rate (%)", color=TEXT_COLOR)
        ax.tick_params(axis='x', colors=TEXT_SECONDARY_COLOR, rotation=45)
        ax.tick_params(axis='y', colors=TEXT_SECONDARY_COLOR)
        ax.spines['bottom'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['top'].set_color(CONTENT_COLOR)
        ax.spines['left'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['right'].set_color(CONTENT_COLOR)

        fig.tight_layout()

        # Embed in Tkinter
        graph_frame = ctk.CTkFrame(self.parent_frame, fg_color=CONTENT_COLOR)
        graph_frame.grid(row=row, column=col, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_historical_revenue_graph(self, row, col):
        """Creates historical revenue graph."""
        historical = self.analytics.get_historical_revenue_trend(6)
        
        # Create Figure
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=CONTENT_COLOR)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CONTENT_COLOR)
        
        if historical['months']:
            ax.bar(historical['months'], historical['revenue'], color=PRIMARY_COLOR)
        else:
            ax.text(0.5, 0.5, "No Revenue Data", ha='center', va='center', 
                   color=TEXT_SECONDARY_COLOR)
        
        ax.set_title("Historical Revenue (Last 6 Months)", color=TEXT_COLOR, fontsize=12)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        ax.set_ylabel("Revenue (PKR)", color=TEXT_COLOR)
        ax.tick_params(axis='x', colors=TEXT_SECONDARY_COLOR, rotation=45)
        ax.tick_params(axis='y', colors=TEXT_SECONDARY_COLOR)
        ax.spines['bottom'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['top'].set_color(CONTENT_COLOR)
        ax.spines['left'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['right'].set_color(CONTENT_COLOR)

        fig.tight_layout()

        # Embed in Tkinter
        graph_frame = ctk.CTkFrame(self.parent_frame, fg_color=CONTENT_COLOR)
        graph_frame.grid(row=row, column=col, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def create_peak_hours_graph(self, row, col):
        """Creates peak hours graph."""
        # Prepare Data (Peak Hours) - Last 7 Days Only
        hours = []
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=7)
        
        for log in self.data_manager.attendance_log:
            check_in = log.get('check_in_time')
            if check_in:
                try:
                    dt = datetime.datetime.fromisoformat(check_in.replace(' ', 'T') if ' ' in check_in else check_in)
                    # Only include check-ins from last 7 days
                    if dt.date() >= seven_days_ago:
                        hours.append(dt.hour)
                except ValueError:
                    pass
        
        hour_counts = Counter(hours)
        x_hours = list(range(6, 23))  # 6 AM to 10 PM
        y_counts = [hour_counts.get(h, 0) for h in x_hours]

        # Create Figure
        fig = Figure(figsize=(6, 4), dpi=100, facecolor=CONTENT_COLOR)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CONTENT_COLOR)
        
        ax.plot(x_hours, y_counts, color=ACCENT_COLOR, marker='o', linewidth=2)
        ax.fill_between(x_hours, y_counts, color=ACCENT_COLOR, alpha=0.3)
        
        ax.set_title("Peak Hours - Last 7 Days (6AM - 10PM)", color=TEXT_COLOR, fontsize=12)
        ax.set_xlabel("Hour of Day", color=TEXT_COLOR)
        ax.set_ylabel("Number of Check-ins", color=TEXT_COLOR)
        ax.set_xticks(x_hours[::2])  # Show every other hour
        ax.tick_params(axis='x', colors=TEXT_SECONDARY_COLOR)
        ax.tick_params(axis='y', colors=TEXT_SECONDARY_COLOR)
        ax.spines['bottom'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['top'].set_color(CONTENT_COLOR)
        ax.spines['left'].set_color(TEXT_SECONDARY_COLOR)
        ax.spines['right'].set_color(CONTENT_COLOR)

        fig.tight_layout()

        # Embed in Tkinter
        graph_frame = ctk.CTkFrame(self.parent_frame, fg_color=CONTENT_COLOR)
        graph_frame.grid(row=row, column=col, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

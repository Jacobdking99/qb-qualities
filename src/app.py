import os
import sys
from dotenv import load_dotenv
from shiny import App, ui, render, reactive
import pandas as pd
from src.components.charts import (
    make_all_qbs_epa_adj_chart,
    make_all_qbs_yards_chart,
    make_all_qbs_td_int_chart,
    make_all_qbs_mean_cpoe_chart,
)

# Add the parent directory of src to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
load_dotenv()

# Get environment variables
host = os.getenv("HOST", "0.0.0.0")  # Default to 0.0.0.0 if HOST is not set
port = int(os.getenv("PORT", 8050))  # Default to 8050 if PORT is not set

# UI Definition
app_ui = ui.page_fluid(
    ui.h1("Quarterback Analytics Dashboard", class_="text-center"),
    ui.p("Explore quarterback performance metrics across different NFL seasons."),
    ui.input_select(
        "year",
        "Select Year",
        choices=["2021", "2022", "2023"],
        selected="2023"
    ),
    ui.page_fluid(
        ui.h2("EPA Adjusted Metrics"),
        ui.p("This chart shows the Expected Points Added (EPA) metrics for quarterbacks."),
        ui.output_plot("epa_chart"),
        ui.h2("Total Yards Gained"),
        ui.p("This chart displays the total yards gained by quarterbacks."),
        ui.output_plot("yards_chart"),
        ui.h2("Touchdowns vs Interceptions"),
        ui.p("This chart compares the number of touchdowns and interceptions for quarterbacks."),
        ui.output_plot("td_int_chart"),
        ui.h2("Mean CPOE"),
        ui.p("This chart shows the mean Completion Percentage Over Expected (CPOE) for quarterbacks."),
        ui.output_plot("cpoe_chart")
    )
)

# Server Definition
def server(input, output, session):
    @reactive.Calc
    def selected_year():
        """Get the selected year from the input."""
        return int(input.year())

    @output
    @render.plot
    def epa_chart():
        return make_all_qbs_epa_adj_chart(season=selected_year())

    @output
    @render.plot
    def yards_chart():
        return make_all_qbs_yards_chart(season=selected_year())

    @output
    @render.plot
    def td_int_chart():
        return make_all_qbs_td_int_chart(season=selected_year())

    @output
    @render.plot
    def cpoe_chart():
        return make_all_qbs_mean_cpoe_chart(season=selected_year())

app = App(app_ui, server)

if __name__ == "__main__":
    app.run(host=host, port=port)  # Use host and port from environment variables
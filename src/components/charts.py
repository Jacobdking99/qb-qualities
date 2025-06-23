import pandas as pd
from dash import dcc
import plotly.graph_objects as go
from src.data.data_processing import (
    fetch_all_qb_pbp_epa, 
    fetch_adv_qb_pbp_stats,
    fetch_all_qb_season_totals,
)

def make_all_qbs_epa_adj_chart(season: int = 2023, qb_name: str = None) -> dcc.Graph:
    """Creates the chart for EPA adjusted quarterback metrics.
    Optionally highlights a specific quarterback.

    Args:
        season (int): Season year (e.g., 2023).
        qb_name (str): Name of the quarterback to highlight (optional).

    Returns:
        dcc.Graph: A Dash Graph component with the quarterback adjusted EPA chart.
    """
    qb_adj = fetch_all_qb_pbp_epa(season)

    # Sort data by avg_epa_per_dropback in descending order
    qb_adj = qb_adj.sort_values(by='avg_epa_per_dropback', ascending=True)

    fig = go.Figure()

    # Add bars for EPA metrics
    fig.add_trace(go.Bar(
        y=qb_adj['passer_player_name'],
        x=qb_adj['avg_epa_per_dropback'],
        name='EPA',
        marker=dict(
            color=['blue' for _ in qb_adj['passer_player_name']],
            opacity=[1.0 if qb_name is None or name == qb_name else 0.5 for name in qb_adj['passer_player_name']]
        ),
        orientation='h',
    ))
    fig.add_trace(go.Bar(
        y=qb_adj['passer_player_name'],
        x=qb_adj['epa_vs_def_and_ol'],
        name='EPA vs Defense and OL',
        marker=dict(
            color=['orange' for _ in qb_adj['passer_player_name']],
            opacity=[1.0 if qb_name is None or name == qb_name else 0.5 for name in qb_adj['passer_player_name']]
        ),
        orientation='h',
    ))

    fig.update_layout(
        title=f'Quarterback EPA Metrics ({season})',
        xaxis_title='EPA Metrics',
        yaxis_title='Quarterback',
        barmode='group',
        height=600,
        template='plotly_white',
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="top",  # Anchor to the top of the legend
            y=-0.2,  # Position below the chart
            xanchor="center",  # Center the legend horizontally
            x=0.5  # Center the legend
        )
    )

    return dcc.Graph(figure=fig)

def make_all_qbs_yards_chart(season: int, qb_name: str = None) -> dcc.Graph:
    qb_stats = fetch_all_qb_season_totals(season)
    qb_stats = qb_stats.sort_values(by='total_yards', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=qb_stats['passer_player_name'],
        x=qb_stats['total_yards'],
        name='Yards Gained',
        marker=dict(
            color=['green' for _ in qb_stats['passer_player_name']],
            opacity=[1.0 if qb_name is None or name == qb_name else 0.5 for name in qb_stats['passer_player_name']]
        ),
        orientation='h',
    ))

    fig.update_layout(
        title=f'Quarterback Yards Gained ({season})',
        xaxis_title='Yards Gained',
        yaxis_title='Quarterback',
        height=600,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return dcc.Graph(figure=fig)

def make_all_qbs_td_int_chart(season: int, qb_name: str = None) -> dcc.Graph:
    qb_stats = fetch_all_qb_season_totals(season)
    qb_stats['td_int_ratio'] = qb_stats['total_touchdowns'] / (qb_stats['total_interceptions'] + 1e-6)
    qb_stats = qb_stats.sort_values(by='td_int_ratio', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=qb_stats['passer_player_name'],
        x=qb_stats['total_touchdowns'],
        name='Touchdowns',
        marker=dict(
            color=['green' for _ in qb_stats['passer_player_name']],
            opacity=[1.0 if qb_name is None or name == qb_name else 0.5 for name in qb_stats['passer_player_name']]
        ),
        orientation='h',
    ))

    fig.add_trace(go.Bar(
        y=qb_stats['passer_player_name'],
        x=qb_stats['total_interceptions'],
        name='Interceptions',
        marker=dict(
            color=['red' for _ in qb_stats['passer_player_name']],
            opacity=[1.0 if qb_name is None or name == qb_name else 0.5 for name in qb_stats['passer_player_name']]
        ),
        orientation='h',
    ))

    fig.update_layout(
        title=f'Quarterback Touchdowns and Interceptions ({season})',
        xaxis_title='Count',
        yaxis_title='Quarterback',
        barmode='group',
        height=600,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return dcc.Graph(figure=fig)

def make_all_qbs_mean_cpoe_chart(season: int, qb_name: str = None) -> dcc.Graph:
    qb_stats = fetch_all_qb_season_totals(season)
    qb_stats = qb_stats.sort_values(by='mean_cpoe', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=qb_stats['passer_player_name'],
        x=qb_stats['mean_cpoe'],
        name='Mean CPOE',
        marker=dict(
            color=['purple' for _ in qb_stats['passer_player_name']],
            opacity=[1.0 if qb_name is None or name == qb_name else 0.5 for name in qb_stats['passer_player_name']]
        ),
        orientation='h',
    ))

    fig.update_layout(
        title=f'Quarterback Mean CPOE ({season})',
        xaxis_title='Mean CPOE',
        yaxis_title='Quarterback',
        height=600,
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return dcc.Graph(figure=fig)


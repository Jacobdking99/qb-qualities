import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
from src.data.data_processing import (
    fetch_all_qb_pbp_epa, 
    fetch_adv_qb_pbp_stats,
    fetch_all_qb_season_totals,
)

def make_all_qbs_epa_adj_chart(season: int = 2023, qb_name: str = None) -> plt.Figure:
    """Creates the chart for EPA adjusted quarterback metrics using Seaborn."""
    qb_adj = fetch_all_qb_pbp_epa(season)
    qb_adj = qb_adj.sort_values(by='avg_epa_per_dropback', ascending=True)

    fig, ax = plt.subplots(figsize=(8, 12))  # Taller and less wide
    sns.barplot(
        y=qb_adj['passer_player_name'],
        x=qb_adj['avg_epa_per_dropback'],
        color="blue",
        alpha=0.8,
        label="EPA",
        ax=ax
    )
    sns.barplot(
        y=qb_adj['passer_player_name'],
        x=qb_adj['epa_vs_def_and_ol'],
        color="orange",
        alpha=0.8,
        label="EPA vs Defense and OL",
        ax=ax
    )
    ax.set_title(f'Quarterback EPA Metrics ({season})', fontsize=18)
    ax.set_xlabel('EPA Metrics (Expected Points Added)', fontsize=14)
    ax.set_ylabel('Quarterback', fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.legend(loc="lower right", fontsize=12)

    # Fix tick labels for better readability
    ax.set_yticks(range(len(qb_adj['passer_player_name'])))
    ax.set_yticklabels(qb_adj['passer_player_name'], rotation=0, horizontalalignment='right')

    return fig

def make_all_qbs_yards_chart(season: int, qb_name: str = None) -> plt.Figure:
    """Creates the chart for yards gained using Seaborn."""
    qb_stats = fetch_all_qb_season_totals(season)
    qb_stats = qb_stats.sort_values(by='total_yards', ascending=True)

    fig, ax = plt.subplots(figsize=(8, 12))  # Taller and less wide
    sns.barplot(
        y=qb_stats['passer_player_name'],
        x=qb_stats['total_yards'],
        color="green",
        alpha=0.8,
        ax=ax
    )
    ax.set_title(f'Quarterback Yards Gained ({season})', fontsize=18)
    ax.set_xlabel('Total Yards Gained', fontsize=14)
    ax.set_ylabel('Quarterback', fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Fix tick labels for better readability
    ax.set_yticks(range(len(qb_stats['passer_player_name'])))
    ax.set_yticklabels(qb_stats['passer_player_name'], rotation=0, horizontalalignment='right')

    return fig

def make_all_qbs_td_int_chart(season: int, qb_name: str = None) -> plt.Figure:
    """Creates the chart for touchdowns and interceptions using Seaborn."""
    qb_stats = fetch_all_qb_season_totals(season)
    qb_stats['td_int_ratio'] = qb_stats['total_touchdowns'] / (qb_stats['total_interceptions'] + 1e-6)
    qb_stats = qb_stats.sort_values(by='td_int_ratio', ascending=True)

    fig, ax = plt.subplots(figsize=(8, 12))  # Taller and less wide
    sns.barplot(
        y=qb_stats['passer_player_name'],
        x=qb_stats['total_touchdowns'],
        color="green",
        alpha=0.8,
        label="Touchdowns",
        ax=ax
    )
    sns.barplot(
        y=qb_stats['passer_player_name'],
        x=qb_stats['total_interceptions'],
        color="red",
        alpha=0.8,
        label="Interceptions",
        ax=ax
    )
    ax.set_title(f'Quarterback Touchdowns and Interceptions ({season})', fontsize=18)
    ax.set_xlabel('Count (Touchdowns vs Interceptions)', fontsize=14)
    ax.set_ylabel('Quarterback', fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)
    ax.legend(loc="lower right", fontsize=12)

    # Fix tick labels for better readability
    ax.set_yticks(range(len(qb_stats['passer_player_name'])))
    ax.set_yticklabels(qb_stats['passer_player_name'], rotation=0, horizontalalignment='right')

    return fig

def make_all_qbs_mean_cpoe_chart(season: int, qb_name: str = None) -> plt.Figure:
    """Creates the chart for mean CPOE using Seaborn."""
    qb_stats = fetch_all_qb_season_totals(season)
    qb_stats = qb_stats.sort_values(by='mean_cpoe', ascending=True)

    fig, ax = plt.subplots(figsize=(8, 12))  # Taller and less wide
    sns.barplot(
        y=qb_stats['passer_player_name'],
        x=qb_stats['mean_cpoe'],
        color="purple",
        alpha=0.8,
        ax=ax
    )
    ax.set_title(f'Quarterback Mean CPOE ({season})', fontsize=18)
    ax.set_xlabel('Mean CPOE (Completion Percentage Over Expected)', fontsize=14)
    ax.set_ylabel('Quarterback', fontsize=14)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    # Fix tick labels for better readability
    ax.set_yticks(range(len(qb_stats['passer_player_name'])))
    ax.set_yticklabels(qb_stats['passer_player_name'], rotation=0, horizontalalignment='right')

    return fig


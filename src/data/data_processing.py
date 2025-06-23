import pandas as pd
import nfl_data_py as nfl
from src.cache import cache  # Import the centralized cache

@cache.memoize(timeout=3600)  # Cache the data for 1 hour
def fetch_qb_pbp_data(season: int) -> pd.DataFrame:
    """Fetches quarterback play-by-play data for a given NFL season.

    Args:
        season (int): The NFL season year (e.g., 2023).
    Returns:
        pd.DataFrame: DataFrame containing play-by-play data for the specified season.
    """
    pbp = nfl.import_pbp_data([season])

    # Filter to dropbacks only
    dropbacks = pbp[pbp['qb_dropback'] == 1].copy()

    # Calculate defensive skill metrics per defense per season
    def_metrics = (
        dropbacks.groupby(['season', 'defteam'])
        .agg(
            def_epa_per_dropback=('epa', 'mean'),
            def_success_rate_allowed=('success', 'mean'),
            def_pressure_rate=('qb_hit', 'sum'),
            def_dropbacks=('qb_dropback', 'count'),
        )
        .assign(def_pressure_rate=lambda df: df.def_pressure_rate / df.def_dropbacks)
        .reset_index()
    )

    # Calculate OL proxy metrics per offense per season
    ol_metrics = (
        dropbacks.groupby(['season', 'posteam'])
        .agg(
            pressures_allowed=('qb_hit', 'sum'),
            sacks_allowed=('sack', 'sum'),
            dropbacks=('qb_dropback', 'count'),
        )
        .assign(
            pressure_rate=lambda df: df.pressures_allowed / df.dropbacks,
            sack_rate=lambda df: df.sacks_allowed / df.dropbacks
        )
        .reset_index()
    )

    # Merge defensive and OL metrics onto dropbacks
    dropbacks = dropbacks.merge(def_metrics, on=['season', 'defteam'], how='left')
    dropbacks = dropbacks.merge(ol_metrics, on=['season', 'posteam'], how='left')

    # Filter for true QBs with min dropbacks threshold
    min_dropbacks = 150
    qb_counts = dropbacks.groupby(['season', 'passer_player_name']).size().reset_index(name='dropbacks')
    true_qbs = qb_counts[qb_counts['dropbacks'] >= min_dropbacks]['passer_player_name'].unique()
    dropbacks_true_qbs = dropbacks[dropbacks['passer_player_name'].isin(true_qbs)].copy()

    # Define clutch situations: 3rd/4th and long, last 5 minutes, close game (within 7 points)
    dropbacks_true_qbs['clutch_situation'] = (
        (dropbacks_true_qbs['down'].isin([3, 4])) &
        (dropbacks_true_qbs['ydstogo'] >= 7) &
        (dropbacks_true_qbs['game_seconds_remaining'] <= 300) &
        (dropbacks_true_qbs['score_differential'].abs() <= 7)
    )

    # Add play-level adjusted EPA
    dropbacks_true_qbs['adj_epa'] = (
        dropbacks_true_qbs['epa'] - dropbacks_true_qbs['def_epa_per_dropback']
    ) / (1 + dropbacks_true_qbs['pressure_rate'])

    return dropbacks_true_qbs

def fetch_qb_pbp_data_cached(season: int) -> pd.DataFrame:
    """Fetches cached quarterback play-by-play data and converts it back to a DataFrame.

    Args:
        season (int): The NFL season year (e.g., 2023).
    Returns:
        pd.DataFrame: DataFrame containing play-by-play data for the specified season.
    """
    cached_data = fetch_qb_pbp_data(season)
    return cached_data

def fetch_all_qb_pbp_epa(season: int) -> pd.DataFrame:
    """Fetches and processes quarterback adjusted EPA data for a given season.

    Args:
        season (int): The NFL season year (e.g., 2023).
    Returns:
        pd.DataFrame: Processed DataFrame with quarterback adjusted EPA metrics.
    """
    
    dropbacks_true_qbs = fetch_qb_pbp_data_cached(season)
    if dropbacks_true_qbs.empty:
        raise ValueError(f"No data found for season {season}.")

    # Aggregate overall QB metrics normalized by defense and OL skill
    qb_adj = (
        dropbacks_true_qbs.groupby(['season', 'passer_player_name'])
        .agg(
            dropbacks=('qb_dropback', 'count'),
            total_epa=('epa', 'sum'),
            avg_epa_per_dropback=('epa', 'mean'),
            avg_def_epa_allowed=('def_epa_per_dropback', 'mean'),
            avg_def_success_rate_allowed=('def_success_rate_allowed', 'mean'),
            avg_def_pressure_rate=('def_pressure_rate', 'mean'),
            avg_ol_pressure_rate_allowed=('pressure_rate', 'mean'),
            avg_ol_sack_rate_allowed=('sack_rate', 'mean'),
        )
        .reset_index()
    )

    # Calculate adjusted EPA metrics
    qb_adj['epa_vs_expectation'] = qb_adj['avg_epa_per_dropback'] - qb_adj['avg_def_epa_allowed']
    qb_adj['epa_vs_def_and_ol'] = qb_adj['epa_vs_expectation'] / (1 + qb_adj['avg_ol_pressure_rate_allowed'])

    # Filter to just QBs with over 200 dropbacks
    qb_adj = qb_adj[qb_adj['dropbacks'] >= 200].copy()

    return qb_adj

def fetch_adv_qb_pbp_stats(season: int, qb_name: str) -> pd.DataFrame:
    """Fetches data for a specific quarterback in a specific season and processes it to compute advanced metrics.

    Args:
        season (int): season year (e.g., 2023).

    Returns:
        pd.DataFrame: DataFrame containing advanced quarterback metrics for the specified season.
    """

    dropbacks_true_qbs = fetch_qb_pbp_data_cached(season)
    if dropbacks_true_qbs.empty:
        raise ValueError(f"No data found for season {season}.")
    
    # Advanced quarterback analytics
    adv_qb_stats = dropbacks_true_qbs.groupby(['season', 'passer_player_name']).agg(
        avg_cpoe=('cpoe', 'mean'),
        avg_adj_epa=('adj_epa', 'mean'),
        avg_pass_yards=('yards_gained', 'mean'),
        avg_air_yards=('air_yards', 'mean'),
        avg_pressure_rate=('pressure_rate', 'mean'),
    ).reset_index()

    # Clutch performance metrics
    clutch_adv_stats = (
        dropbacks_true_qbs[dropbacks_true_qbs['clutch_situation']]
        .groupby('passer_player_name').agg(
            clutch_avg_cpoe=('cpoe', 'mean'),
            clutch_avg_adj_epa=('adj_epa', 'mean'),
            clutch_avg_pass_yards=('yards_gained', 'mean'),
            clutch_avg_air_yards=('air_yards', 'mean'),
            clutch_avg_pressure_rate=('pressure_rate', 'mean'),
        ).reset_index()
    )
    # Non-clutch performance metrics
    non_clutch_adv_stats = (
        dropbacks_true_qbs[~dropbacks_true_qbs['clutch_situation']]
        .groupby('passer_player_name').agg(
            non_clutch_avg_cpoe=('cpoe', 'mean'),
            non_clutch_avg_adj_epa=('adj_epa', 'mean'),
            non_clutch_avg_pass_yards=('yards_gained', 'mean'),
            non_clutch_avg_air_yards=('air_yards', 'mean'),
            non_clutch_avg_pressure_rate=('pressure_rate', 'mean'),
        ).reset_index()
    )

    # Merge advanced all advanced stats
    adv_qb_stats = adv_qb_stats.merge(clutch_adv_stats, on='passer_player_name', how='left')    
    adv_qb_stats = adv_qb_stats.merge(non_clutch_adv_stats, on='passer_player_name', how='left')

    return adv_qb_stats[adv_qb_stats['passer_player_name'] == qb_name].reset_index(drop=True)

def fetch_all_qb_season_totals(season: int) -> pd.DataFrame:
    """Fetches and processes all quarterbacks' season aggregate stats for a given season.

    Args:
        season (int): The NFL season year (e.g., 2023).
    Returns:
        pd.DataFrame: DataFrame with all quarterbacks' aggregate stats for the specified season.
    """
    
    dropbacks_true_qbs = fetch_qb_pbp_data_cached(season)
   
    qb_season_totals = (
        dropbacks_true_qbs.groupby(['season', 'passer_player_name'])
        .agg(
            total_dropbacks=('qb_dropback', 'count'),
            total_epa=('epa', 'sum'),
            total_yards=('yards_gained', 'sum'),
            total_air_yards=('air_yards', 'sum'),
            mean_cpoe=('cpoe', 'mean'),
            total_touchdowns=('touchdown', 'sum'),
            total_interceptions=('interception', 'sum'),
            mean_success_rate=('success', 'mean'),
        )
        .reset_index()
    )
    return qb_season_totals



from pathlib import Path

import polars as pl

from ncaa_baseball.metadata.seasons import Season
from ncaa_baseball.metadata.options import SelectOption
from ncaa_baseball.metadata.scoreboards import ScoreboardGame


def seasons_to_dataframe(seasons: list[Season]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "ncaa_game_sport_year_ctl_id": s.ncaa_game_sport_year_ctl_id,
                "season_label": s.season_label,
                "academic_year": s.academic_year,
                "is_selected": s.is_selected,
            }
            for s in seasons
        ]
    )


def write_parquet(dataframe: pl.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.write_parquet(output_path)


def select_options_to_dataframe(
    options: list[SelectOption],
    id_column: str,
    label_column: str,
) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                id_column: option.ncaa_id,
                label_column: option.label,
                "is_selected": option.is_selected,
            }
            for option in options
        ]
    )

def scoreboard_games_to_dataframe(
    games: list[ScoreboardGame],
) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "ncaa_contest_id": game.ncaa_contest_id,
                "game_datetime_text": game.game_datetime_text,
                "attendance": game.attendance,
                "venue_text": game.venue_text,
                "status": game.status,
                "team_1_ncaa_team_id": game.team_1_ncaa_team_id,
                "team_1_name": game.team_1_name,
                "team_1_record": game.team_1_record,
                "team_1_score": game.team_1_score,
                "team_1_seed": game.team_1_seed,
                "team_1_runs_by_inning": game.team_1_runs_by_inning,
                "team_1_hits": game.team_1_hits,
                "team_1_errors": game.team_1_errors,
                "team_2_ncaa_team_id": game.team_2_ncaa_team_id,
                "team_2_name": game.team_2_name,
                "team_2_record": game.team_2_record,
                "team_2_score": game.team_2_score,
                "team_2_seed": game.team_2_seed,
                "team_2_runs_by_inning": game.team_2_runs_by_inning,
                "team_2_hits": game.team_2_hits,
                "team_2_errors": game.team_2_errors,
                "box_score_url": game.box_score_url,
                "winning_pitcher_ncaa_player_id": game.winning_pitcher_ncaa_player_id,
                "winning_pitcher_name": game.winning_pitcher_name,
                "losing_pitcher_ncaa_player_id": game.losing_pitcher_ncaa_player_id,
                "losing_pitcher_name": game.losing_pitcher_name,
                "save_pitcher_ncaa_player_id": game.save_pitcher_ncaa_player_id,
                "save_pitcher_name":
                game.save_pitcher_name,
            }
            for game in games
        ]
    )

def append_parquet(
    dataframe: pl.DataFrame,
    output_path: Path,
    subset: list[str] | None = None,
) -> None:
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_path.exists():
        existing = pl.read_parquet(output_path)

        dataframe = pl.concat(
            [existing, dataframe],
            how="vertical",
        )

    if subset is not None:
        dataframe = dataframe.unique(
            subset=subset,
            maintain_order=True,
        )

    dataframe.write_parquet(output_path)

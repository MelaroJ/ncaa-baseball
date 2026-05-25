from datetime import date, datetime, timedelta
from pathlib import Path

import typer

from ncaa_baseball.browser import fetch_page
from ncaa_baseball.config import load_config
from ncaa_baseball.snapshots import save_html_snapshot
from ncaa_baseball.metadata.seasons import parse_seasons
from ncaa_baseball.storage.parquet import seasons_to_dataframe, write_parquet, append_parquet
from ncaa_baseball.metadata.options import parse_select_options
from ncaa_baseball.storage.parquet import select_options_to_dataframe
from ncaa_baseball.metadata.scoreboards import parse_scoreboard_games
from ncaa_baseball.storage.parquet import scoreboard_games_to_dataframe


__version__ = "0.1.0"

app = typer.Typer(no_args_is_help=True)


def version_callback(value: bool) -> None:
    if value:
        print(f"ncaa-baseball {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the application version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    pass


@app.command()
def discover_scoreboard(
    date: str = typer.Option(..., "--date"),
) -> None:
    config = load_config()

    parsed_date = datetime.strptime(date, "%Y-%m-%d")
    ncaa_date = parsed_date.strftime("%m/%d/%Y")

    url = (
        "https://stats.ncaa.org/season_divisions/18783/"
        f"livestream_scoreboards?game_date={ncaa_date}"
    )

    result = fetch_page(
        url=url,
        config=config,
    )

    output_path = (
        config.raw_scoreboard_dir
        / f"{date}.html"
    )

    save_html_snapshot(
        html=result.html,
        output_path = output_path
    )

    print(output_path)

@app.command()
def parse_seasons_from_snapshot(
    path: Path = typer.Option(..., "--path", exists=True, readable=True),
) -> None:
    """Parse NCAA baseball season IDs from a saved scoreboard snapshot."""
    html = path.read_text(encoding="utf-8")

    for season in parse_seasons(html):
        print(
            season.ncaa_game_sport_year_ctl_id,
            season.season_label,
            season.academic_year,
            season.is_selected,
        )

@app.command()
def discover_seasons(
    snapshot: Path = typer.Option(
        ...,
        "--snapshot",
        exists=True,
        readable=True,
    ),
) -> None:
    """Extract NCAA baseball season metadata from a scoreboard snapshot."""

    html = snapshot.read_text(encoding="utf-8")

    seasons = parse_seasons(html)

    dataframe = seasons_to_dataframe(seasons)

    config = load_config()
    output_path = config.metadata_dir / "seasons.parquet"

    write_parquet(
        dataframe=dataframe,
        output_path=output_path,
    )

    print(output_path)

@app.command()
def discover_scoreboard_metadata(
    snapshot: Path = typer.Option(
        ...,
        "--snapshot",
        exists=True,
        readable=True,
    ),
) -> None:
    """Extract dropdown metadata from a saved scoreboard snapshot."""

    config = load_config()
    html = snapshot.read_text(encoding="utf-8")

    outputs = [
        (
            "#season_division_id_select",
            "ncaa_season_division_id",
            "division_label",
            "divisions.parquet",
        ),
        (
            "#conference_id_select",
            "ncaa_conference_id",
            "conference_label",
            "conferences.parquet",
        ),
        (
            "#tournament_id_select",
            "ncaa_tournament_id",
            "tournament_label",
            "tournaments.parquet",
        ),
    ]

    for selector, id_column, label_column, filename in outputs:
        options = parse_select_options(
            html=html,
            selector=selector,
        )

        dataframe = select_options_to_dataframe(
            options=options,
            id_column=id_column,
            label_column=label_column,
        )

        output_path = config.metadata_dir / filename

        write_parquet(
            dataframe=dataframe,
            output_path=output_path,
        )

        print(output_path)

@app.command()
def discover_games(
    snapshot: Path = typer.Option(
        ...,
        "--snapshot",
        exists=True,
        readable=True,
    ),
) -> None:
    """Extract NCAA contest IDs and box score URLs from a scoreboard snapshot."""

    config = load_config()
    html = snapshot.read_text(encoding="utf-8")

    games = parse_scoreboard_games(html)

    dataframe = scoreboard_games_to_dataframe(games)

    output_path = config.parquet_dir / "scoreboard_games.parquet"

    append_parquet(
        dataframe=dataframe,
        output_path=output_path,
        subset=["ncaa_contest_id"],
    )

    print(f"{len(games)} games")
    print(output_path)



def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def iter_dates(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)

@app.command()
def ingest_scoreboards(
    start_date: str = typer.Option(..., "--start-date"),
    end_date: str = typer.Option(..., "--end-date"),
    refresh: bool = typer.Option(False, "--refresh"),
) -> None:
    config = load_config()

    output_path = config.parquet_dir / "scoreboard_games.parquet"

    total_games = 0

    for current_date in iter_dates(
        parse_iso_date(start_date),
        parse_iso_date(end_date),
    ):
        date_text = current_date.isoformat()
        snapshot_path = config.raw_scoreboard_dir / f"{date_text}.html"

        if refresh or not snapshot_path.exists():
            ncaa_date = current_date.strftime("%m/%d/%Y")

            url = (
                "https://stats.ncaa.org/season_divisions/18783/"
                f"livestream_scoreboards?game_date={ncaa_date}"
            )

            result = fetch_page(url=url, config=config)

            save_html_snapshot(
                html=result.html,
                output_path=snapshot_path,
            )

        html = snapshot_path.read_text(encoding="utf-8")
        games = parse_scoreboard_games(html)
        dataframe = scoreboard_games_to_dataframe(games)

        append_parquet(
            dataframe=dataframe,
            output_path=output_path,
            subset=["ncaa_contest_id"],
        )

        total_games += len(games)
        print(f"{date_text}: {len(games)} games")

    print(f"parsed {total_games} games")
    print(output_path)

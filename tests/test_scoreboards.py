from pathlib import Path

from ncaa_baseball.metadata.scoreboards import (
    parse_scoreboard_games,
)


FIXTURE_PATH = Path(
    "tests/fixtures/scoreboard_2026-05-22.html"
)


def test_parse_scoreboard_games() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    games = parse_scoreboard_games(html)

    assert len(games) > 0

    first_game = games[0]

    assert first_game.ncaa_contest_id == 6581970

    assert first_game.team_1_name == "The Citadel"
    assert first_game.team_2_name == "Mercer"

    assert first_game.team_1_seed == 5
    assert first_game.team_2_seed == 1

    assert first_game.team_1_score == 14
    assert first_game.team_2_score == 4

    assert first_game.team_1_hits == 16
    assert first_game.team_2_hits == 10

    assert first_game.winning_pitcher_name == "Bryce Coulter"
    assert first_game.winning_pitcher_ncaa_player_id == 11220561

    assert first_game.losing_pitcher_name == "Jeb Johnson"
    assert first_game.losing_pitcher_ncaa_player_id == 11211604

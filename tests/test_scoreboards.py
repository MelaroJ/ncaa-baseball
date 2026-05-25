from pathlib import Path

from ncaa_baseball.metadata.scoreboards import parse_scoreboard_games


FIXTURE_PATH = Path("tests/fixtures/scoreboard_minimal.html")


def test_parse_scoreboard_games() -> None:
    html = FIXTURE_PATH.read_text(encoding="utf-8")

    games = parse_scoreboard_games(html)

    assert len(games) == 2

    first_game = games[0]

    assert first_game.ncaa_contest_id == 6581970
    assert first_game.team_1_name == "The Citadel"
    assert first_game.team_2_name == "Mercer"
    assert first_game.team_1_seed == 5
    assert first_game.team_2_seed == 1
    assert first_game.team_1_score == 14
    assert first_game.team_2_score == 4
    assert first_game.winning_pitcher_name == "Bryce Coulter"
    assert first_game.losing_pitcher_name == "Jeb Johnson"
    assert first_game.save_pitcher_name is None

    second_game = games[1]

    assert second_game.ncaa_contest_id == 6581859
    assert second_game.team_1_name == "Rice"
    assert second_game.team_2_name == "East Carolina"
    assert second_game.save_pitcher_name == "Ethan Norby"
    assert second_game.save_pitcher_ncaa_player_id == 9687983

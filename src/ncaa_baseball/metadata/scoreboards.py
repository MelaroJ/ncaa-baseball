import re
from dataclasses import dataclass

from bs4 import BeautifulSoup
from bs4.element import Tag

from ncaa_baseball.constants import NCAA_BASE_URL


@dataclass(slots=True)
class ScoreboardGame:
    ncaa_contest_id: int

    game_datetime_text: str | None
    attendance: int | None
    venue_text: str | None
    status: str | None

    team_1_ncaa_team_id: int | None
    team_1_name: str
    team_1_record: str | None
    team_1_score: int | None
    team_1_seed: int | None
    team_1_runs_by_inning: list[int | None]
    team_1_hits: int | None
    team_1_errors: int | None

    team_2_ncaa_team_id: int | None
    team_2_name: str
    team_2_record: str | None
    team_2_score: int | None
    team_2_seed: int | None
    team_2_runs_by_inning: list[int | None]
    team_2_hits: int | None
    team_2_errors: int | None

    winning_pitcher_ncaa_player_id: int | None
    winning_pitcher_name: str | None

    losing_pitcher_ncaa_player_id: int | None
    losing_pitcher_name: str | None

    save_pitcher_ncaa_player_id: int | None
    save_pitcher_name: str | None

    box_score_url: str


def parse_int(text: str) -> int | None:
    cleaned = text.replace(",", "").strip()
    if not cleaned:
        return None
    return int(cleaned)


def parse_team_text(text: str) -> tuple[str, str | None, int | None]:
    cleaned = " ".join(text.split())

    record: str | None = None
    seed: int | None = None

    record_match = re.search(r"\((?P<record>[^)]+)\)$", cleaned)
    if record_match is not None:
        record = record_match.group("record")
        cleaned = cleaned[: record_match.start()].strip()

    seed_match = re.match(r"^#(?P<seed>\d+)\s+(?P<name>.+)$", cleaned)
    if seed_match is not None:
        seed = int(seed_match.group("seed"))
        cleaned = seed_match.group("name").strip()

    return cleaned, record, seed


def parse_team_id(href: str | None) -> int | None:
    if href is None:
        return None

    match = re.search(r"/teams/(\d+)$", href)
    if match is None:
        return None

    return int(match.group(1))


def parse_player_id(href: str | None) -> int | None:
    if href is None:
        return None

    match = re.search(r"/players/(\d+)$", href)
    if match is None:
        return None

    return int(match.group(1))


def parse_score_from_row(row: Tag) -> int | None:
    score_div = row.select_one('div[id^="score_"]')
    if score_div is None:
        return None

    return parse_int(score_div.get_text(strip=True))


def parse_stat_from_row(row: Tag, prefix: str) -> int | None:
    div = row.select_one(f'div[id^="{prefix}_"]')
    if div is None:
        return None

    return parse_int(div.get_text(strip=True))


def parse_linescores(table: Tag, contest_id: int) -> tuple[list[int | None], list[int | None]]:
    linescore_table = table.select_one(f"#linescore_{contest_id}_table")
    if linescore_table is None:
        return [], []

    rows = linescore_table.select("tr")
    if len(rows) < 2:
        return [], []

    def parse_row(row: Tag) -> list[int | None]:
        values: list[int | None] = []

        for cell in row.select("td"):
            text = cell.get_text(strip=True)
            values.append(parse_int(text) if text else None)

        return values

    return parse_row(rows[0]), parse_row(rows[1])


def parse_game_datetime_and_attendance(table: Tag) -> tuple[str | None, int | None]:
    first_row = table.select_one("tbody > tr")
    if first_row is None:
        return None, None

    text = " ".join(first_row.get_text(" ", strip=True).split())

    attendance: int | None = None
    attendance_match = re.search(r"Attend:\s*([\d,]+)", text)
    if attendance_match is not None:
        attendance = parse_int(attendance_match.group(1))
        text = re.sub(r"Attend:\s*[\d,]+", "", text).strip()

    return text or None, attendance


def parse_venue(table: Tag) -> str | None:
    rows = table.select("tbody > tr")

    for row in rows[:3]:
        text = " ".join(row.get_text(" ", strip=True).split())
        if text.startswith("@"):
            return text

    return None


def parse_status(table: Tag, contest_id: int) -> str | None:
    status = table.select_one(f".livestream_status_{contest_id}")
    if status is None:
        return None

    text = " ".join(status.get_text(" ", strip=True).split())
    return text or None


def parse_pitcher_decision(
    table: Tag,
    prefix: str,
) -> tuple[int | None, str | None]:
    text_pattern = f"{prefix}:"

    for cell in table.select("tfoot td"):
        text = " ".join(cell.get_text(" ", strip=True).split())

        if text_pattern not in text:
            continue

        for link in cell.select('a[href^="/players/"]'):
            previous_text = link.previous_sibling
            if previous_text is None:
                continue

            if text_pattern in str(previous_text):
                return (
                    parse_player_id(link.get("href")),
                    link.get_text(" ", strip=True),
                )

    return None, None


def parse_game_table(table: Tag) -> ScoreboardGame | None:
    box_score_link = table.select_one('a[href*="/contests/"][href$="/box_score"]')
    if box_score_link is None:
        return None

    href = box_score_link.get("href")
    if href is None:
        return None

    contest_match = re.search(r"/contests/(\d+)/box_score$", href)
    if contest_match is None:
        return None

    contest_id = int(contest_match.group(1))

    team_rows = table.select(f'tr[id="contest_{contest_id}"]')
    if len(team_rows) < 2:
        return None

    team_1_link = team_rows[0].select_one('a[href^="/teams/"]')
    team_2_link = team_rows[1].select_one('a[href^="/teams/"]')

    if team_1_link is None or team_2_link is None:
        return None

    team_1_name, team_1_record, team_1_seed = parse_team_text(
        team_1_link.get_text(" ", strip=True)
    )
    team_2_name, team_2_record, team_2_seed = parse_team_text(
        team_2_link.get_text(" ", strip=True)
    )

    team_1_runs_by_inning, team_2_runs_by_inning = parse_linescores(
        table=table,
        contest_id=contest_id,
    )

    game_datetime_text, attendance = parse_game_datetime_and_attendance(table)

    winning_pitcher_id, winning_pitcher_name = parse_pitcher_decision(table, "W")
    losing_pitcher_id, losing_pitcher_name = parse_pitcher_decision(table, "L")
    save_pitcher_id, save_pitcher_name = parse_pitcher_decision(table, "S")

    return ScoreboardGame(
        ncaa_contest_id=contest_id,
        game_datetime_text=game_datetime_text,
        attendance=attendance,
        venue_text=parse_venue(table),
        status=parse_status(table, contest_id),
        team_1_ncaa_team_id=parse_team_id(team_1_link.get("href")),
        team_1_name=team_1_name,
        team_1_record=team_1_record,
        team_1_score=parse_score_from_row(team_rows[0]),
        team_1_seed=team_1_seed,
        team_1_runs_by_inning=team_1_runs_by_inning,
        team_1_hits=parse_stat_from_row(team_rows[0], "hits"),
        team_1_errors=parse_stat_from_row(team_rows[0], "errors"),
        team_2_ncaa_team_id=parse_team_id(team_2_link.get("href")),
        team_2_name=team_2_name,
        team_2_record=team_2_record,
        team_2_score=parse_score_from_row(team_rows[1]),
        team_2_seed=team_2_seed,
        team_2_runs_by_inning=team_2_runs_by_inning,
        team_2_hits=parse_stat_from_row(team_rows[1], "hits"),
        team_2_errors=parse_stat_from_row(team_rows[1], "errors"),
        winning_pitcher_ncaa_player_id=winning_pitcher_id,
        winning_pitcher_name=winning_pitcher_name,
        losing_pitcher_ncaa_player_id=losing_pitcher_id,
        losing_pitcher_name=losing_pitcher_name,
        save_pitcher_ncaa_player_id=save_pitcher_id,
        save_pitcher_name=save_pitcher_name,
        box_score_url=f"{NCAA_BASE_URL}{href}",
    )


def parse_scoreboard_games(html: str) -> list[ScoreboardGame]:
    soup = BeautifulSoup(html, "lxml")

    games: list[ScoreboardGame] = []
    seen_contest_ids: set[int] = set()

    for table in soup.select("table"):
        game = parse_game_table(table)
        if game is None:
            continue

        if game.ncaa_contest_id in seen_contest_ids:
            continue

        seen_contest_ids.add(game.ncaa_contest_id)
        games.append(game)

    return games

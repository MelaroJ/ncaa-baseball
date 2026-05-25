from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(slots=True)
class Season:
    ncaa_game_sport_year_ctl_id: int
    season_label: str
    academic_year: int
    is_selected: bool


def academic_year_from_label(season_label: str) -> int:
    """Convert '2024-25' to 2025."""
    start_year = int(season_label.split("-")[0])
    return start_year + 1


def parse_seasons(html: str) -> list[Season]:
    soup = BeautifulSoup(html, "lxml")

    select = soup.select_one("#game_sport_year_ctl_id_select")
    if select is None:
        raise ValueError("Could not find #game_sport_year_ctl_id_select")

    seasons: list[Season] = []

    for option in select.select("option"):
        value = option.get("value")
        label = option.get_text(strip=True)

        if not value or not label:
            continue

        seasons.append(
            Season(
                ncaa_game_sport_year_ctl_id=int(value),
                season_label=label,
                academic_year=academic_year_from_label(label),
                is_selected=option.has_attr("selected"),
            )
        )

    return seasons

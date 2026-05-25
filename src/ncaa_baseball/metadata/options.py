from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(slots=True)
class SelectOption:
    ncaa_id: int
    label: str
    is_selected: bool


def parse_select_options(html: str, selector: str) -> list[SelectOption]:
    soup = BeautifulSoup(html, "lxml")
    select = soup.select_one(selector)

    if select is None:
        raise ValueError(f"Could not find {selector}")

    options: list[SelectOption] = []

    for option in select.select("option"):
        value = option.get("value")
        label = option.get_text(strip=True)

        if not value or not label or label.startswith("Select "):
            continue

        options.append(
            SelectOption(
                ncaa_id=int(value),
                label=label,
                is_selected=option.has_attr("selected"),
            )
        )

    return options

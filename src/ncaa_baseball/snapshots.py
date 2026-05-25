from pathlib import Path


def save_html_snapshot(
    html: str,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        html,
        encoding="utf-8",
    )

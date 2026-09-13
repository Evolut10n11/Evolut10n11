from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

MISSIONS_URL = (
    "https://raw.githubusercontent.com/Evolut10n11/lumen-lab/main/state/missions.json"
)
PROFILE_URL = (
    "https://raw.githubusercontent.com/Evolut10n11/lumen-lab/main/state/profile.json"
)
README_PATH = Path("README.md")
START_MARKER = "<!-- LUMEN:FOCUS_START -->"
END_MARKER = "<!-- LUMEN:FOCUS_END -->"


def fetch_json(url: str) -> Any:
    request = Request(url, headers={"User-Agent": "Evolut10n11-profile-focus-sync"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)


def base_score(mission: dict[str, Any]) -> float:
    feasibility = 11 - int(mission["effort"])
    value = (
        int(mission["impact"]) * 0.30
        + int(mission["urgency"]) * 0.20
        + int(mission["leverage"]) * 0.25
        + int(mission["momentum"]) * 0.15
        + feasibility * 0.10
        - int(mission["risk"]) * 0.15
    )
    return round(value, 2)


def profile_alignment(mission: dict[str, Any], profile: dict[str, Any]) -> float:
    priorities = {
        str(key).strip().casefold(): int(value)
        for key, value in profile.get("priorities", {}).items()
    }
    weights = [
        priorities[tag.strip().casefold()]
        for tag in mission.get("tags", [])
        if tag.strip().casefold() in priorities
    ]
    return float(max(weights)) if weights else 5.0


def mission_score(mission: dict[str, Any], profile: dict[str, Any]) -> float:
    base = base_score(mission)
    alignment = profile_alignment(mission, profile)
    alignment_adjustment = (alignment - 5.0) * 0.30
    risk_tolerance = int(profile["risk_tolerance"])
    risk_over_tolerance = max(0, int(mission["risk"]) - risk_tolerance)
    risk_adjustment = risk_over_tolerance * 0.10
    return round(min(10.0, max(0.0, base + alignment_adjustment - risk_adjustment)), 2)


def choose_focus(missions: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    active = [mission for mission in missions if mission.get("status") == "active"]
    if not active:
        raise RuntimeError("Lumen has no active missions")
    return sorted(
        active,
        key=lambda mission: (-mission_score(mission, profile), str(mission["id"])),
    )[0]


def one_line(value: Any) -> str:
    return " ".join(str(value).split())


def render_focus(mission: dict[str, Any], profile: dict[str, Any]) -> str:
    score = mission_score(mission, profile)
    base = base_score(mission)
    title = one_line(mission["title"])
    mission_id = one_line(mission["id"])
    profile_id = one_line(profile["id"])
    why_now = one_line(mission["why_now"])
    next_action = one_line(mission["next_action"])
    return "\n".join(
        [
            START_MARKER,
            f"> **Current focus — {title}**  ",
            f"> `{mission_id}` · Lumen priority `{score:.2f}` (base `{base:.2f}`) · profile `{profile_id}`  ",
            f"> {why_now}  ",
            f"> **Next:** {next_action}",
            END_MARKER,
        ]
    )


def replace_focus(readme: str, block: str) -> str:
    start = readme.find(START_MARKER)
    end = readme.find(END_MARKER)
    if start == -1 or end == -1 or end < start:
        raise RuntimeError("README Lumen focus markers are missing or invalid")
    end += len(END_MARKER)
    return readme[:start] + block + readme[end:]


def main() -> int:
    missions = fetch_json(MISSIONS_URL)
    profile = fetch_json(PROFILE_URL)
    if not isinstance(missions, list) or not isinstance(profile, dict):
        raise RuntimeError("Unexpected Lumen state shape")

    focus = choose_focus(missions, profile)
    current = README_PATH.read_text(encoding="utf-8")
    updated = replace_focus(current, render_focus(focus, profile))

    if updated == current:
        print(f"Lumen focus already current: {focus['id']}")
        return 0

    README_PATH.write_text(updated, encoding="utf-8")
    print(
        "Updated Lumen focus: "
        f"{focus['id']} score={mission_score(focus, profile):.2f} profile={profile['id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

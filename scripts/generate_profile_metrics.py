from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

USERNAME = os.getenv("PROFILE_USERNAME", "Evolut10n11")
TOKEN = os.getenv("GITHUB_TOKEN", "")
OUT_DIR = Path("assets/metrics")
API = "https://api.github.com"


def github_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Evolut10n11-profile-metrics",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            return json.load(response)
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"GitHub API request failed for {url}: {exc}") from exc


def load_repositories(username: str) -> list[dict]:
    repos: list[dict] = []
    page = 1
    while True:
        batch = github_json(
            f"{API}/users/{username}/repos?type=owner&sort=updated&per_page=100&page={page}"
        )
        if not isinstance(batch, list):
            raise RuntimeError("GitHub repositories response was not a list")
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def collect_metrics(username: str) -> tuple[dict[str, int], Counter[str]]:
    profile = github_json(f"{API}/users/{username}")
    repositories = load_repositories(username)
    public_repos = [
        repo
        for repo in repositories
        if not repo.get("fork")
        and not repo.get("archived")
        and repo.get("name") != username
    ]

    stats = {
        "Public repos": int(profile.get("public_repos", len(repositories))),
        "Stars": sum(int(repo.get("stargazers_count", 0)) for repo in public_repos),
        "Forks": sum(int(repo.get("forks_count", 0)) for repo in public_repos),
        "Followers": int(profile.get("followers", 0)),
    }

    languages: Counter[str] = Counter()
    for repo in public_repos:
        language_url = repo.get("languages_url")
        if not language_url:
            continue
        payload = github_json(language_url)
        if not isinstance(payload, dict):
            continue
        for language, byte_count in payload.items():
            if isinstance(language, str) and isinstance(byte_count, int):
                languages[language] += byte_count

    return stats, languages


def svg_header(width: int, height: int, background: str, border: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}</style>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{background}" stroke="{border}"/>',
    ]


def write_stats_card(path: Path, stats: dict[str, int], *, dark: bool) -> None:
    width, height = 420, 165
    background = "#0d1117" if dark else "#ffffff"
    border = "#30363d" if dark else "#d0d7de"
    title = "#58a6ff" if dark else "#0969da"
    text = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#656d76"

    parts = svg_header(width, height, background, border)
    parts.append(f'<text x="22" y="34" font-size="18" font-weight="600" fill="{title}">GitHub stats</text>')

    positions = [(22, 76), (220, 76), (22, 128), (220, 128)]
    for (label, value), (x, y) in zip(stats.items(), positions):
        parts.append(f'<text x="{x}" y="{y}" font-size="24" font-weight="700" fill="{text}">{value}</text>')
        parts.append(f'<text x="{x}" y="{y + 20}" font-size="12" fill="{muted}">{escape(label)}</text>')

    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_languages_card(path: Path, languages: Counter[str], *, dark: bool) -> None:
    width, height = 420, 165
    background = "#0d1117" if dark else "#ffffff"
    border = "#30363d" if dark else "#d0d7de"
    title = "#58a6ff" if dark else "#0969da"
    text = "#e6edf3" if dark else "#1f2328"
    muted = "#8b949e" if dark else "#656d76"
    bar_bg = "#21262d" if dark else "#eaeef2"
    accent = "#2f81f7" if dark else "#0969da"

    top = languages.most_common(5)
    total = sum(value for _, value in top) or 1

    parts = svg_header(width, height, background, border)
    parts.append(f'<text x="22" y="34" font-size="18" font-weight="600" fill="{title}">Top languages</text>')

    if not top:
        parts.append(f'<text x="22" y="82" font-size="13" fill="{muted}">No public language data yet.</text>')
    else:
        y = 60
        for language, value in top:
            percent = value / total
            bar_width = max(2, round(205 * percent))
            parts.append(f'<text x="22" y="{y}" font-size="12" font-weight="600" fill="{text}">{escape(language)}</text>')
            parts.append(f'<text x="382" y="{y}" text-anchor="end" font-size="11" fill="{muted}">{percent * 100:.1f}%</text>')
            parts.append(f'<rect x="145" y="{y - 9}" width="205" height="8" rx="4" fill="{bar_bg}"/>')
            parts.append(f'<rect x="145" y="{y - 9}" width="{bar_width}" height="8" rx="4" fill="{accent}"/>')
            y += 23

    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stats, languages = collect_metrics(USERNAME)

    write_stats_card(OUT_DIR / "stats-light.svg", stats, dark=False)
    write_stats_card(OUT_DIR / "stats-dark.svg", stats, dark=True)
    write_languages_card(OUT_DIR / "languages-light.svg", languages, dark=False)
    write_languages_card(OUT_DIR / "languages-dark.svg", languages, dark=True)

    print(
        f"Generated profile metrics for {USERNAME}: "
        f"{stats['Public repos']} repos, {len(languages)} languages"
    )


if __name__ == "__main__":
    main()

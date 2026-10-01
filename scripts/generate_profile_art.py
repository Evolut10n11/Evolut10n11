"""Generate restrained, theme-aware profile cards and technology labels."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parents[1] / "assets" / "profile"
THEMES = {
    "dark": {"bg": "#131922", "border": "#2a3442", "text": "#edf1f7", "muted": "#a5afbf", "chip": "#1b2330", "chip_text": "#c2cbd8"},
    "light": {"bg": "#fafbfd", "border": "#dce2eb", "text": "#202a3c", "muted": "#5e6a7e", "chip": "#f0f3f8", "chip_text": "#4e5c73"},
}
PROJECTS = [
    {"id": "robotci", "title": "RobotCI", "category": "ROBOTICS / DEVEX", "colors": ("#99b8fa", "#456ba7"),
     "description": ["Регрессионные проверки роботов.", "Сценарии ROS 2 / Nav2, сравнение", "запусков и 2D/3D-просмотр."],
     "tags": ["Python", "ROS 2", "MCP"],
     "icon": '<rect x="15" y="22" width="46" height="34" rx="9"/><path d="M38 14v8M9 35v11m58-11v11M26 56v7m24-7v7"/><circle cx="29" cy="38" r="2"/><circle cx="47" cy="38" r="2"/><path d="M30 47h16"/>'},
    {"id": "lumen", "title": "Lumen Lab", "category": "PERSONAL AI", "colors": ("#b9a9e6", "#7c60a5"),
     "description": ["Desktop-ассистент для работы", "с целями и задачами.", "Контекст хранится локально."],
     "tags": ["Python", "React", "Tauri"],
     "icon": '<rect x="12" y="16" width="52" height="40" rx="7"/><path d="M12 29h52M25 64h26M38 56v8M22 22h1m6 0h1M24 39h13m-13 8h27"/>'},
    {"id": "elaine", "title": "Elaine", "category": "VOICE / LLM", "colors": ("#83cbbd", "#387d71"),
     "description": ["Голосовой ассистент для Twitch.", "Распознавание речи, локальная LLM", "и озвучивание ответов."],
     "tags": ["Whisper", "LLM", "Silero TTS"],
     "icon": '<path d="M12 33v10m9-19v28m9-37v46m9-35v24m9-30v36m9-43v50m9-34v18" stroke-linecap="round"/>'},
    {"id": "documents", "title": "Local AI Doc Agent", "category": "DOCUMENT AI", "colors": ("#aabbd6", "#627ca3"),
     "description": ["Ответы по PDF, DOCX и TXT.", "Извлечение данных по правилам", "и локальный LLM fallback."],
     "tags": ["Python", "FastAPI", "llama.cpp"],
     "icon": '<path d="M24 12h26l12 12v37a4 4 0 0 1-4 4H24a4 4 0 0 1-4-4V16a4 4 0 0 1 4-4ZM49 12v15h13M29 38h23M29 47h23M29 56h15M12 24v40a8 8 0 0 0 8 8"/>'},
]
TOOLS = [("python", "Python"), ("fastapi", "FastAPI"), ("postgresql", "PostgreSQL"), ("qwen", "Qwen"), ("langfuse", "Langfuse"), ("github-actions", "GitHub Actions")]


def text(x, y, value, size, color, weight=400, extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>'


def svg(width, height, title, body, padding=0):
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + 2 * padding}" height="{height + 2 * padding}" viewBox="{-padding} {-padding} {width + 2 * padding} {height + 2 * padding}" role="img" aria-labelledby="title">',
        f'<title id="title">{escape(title)}</title>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}</style>',
        *body, '</svg>', '',
    ])


def card(project, theme):
    c = THEMES[theme]
    accent = project["colors"][theme == "light"]
    body = [
        f'<rect x="1" y="1" width="798" height="372" rx="20" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        text(40, 51, project["category"], 19, accent, 500, 'letter-spacing="2"'),
        text(40, 116, project["title"], 48, c["text"], 600, 'letter-spacing="-1"'),
        f'<rect x="672" y="32" width="86" height="86" rx="21" fill="{accent}" fill-opacity=".07"/>',
        f'<g transform="translate(677 37)" fill="none" stroke="{accent}" stroke-width="2.4" stroke-linejoin="round">{project["icon"]}</g>',
    ]
    for i, line in enumerate(project["description"]):
        body.append(text(42, 179 + i * 36, line, 29, c["muted"]))
    x = 40
    for tag in project["tags"]:
        width = len(tag) * 13 + 30
        body.extend([
            f'<rect x="{x}" y="298" width="{width}" height="40" rx="9" fill="{c["chip"]}"/>',
            text(x + 15, 325, tag, 22, c["chip_text"], 450),
        ])
        x += width + 12
    body.append(f'<path d="M716 321h30m0 0-10-10m10 10-10 10" fill="none" stroke="{c["muted"]}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(800, 374, project["title"] + ". " + " ".join(project["description"]), body, padding=12)


def badge(label, theme):
    c = THEMES[theme]
    width = len(label) * 7.1 + 26
    body = [
        f'<rect x=".5" y=".5" width="{width - 1}" height="29" rx="7" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        text(width / 2, 20, label, 12.5, c["chip_text"], 500, 'text-anchor="middle"'),
    ]
    return svg(round(width, 1), 30, label, body, padding=3)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        for project in PROJECTS:
            (OUT / f'{project["id"]}-{theme}.svg').write_text(card(project, theme), encoding="utf-8")
        for key, label in TOOLS:
            (OUT / f"tool-{key}-{theme}.svg").write_text(badge(label, theme), encoding="utf-8")
    print("Generated 8 project cards and 12 technology labels.")


if __name__ == "__main__":
    main()

"""Generate the profile's self-contained, theme-aware SVG artwork (stdlib only)."""

from pathlib import Path
from xml.sax.saxutils import escape
import math

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "profile"
THEMES = {
    "dark": dict(bg="#111a22", panel="#15222b", border="#26343e", text="#edf4f1", muted="#9aaca8", accent="#80d7bd", line="#36584f"),
    "light": dict(bg="#f6f9f7", panel="#edf3ef", border="#d8e4dd", text="#172b25", muted="#586e63", accent="#176b50", line="#b2ccbf"),
}


def text(x, y, value, size, color, weight=400, extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" {extra}>{escape(value)}</text>'


def svg(width, height, title, body, padding=0):
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width + padding * 2}" height="{height + padding * 2}" viewBox="{-padding} {-padding} {width + padding * 2} {height + padding * 2}" role="img" aria-labelledby="title">',
        f'<title id="title">{escape(title)}</title>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}</style>',
        *body,
        '</svg>',
        '',
    ])


def hero(c):
    body = [
        f'<rect x="1" y="1" width="1198" height="418" rx="24" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        f'<path d="M48 56h24" stroke="{c["accent"]}" stroke-width="3"/>',
        text(86, 63, "IVAN RODIONOV", 19, c["text"], 600, 'letter-spacing="3"'),
        text(48, 157, "Инженерия AI.", 66, c["text"], 650, 'letter-spacing="-2"'),
        text(48, 229, "От идеи до системы.", 53, c["text"], 450, 'letter-spacing="-1.5"'),
        text(50, 279, "Агенты · Голос · Инструменты разработчика", 23, c["muted"]),
        f'<path d="M48 335h1104" stroke="{c["border"]}"/>',
        text(50, 378, "AI / LLM ENGINEER", 16, c["accent"], 600, 'letter-spacing="2.5"'),
        text(1150, 378, "@Evolut10n11", 17, c["muted"], 400, 'text-anchor="end"'),
    ]
    # An orbital signal: original vector geometry, no fonts or remote assets required.
    body.append(f'<g fill="none" stroke="{c["line"]}" stroke-width="1.4">')
    for radius in [61, 105, 149]:
        body.append(f'<circle cx="978" cy="174" r="{radius}"/>')
    body.extend([
        '<path d="M804 174h348M978 22v304" stroke-dasharray="3 9"/>',
        '<ellipse cx="978" cy="174" rx="158" ry="55" transform="rotate(-32 978 174)"/>',
        '</g>',
    ])
    pts = []
    for i in range(301):
        x = 821 + i
        envelope = math.exp(-((i - 150) / 58) ** 2)
        y = 174 + math.sin(i / 7.3) * envelope * 49
        pts.append(f'{x},{y:.2f}')
    body.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{c["accent"]}" stroke-width="2.8"/>')
    for x, y, r in [(1104, 95, 5), (922, 264, 4), (978, 174, 6)]:
        body.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c["accent"]}"/>')
    return svg(1200, 420, "Иван Родионов — AI / LLM Engineer. Инженерия AI: от идеи до системы.", body)


def mobile_hero(c):
    body = [
        f'<rect x="1" y="1" width="798" height="458" rx="24" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        f'<path d="M40 59h25" stroke="{c["accent"]}" stroke-width="3"/>',
        text(82, 68, "IVAN RODIONOV", 28, c["text"], 600, 'letter-spacing="3"'),
        text(40, 168, "Инженерия AI.", 74, c["text"], 650, 'letter-spacing="-2"'),
        text(40, 239, "От идеи до системы.", 54, c["text"], 450, 'letter-spacing="-1.5"'),
        text(42, 299, "Агенты · Голос · Инструменты", 28, c["muted"]),
        f'<path d="M40 351h720" stroke="{c["border"]}"/>',
        text(42, 409, "AI / LLM ENGINEER", 24, c["accent"], 600, 'letter-spacing="2"'),
        f'<path d="M653 399h24l10-20 15 37 15-28 10 11h30" fill="none" stroke="{c["accent"]}" stroke-width="3"/>',
    ]
    return svg(800, 460, "Иван Родионов — AI / LLM Engineer. Инженерия AI: от идеи до системы.", body)


PROJECTS = [
    ("robotci", "01 / ROBOTICS & DEVEX", "RobotCI", ["Проверки поведения роботов.", "Повторяемые сценарии ROS 2 / Nav2,", "сравнение с эталоном и просмотр", "запусков в 2D и 3D."], "Python  /  ROS 2  /  MCP", "ПУБЛИЧНАЯ АЛЬФА"),
    ("lumen", "02 / PERSONAL AI", "Lumen Lab", ["Персональный desktop-ассистент.", "Цели, обратная связь и выбор", "следующей задачи — с контекстом,", "который хранится локально."], "Python  /  React  /  Tauri", "ЛОКАЛЬНЫЙ КОНТЕКСТ"),
    ("elaine", "03 / VOICE INTERFACES", "Elaine", ["Голосовой AI-ассистент для Twitch.", "Распознавание речи, локальная LLM", "и озвучивание ответов в одном", "диалоговом цикле."], "Python  /  Whisper  /  Silero TTS", "ГОЛОС + LLM"),
    ("documents", "04 / DOCUMENT AI", "Local AI Doc Agent", ["Ответы на вопросы по документам.", "PDF, DOCX и TXT, правила извлечения", "данных и LLM fallback без", "облачных API."], "Python  /  FastAPI  /  llama.cpp", "ЛОКАЛЬНАЯ ОБРАБОТКА"),
]


def card(c, category, title, lines, stack, label):
    body = [
        f'<rect x="1" y="1" width="798" height="434" rx="22" fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="2"/>',
        text(38, 49, category, 20, c["accent"], 500, 'letter-spacing="2"'),
        text(38, 121, title, 49, c["text"], 600, 'letter-spacing="-1"'),
        f'<path d="M726 95h28m0 0-12-12m12 12-12 12" fill="none" stroke="{c["accent"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
    ]
    for i, line in enumerate(lines):
        body.append(text(40, 180 + i * 36, line, 28, c["muted"]))
    body.extend([
        f'<path d="M38 320h724" stroke="{c["border"]}" stroke-width="2"/>',
        text(40, 361, stack, 22, c["text"], 500),
        f'<circle cx="44" cy="402" r="4" fill="{c["accent"]}"/>',
        text(61, 408, label, 16, c["muted"], 400, 'letter-spacing="1.5"'),
    ])
    return svg(800, 436, f'{title}. {" ".join(lines)} {stack}. {label}.', body, padding=10)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme, colors in THEMES.items():
        (OUT / f"hero-{theme}.svg").write_text(hero(colors), encoding="utf-8")
        (OUT / f"hero-mobile-{theme}.svg").write_text(mobile_hero(colors), encoding="utf-8")
        for key, category, title, lines, stack, label in PROJECTS:
            (OUT / f"{key}-{theme}.svg").write_text(card(colors, category, title, lines, stack, label), encoding="utf-8")
    print("Generated 12 self-contained profile SVGs.")


if __name__ == "__main__":
    main()

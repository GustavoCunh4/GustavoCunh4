from __future__ import annotations

import colorsys
import datetime as dt
import html
import io
import json
import os
import urllib.request
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parents[2]
USERNAME = "GustavoCunh4"
AVATAR_URL = f"https://github.com/{USERNAME}.png?size=420"

CARD_W = 1200
CARD_H = 620
ASCII_COLS = 54
ASCII_ROWS = 38
ASCII_FONT = 8.2
ASCII_LINE = 10.0
ASCII_X = 148
ASCII_Y = 78
ASCII_CHARS = " .:-=+*#%@"


THEMES = {
    "dark": {
        "file": "dark_mode.svg",
        "bg": "#050b12",
        "panel": "#071523",
        "grid": "#10263a",
        "border": "#23384f",
        "primary": "#e9f0fb",
        "muted": "#93a7bd",
        "dim": "#5f748c",
        "accent": "#ff8a3d",
        "blue": "#38bdf8",
        "purple": "#a78bfa",
        "shadow": "#000000",
        "ascii_boost": 1.12,
    },
    "light": {
        "file": "light_mode.svg",
        "bg": "#f8fbff",
        "panel": "#ffffff",
        "grid": "#e8eef7",
        "border": "#cad7e6",
        "primary": "#172033",
        "muted": "#546477",
        "dim": "#7d8b9d",
        "accent": "#d85b18",
        "blue": "#0969da",
        "purple": "#6f42c1",
        "shadow": "#dce6f3",
        "ascii_boost": 0.84,
    },
}


PROFILE_LINES = [
    ("OS", "Computer Engineering"),
    ("Host", "SENAI CIMATEC"),
    ("Kernel", "Software Development @ IPQ Tecnologia"),
    ("Location", "Salvador, BA, Brazil"),
    ("Build", "GC Corporation"),
    ("", ""),
    ("Languages.Code", "TypeScript, JavaScript, Python, SQL, C"),
    ("Stack.Frontend", "Next.js, React, Tailwind CSS"),
    ("Stack.Backend", "Node.js, FastAPI, REST APIs"),
    ("Stack.Data", "PostgreSQL, Redis, MongoDB, Prisma"),
    ("Stack.Infra", "Docker, Linux, CI/CD"),
    ("", ""),
    ("Systems", "AI Agents, API Integrations, Automation"),
    ("Domains", "IoT, Computer Vision, LPR, CCTV"),
    ("Human", "Portuguese [Native], English [C1]"),
]


def request_json(url: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GustavoCunh4-profile-card",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def github_stats() -> dict[str, str]:
    try:
        user = request_json(f"https://api.github.com/users/{USERNAME}")
        repos = request_json(
            f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner"
        )
        stars = sum(int(repo.get("stargazers_count", 0)) for repo in repos)
        return {
            "Repos": str(user.get("public_repos", len(repos))),
            "Stars": str(stars),
            "Followers": str(user.get("followers", "-")),
            "Updated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d"),
        }
    except Exception:
        return {
            "Repos": "-",
            "Stars": "-",
            "Followers": "-",
            "Updated": dt.datetime.now(dt.UTC).strftime("%Y-%m-%d"),
        }


def fetch_avatar() -> Image.Image:
    req = urllib.request.Request(AVATAR_URL, headers={"User-Agent": "GustavoCunh4-profile-card"})
    with urllib.request.urlopen(req, timeout=25) as response:
        data = response.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")
    return ImageOps.fit(image, (ASCII_COLS, ASCII_ROWS), Image.Resampling.LANCZOS)


def ascii_pixels(image: Image.Image) -> list[list[tuple[str, tuple[int, int, int]]]]:
    gray = ImageOps.grayscale(image)
    gray = ImageOps.autocontrast(gray)
    image = ImageEnhance.Color(image).enhance(1.35)
    rows: list[list[tuple[str, tuple[int, int, int]]]] = []

    for y in range(ASCII_ROWS):
        row: list[tuple[str, tuple[int, int, int]]] = []
        for x in range(ASCII_COLS):
            lum = gray.getpixel((x, y))
            index = round((lum / 255) * (len(ASCII_CHARS) - 1))
            char = ASCII_CHARS[index]
            rgb = image.getpixel((x, y))
            row.append((char, rgb))
        rows.append(row)
    return rows


def tune_color(rgb: tuple[int, int, int], theme: dict[str, str | float]) -> str:
    r, g, b = [channel / 255 for channel in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(1.0, s * 1.35)
    v = min(1.0, max(0.18, v * float(theme["ascii_boost"])))
    rr, gg, bb = colorsys.hsv_to_rgb(h, s, v)
    return f"#{round(rr * 255):02x}{round(gg * 255):02x}{round(bb * 255):02x}"


def text(x: int, y: int, value: str, color: str, size: int = 18, weight: int = 400) -> str:
    escaped = html.escape(value)
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="Consolas, '
        f"'SFMono-Regular', 'Liberation Mono', monospace\" font-size=\"{size}\" "
        f'font-weight="{weight}">{escaped}</text>'
    )


def profile_text(theme: dict[str, str | float], stats: dict[str, str]) -> str:
    parts: list[str] = []
    y = 128
    for label, value in PROFILE_LINES:
        if not label:
            y += 15
            continue
        parts.append(text(610, y, f"{label:<15}", str(theme["accent"]), 17, 700))
        parts.append(text(790, y, value, str(theme["primary"]), 17, 400))
        y += 28

    y += 10
    parts.append(text(610, y, "GitHub.Stats", str(theme["blue"]), 17, 700))
    y += 30
    stat_line = (
        f"Repos {stats['Repos']}  |  Stars {stats['Stars']}  |  "
        f"Followers {stats['Followers']}"
    )
    parts.append(text(610, y, stat_line, str(theme["primary"]), 17, 400))
    y += 28
    parts.append(text(610, y, f"Last refresh {stats['Updated']}", str(theme["muted"]), 15, 400))
    return "\n".join(parts)


def ascii_svg(rows: list[list[tuple[str, tuple[int, int, int]]]], theme: dict[str, str | float]) -> str:
    snippets: list[str] = []
    snippets.append(
        f'<text font-family="Consolas, \'SFMono-Regular\', \'Liberation Mono\', monospace" '
        f'font-size="{ASCII_FONT}" xml:space="preserve">'
    )
    for y, row in enumerate(rows):
        yy = ASCII_Y + y * ASCII_LINE
        for x, (char, rgb) in enumerate(row):
            if char == " ":
                continue
            xx = ASCII_X + x * 6.2
            snippets.append(
                f'<tspan x="{xx:.1f}" y="{yy:.1f}" fill="{tune_color(rgb, theme)}">'
                f"{html.escape(char)}</tspan>"
            )
    snippets.append("</text>")
    return "\n".join(snippets)


def render(theme_name: str, rows: list[list[tuple[str, tuple[int, int, int]]]], stats: dict[str, str]) -> None:
    theme = THEMES[theme_name]
    svg = f'''<svg width="{CARD_W}" height="{CARD_H}" viewBox="0 0 {CARD_W} {CARD_H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
<title id="title">Luiz Gustavo Cunha profile card</title>
<desc id="desc">Terminal inspired profile card with ASCII avatar and software engineering focus.</desc>
<rect width="{CARD_W}" height="{CARD_H}" rx="22" fill="{theme["bg"]}"/>
<rect x="22" y="22" width="1156" height="576" rx="18" fill="{theme["panel"]}" stroke="{theme["border"]}" stroke-width="2"/>
<path d="M42 84H1170" stroke="{theme["grid"]}" stroke-width="1"/>
<circle cx="56" cy="54" r="7" fill="{theme["accent"]}"/>
<circle cx="80" cy="54" r="7" fill="{theme["blue"]}"/>
<circle cx="104" cy="54" r="7" fill="{theme["purple"]}"/>
{text(130, 61, "gustavocunh4@github:~$ profile", str(theme["muted"]), 16)}
<rect x="44" y="104" width="500" height="448" rx="14" fill="{theme["bg"]}" stroke="{theme["grid"]}"/>
{text(70, 154, "IDEAS", str(theme["blue"]), 15, 700)}
{text(70, 181, "CODE", str(theme["blue"]), 15, 700)}
{text(70, 208, "DEPLOY", str(theme["blue"]), 15, 700)}
{text(70, 235, "LEARN", str(theme["blue"]), 15, 700)}
{text(70, 262, "REPEAT", str(theme["blue"]), 15, 700)}
{text(70, 292, "_", str(theme["accent"]), 18, 700)}
{ascii_svg(rows, theme)}
{text(70, 528, "> I build software that moves from idea to deployment.", str(theme["purple"]), 15, 700)}
{text(610, 80, "Luiz Gustavo Cunha", str(theme["primary"]), 30, 800)}
{text(610, 106, "Software Developer | Backend | AI Systems | IoT", str(theme["muted"]), 16)}
{profile_text(theme, stats)}
</svg>
'''
    (ROOT / str(theme["file"])).write_text(svg, encoding="utf-8", newline="\n")


def main() -> None:
    avatar = fetch_avatar()
    rows = ascii_pixels(avatar)
    stats = github_stats()
    render("dark", rows, stats)
    render("light", rows, stats)


if __name__ == "__main__":
    main()

from __future__ import annotations

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
AVATAR_URL = f"https://github.com/{USERNAME}.png?size=920"

WIDTH = 985
HEIGHT = 540
FONT = "ConsolasFallback, Consolas, Monaco, monospace"
TEXT_X = 390
LINE_HEIGHT = 18

THEMES = {
    "dark": {
        "file": "dark_mode.svg",
        "bg": "#161b22",
        "panel": "#0d1117",
        "border": "#30363d",
        "text": "#c9d1d9",
        "key": "#ffa657",
        "value": "#a5d6ff",
        "sep": "#616e7f",
        "add": "#3fb950",
        "del": "#f85149",
        "muted": "#8b949e",
    },
    "light": {
        "file": "light_mode.svg",
        "bg": "#f6f8fa",
        "panel": "#ffffff",
        "border": "#d0d7de",
        "text": "#24292f",
        "key": "#953800",
        "value": "#0969da",
        "sep": "#6e7781",
        "add": "#1a7f37",
        "del": "#cf222e",
        "muted": "#57606a",
    },
}

SECTIONS = [
    (
        "gustavo@cunha",
        [
            ("OS", "Computer Engineering"),
            ("Host", "SENAI CIMATEC"),
            ("Kernel", "Software Development @ IPQ Tecnologia"),
            ("Shell", "Founder @ GC Corporation"),
            ("Location", "Salvador, BA, Brazil"),
        ],
    ),
    (
        None,
        [
            ("Languages.Code", "TypeScript, JavaScript, Python, SQL, C"),
            ("Stack.Frontend", "Next.js, React, Tailwind CSS"),
            ("Stack.Backend", "Node.js, FastAPI, REST APIs"),
            ("Stack.Data", "PostgreSQL, Redis, MongoDB, Prisma"),
            ("Stack.Infra", "Docker, Linux, GitHub, Vercel, CI/CD"),
        ],
    ),
    (
        None,
        [
            ("Systems.Software", "Backend, Full-stack, API Integrations"),
            ("Systems.AI", "AI Systems, AI Agents, Automation"),
            ("Systems.Field", "IoT, Computer Vision, LPR, CCTV"),
            ("Human", "Portuguese [Native], English [C1]"),
        ],
    ),
    (
        "- Contact",
        [
            ("Email", "luizgustavocunha.dev@gmail.com"),
            ("LinkedIn", "luiz-gustavo-santos-cunha-854988256"),
            ("Portfolio", "gustavocunhadev.vercel.app"),
            ("Company", "gccorp.vercel.app"),
        ],
    ),
]


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def http_json(url: str) -> object:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GustavoCunh4-profile-readme",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def http_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "GustavoCunh4-profile-readme"})
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()


def github_stats() -> dict[str, str]:
    try:
        user = http_json(f"https://api.github.com/users/{USERNAME}")
        repos = []
        page = 1
        while page <= 3:
            batch = http_json(
                f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner&page={page}"
            )
            if not batch:
                break
            repos.extend(batch)
            page += 1

        stars = sum(int(repo.get("stargazers_count", 0)) for repo in repos)
        created = dt.datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
        today = dt.datetime.now(dt.timezone.utc)
        uptime_days = max(0, (today - created).days)
        years, days = divmod(uptime_days, 365)
        months, days = divmod(days, 30)

        return {
            "repos": f"{int(user.get('public_repos', len(repos))):,}",
            "stars": f"{stars:,}",
            "followers": f"{int(user.get('followers', 0)):,}",
            "following": f"{int(user.get('following', 0)):,}",
            "created": created.strftime("%Y-%m-%d"),
            "uptime": f"{years} years, {months} months, {days} days",
        }
    except Exception:
        return {
            "repos": "17",
            "stars": "0",
            "followers": "7",
            "following": "3",
            "created": "GitHub",
            "uptime": "active",
        }


def avatar_mosaic(theme: dict[str, str], light: bool = False) -> str:
    image = Image.open(io.BytesIO(http_bytes(AVATAR_URL))).convert("RGB")

    # The avatar is a wide scene. This crop keeps the seated profile subject and blue setup visible.
    image = image.crop((42, 36, 438, 438))
    image = ImageOps.fit(image, (72, 72), Image.Resampling.LANCZOS)
    image = ImageEnhance.Color(image).enhance(1.26)
    image = ImageEnhance.Contrast(image).enhance(1.18)
    image = ImageEnhance.Brightness(image).enhance(1.06 if not light else 1.12)

    cell = 4
    x0 = 36
    y0 = 82
    pieces = [
        f'<rect x="24" y="70" width="324" height="324" rx="16" fill="{theme["panel"]}" stroke="{theme["border"]}"/>'
    ]

    for y in range(72):
        for x in range(72):
            r, g, b = image.getpixel((x, y))
            luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
            if luminance < 12:
                continue
            if not light:
                r = min(255, int(r * 1.08))
                g = min(255, int(g * 1.08))
                b = min(255, int(b * 1.12))
            color = f"#{r:02x}{g:02x}{b:02x}"
            pieces.append(
                f'<rect x="{x0 + x * cell}" y="{y0 + y * cell}" width="3" height="3" rx="0.7" fill="{color}"/>'
            )

    return "\n".join(pieces)


def separator(title: str, length: int = 59) -> str:
    return f"{title} " + "-" * max(0, length - len(title) - 1)


def row(key: str, value: str, y: int) -> str:
    dots = " " + "." * max(2, 32 - len(key) - min(len(value), 24)) + " "
    return (
        f'<tspan x="{TEXT_X}" y="{y}" class="cc">. </tspan>'
        f'<tspan class="key">{escape(key)}</tspan>:'
        f'<tspan class="cc">{escape(dots)}</tspan>'
        f'<tspan class="value">{escape(value)}</tspan>'
    )


def text_block(stats: dict[str, str]) -> str:
    lines = []
    y = 30
    for title, fields in SECTIONS:
        if title:
            lines.append(f'<tspan x="{TEXT_X}" y="{y}">{escape(separator(title))}</tspan>')
            y += LINE_HEIGHT
        for key, value in fields:
            lines.append(row(key, value, y))
            y += LINE_HEIGHT
        y += LINE_HEIGHT

    lines.append(f'<tspan x="{TEXT_X}" y="{y}">{escape(separator("- GitHub Stats"))}</tspan>')
    y += LINE_HEIGHT
    lines.append(
        f'<tspan x="{TEXT_X}" y="{y}" class="cc">. </tspan><tspan class="key">Repos</tspan>:'
        f'<tspan class="cc"> .... </tspan><tspan class="value">{stats["repos"]}</tspan>'
        f' {{<tspan class="key">Following</tspan>: <tspan class="value">{stats["following"]}</tspan>}} | '
        f'<tspan class="key">Stars</tspan>:<tspan class="cc"> ..... </tspan><tspan class="value">{stats["stars"]}</tspan>'
    )
    y += LINE_HEIGHT
    lines.append(
        f'<tspan x="{TEXT_X}" y="{y}" class="cc">. </tspan><tspan class="key">Created</tspan>:'
        f'<tspan class="cc"> ........ </tspan><tspan class="value">{stats["created"]}</tspan> | '
        f'<tspan class="key">Followers</tspan>:<tspan class="cc"> .. </tspan><tspan class="value">{stats["followers"]}</tspan>'
    )
    y += LINE_HEIGHT
    lines.append(
        f'<tspan x="{TEXT_X}" y="{y}" class="cc">. </tspan><tspan class="key">GitHub Uptime</tspan>:'
        f'<tspan class="cc"> ........ </tspan><tspan class="value">{escape(stats["uptime"])}</tspan>'
    )
    return "\n".join(lines)


def render(name: str, stats: dict[str, str]) -> None:
    theme = THEMES[name]
    light = name == "light"
    svg = f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="{FONT}" width="{WIDTH}px" height="{HEIGHT}px" viewBox="0 0 {WIDTH} {HEIGHT}" font-size="15px" role="img" aria-labelledby="title desc">
<title id="title">Luiz Gustavo Cunha GitHub Neofetch profile</title>
<desc id="desc">Profile card generated from code with terminal-style system information and a mosaic based on the GitHub profile picture.</desc>
<style>
@font-face {{
  src: local('Consolas'), local('Monaco'), local('monospace');
  font-family: 'ConsolasFallback';
  font-display: swap;
  -webkit-size-adjust: 109%;
  size-adjust: 109%;
}}
.key {{ fill: {theme["key"]}; }}
.value {{ fill: {theme["value"]}; }}
.addColor {{ fill: {theme["add"]}; }}
.delColor {{ fill: {theme["del"]}; }}
.cc {{ fill: {theme["sep"]}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="{WIDTH}px" height="{HEIGHT}px" fill="{theme["bg"]}" rx="15"/>
<path d="M370 22V518" stroke="{theme["border"]}" stroke-width="1"/>
{avatar_mosaic(theme, light)}
<text x="42" y="430" fill="{theme["muted"]}" font-size="15px">
<tspan x="42" y="430">github avatar rendered as</tspan>
<tspan x="42" y="450">terminal pixel output</tspan>
<tspan x="42" y="482" fill="{theme["key"]}">&gt;</tspan><tspan fill="{theme["value"]}"> build. integrate. automate. deploy.</tspan>
</text>
<text x="{TEXT_X}" y="30" fill="{theme["text"]}">
{text_block(stats)}
</text>
</svg>
"""
    (ROOT / str(theme["file"])).write_text(svg, encoding="utf-8", newline="\n")


def main() -> None:
    stats = github_stats()
    render("dark", stats)
    render("light", stats)


if __name__ == "__main__":
    main()

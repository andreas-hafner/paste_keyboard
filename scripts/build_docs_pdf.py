from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the end-user PDF documentation.")
    parser.add_argument("--source", default="docs/enduser.md", help="Markdown source file.")
    parser.add_argument("--output", default="dist/PasteKeyboard-Anleitung.pdf", help="PDF output file.")
    parser.add_argument("--lang", default="de", help="HTML language code.")
    parser.add_argument("--title", default="Paste Keyboard Anleitung", help="HTML document title.")
    return parser.parse_args()


def find_browser() -> str:
    candidates = [
        shutil.which("chrome"),
        shutil.which("chrome.exe"),
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(candidate)
    raise RuntimeError("Neither Microsoft Edge nor Google Chrome was found for PDF generation.")


def render_inline(value: str) -> str:
    placeholders: list[str] = []

    def store(rendered: str) -> str:
        placeholders.append(rendered)
        return f"\u0000{len(placeholders) - 1}\u0000"

    value = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda match: store(
            f'<img src="{html.escape(resolve_image_src(match.group(2)), quote=True)}" '
            f'alt="{html.escape(match.group(1), quote=True)}">'
        ),
        value,
    )
    value = re.sub(r"`([^`]+)`", lambda match: store(f"<code>{html.escape(match.group(1))}</code>"), value)
    escaped = html.escape(value)
    for index, rendered in enumerate(placeholders):
        escaped = escaped.replace(f"\u0000{index}\u0000", rendered)
    return escaped


def resolve_image_src(path: str) -> str:
    image_path = (ROOT / "docs" / path).resolve()
    return image_path.as_uri()


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_code = False
    in_list = False
    in_ordered_list = False

    def close_lists() -> None:
        nonlocal in_list, in_ordered_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False
        if in_ordered_list:
            html_lines.append("</ol>")
            in_ordered_list = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                close_lists()
                in_code = True
                html_lines.append("<pre><code>")
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        if not stripped:
            close_lists()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            close_lists()
            level = len(heading.group(1))
            html_lines.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            continue

        unordered = re.match(r"^-\s+(.+)$", stripped)
        if unordered:
            if in_ordered_list:
                html_lines.append("</ol>")
                in_ordered_list = False
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{render_inline(unordered.group(1))}</li>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ordered:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if not in_ordered_list:
                html_lines.append("<ol>")
                in_ordered_list = True
            html_lines.append(f"<li>{render_inline(ordered.group(1))}</li>")
            continue

        close_lists()
        html_lines.append(f"<p>{render_inline(stripped)}</p>")

    close_lists()
    if in_code:
        html_lines.append("</code></pre>")
    return "\n".join(html_lines)


def build_html(markdown: str, lang: str, title: str) -> str:
    body = markdown_to_html(markdown)
    return f"""<!doctype html>
<html lang="{html.escape(lang, quote=True)}">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    @page {{ margin: 18mm; }}
    body {{
      color: #111827;
      font-family: "Segoe UI", Arial, sans-serif;
      font-size: 10.5pt;
      line-height: 1.45;
    }}
    h1 {{ font-size: 24pt; margin: 0 0 16pt; }}
    h2 {{ border-bottom: 1px solid #d1d5db; font-size: 16pt; margin-top: 22pt; padding-bottom: 4pt; }}
    h3 {{ font-size: 12.5pt; margin-top: 16pt; }}
    code {{
      background: #f3f4f6;
      border-radius: 3px;
      font-family: Consolas, monospace;
      padding: 1px 3px;
    }}
    pre {{
      background: #f3f4f6;
      border: 1px solid #e5e7eb;
      border-radius: 4px;
      padding: 8pt;
      white-space: pre-wrap;
    }}
    img {{
      border: 1px solid #d1d5db;
      display: block;
      margin: 10pt 0 14pt;
      max-width: 100%;
    }}
    li {{ margin: 3pt 0; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def print_pdf(browser: str, html_path: Path, output_path: Path, user_data_dir: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        browser,
        "--headless",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-gpu",
        "--disable-extensions",
        f"--user-data-dir={user_data_dir}",
        f"--print-to-pdf={output_path}",
        html_path.as_uri(),
    ]
    completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "Browser PDF export failed.")
    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"PDF was not created: {output_path}")


def main() -> int:
    args = parse_args()
    source = (ROOT / args.source).resolve()
    output = (ROOT / args.output).resolve()
    if not source.exists():
        raise RuntimeError(f"Documentation source not found: {source}")

    browser = find_browser()
    with tempfile.TemporaryDirectory(prefix="paste-keyboard-docs-") as temp_dir:
        temp_path = Path(temp_dir)
        html_path = temp_path / "PasteKeyboard-Anleitung.html"
        user_data_dir = temp_path / "browser-profile"
        html_path.write_text(build_html(source.read_text(encoding="utf-8"), args.lang, args.title), encoding="utf-8")
        print_pdf(browser, html_path, output, user_data_dir)

    print(f"Built PDF: {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)

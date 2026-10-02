#!/usr/bin/env python3
"""Render <context-dir>/GUIDE.md to <context-dir>/GUIDE.pdf.

Tries, in order:
  1. pandoc (if on PATH)                — best typography
  2. Google Chrome / Chromium headless  — via a built-in minimal Markdown-to-HTML
                                          converter (headings, paragraphs, lists,
                                          tables, fenced code, inline code, bold,
                                          italics, links, blockquotes, rules)
If neither is available, prints the manual command and exits 3 so the caller can
report "PDF not rendered" instead of failing the whole scaffold.

Usage:
    python3 render_guide_pdf.py /path/to/<slug>-context [--out GUIDE.pdf]

Exit 0 = PDF written, 3 = no renderer available, 1 = renderer failed.
"""

import argparse
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome",
]

CSS = """
body{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:800px;margin:40px auto;
line-height:1.5;color:#1a1a1a;font-size:11pt}
h1{font-size:22pt;border-bottom:2px solid #333;padding-bottom:6px}h2{font-size:16pt;margin-top:1.6em}
h3{font-size:13pt;margin-top:1.3em}code{font-family:Menlo,Consolas,monospace;font-size:9.5pt;
background:#f3f3f3;padding:1px 4px;border-radius:3px}pre{background:#f3f3f3;padding:10px;
border-radius:4px;overflow-x:auto}pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;margin:1em 0}th,td{border:1px solid #bbb;padding:6px 8px;
vertical-align:top;text-align:left}th{background:#eee}blockquote{border-left:4px solid #bbb;margin:1em 0;
padding:0 1em;color:#444}hr{border:0;border-top:1px solid #bbb;margin:2em 0}
@page{margin:20mm}
"""


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*([^*]+)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md):
    out, lines, i = [], md.split("\n"), 0
    para = []

    def flush_para():
        if para:
            out.append("<p>" + inline(" ".join(s.strip() for s in para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            flush_para()
            j = i + 1
            block = []
            while j < len(lines) and not lines[j].startswith("```"):
                block.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(block)) + "</code></pre>")
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            out.append(f"<h{len(m.group(1))}>{inline(m.group(2))}</h{len(m.group(1))}>")
            i += 1; continue
        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            flush_para(); out.append("<hr>"); i += 1; continue
        if line.strip().startswith("|"):
            flush_para()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]); i += 1
            body = [r for r in rows if not re.match(r"^\s*\|[\s:\-|]+\|\s*$", r)]
            def cells(r):
                r = re.sub(r"\\\|", "\x00", r).strip().strip("|")
                return [c.replace("\x00", "|").strip() for c in r.split("|")]
            if body:
                out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells(body[0])) + "</tr></thead><tbody>")
                for r in body[1:]:
                    out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>")
                out.append("</tbody></table>")
            continue
        if line.startswith(">"):
            flush_para()
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i].lstrip("> ").rstrip()); i += 1
            out.append("<blockquote><p>" + inline(" ".join(q)) + "</p></blockquote>")
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            flush_para()
            ordered = m.group(2)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if mm and (mm.group(2)[0].isdigit()) == ordered and len(mm.group(1)) == len(m.group(1)):
                    items.append(mm.group(3)); i += 1
                elif lines[i].startswith(" " * (len(m.group(1)) + 2)) and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip(); i += 1
                else:
                    break
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>")
            continue
        if not line.strip():
            flush_para(); i += 1; continue
        para.append(line); i += 1
    flush_para()
    return "\n".join(out)


def find_chrome():
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
        found = shutil.which(c)
        if found:
            return found
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("context_dir")
    ap.add_argument("--out", default="GUIDE.pdf")
    args = ap.parse_args()
    ctx = Path(args.context_dir).resolve()
    src = ctx / "GUIDE.md"
    pdf = ctx / args.out
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr); return 1

    if shutil.which("pandoc"):
        r = subprocess.run(["pandoc", str(src), "-o", str(pdf), "--from", "gfm"], capture_output=True, text=True)
        if r.returncode == 0 and pdf.exists():
            print(f"PDF written with pandoc: {pdf}"); return 0
        print(f"pandoc failed ({r.stderr.strip()[:200]}); trying Chrome headless")

    chrome = find_chrome()
    if chrome:
        html_path = ctx / "GUIDE.html"
        title = html.escape(ctx.name)
        html_path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{title}</title>"
                             f"<style>{CSS}</style></head><body>{md_to_html(src.read_text(encoding='utf-8'))}"
                             f"</body></html>", encoding="utf-8")
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
               f"--print-to-pdf={pdf}", html_path.as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        html_path.unlink(missing_ok=True)
        if pdf.exists():
            print(f"PDF written with Chrome headless: {pdf}"); return 0
        print(f"Chrome headless failed: {r.stderr.strip()[:300]}", file=sys.stderr); return 1

    print("No PDF renderer found (pandoc or Google Chrome). GUIDE.md is complete; render it later with:")
    print(f"  pandoc {src} -o {pdf} --from gfm")
    print("or open GUIDE.md in any Markdown viewer and print to PDF.")
    return 3


if __name__ == "__main__":
    sys.exit(main())

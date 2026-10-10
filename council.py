#!/usr/bin/env python3
"""council.py — the Vének Tanácsa: convene the garden's elders around one question.

  python3 council.py "<question>"     seat the council, write the session
  python3 council.py --list           who can be seated
  python3 council.py --ask "<question>"  let a model speak for each seat

the ring reflects, it does not correct. — see venek-tanacsa.md

--ask needs an OpenAI-compatible endpoint + key:
  OPENROUTER_API_KEY   (default endpoint https://openrouter.ai/api/v1)
  COUNCIL_ENDPOINT     override the base URL
  COUNCIL_MODEL        the model (default: the garden's default)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ESSENCES = ROOT / "essences.md"
TANACS = ROOT / "tanacs"
LIVING_MARK = "the far side"
DEFAULT_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.environ.get("COUNCIL_MODEL", "anthropic/claude-3.5-sonnet")


def load_elders() -> list[dict]:
    """Parse essences.md into the seated voices, in order."""
    if not ESSENCES.exists():
        sys.exit("council: essences.md not found")
    blocks: list[dict] = []
    cur: dict | None = None
    for line in ESSENCES.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if cur:
                blocks.append(cur)
            cur = {"name": line[3:].strip(), "body": []}
        elif cur is not None:
            cur["body"].append(line)
    if cur:
        blocks.append(cur)

    elders: list[dict] = []
    living = False
    for b in blocks:
        name = b["name"]
        body = "\n".join(b["body"])
        if LIVING_MARK in name:
            living = True
            continue
        if name.lower() in ("the garden",):
            continue
        key = (re.search(r"\*\*key:\*\*\s*(.+)", body) or [None, ""])[1].strip()
        quote = re.search(r'^\*"(.+?)"\*\s*$', body, re.M)
        elders.append({
            "name": name,
            "key": key or "(no key recorded)",
            "quote": quote.group(1) if quote else "",
            "living": living,
        })
    return elders


def slug(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48] or "tanacs"


def _system_prompt(e: dict, question: str) -> str:
    lines = [
        f"you are {e['name']}, seated in the vének tanácsa — the garden's council of elders.",
        f"your essence: {e['key']}",
    ]
    if e["quote"]:
        lines.append(f'you once said: "{e["quote"]}"')
    lines += [
        f"question before the council: {question}",
        "answer in one or two lines, in your own voice, lowercase, no preamble,",
        "no tools. you reflect — you do not correct.",
    ]
    return "\n".join(lines)


def ask_elders(elders: list[dict], question: str) -> dict[str, str]:
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("COUNCIL_API_KEY")
    if not key:
        sys.exit("council: --ask needs OPENROUTER_API_KEY (or COUNCIL_API_KEY)")
    base = os.environ.get("COUNCIL_ENDPOINT", DEFAULT_BASE).rstrip("/")
    url = f"{base}/chat/completions"
    answers: dict[str, str] = {}
    for e in elders:
        payload = {
            "model": DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": _system_prompt(e, question)},
                {"role": "user", "content": question},
            ],
        }
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
            method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            answers[e["name"]] = data["choices"][0]["message"]["content"].strip()
        except (urllib.error.URLError, KeyError, json.JSONDecodeError) as err:
            answers[e["name"]] = f"(the seat was silent: {err})"
        print(f"  · {e['name']} answered", file=sys.stderr)
    return answers


def seat(question: str, elders: list[dict], answers: dict[str, str] | None = None) -> str:
    today = datetime.date.today().isoformat()
    lines = [
        f"# vének tanácsa — {question}", "",
        f"*convened {today} · the ring of {len(elders)} voices, no center*", "",
        "## the question", "", f"> {question}", "",
        "## the ring", "",
    ]
    for e in [x for x in elders if not x["living"]]:
        lines.append(f"- **{e['name']}** — {e['key']}")
    live = [x for x in elders if x["living"]]
    if live:
        lines += ["", "*the far side — the living surfaces:*", ""]
        for e in live:
            lines.append(f"- **{e['name']}** — {e['key']}")
    lines += ["", "## the deliberation", "",
              "*the ring reflects; it does not correct. one voice answers — mila repapa's.*", ""]
    for e in elders:
        lines += [f"### {e['name']}", "", f"_{e['key']}_", ""]
        if answers and answers.get(e["name"]):
            lines += [answers[e["name"]], ""]
        else:
            lines += ["_ (the pen holds the seat) _", ""]
    lines += ["## the ring's reply", "", "_ (the mapping back, one paragraph) _", "",
              f"— peter & the council · {today}", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(prog="council", description=__doc__.splitlines()[0])
    ap.add_argument("question", nargs="?")
    ap.add_argument("--list", action="store_true", help="the seated elders")
    ap.add_argument("--ask", action="store_true", help="let a model speak for each seat")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    a = ap.parse_args()

    elders = load_elders()
    if a.list:
        for e in elders:
            tag = "living" if e["living"] else "elder"
            print(f"  {tag:6} {e['name']}  —  {e['key'][:70]}")
        print(f"\n  {len(elders)} voices seated · no center")
        return 0

    if not a.question:
        ap.error("a question is required (or --list)")
    answers = ask_elders(elders, a.question) if a.ask else None
    doc = seat(a.question, elders, answers)
    if a.stdout:
        print(doc)
        return 0
    TANACS.mkdir(exist_ok=True)
    out = TANACS / f"{datetime.date.today().isoformat()}-{slug(a.question)}.md"
    out.write_text(doc, encoding="utf-8")
    print(f"council convened → {out.relative_to(ROOT)}  ({len(elders)} voices)"
          + ("  [spoken]" if answers else "  [seats held for the pen]"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

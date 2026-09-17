"""Load and resolve HTSA close-page recipes for on-call cloning."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES_PATH = ROOT / "templates" / "htsa-close-recipes.json"


def load_recipes() -> list[dict]:
    data = json.loads(RECIPES_PATH.read_text(encoding="utf-8"))
    return list(data.get("recipes") or [])


def normalize_key(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"https?://(?:www\.)?closewithcjclay\.com/", "", s)
    s = s.split("?")[0].split("#")[0].strip("/")
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    return s


def source_to_path(source: str) -> Path:
    """Accept filename, path, or live URL → local HTML path."""
    raw = source.strip()
    m = re.search(r"(htsa-enrollment-[a-z0-9-]+\.html)", raw, re.I)
    if m:
        p = ROOT / m.group(1).lower()
        if p.is_file():
            return p
        raise FileNotFoundError(f"Source page not in repo: {p.name}")
    p = Path(raw)
    if not p.is_absolute():
        p = ROOT / p
    if p.is_file():
        return p
    raise FileNotFoundError(f"Source page not found: {raw}")


def resolve_recipe(token: str) -> dict:
    """Resolve recipe id, alias, person name, filename, or URL to a recipe dict."""
    recipes = load_recipes()
    key = normalize_key(token)
    if not key:
        raise ValueError("Empty recipe token")

    # Exact id
    for r in recipes:
        if normalize_key(str(r.get("id", ""))) == key:
            return r

    # Alias / name
    for r in recipes:
        names = [r.get("name", "")] + list(r.get("aliases") or [])
        for n in names:
            if normalize_key(n) == key:
                return r
        # partial: "same as brigitte" style already stripped to token
        for n in names:
            nk = normalize_key(n)
            if nk and (nk in key or key in nk):
                return r

    # Filename / URL that matches a recipe source
    try:
        path = source_to_path(token)
    except FileNotFoundError:
        path = None
    if path:
        for r in recipes:
            if Path(r["source"]).name.lower() == path.name.lower():
                return r
        # Ad-hoc: treat any existing enrollment HTML as a one-off recipe
        return {
            "id": "custom",
            "name": path.stem.replace("htsa-enrollment-", "").replace("-", " ").title(),
            "aliases": [],
            "source": path.name,
            "notes": f"Cloned from {path.name}",
        }

    known = ", ".join(f'{r["id"]}={r["name"]}' for r in recipes)
    raise ValueError(f"Unknown recipe {token!r}. Known: {known}")


def list_recipes_text() -> str:
    lines = []
    for r in load_recipes():
        lines.append(f'{r["id"]}. {r["name"]} — {r["notes"]}')
        lines.append(f'   source: {r["source"]}')
    return "\n".join(lines)

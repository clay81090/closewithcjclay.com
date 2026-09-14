#!/usr/bin/env python3
"""Format CJ closed-call transcripts for Notion — one number per unique client."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(
    "/Users/charlesclay/Downloads/Private & Shared 7/"
    "CJ - CLOSED TRANSCRIPTS 2c976776007b80c28ed3d29dcd6bdb84.md"
)
OUT = Path(__file__).resolve().parents[1] / "CJ-CLOSED-TRANSCRIPTS-NOTION.md"

CJ_NAMES = {"Charles Clay", "CJ Clay"}
NUMBERED_CLIENT = re.compile(r"^# (\d+)\.\)\s*(.+)$", re.I)
PARTICIPANTS = re.compile(r"^# Participants\s*$", re.I)
FOLLOW_UP = re.compile(r"^# Follow Up\s*$", re.I)
TRANSCRIPT_HDR = re.compile(r"^# Transcript\s*$", re.I)
HUBSPOT = re.compile(r"^## HubSpot\s*$", re.I)
CONTACT = re.compile(r"^## Contact\s*$", re.I)
SPEAKER_LINE = re.compile(r"^\*\*Speaker (\d)\*\* \(([^)]+)\): (.*)$")
PLAIN_TS = re.compile(r"^(.+?) (\d{2}:\d{2}:\d{2})$")
CALL_LABEL = re.compile(
    r"^(\*\*Call.*?\*\*|Call #\d+.*|Call - Part \d+|^Call 1:|^Call 2:)$",
    re.I,
)
NOTE_LINE = re.compile(
    r"^(?:\*{3,}\s*)?(?:Then .+signed|Abraham then|Then Amy signed)",
    re.I,
)


def is_note_line(s: str) -> bool:
    if s.startswith("**Speaker"):
        return False
    if NOTE_LINE.match(s):
        return True
    if s.startswith("*") and any(
        k in s
        for k in ("signed", "Abraham then", "enrollment page", "Paid in Full", "Paid In Full")
    ):
        return True
    return False
CLOSED_WON = re.compile(r"^## Closed Won", re.I)
STOP_SECTION = re.compile(
    r"^(# Participants|# Follow Up|# \d+\.\)|## Closed Won|\*\*Call #|\*\*Call - Part)",
    re.I,
)


def format_ts(ts: str) -> str:
    h, m, s = (int(x) for x in ts.split(":"))
    if h:
        return f"({h}:{m:02d}:{s:02d})"
    return f"({m}:{s:02d})"


def normalize_name(name: str) -> str:
    return " ".join(name.strip().split()).upper()


def skip_blank(lines: list[str], i: int) -> int:
    while i < len(lines) and not lines[i].strip():
        i += 1
    return i


def parse_hubspot_contact(lines: list[str], start: int) -> tuple[str, str, int]:
    hubspot = "CJ Clay"
    contact = ""
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if HUBSPOT.match(line):
            i = skip_blank(lines, i + 1)
            if i < len(lines) and lines[i].strip().startswith("- "):
                hubspot = lines[i].strip()[2:].strip()
                i += 1
            continue
        if CONTACT.match(line):
            i = skip_blank(lines, i + 1)
            if i < len(lines) and lines[i].strip().startswith("- "):
                contact = lines[i].strip()[2:].strip()
                i += 1
            continue
        if line == "---":
            return hubspot, contact, i + 1
        if TRANSCRIPT_HDR.match(line) or STOP_SECTION.match(line):
            break
        i += 1
    return hubspot, contact, i


def convert_plain_block(raw_lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i].rstrip("\n")
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if CALL_LABEL.match(stripped):
            out.append(f"\n## {stripped.strip('*').strip()}\n")
            i += 1
            continue
        if stripped.startswith("**Call Disconnected") or (
            stripped.startswith("**") and "Call Disconnected" in stripped
        ):
            out.append(f"\n## {stripped.strip('*').strip()}\n")
            i += 1
            continue
        m = PLAIN_TS.match(stripped)
        if m:
            name, ts = m.group(1).strip(), m.group(2)
            sp = "1" if name in CJ_NAMES else "2"
            i += 1
            chunks: list[str] = []
            while i < len(raw_lines):
                nxt = raw_lines[i].strip()
                if not nxt:
                    i += 1
                    if chunks and i < len(raw_lines) and PLAIN_TS.match(raw_lines[i].strip()):
                        break
                    continue
                if PLAIN_TS.match(nxt) or STOP_SECTION.match(nxt) or PARTICIPANTS.match(nxt):
                    break
                if CALL_LABEL.match(nxt) or nxt.startswith("**Call Disconnected"):
                    break
                if is_note_line(nxt) or CLOSED_WON.match(nxt):
                    break
                chunks.append(nxt)
                i += 1
            text = " ".join(chunks).strip()
            if text:
                out.append(f"**Speaker {sp}** {format_ts(ts)}: {text}")
            continue
        if SPEAKER_LINE.match(stripped):
            out.append(stripped)
            i += 1
            continue
        i += 1
    return out


def read_formatted_transcript(lines: list[str], start: int) -> tuple[list[str], int]:
    body: list[str] = []
    i = start
    while i < len(lines):
        s = lines[i].strip()
        if STOP_SECTION.match(s) or PARTICIPANTS.match(s) or NUMBERED_CLIENT.match(s):
            break
        if PLAIN_TS.match(s):
            break
        if TRANSCRIPT_HDR.match(s):
            i += 1
            continue
        if is_note_line(s) or CLOSED_WON.match(s):
            break
        if s.startswith("# ") and not s.startswith("# Transcript"):
            break
        body.append(lines[i].rstrip("\n"))
        i += 1
    return body, i


def read_plain_transcript(lines: list[str], start: int) -> tuple[list[str], int]:
    raw: list[str] = []
    i = start
    while i < len(lines):
        s = lines[i].strip()
        if STOP_SECTION.match(s) or PARTICIPANTS.match(s) or NUMBERED_CLIENT.match(s):
            break
        if is_note_line(s) or CLOSED_WON.match(s):
            break
        if (
            SPEAKER_LINE.match(s)
            and raw
            and any(PLAIN_TS.match(x.strip()) for x in raw if x.strip())
        ):
            break
        raw.append(lines[i])
        i += 1
    return convert_plain_block(raw), i


def first_plain_client_name(lines: list[str], start: int) -> str | None:
    for j in range(start, min(start + 30, len(lines))):
        m = PLAIN_TS.match(lines[j].strip())
        if m and m.group(1).strip() not in CJ_NAMES:
            return m.group(1).strip()
    return None


class Call:
    def __init__(self, label: str, hubspot: str, contact: str, transcript: list[str]):
        self.label = label
        self.hubspot = hubspot
        self.contact = contact
        self.transcript = [t for t in transcript if t.strip()]


class Client:
    def __init__(self, name: str):
        self.name = name.strip()
        self.key = normalize_name(name)
        self.notes: list[str] = []
        self.calls: list[Call] = []

    def add_call(self, call: Call) -> None:
        self.calls.append(call)


def clean_note(note: str) -> str:
    n = note.strip().strip("*").strip()
    return re.sub(r"^#+\s*", "", n)


def parse_file(text: str) -> list[Client]:
    lines = text.splitlines(keepends=True)
    clients: list[Client] = []
    by_key: dict[str, Client] = {}
    pending_prev: list[str] = []
    pending_next: list[str] = []
    i = 0

    def flush_notes_to_previous() -> None:
        if pending_prev and clients:
            clients[-1].notes.extend(pending_prev)
            pending_prev.clear()

    def attach_notes_to_new_client(client: Client) -> None:
        if pending_next:
            client.notes.extend(pending_next)
            pending_next.clear()

    def get_or_create(name: str) -> Client:
        key = normalize_name(name)
        if key not in by_key:
            flush_notes_to_previous()
            c = Client(name)
            attach_notes_to_new_client(c)
            by_key[key] = c
            clients.append(c)
        return by_key[key]

    def next_call_label(client: Client, explicit: str | None = None) -> str:
        if explicit:
            return explicit.strip("*").strip()
        n = len(client.calls) + 1
        return "Call 1" if n == 1 else f"Call {n}"

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if CLOSED_WON.match(line):
            pending_next.append(clean_note(line))
            i += 1
            continue
        if is_note_line(line):
            pending_prev.append(clean_note(line))
            i += 1
            continue

        if CALL_LABEL.match(line):
            if i + 1 < len(lines):
                nxt_i = skip_blank(lines, i + 1)
                if nxt_i < len(lines) and PARTICIPANTS.match(lines[nxt_i].strip()):
                    i += 1
                    continue
            i += 1
            continue

        if m_num := NUMBERED_CLIENT.match(line):
            flush_notes_to_previous()
            name = m_num.group(2).strip()
            client = get_or_create(name)
            i += 1
            call_label = "Call 1"
            hubspot = "Charles Clay"
            contact = name
            while i < len(lines):
                s = lines[i].strip()
                if FOLLOW_UP.match(s):
                    call_label = "Follow Up"
                    i += 1
                    continue
                if HUBSPOT.match(s) or CONTACT.match(s) or s == "---":
                    hubspot, contact, i = parse_hubspot_contact(lines, i)
                    if TRANSCRIPT_HDR.match(lines[i].strip() if i < len(lines) else ""):
                        i += 1
                    break
                if TRANSCRIPT_HDR.match(s):
                    i += 1
                    break
                if s.startswith("**Speaker"):
                    break
                i += 1
            body, i = read_formatted_transcript(lines, i)
            client.add_call(Call(call_label, hubspot, contact, body))
            continue

        if FOLLOW_UP.match(line):
            if not clients:
                i += 1
                continue
            client = clients[-1]
            i += 1
            hubspot, contact, i = parse_hubspot_contact(lines, i)
            if i < len(lines) and TRANSCRIPT_HDR.match(lines[i].strip()):
                i += 1
            body, i = read_formatted_transcript(lines, i)
            client.add_call(Call("Follow Up", hubspot, contact or client.name, body))
            continue

        if PARTICIPANTS.match(line):
            i += 1
            explicit_label: str | None = None
            j = i - 2
            while j >= 0 and not lines[j].strip():
                j -= 1
            if j >= 0 and CALL_LABEL.match(lines[j].strip()):
                explicit_label = lines[j].strip().strip("*").strip()
            hubspot, contact, i = parse_hubspot_contact(lines, i)
            if not contact:
                i += 1
                continue
            client = get_or_create(contact)
            if i < len(lines) and TRANSCRIPT_HDR.match(lines[i].strip()):
                i += 1
            body, i = read_formatted_transcript(lines, i)
            label = next_call_label(client, explicit_label)
            client.add_call(Call(label, hubspot, contact, body))
            continue

        if PLAIN_TS.match(line):
            name = first_plain_client_name(lines, i)
            if not name:
                i += 1
                continue
            client = get_or_create(name)
            # check for "Call 1:" label a few lines back
            explicit = None
            for back in range(max(0, i - 5), i):
                if CALL_LABEL.match(lines[back].strip()):
                    explicit = lines[back].strip().strip("*").strip()
                    break
            body, i = read_plain_transcript(lines, i)
            label = next_call_label(client, explicit)
            client.add_call(Call(label, "CJ Clay", name, body))
            continue

        i += 1

    flush_notes_to_previous()
    return clients


def render(clients: list[Client]) -> str:
    parts = ["# CJ - CLOSED TRANSCRIPTS\n"]
    for n, client in enumerate(clients, 1):
        parts.append(f"\n# {n}.) {client.name.upper()}\n")
        for note in client.notes:
            parts.append(f"\n*{clean_note(note)}*\n")
        for idx, call in enumerate(client.calls):
            if idx == 0:
                parts.append("\n## HubSpot\n")
                parts.append(f"- {call.hubspot}\n")
                parts.append("\n## Contact\n")
                parts.append(f"- {call.contact}\n")
                parts.append("\n---\n")
            else:
                parts.append(f"\n## {call.label}\n")
                parts.append("\n## HubSpot\n")
                parts.append(f"- {call.hubspot}\n")
                parts.append("\n## Contact\n")
                parts.append(f"- {call.contact}\n")
                parts.append("\n---\n")
            parts.append("\n# Transcript\n\n")
            for tline in call.transcript:
                if tline.startswith("\n## "):
                    parts.append(tline.strip() + "\n\n")
                else:
                    parts.append(tline + "\n")
    return "".join(parts)


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    clients = parse_file(text)
    out = render(clients)
    OUT.write_text(out, encoding="utf-8")
    print(f"Wrote {len(clients)} clients -> {OUT}")
    for n, c in enumerate(clients, 1):
        labels = ", ".join(call.label for call in c.calls)
        print(f"  {n}. {c.name} — {len(c.calls)} section(s): {labels}")


if __name__ == "__main__":
    main()

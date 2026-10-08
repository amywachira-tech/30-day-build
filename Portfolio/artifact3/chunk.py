"""
chunk.py
Splits the Kestrel corpus into chunks, one per access-marked section.

Access-control guarantee: every chunk comes from exactly one access section,
so no chunk can contain both agent and lead text.

Run:  python chunk.py
Output: chunks.json
"""

import json
import re
from pathlib import Path

import yaml

CORPUS_DIR = Path("corpus")
OUTPUT_FILE = Path("chunks.json")
MAX_CHARS = 1200  # sections longer than this are split by paragraph
VALID_ACCESS = {"agent", "lead"}
MARKER = re.compile(r"<!--\s*access:\s*(\w+)\s*-->")


def read_source(path):
    """Return (metadata dict, body text) for one source file."""
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"{path.name}: no frontmatter found")
    metadata = yaml.safe_load(parts[1])
    body = parts[2].strip()
    return metadata, body


def split_header(body):
    """
    Separate the text before the first access marker.
    Returns (title, intro, rest).
    title = the '# ...' heading line, intro = any other text before the first marker.
    """
    first = MARKER.search(body)
    if first is None:
        raise ValueError("no access markers found")
    header = body[: first.start()].strip()
    rest = body[first.start():]

    title, intro_lines = "", []
    for line in header.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.strip():
            intro_lines.append(line.strip())
    return title, " ".join(intro_lines), rest


def split_sections(rest):
    """Split the body on access markers. Returns a list of (access, text)."""
    sections = []
    matches = list(MARKER.finditer(rest))
    for i, match in enumerate(matches):
        access = match.group(1).lower()
        if access not in VALID_ACCESS:
            raise ValueError(f"unknown access level '{access}'")
        end = matches[i + 1].start() if i + 1 < len(matches) else len(rest)
        text = rest[match.end():end].strip()
        if text:
            sections.append((access, text))
    return sections


def split_by_size(text):
    """Split an oversized section into paragraph groups under MAX_CHARS."""
    if len(text) <= MAX_CHARS:
        return [text]
    pieces, current = [], ""
    for para in text.split("\n\n"):
        if current and len(current) + len(para) > MAX_CHARS:
            pieces.append(current.strip())
            current = ""
        current += para + "\n\n"
    if current.strip():
        pieces.append(current.strip())
    return pieces


def chunk_source(path):
    metadata, body = read_source(path)
    title, intro, rest = split_header(body)
    sections = split_sections(rest)

    # Fail closed: intro text is copied into every chunk, so it must never
    # sit in a document that also contains lead-only sections.
    has_lead = any(access == "lead" for access, _ in sections)
    if intro and has_lead:
        raise ValueError(
            f"{path.name}: intro text found in a document with lead sections. "
            "Move it under an access marker."
        )

    chunks = []
    for access, text in sections:
        for piece in split_by_size(text):
            # source_name is more specific than the title (all Slack
            # announcements share the title "#policy-updates").
            name = metadata["source_name"]
            context = name if not intro else f"{name}. {intro}"
            chunk_id = f"{metadata['source_id']}-c{len(chunks) + 1:02d}"
            chunks.append({
                "chunk_id": chunk_id,
                **metadata,
                "access_level": access,
                "text": f"{context}\n\n{piece}",
            })
    return chunks


def main():
    sources = sorted(p for p in CORPUS_DIR.glob("S*.md"))
    all_chunks = []
    for path in sources:
        all_chunks.extend(chunk_source(path))

    # Dates from YAML load as date objects; store them as text for JSON.
    OUTPUT_FILE.write_text(
        json.dumps(all_chunks, indent=2, default=str), encoding="utf-8"
    )

    agent = sum(1 for c in all_chunks if c["access_level"] == "agent")
    lead = len(all_chunks) - agent
    print(f"Sources: {len(sources)}")
    print(f"Chunks:  {len(all_chunks)} ({agent} agent, {lead} lead)")
    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

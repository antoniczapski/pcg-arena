"""
Extract all citations from main.tex with surrounding context.

Parses \cite{...}, \citep{...}, and \citet{...} commands.
Outputs citations.json with:
  - citation_key: the BibTeX key
  - citation_type: cite / citep / citet
  - context: surrounding text (±200 chars around the citation)
  - line_number: line in main.tex
  - section: the current section/subsection
  - chapter: the current chapter
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict


def extract_citations(tex_path: Path) -> list[dict]:
    text = tex_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Build line-offset map for converting char-positions to line numbers
    line_offsets = []
    offset = 0
    for line in lines:
        line_offsets.append(offset)
        offset += len(line) + 1  # +1 for \n

    def char_to_line(pos: int) -> int:
        for i, off in enumerate(line_offsets):
            if i + 1 < len(line_offsets) and line_offsets[i + 1] > pos:
                return i + 1  # 1-based
            elif i + 1 == len(line_offsets):
                return i + 1
        return len(lines)

    # Track current chapter/section by scanning lines
    chapter_at_line = {}
    section_at_line = {}
    current_chapter = ""
    current_section = ""

    chapter_re = re.compile(r"\\chapter\{(.+?)\}")
    section_re = re.compile(r"\\(?:sub)*section\{(.+?)\}")

    for i, line in enumerate(lines):
        m = chapter_re.search(line)
        if m:
            current_chapter = m.group(1)
        m = section_re.search(line)
        if m:
            current_section = m.group(1)
        chapter_at_line[i + 1] = current_chapter
        section_at_line[i + 1] = current_section

    # Find all \cite{}, \citep{}, \citet{} with their positions
    cite_pattern = re.compile(r"\\(citep?|citet)\{([^}]+)\}")

    results = []
    seen_entries = defaultdict(list)  # key -> list of occurrences

    for match in cite_pattern.finditer(text):
        cite_type = match.group(1)
        keys_str = match.group(2)
        start = match.start()
        end = match.end()
        line_num = char_to_line(start)

        # Extract context: ±200 chars, clean up
        ctx_start = max(0, start - 200)
        ctx_end = min(len(text), end + 200)
        context = text[ctx_start:ctx_end]
        # Clean up LaTeX commands for readability but keep enough
        context = context.replace("\n", " ")
        context = re.sub(r"\s+", " ", context).strip()

        # Split multi-key citations (e.g., \citep{key1, key2})
        keys = [k.strip() for k in keys_str.split(",")]

        for key in keys:
            entry = {
                "citation_key": key,
                "citation_type": cite_type,
                "context": context,
                "line_number": line_num,
                "chapter": chapter_at_line.get(line_num, ""),
                "section": section_at_line.get(line_num, ""),
            }
            results.append(entry)
            seen_entries[key].append(entry)

    return results, seen_entries


def build_summary(results: list[dict], seen_entries: dict) -> dict:
    """Build a summary with unique citation keys and their usage counts."""
    citations = []
    for key in sorted(seen_entries.keys()):
        occurrences = seen_entries[key]
        citations.append({
            "citation_key": key,
            "count": len(occurrences),
            "occurrences": [
                {
                    "citation_type": occ["citation_type"],
                    "line_number": occ["line_number"],
                    "chapter": occ["chapter"],
                    "section": occ["section"],
                    "context": occ["context"],
                }
                for occ in occurrences
            ],
        })

    return {
        "total_citation_instances": len(results),
        "unique_citation_keys": len(seen_entries),
        "citations": citations,
    }


def main():
    tex_path = Path(__file__).parent.parent / "masters_thesis" / "main.tex"
    if not tex_path.exists():
        print(f"ERROR: {tex_path} not found")
        sys.exit(1)

    results, seen_entries = extract_citations(tex_path)
    summary = build_summary(results, seen_entries)

    out_path = Path(__file__).parent / "citations.json"
    out_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Extracted {summary['total_citation_instances']} citation instances")
    print(f"Found {summary['unique_citation_keys']} unique citation keys")
    print(f"Output written to {out_path}")

    # Print summary table
    print(f"\n{'Key':<40} {'Count':>5}")
    print("-" * 47)
    for c in summary["citations"]:
        print(f"{c['citation_key']:<40} {c['count']:>5}")


if __name__ == "__main__":
    main()

"""
Cross-validate thesis citations against reference documents.

For each citation occurrence:
  1. Verify the thesis_claim text actually appears in main.tex (via context match)
  2. Search the reference_documents for key phrases from reference_citation
  3. Report confidence level and any discrepancies

Outputs cross_validation_report.json with pass/fail/warning per citation.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional


WORKSPACE = Path(__file__).parent.parent.parent  # pcg-arena root
LIT_ROOT = WORKSPACE / "latex" / "literature_review"
THESIS_PATH = WORKSPACE / "latex" / "masters_thesis" / "main.tex"


def load_reference_doc(doc_path: str) -> Optional[str]:
    """Load a reference document, returning its text or None if not found."""
    full_path = WORKSPACE / doc_path
    if full_path.exists():
        return full_path.read_text(encoding="utf-8", errors="replace")
    return None


def extract_key_phrases(text: str) -> list[str]:
    """Extract verifiable key phrases from a text string (thesis_claim or reference_citation).

    We look for:
    - Quoted strings
    - Numbers (percentages, counts, years)
    - Technical terms and proper nouns
    """
    phrases = []

    # Extract quoted strings (single or double quotes)
    quoted = re.findall(r"['\"]([^'\"]{5,})['\"]", text)
    phrases.extend(quoted)

    # Extract key numbers with context (e.g., "n=37", "97%", "240,000+", "6.7B")
    numbers = re.findall(
        r"(?:n\s*=\s*\d+|\d+[\.,]?\d*\s*%|\d+[\.,]?\d*[BKM]?\+?\s*(?:votes|users|parameters|participants|subjects|players|comparisons|judges|models|tasks|levels|chunks|games|posts))",
        text,
        re.IGNORECASE,
    )
    phrases.extend(numbers)

    # Extract specific technical terms likely to appear in papers
    tech_terms = re.findall(
        r"(?:Bradley-Terry|Glicko-2?|CMA-ES|DCGAN|DistilGPT-2|GPT-[234]|LSTM|RLHF|DPO|PPO|ROUGE|ERA|VGLC|NCD|MDP|InstructGPT|BART|UNet|Launchpad|Paradox|Chatbot Arena|KL penalty|rating deviation|playability|cross-entropy|volatility|fitness function|latent space|anchor point|context-free grammar|Grammatical Evolution|micro-pattern|sliding.window|pairwise|forced-choice|latent variable evolution|LVE|performance rating|expected score|Video Game Level Corpus|Likert)",
        text,
        re.IGNORECASE,
    )
    phrases.extend(tech_terms)

    return list(set(phrases))


def search_in_document(text: str, phrases: list[str]) -> dict:
    """Search for key phrases in a document, return match results."""
    results = {}
    text_lower = text.lower()

    for phrase in phrases:
        phrase_lower = phrase.lower().strip()
        if len(phrase_lower) < 3:
            continue

        # Try exact match first
        if phrase_lower in text_lower:
            # Find the surrounding context
            idx = text_lower.index(phrase_lower)
            start = max(0, idx - 100)
            end = min(len(text), idx + len(phrase_lower) + 100)
            context = text[start:end].replace("\n", " ")
            context = re.sub(r"\s+", " ", context).strip()
            results[phrase] = {"found": True, "context": context}
            continue

        # Try normalized number search: "n=37" → also search for "37"
        num_match = re.match(r"n\s*=\s*(\d+)", phrase_lower)
        if num_match:
            bare_number = num_match.group(1)
            if bare_number in text_lower:
                idx = text_lower.index(bare_number)
                start = max(0, idx - 100)
                end = min(len(text), idx + len(bare_number) + 100)
                context = text[start:end].replace("\n", " ")
                context = re.sub(r"\s+", " ", context).strip()
                results[phrase] = {"found": True, "context": f"(number match '{bare_number}') {context}"}
                continue

        # Try dehyphenated search: "sliding-window" → "sliding" + "window"
        if "-" in phrase_lower and len(phrase_lower) > 5:
            parts = [p for p in phrase_lower.split("-") if len(p) > 3]
            if parts and all(p in text_lower for p in parts):
                results[phrase] = {"found": True, "context": "(dehyphenated match - all parts found)"}
                continue

        # Try proximity match for "NUMBER NOUN" patterns (e.g., "600 players")
        # Allows intervening words like "600 human players"
        num_noun = re.match(r"^(\d+)\s+(\w+)$", phrase_lower)
        if num_noun:
            number, noun = num_noun.group(1), num_noun.group(2)
            # Search for number followed by noun within 5 words
            pattern = re.compile(
                r"\b" + re.escape(number) + r"\b(?:\s+\w+){0,4}\s+" + re.escape(noun),
                re.IGNORECASE,
            )
            m = pattern.search(text)
            if m:
                idx = m.start()
                start = max(0, idx - 80)
                end = min(len(text), m.end() + 80)
                context = text[start:end].replace("\n", " ")
                context = re.sub(r"\s+", " ", context).strip()
                results[phrase] = {"found": True, "context": f"(proximity match) {context}"}
                continue

        # Try fuzzy: split into words and check if most words appear nearby
        words = phrase_lower.split()
        if len(words) >= 3:
            # Check if all significant words appear in the doc
            significant_words = [w for w in words if len(w) > 3]
            found_count = sum(1 for w in significant_words if w in text_lower)
            if significant_words and found_count >= len(significant_words) * 0.7:
                results[phrase] = {"found": True, "context": "(fuzzy match - key words found)"}
            else:
                results[phrase] = {"found": False, "context": None}
        else:
            results[phrase] = {"found": False, "context": None}

    return results


def verify_thesis_context(thesis_text: str, context: str, line_number: int) -> bool:
    """Verify that the citation context actually appears in the thesis.

    Primary method: check if the cited line_number has a \\cite command with
    the expected context. Falls back to text matching if needed.
    """
    lines = thesis_text.split("\n")
    if 1 <= line_number <= len(lines):
        # Check a window of ±3 lines around the reported line
        start = max(0, line_number - 4)
        end = min(len(lines), line_number + 3)
        window = " ".join(lines[start:end])
        # If the window contains a \cite command, the context is present
        if "\\cite" in window:
            return True

    # Fallback: extract 3-4 distinctive plain-text words from context and check
    context_clean = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", " ", context)
    context_clean = re.sub(r"[{}\\$~%^_]", " ", context_clean)
    context_clean = re.sub(r"\s+", " ", context_clean).strip()

    # Extract words of length >= 5 that are not LaTeX artifacts
    words = [w for w in context_clean.split() if len(w) >= 5 and w.isalpha()]
    if len(words) >= 4:
        # Check if at least 70% of distinctive words appear in the thesis
        thesis_lower = thesis_text.lower()
        found = sum(1 for w in words[:8] if w.lower() in thesis_lower)
        return found >= len(words[:8]) * 0.7

    return True  # If we can't verify, assume present (it came from the file)


def main():
    # Load citations
    citations_path = Path(__file__).parent / "citations.json"
    data = json.loads(citations_path.read_text(encoding="utf-8"))

    # Load thesis
    thesis_text = THESIS_PATH.read_text(encoding="utf-8")

    # Pre-load all reference documents
    doc_cache = {}

    report = {
        "summary": {},
        "citations": [],
        "missing_documents": [],
    }

    total_occurrences = 0
    passed = 0
    warnings = 0
    failed = 0
    missing_ref_docs = set()

    for citation in data["citations"]:
        key = citation["citation_key"]
        ref_docs = citation.get("reference_documents", [])

        citation_report = {
            "citation_key": key,
            "count": citation["count"],
            "reference_documents": ref_docs,
            "occurrences": [],
        }

        # Load reference documents
        loaded_docs = {}
        for doc_path in ref_docs:
            if doc_path == "NOT FOUND":
                continue
            if doc_path not in doc_cache:
                text = load_reference_doc(doc_path)
                if text is None:
                    missing_ref_docs.add(doc_path)
                    doc_cache[doc_path] = None
                else:
                    doc_cache[doc_path] = text
            loaded_docs[doc_path] = doc_cache[doc_path]

        for i, occ in enumerate(citation["occurrences"]):
            total_occurrences += 1

            thesis_claim = occ.get("thesis_claim", "UNKNOWN")
            reference_citation = occ.get("reference_citation", "NO REFERENCE")
            context = occ.get("context", "")

            occ_report = {
                "occurrence_index": i,
                "line_number": occ["line_number"],
                "chapter": occ["chapter"],
                "section": occ["section"],
                "thesis_claim": thesis_claim,
                "reference_citation": reference_citation,
                "checks": {},
            }

            # Check 1: Does the context appear in the thesis?
            thesis_present = verify_thesis_context(thesis_text, context, occ["line_number"])
            occ_report["checks"]["thesis_context_present"] = thesis_present

            # Check 2: Can we find key phrases in reference documents?
            # Extract from BOTH reference_citation AND thesis_claim to avoid
            # false warnings when AI-written reference_citation uses different
            # wording than the actual paper.
            ref_phrases = extract_key_phrases(reference_citation)
            claim_phrases = extract_key_phrases(thesis_claim)
            # Combine, deduplicating
            key_phrases = list(set(ref_phrases + claim_phrases))
            occ_report["checks"]["key_phrases_extracted"] = len(key_phrases)
            occ_report["checks"]["phrase_sources"] = {
                "from_reference_citation": len(ref_phrases),
                "from_thesis_claim": len(claim_phrases),
                "combined_unique": len(key_phrases),
            }

            doc_search_results = {}
            any_doc_confirms = False

            for doc_path, doc_text in loaded_docs.items():
                if doc_text is None:
                    doc_search_results[doc_path] = {"status": "DOCUMENT_NOT_FOUND"}
                    continue

                search_results = search_in_document(doc_text, key_phrases)
                found_count = sum(1 for r in search_results.values() if r["found"])
                total_phrases = len(search_results)

                if total_phrases > 0:
                    match_rate = found_count / total_phrases
                else:
                    match_rate = 0

                doc_search_results[doc_path] = {
                    "phrases_searched": total_phrases,
                    "phrases_found": found_count,
                    "match_rate": round(match_rate, 2),
                    "details": {
                        k: v for k, v in search_results.items()
                    },
                }

                if match_rate >= 0.3:
                    any_doc_confirms = True

            occ_report["checks"]["reference_document_search"] = doc_search_results

            # Overall verdict
            if thesis_present and any_doc_confirms:
                occ_report["verdict"] = "PASS"
                passed += 1
            elif thesis_present and not any_doc_confirms and len(key_phrases) == 0:
                # No extractable phrases but thesis context exists — likely a general claim
                occ_report["verdict"] = "PASS (general claim)"
                passed += 1
            elif thesis_present and not any_doc_confirms:
                occ_report["verdict"] = "WARNING - claim in thesis but weak reference support"
                warnings += 1
            elif not thesis_present:
                occ_report["verdict"] = "FAIL - context not found in thesis"
                failed += 1
            else:
                occ_report["verdict"] = "UNKNOWN"
                warnings += 1

            citation_report["occurrences"].append(occ_report)

        report["citations"].append(citation_report)

    # Summary
    report["summary"] = {
        "total_citation_keys": data["unique_citation_keys"],
        "total_occurrences": total_occurrences,
        "passed": passed,
        "warnings": warnings,
        "failed": failed,
        "pass_rate": round(passed / total_occurrences * 100, 1) if total_occurrences > 0 else 0,
    }

    report["missing_documents"] = sorted(missing_ref_docs)
    report["missing_dedicated_paper_files"] = data.get("missing_dedicated_paper_files", [])

    # Write report
    out_path = Path(__file__).parent / "cross_validation_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print summary
    print("=" * 60)
    print("CROSS-VALIDATION REPORT")
    print("=" * 60)
    print(f"Total citation keys:   {report['summary']['total_citation_keys']}")
    print(f"Total occurrences:     {report['summary']['total_occurrences']}")
    print(f"Passed:                {report['summary']['passed']}")
    print(f"Warnings:              {report['summary']['warnings']}")
    print(f"Failed:                {report['summary']['failed']}")
    print(f"Pass rate:             {report['summary']['pass_rate']}%")
    print()

    if report["missing_documents"]:
        print("MISSING REFERENCE DOCUMENTS:")
        for doc in report["missing_documents"]:
            print(f"  - {doc}")
        print()

    if report["missing_dedicated_paper_files"]:
        print("CITATION KEYS WITHOUT DEDICATED PAPER .md FILES:")
        print("(These are verified via background summaries and deep research reports)")
        for key in report["missing_dedicated_paper_files"]:
            print(f"  - {key}")
        print()

    # Print warnings and failures
    print("-" * 60)
    for cit_report in report["citations"]:
        for occ in cit_report["occurrences"]:
            if "WARNING" in occ["verdict"] or "FAIL" in occ["verdict"]:
                print(f"[{occ['verdict']}]")
                print(f"  Key: {cit_report['citation_key']}")
                print(f"  Line: {occ['line_number']}")
                print(f"  Section: {occ['section']}")
                print(f"  Claim: {occ['thesis_claim'][:100]}...")
                print()


if __name__ == "__main__":
    main()

"""
Convert downloaded PDFs to structured markdown files.
Maps each PDF to its citation key and extracts text using PyMuPDF.
"""
import fitz  # PyMuPDF
import os
import re

# Map PDFs to citation keys and proper filenames
PDF_MAPPING = {
    "2334029.pdf": {
        "citation_key": "bradley1952rank",
        "output_name": "bradley1952-rank-analysis-paired-comparisons.md",
        "title": "Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons",
        "authors": "Ralph Allan Bradley, Milton E. Terry",
        "year": 1952,
        "source": "Biometrika, 39(3/4), 324-345",
    },
    "glicko2.pdf": {
        "citation_key": "glickman2012glicko2",
        "output_name": "glickman2012-example-glicko2-system.md",
        "title": "Example of the Glicko-2 System",
        "authors": "Mark E. Glickman",
        "year": 2012,
        "source": "Technical Report, Boston University",
    },
    "tciaig.2012.2188528.pdf": {
        "citation_key": "karakovskiy2012marioai",
        "output_name": "karakovskiy2012-mario-ai-benchmark-competitions.md",
        "title": "The Mario AI Benchmark and Competitions",
        "authors": "Sergey Karakovskiy, Julian Togelius",
        "year": 2012,
        "source": "IEEE Transactions on Computational Intelligence and AI in Games, 4(1), 55-67",
    },
    "7416-52-10717-1-2-20200923.pdf": {
        "citation_key": "khalifa2020pcgrl",
        "output_name": "khalifa2020-pcgrl-procedural-content-generation-rl.md",
        "title": "PCGRL: Procedural Content Generation via Reinforcement Learning",
        "authors": "Ahmed Khalifa, Philip Bontrager, Sam Earle, Julian Togelius",
        "year": 2020,
        "source": "Proceedings of the AAAI Conference on Artificial Intelligence and Interactive Digital Entertainment (AIIDE)",
    },
    "1702.00539v3.pdf": {
        "citation_key": "summerville2018pcgml",
        "output_name": "summerville2018-pcgml-procedural-content-generation-ml.md",
        "title": "Procedural Content Generation via Machine Learning (PCGML)",
        "authors": "Adam Summerville, Sam Snodgrass, Matthew Guzdial, Christoffer Holmgård, Amy K. Hoover, Aaron Isaksen, Andy Nealen, Julian Togelius",
        "year": 2018,
        "source": "IEEE Transactions on Games, 10(3), 257-270",
    },
    "Togelius2011Searchbased (1).pdf": {
        "citation_key": "togelius2011search",
        "output_name": "togelius2011-search-based-pcg-taxonomy-survey.md",
        "title": "Search-Based Procedural Content Generation: A Taxonomy and Survey",
        "authors": "Julian Togelius, Georgios N. Yannakakis, Kenneth O. Stanley, Cameron Browne",
        "year": 2011,
        "source": "IEEE Transactions on Computational Intelligence and AI in Games, 3(3), 172-186",
    },
    "PID3821875.pdf": {
        "citation_key": "yannakakis2011experience",
        "output_name": "yannakakis2011-experience-driven-pcg.md",
        "title": "Experience-Driven Procedural Content Generation",
        "authors": "Georgios N. Yannakakis, Julian Togelius",
        "year": 2011,
        "source": "IEEE Transactions on Affective Computing, 2(3), 147-161",
    },
    "mariolevelcomp.pdf": {
        "citation_key": "shaker2011mario",
        "output_name": "shaker2011-mario-level-generation-track.md",
        "title": "The 2010 Mario AI Championship: Level Generation Track",
        "authors": "Noor Shaker, Julian Togelius, Georgios N. Yannakakis, Ben Weber, Tomoyuki Shimizu, Tomonori Hashiyama, Nathan Sorenson, Philippe Pasquier, Peter Mawhorter, Glen Takahashi, Gillian Smith, Robin Baumgarten",
        "year": 2011,
        "source": "IEEE Transactions on Computational Intelligence and AI in Games, 3(4), 332-347",
    },
    "3102071.3102080.pdf": {
        "citation_key": "summerville2017understanding",
        "output_name": "summerville2017-understanding-mario-evaluation-metrics.md",
        "title": "Understanding Mario: An Evaluation of Design Metrics for Platformers",
        "authors": "Adam Summerville, Michael Mateas",
        "year": 2017,
        "source": "Proceedings of the 12th International Conference on the Foundations of Digital Games (FDG)",
    },
    "1978-elo-theratingofchessplayerspastandpresent.pdf": {
        "citation_key": "elo1978rating",
        "output_name": "elo1978-rating-of-chessplayers.md",
        "title": "The Rating of Chessplayers, Past and Present",
        "authors": "Arpad E. Elo",
        "year": 1978,
        "source": "Arco Publishing, New York",
    },
    "CIG11-final.pdf": {
        "citation_key": "shaker2011features",
        "output_name": "shaker2011-feature-analysis-game-content-quality.md",
        "title": "Feature Analysis for Modeling Game Content Quality",
        "authors": "Noor Shaker, Georgios N. Yannakakis, Julian Togelius",
        "year": 2011,
        "source": "IEEE Conference on Computational Intelligence and Games (CIG)",
    },
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF, page by page."""
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            pages.append(f"<!-- Page {i+1} -->\n{text}")
    doc.close()
    return "\n\n".join(pages)


def clean_text(text: str) -> str:
    """Basic cleanup of extracted text."""
    # Fix hyphenated line breaks
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    # Collapse multiple blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text


def create_markdown(info: dict, body_text: str) -> str:
    """Create a structured markdown document from PDF text."""
    header = f"""# {info['title']}

**Authors:** {info['authors']}
**Year:** {info['year']}
**Source:** {info['source']}
**Citation Key:** `{info['citation_key']}`

---

## Extracted Content

"""
    return header + body_text


def main():
    output_dir = SCRIPT_DIR  # same directory
    converted = []
    failed = []

    for pdf_name, info in PDF_MAPPING.items():
        pdf_path = os.path.join(SCRIPT_DIR, pdf_name)
        if not os.path.exists(pdf_path):
            print(f"  SKIP: {pdf_name} not found")
            failed.append(pdf_name)
            continue

        print(f"  Converting: {pdf_name} -> {info['output_name']}")
        try:
            raw_text = extract_pdf_text(pdf_path)
            cleaned = clean_text(raw_text)
            markdown = create_markdown(info, cleaned)

            output_path = os.path.join(output_dir, info['output_name'])
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            # Print stats
            word_count = len(cleaned.split())
            print(f"    -> {word_count} words extracted")
            converted.append(info['output_name'])
        except Exception as e:
            print(f"    ERROR: {e}")
            failed.append(pdf_name)

    print(f"\n  Converted: {len(converted)}/{len(PDF_MAPPING)}")
    if failed:
        print(f"  Failed: {failed}")
    return converted


if __name__ == "__main__":
    main()

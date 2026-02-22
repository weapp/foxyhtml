#!/usr/bin/env python3
"""
Benchmark of FoxyHTML vs popular Python HTML parsing libraries.

Two scenarios:
  - "article"  : synthetic HTML (~1 KB / 25 KB / 248 KB), scrapes article structure
  - "actor"    : Wikipedia — Charlie Chaplin (~1.4 MB, CC-BY-SA), scrapes an actor
                 profile (infobox, sections, award tables) buried in ~38 000 nodes

Metrics measured per library:
  - parse time   : tokenise raw HTML and build internal representation
  - scrape time  : extraction pipeline (queries + subqueries) on the pre-parsed doc
  - parse memory : peak heap allocated during parse (tracemalloc)

Usage:
    python benchmarks/bench.py [--size small|medium|large|wikipedia|all] [--runs N]

Optional dependencies:
    pip install -e ".[benchmark]"

Wikipedia fixture (CC-BY-SA):
    python benchmarks/download_fixtures.py
"""
import argparse
import json
import subprocess
import sys
import timeit
from pathlib import Path

# ---------------------------------------------------------------------------
# Library detection
# ---------------------------------------------------------------------------

LIBS: dict[str, bool] = {}

try:
    from foxyhtml import FoxyHtml
    LIBS["foxyhtml"] = True
except ImportError:
    LIBS["foxyhtml"] = False

try:
    from bs4 import BeautifulSoup
    LIBS["bs4_html_parser"] = True
    LIBS["bs4_lxml"] = False
    try:
        import lxml  # noqa: F401
        LIBS["bs4_lxml"] = True
    except ImportError:
        pass
except ImportError:
    LIBS["bs4_html_parser"] = False
    LIBS["bs4_lxml"] = False

try:
    from lxml import html as lxml_html
    LIBS["lxml"] = True
except ImportError:
    LIBS["lxml"] = False

try:
    from selectolax.parser import HTMLParser as SelectolaxParser
    LIBS["selectolax"] = True
except ImportError:
    LIBS["selectolax"] = False

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_html(name: str) -> str:
    path = FIXTURES_DIR / f"{name}.html"
    if not path.exists():
        sys.exit(
            f"\nERROR: fixture not found: {path}\n"
            f"Download it with: python benchmarks/download_fixtures.py\n"
        )
    return path.read_text(encoding="utf-8")


def make_large(medium_html: str, factor: int = 10) -> str:
    body_start = medium_html.find("<body>") + len("<body>")
    body_end = medium_html.rfind("</body>")
    return (
        medium_html[:body_start]
        + medium_html[body_start:body_end] * factor
        + medium_html[body_end:]
    )


# ---------------------------------------------------------------------------
# Scenario 1: article (small / medium / large)
#
# Extracts: metadata (h1, time, author, tags), per-section subqueries
# (h2, paragraphs, list items), related post cards, and nav links.
# ---------------------------------------------------------------------------

def scrape_article_foxyhtml(doc) -> None:
    list(doc.select("h1").joinedtexts())
    list(doc.select("time").attr("datetime"))
    list(doc.select(".author-link").joinedtexts())
    list(doc.search(cls="tag").joinedtexts())

    for section in doc.search("section"):
        list(section.search("h2").joinedtexts())
        list(section.search("p").joinedtexts())
        list(section.search("li").joinedtexts())

    for card in doc.search(cls="post-card"):
        list(card.search("h3").joinedtexts())
        list(card.search(cls="post-card-excerpt").joinedtexts())

    list(doc.search(cls="nav-link").joinedtexts())


def scrape_article_bs4(soup) -> None:
    h1 = soup.find("h1")
    _ = h1.get_text(strip=True) if h1 else ""
    t = soup.find("time")
    _ = t.get("datetime", "") if t else ""
    a = soup.find(class_="author-link")
    _ = a.get_text(strip=True) if a else ""
    _ = [el.get_text(strip=True) for el in soup.find_all(class_="tag")]

    for section in soup.find_all("section"):
        h2 = section.find("h2")
        _ = h2.get_text(strip=True) if h2 else ""
        _ = [p.get_text(strip=True) for p in section.find_all("p")]
        _ = [li.get_text(strip=True) for li in section.find_all("li")]

    for card in soup.find_all(class_="post-card"):
        h3 = card.find("h3")
        _ = h3.get_text(strip=True) if h3 else ""
        exc = card.find(class_="post-card-excerpt")
        _ = exc.get_text(strip=True) if exc else ""

    _ = [a.get_text(strip=True) for a in soup.find_all(class_="nav-link")]


def scrape_article_lxml(tree) -> None:
    h1 = tree.find(".//h1")
    _ = h1.text_content().strip() if h1 is not None else ""
    t = tree.find(".//time")
    _ = t.get("datetime", "") if t is not None else ""
    authors = tree.xpath('//*[contains(concat(" ",@class," ")," author-link ")]')
    _ = authors[0].text_content().strip() if authors else ""
    _ = [el.text_content().strip()
         for el in tree.xpath('//*[contains(concat(" ",@class," ")," tag ")]')]

    for section in tree.findall(".//section"):
        h2 = section.find(".//h2")
        _ = h2.text_content().strip() if h2 is not None else ""
        _ = [p.text_content().strip() for p in section.findall(".//p")]
        _ = [li.text_content().strip() for li in section.findall(".//li")]

    for card in tree.xpath('//*[contains(concat(" ",@class," ")," post-card ")]'):
        h3 = card.find(".//h3")
        _ = h3.text_content().strip() if h3 is not None else ""
        exc = card.xpath('.//*[contains(concat(" ",@class," ")," post-card-excerpt ")]')
        _ = exc[0].text_content().strip() if exc else ""

    _ = [a.text_content().strip()
         for a in tree.xpath('//*[contains(concat(" ",@class," ")," nav-link ")]')]


def scrape_article_selectolax(tree) -> None:
    h1 = tree.css_first("h1")
    _ = h1.text(strip=True) if h1 else ""
    t = tree.css_first("time")
    _ = t.attributes.get("datetime", "") if t else ""
    a = tree.css_first(".author-link")
    _ = a.text(strip=True) if a else ""
    _ = [el.text(strip=True) for el in tree.css(".tag")]

    for section in tree.css("section"):
        h2 = section.css_first("h2")
        _ = h2.text(strip=True) if h2 else ""
        _ = [p.text(strip=True) for p in section.css("p")]
        _ = [li.text(strip=True) for li in section.css("li")]

    for card in tree.css(".post-card"):
        h3 = card.css_first("h3")
        _ = h3.text(strip=True) if h3 else ""
        exc = card.css_first(".post-card-excerpt")
        _ = exc.text(strip=True) if exc else ""

    _ = [a.text(strip=True) for a in tree.css(".nav-link")]


# ---------------------------------------------------------------------------
# Scenario 2: actor profile (Wikipedia ~1.4 MB, CC-BY-SA)
#
# Extracts: infobox rows (th/td pairs), h2 section headings, all rows and
# cells from wikitable award/filmography tables, page categories.
# The target data is a small fraction buried in ~38 000 nodes of navigation,
# references, CSS templates and scripts.
# ---------------------------------------------------------------------------

def scrape_actor_foxyhtml(doc) -> None:
    for ib in doc.search("table", cls="infobox"):
        for row in ib.search("tr"):
            th = row.search("th")
            td = row.search("td")
            _ = th[0].joinedtexts() if th else ""
            _ = td[0].joinedtexts() if td else ""

    list(doc.search("h2").joinedtexts())

    for table in doc.search("table", cls="wikitable"):
        for row in table.search("tr"):
            list(row.search("th").joinedtexts())
            list(row.search("td").joinedtexts())

    cats = doc.search(cls="mw-normal-catlinks")
    if cats:
        list(cats[0].search("a").joinedtexts())


def scrape_actor_bs4(soup) -> None:
    for ib in soup.find_all("table", class_="infobox"):
        for row in ib.find_all("tr"):
            th = row.find("th")
            td = row.find("td")
            _ = th.get_text(strip=True) if th else ""
            _ = td.get_text(strip=True) if td else ""

    _ = [h.get_text(strip=True) for h in soup.find_all("h2")]

    for table in soup.find_all("table", class_="wikitable"):
        for row in table.find_all("tr"):
            _ = [td.get_text(strip=True) for td in row.find_all("td")]
            _ = [th.get_text(strip=True) for th in row.find_all("th")]

    cats = soup.find(class_="mw-normal-catlinks")
    if cats:
        _ = [a.get_text(strip=True) for a in cats.find_all("a")]


def scrape_actor_lxml(tree) -> None:
    for ib in tree.xpath('//table[contains(@class,"infobox")]'):
        for row in ib.findall(".//tr"):
            th = row.find(".//th")
            td = row.find(".//td")
            _ = th.text_content().strip() if th is not None else ""
            _ = td.text_content().strip() if td is not None else ""

    _ = [h.text_content().strip() for h in tree.findall(".//h2")]

    for table in tree.xpath('//table[contains(@class,"wikitable")]'):
        for row in table.findall(".//tr"):
            _ = [td.text_content().strip() for td in row.findall(".//td")]
            _ = [th.text_content().strip() for th in row.findall(".//th")]

    cats = tree.xpath('//*[contains(@class,"mw-normal-catlinks")]')
    if cats:
        _ = [a.text_content().strip() for a in cats[0].findall(".//a")]


def scrape_actor_selectolax(tree) -> None:
    for ib in tree.css("table.infobox"):
        for row in ib.css("tr"):
            th = row.css_first("th")
            td = row.css_first("td")
            _ = th.text(strip=True) if th else ""
            _ = td.text(strip=True) if td else ""

    _ = [h.text(strip=True) for h in tree.css("h2")]

    for table in tree.css("table.wikitable"):
        for row in table.css("tr"):
            _ = [td.text(strip=True) for td in row.css("td")]
            _ = [th.text(strip=True) for th in row.css("th")]

    cats = tree.css_first(".mw-normal-catlinks")
    if cats:
        _ = [a.text(strip=True) for a in cats.css("a")]


# ---------------------------------------------------------------------------
# Library registry
# ---------------------------------------------------------------------------

def _make_foxyhtml(html, scrape_fn):
    def parse(): FoxyHtml(html)
    doc = FoxyHtml(html)
    def scrape(): scrape_fn(doc)
    return parse, scrape

def _make_bs4_html_parser(html, scrape_fn):
    def parse(): BeautifulSoup(html, "html.parser")
    soup = BeautifulSoup(html, "html.parser")
    def scrape(): scrape_fn(soup)
    return parse, scrape

def _make_bs4_lxml(html, scrape_fn):
    def parse(): BeautifulSoup(html, "lxml")
    soup = BeautifulSoup(html, "lxml")
    def scrape(): scrape_fn(soup)
    return parse, scrape

def _make_lxml(html, scrape_fn):
    def parse(): lxml_html.fromstring(html)
    tree = lxml_html.fromstring(html)
    def scrape(): scrape_fn(tree)
    return parse, scrape

def _make_selectolax(html, scrape_fn):
    from selectolax.parser import HTMLParser
    def parse(): HTMLParser(html)
    tree = HTMLParser(html)
    def scrape(): scrape_fn(tree)
    return parse, scrape


LIB_FACTORIES = [
    ("foxyhtml",          _make_foxyhtml,         LIBS["foxyhtml"]),
    ("bs4 + html.parser", _make_bs4_html_parser,  LIBS.get("bs4_html_parser", False)),
    ("bs4 + lxml",        _make_bs4_lxml,         LIBS.get("bs4_lxml", False)),
    ("lxml.html",         _make_lxml,             LIBS.get("lxml", False)),
    ("selectolax",        _make_selectolax,       LIBS.get("selectolax", False)),
]

ARTICLE_SCRAPES = {
    "foxyhtml":          scrape_article_foxyhtml,
    "bs4 + html.parser": scrape_article_bs4,
    "bs4 + lxml":        scrape_article_bs4,
    "lxml.html":         scrape_article_lxml,
    "selectolax":        scrape_article_selectolax,
}

ACTOR_SCRAPES = {
    "foxyhtml":          scrape_actor_foxyhtml,
    "bs4 + html.parser": scrape_actor_bs4,
    "bs4 + lxml":        scrape_actor_bs4,
    "lxml.html":         scrape_actor_lxml,
    "selectolax":        scrape_actor_selectolax,
}

# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

_WORKER = Path(__file__).parent / "_mem_worker.py"
_LIB_KEYS = {
    "foxyhtml":          "foxyhtml",
    "bs4 + html.parser": "bs4_html_parser",
    "bs4 + lxml":        "bs4_lxml",
    "lxml.html":         "lxml",
    "selectolax":        "selectolax",
}


def measure_memory_rss(lib_name: str, html_path: Path) -> float | None:
    """
    Spawn an isolated subprocess that parses the fixture and reports RSS delta.
    Each call starts from a clean heap, so C-level allocations (lxml, selectolax)
    are captured correctly alongside Python-level ones.
    Returns KB, or None on failure.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(_WORKER), _LIB_KEYS[lib_name], str(html_path)],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)["rss_kb"]
    except Exception:
        return None


def run_benchmarks(html: str, html_path: Path, scrape_map: dict, runs: int) -> dict:
    results = {}
    for lib_name, factory_fn, available in LIB_FACTORIES:
        if not available:
            results[lib_name] = None
            continue
        scrape_fn = scrape_map[lib_name]
        try:
            parse_fn, scrape_fn_bound = factory_fn(html, scrape_fn)
            t_parse  = timeit.timeit(parse_fn,        number=runs) / runs * 1000
            t_scrape = timeit.timeit(scrape_fn_bound, number=runs) / runs * 1000
            mem_kb   = measure_memory_rss(lib_name, html_path)
            results[lib_name] = {
                "parse":  t_parse,
                "scrape": t_scrape,
                "mem_kb": mem_kb,
            }
        except Exception as e:
            results[lib_name] = {"_error": str(e)}
    return results

# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def fmt_time(ms: float) -> str:
    if ms < 1:
        return f"{ms * 1000:.1f} µs"
    elif ms < 100:
        return f"{ms:.2f} ms"
    else:
        return f"{ms:.0f} ms"


def fmt_mem(kb: float) -> str:
    if kb >= 1024:
        return f"{kb / 1024:.1f} MB"
    return f"{kb:.0f} KB"


def ratio(val: float, ref: float) -> str:
    if not ref:
        return "—"
    return f"×{val / ref:.1f}"


def print_table(label: str, html: str, results: dict, runs: int) -> None:
    kb = len(html.encode()) / 1024
    print(f"\n{'=' * 84}")
    print(f"  {label}  ({kb:.0f} KB input, {runs} runs)")
    print(f"{'=' * 84}")
    print(
        f"  {'Library':<22}"
        f" {'Parse':>9} {'vs':>5}"
        f"  {'Scrape':>9} {'vs':>5}"
        f"  {'Mem (parse)':>11} {'vs':>5}"
    )
    print(
        f"  {'-'*22}"
        f" {'-'*9} {'-'*5}"
        f"  {'-'*9} {'-'*5}"
        f"  {'-'*11} {'-'*5}"
    )

    ref = results.get("foxyhtml")
    ref_parse  = ref["parse"]  if ref and "_error" not in ref else None
    ref_scrape = ref["scrape"] if ref and "_error" not in ref else None
    ref_mem    = ref["mem_kb"] if ref and "_error" not in ref else None

    for lib_name, _, _ in LIB_FACTORIES:
        t = results.get(lib_name)
        if t is None:
            print(f"  {lib_name:<22}  (not installed)")
            continue
        if "_error" in t:
            print(f"  {lib_name:<22}  ERROR: {t['_error']}")
            continue
        print(
            f"  {lib_name:<22}"
            f" {fmt_time(t['parse']):>9} {ratio(t['parse'],  ref_parse):>5}"
            f"  {fmt_time(t['scrape']):>9} {ratio(t['scrape'], ref_scrape):>5}"
            f"  {fmt_mem(t['mem_kb']):>11} {ratio(t['mem_kb'],  ref_mem):>5}"
        )
    print()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark FoxyHTML vs popular HTML parsing libraries"
    )
    parser.add_argument(
        "--size", choices=["small", "medium", "large", "wikipedia", "all"],
        default="all", help="HTML fixture to benchmark (default: all)",
    )
    parser.add_argument(
        "--runs", type=int, default=200,
        help="Repetitions per operation (default: 200)",
    )
    args = parser.parse_args()

    print("\nDetected libraries:")
    for lib, _, available in LIB_FACTORIES:
        print(f"  {'✓' if available else '✗'} {lib}")

    if any(not av for _, _, av in LIB_FACTORIES):
        print(f"\n  Install missing libraries: pip install -e \".[benchmark]\"")

    if not LIBS["foxyhtml"]:
        print("\nERROR: foxyhtml is not installed. Run: pip install -e .", file=sys.stderr)
        sys.exit(1)

    import tempfile

    small_html  = load_html("small")
    medium_html = load_html("medium")
    large_html  = make_large(medium_html, factor=10)

    # Write generated fixtures to temp files so the memory worker can read them
    _tmp_large = tempfile.NamedTemporaryFile(
        suffix=".html", delete=False, mode="w", encoding="utf-8"
    )
    _tmp_large.write(large_html)
    _tmp_large.flush()
    large_path = Path(_tmp_large.name)

    SIZES: dict[str, tuple] = {
        "small":  (small_html,  FIXTURES_DIR / "small.html",  ARTICLE_SCRAPES, "SMALL   — synthetic article HTML"),
        "medium": (medium_html, FIXTURES_DIR / "medium.html", ARTICLE_SCRAPES, "MEDIUM  — synthetic article HTML"),
        "large":  (large_html,  large_path,                   ARTICLE_SCRAPES, "LARGE   — synthetic article HTML"),
    }

    if args.size in ("wikipedia", "all"):
        wiki_html = load_html("wikipedia_actor")
        SIZES["wikipedia"] = (wiki_html, FIXTURES_DIR / "wikipedia_actor.html", ACTOR_SCRAPES, "WIKIPEDIA — Charlie Chaplin (CC-BY-SA)")

    selected = list(SIZES.keys()) if args.size == "all" else [args.size]

    print(f"\nScenario: parse once → scrape with queries + subqueries.")
    print(f"  article : metadata, sections (h2/p/li), post cards, nav links")
    print(f"  actor   : infobox th/td rows, h2 sections, wikitable rows, categories")
    print(f"  memory  : RSS delta in an isolated subprocess (captures C heap)")
    print(f"\nRunning {args.runs} repetitions (Wikipedia: {max(20, args.runs // 10)})...\n")

    try:
        for size_key in selected:
            html, html_path, scrape_map, label = SIZES[size_key]
            runs = args.runs if size_key != "wikipedia" else max(20, args.runs // 10)
            results = run_benchmarks(html, html_path, scrape_map, runs)
            print_table(label, html, results, runs)
    finally:
        large_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()

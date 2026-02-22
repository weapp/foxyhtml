# Benchmarks

FoxyHTML is compared against the most popular Python HTML parsing libraries
in a **realistic usage scenario**: parse once, then run multiple queries and subqueries
on the same document.

## Libraries

| Library | Implementation | Notes |
|---|---|---|
| **foxyhtml** | Pure Python | Zero external dependencies |
| **bs4 + html.parser** | Pure Python | BeautifulSoup with stdlib parser |
| **bs4 + lxml** | C (libxml2) | BeautifulSoup with lxml backend |
| **lxml.html** | C (libxml2) | lxml directly, without bs4 |
| **selectolax** | C (Lexbor) | Modern, very fast parser |

## Methodology

Three metrics are measured per library:

- **Parse** — tokenise raw HTML and build the internal representation; average of N runs
- **Scrape** — extraction pipeline (queries + subqueries) on the pre-parsed document; average of N runs
- **Mem (parse)** — RSS delta measured in an **isolated subprocess** via `psutil`,
  so C-level heap from lxml and selectolax is captured alongside Python objects

Two scenarios:

**Article** (synthetic HTML, 1 KB / 25 KB / 248 KB)
Extracts title, date, author, tags; iterates sections with subqueries for headings,
paragraphs and list items; collects related post cards; gathers nav links.

**Actor profile** ([Charlie Chaplin — Wikipedia](https://en.wikipedia.org/wiki/Charlie_Chaplin), CC-BY-SA, ~1.4 MB)
Simulates scraping a real-world page with a lot of noise: ~38 000 nodes to search
through in order to find the infobox (th/td rows with name, birth, occupation…),
section headings, award and filmography wikitables, and page categories.

```bash
pip install -e ".[benchmark]"
python benchmarks/download_fixtures.py   # download Wikipedia fixture (~1.4 MB)
python benchmarks/bench.py
```

---

## Results

!!! note "Memory on small fixtures"
    For the 1 KB and 25 KB fixtures, the RSS delta is dominated by the cost of
    importing the library into a fresh subprocess (~5–14 MB), not by parsing itself.
    Memory figures are only meaningful for the 248 KB and Wikipedia fixtures.

### Small — 1 KB

| Library | Parse | vs | Scrape | vs |
|---|---|---|---|---|
| **foxyhtml** | 154 µs | ×1.0 | 172 µs | ×1.0 |
| bs4 + html.parser | 360 µs | ×2.3 | 225 µs | ×1.3 |
| bs4 + lxml | 291 µs | ×1.9 | 226 µs | ×1.3 |
| lxml.html | 21 µs | ×0.1 | 85 µs | ×0.5 |
| selectolax | 18 µs | ×0.1 | 50 µs | ×0.3 |

### Medium — 25 KB

| Library | Parse | vs | Scrape | vs |
|---|---|---|---|---|
| **foxyhtml** | 1.98 ms | ×1.0 | 1.78 ms | ×1.0 |
| bs4 + html.parser | 4.10 ms | ×2.1 | 1.60 ms | **×0.9** |
| bs4 + lxml | 3.24 ms | ×1.6 | 1.61 ms | **×0.9** |
| lxml.html | 249 µs | ×0.1 | 731 µs | ×0.4 |
| selectolax | 128 µs | ×0.1 | 201 µs | ×0.1 |

### Large — 248 KB (synthetic)

| Library | Parse | vs | Scrape | vs | Mem (parse) | vs |
|---|---|---|---|---|---|---|
| **foxyhtml** | 19.8 ms | ×1.0 | 17.6 ms | ×1.0 | **4.9 MB** | ×1.0 |
| bs4 + html.parser | 41.5 ms | ×2.1 | 15.2 ms | **×0.9** | 17.6 MB | ×3.6 |
| bs4 + lxml | 31.4 ms | ×1.6 | 15.4 ms | **×0.9** | 17.7 MB | ×3.6 |
| lxml.html | 2.64 ms | ×0.1 | 7.05 ms | ×0.4 | 9.0 MB | ×1.8 |
| selectolax | 1.29 ms | ×0.1 | 1.91 ms | ×0.1 | 9.1 MB | ×1.8 |

### Wikipedia — 1.4 MB (real-world, noisy)

| Library | Parse | vs | Scrape | vs | Mem (parse) | vs |
|---|---|---|---|---|---|---|
| **foxyhtml** | 148 ms | ×1.0 | 22.5 ms | ×1.0 | **16.9 MB** | ×1.0 |
| bs4 + html.parser | 144 ms | ×1.0 | 28.0 ms | ×1.2 | 29.4 MB | ×1.7 |
| bs4 + lxml | 108 ms | ×0.7 | 27.5 ms | ×1.2 | 30.9 MB | ×1.8 |
| lxml.html | 15.4 ms | ×0.1 | 4.75 ms | ×0.2 | 19.4 MB | ×1.1 |
| selectolax | 5.39 ms | ×0.0 | 1.01 ms | ×0.0 | 20.9 MB | ×1.2 |

---

## Reading the results

### Speed

FoxyHTML is **~2× faster than BeautifulSoup** at parse across all sizes.
lxml and selectolax are 8–16× faster thanks to their C extensions.

On the real-world Wikipedia page FoxyHTML's **scrape is ×1.2 faster than
BeautifulSoup** (22 ms vs 28–28 ms). Searching through 38 000 noisy nodes for a
handful of infobox rows and table cells favours FoxyHTML's flat-list linear scan
over bs4's tree traversal.

!!! note "Why FoxyHTML is efficient in noisy documents"
    FoxyHTML stores all tokens in a flat list. `isearch()` makes a single linear
    pass looking for the matching tag and class, with no tree allocation or pointer
    chasing. On pages where useful data is sparse relative to total size, this
    cache-friendly scan outperforms tree-based lookup.

### Memory

The RSS figures below show the real heap cost — including C-level allocations
from lxml and selectolax that `tracemalloc` would miss.

On the **248 KB** document, FoxyHTML is the **most memory-efficient** option:

- **FoxyHTML: 4.9 MB** — flat list of Python namedtuples, no tree overhead
- lxml: 9.0 MB — efficient C tree, but still 1.8× more than foxyhtml
- selectolax: 9.1 MB — similar to lxml
- BeautifulSoup: 17.6 MB — DOM tree plus bs4's Python wrapper layer (3.6×)

On the **1.4 MB Wikipedia** page the same pattern holds at larger scale:

- **FoxyHTML: 16.9 MB** — lowest footprint
- lxml: 19.4 MB (×1.1) — C tree is compact despite the document size
- selectolax: 20.9 MB (×1.2)
- BeautifulSoup: 29–31 MB (×1.7–1.8) — nearly double foxyhtml

FoxyHTML's flat namedtuple list turns out to be more memory-compact than a
linked DOM tree for the same HTML content, at the cost of slower queries on
heavily nested structure.

---

## When to use FoxyHTML

| Use case | Recommendation |
|---|---|
| Millions of pages per hour | **selectolax** or **lxml** |
| XPath / XSLT | **lxml** |
| Heavily malformed HTML | **BeautifulSoup** |
| Large noisy documents, targeted queries | **FoxyHTML** |
| Memory-constrained environments | **FoxyHTML** |
| Zero external dependencies | **FoxyHTML** |
| jQuery-like expressive API | **FoxyHTML** |

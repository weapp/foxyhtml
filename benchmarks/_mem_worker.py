#!/usr/bin/env python3
"""
Isolated subprocess worker for RSS memory measurement.

Called by bench.py as:
    python benchmarks/_mem_worker.py <lib_key> <html_path>

Prints a single float: RSS delta in KB consumed by parsing <html_path>
with the requested library.

Isolation guarantees that each measurement starts from a clean heap,
so C-level allocations from lxml and selectolax are captured correctly.
"""
import gc
import json
import os
import sys

# Allow importing foxyhtml from a dev install
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import psutil

LIB_KEY  = sys.argv[1]
HTML_PATH = sys.argv[2]

with open(HTML_PATH, encoding="utf-8") as f:
    html = f.read()

proc = psutil.Process(os.getpid())

gc.collect()
gc.collect()
before = proc.memory_info().rss

if LIB_KEY == "foxyhtml":
    from foxyhtml import FoxyHtml
    result = FoxyHtml(html)

elif LIB_KEY == "bs4_html_parser":
    from bs4 import BeautifulSoup
    result = BeautifulSoup(html, "html.parser")

elif LIB_KEY == "bs4_lxml":
    from bs4 import BeautifulSoup
    result = BeautifulSoup(html, "lxml")

elif LIB_KEY == "lxml":
    from lxml import html as lxml_html
    result = lxml_html.fromstring(html)

elif LIB_KEY == "selectolax":
    from selectolax.parser import HTMLParser
    result = HTMLParser(html)

else:
    sys.exit(f"Unknown library key: {LIB_KEY}")

after = proc.memory_info().rss

print(json.dumps({"rss_kb": (after - before) / 1024}))

# Getting Started

## Installation

```bash
pip install foxyhtml
```

To install development tools (pytest, coverage):

```bash
pip install foxyhtml[dev]
```

## Parsing HTML

`FoxyHtml` accepts three input types:

### String

```python
from foxyhtml import FoxyHtml

doc = FoxyHtml("<p>Hello <b>world</b></p>")
```

### Bytes

```python
doc = FoxyHtml(b"<p>Hello</p>")   # decoded as UTF-8
```

### File-like object

```python
with open("page.html", "rb") as f:
    doc = FoxyHtml(f)
```

You can also pass a URL response directly — any object with a `.read()` method works.

## First complete example

```python
from foxyhtml import FoxyHtml

html = """
<html>
  <body>
    <nav id="menu">
      <ul>
        <li class="active"><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </nav>
    <main>
      <h1>Welcome</h1>
      <p>FoxyHTML makes scraping easy.</p>
    </main>
  </body>
</html>
"""

doc = FoxyHtml(html)

# Find all links
links = doc.search("a")
for link in links:
    print(link.attr("href"), link.joinedtexts())
# /        Home
# /about   About
# /contact Contact

# Get only the active item
active = doc.select("li.active a")
print(active.joinedtexts())  # "Home"

# Get the heading text
h1 = doc.select("h1")
print(h1.joinedtexts())  # "Welcome"
```

## What you get

- `FoxyHtml` — a `list` of `Node` tokens representing the parsed document
- `search()` — returns a `CollectionFoxyHtml` (list of matching `FoxyHtml` subtrees)
- `select(css)` — CSS selector interface, returns one item or a collection
- `attr(name)` — reads an HTML attribute from the first node
- `joinedtexts()` — extracts all text content as a single string

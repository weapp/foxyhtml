FoxyHTML
========

A lightweight HTML parser with a jQuery-like API for Python 3.

## Installation

```bash
pip install foxyhtml
```

Or in editable mode from source:

```bash
pip install -e .
```

## Usage

```python
from foxyhtml import FoxyHtml

html = """
<html>
  <body>
    <ul class="menu">
      <li>Item 1</li>
      <li>Item 2</li>
      <li>Item 3</li>
    </ul>
    <div id="main">
      <p class="intro">Hello world</p>
      <img src="photo.jpg" alt="A photo" />
    </div>
  </body>
</html>
"""

parsed = FoxyHtml(html)

# Search by tag name
items = parsed.search(tagname="li")
for item in items:
    print(item.joinedtexts())

# Search by CSS class
intro = parsed.search(cls="intro")
print(intro[0].joinedtexts())  # 'Hello world'

# Search by id
main = parsed.search(id="main")

# CSS selector shorthand
items = parsed.select("ul.menu li")

# Get attribute value
imgs = parsed.search(tagname="img")
print(imgs[0].attr("src"))  # 'photo.jpg'

# Rebuild HTML from nodes
print(parsed.search(tagname="ul")[0].rebuild())

# foxycss: indented selector rules
results = parsed.foxycss("""
.menu
    li
""")

# Collect all text nodes
texts = parsed.search(tagname="p")[0].texts()
```

## Documentation

The docs site is built with [Zensical](https://zensical.org).

```bash
# Install dev dependencies (includes zensical)
pip install -e ".[dev]"

# Local preview
zensical serve

# Build static site to ./site/
zensical build
```

## API

### `FoxyHtml(html)`

Parses an HTML string (or bytes, or file-like object). Returns a list-like object of nodes.

| Method | Description |
|--------|-------------|
| `search(tagname=None, id=None, cls=None)` | Flat search, returns `CollectionFoxyHtml` |
| `isearch(...)` | Generator that yields `FoxyHtml` slices per matched element |
| `select(css)` | CSS selector (tag, `.class`, `#id`, `:first`, `:last`, `:even`, `:odd`) |
| `foxycss(css)` | Indented CSS rules with optional `@` transforms |
| `rebuild()` | Reconstruct HTML string from nodes |
| `texts()` | List of raw text content strings |
| `joinedtexts()` | All text joined and whitespace-normalised |
| `attr(name)` | Attribute value of the first node |
| `clean(...)` | Strip tags to a safe subset |

### `CollectionFoxyHtml`

Returned by `search()`. Supports `attr()`, `texts()`, `joinedtexts()`, `search()`, `select()`.

## foxycss `@` operator

Apply Python transformations to matched results. The `@` is followed by a method call on the matched collection:

```python
# Extract joined text from each matched element
parsed.foxycss("li@.joinedtexts()")  # ["Item 1", "Item 2", "Item 3"]

# Rebuild HTML of each matched element
parsed.foxycss("li@.rebuild()")
```

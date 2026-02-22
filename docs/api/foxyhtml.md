# FoxyHtml API

`FoxyHtml` inherits from `list`. Each element is a [`Node`](node.md).

## Constructor

```python
FoxyHtml(html=None)
```

| Argument | Type | Description |
|----------|------|-------------|
| `html` | `str`, `bytes`, file-like, or `None` | Source to parse. `None` creates an empty instance. |

```python
from foxyhtml import FoxyHtml

doc = FoxyHtml("<p>Hello</p>")         # from string
doc = FoxyHtml(b"<p>Hello</p>")        # from bytes (UTF-8)
doc = FoxyHtml(open("page.html"))      # from file-like
doc = FoxyHtml()                       # empty
```

## Search methods

### `search(tagname=None, id=None, cls=None, fun=None)`

Flat scan. Returns a `CollectionFoxyHtml` containing one `FoxyHtml` subtree per match.

| Parameter | Type | Description |
|-----------|------|-------------|
| `tagname` | `str` | Match by tag name (case-insensitive) |
| `id` | `str` | Match by `id` attribute |
| `cls` | `str` | Match by CSS class (single class name) |
| `fun` | `callable` | Custom filter — receives a `Node`, return truthy to include |

```python
doc.search("li")               # all <li> elements
doc.search(cls="active")       # elements with class="active"
doc.search("a", id="logo")     # <a id="logo">
doc.search(fun=lambda n: n.attr("href"))  # any tag with href
```

### `isearch(tagname=None, id=None, cls=None, fun=None)`

Generator version of `search()`. Yields one `FoxyHtml` per match. Tracks nesting via a depth counter so each yielded slice includes the full subtree (opening tag through closing tag).

```python
for item in doc.isearch("li"):
    print(item.joinedtexts())
```

### `select(css)`

CSS selector interface. Parses `css` with [`CssSelector`](selectors.md) and calls `_select()`.

```python
doc.select("ul li")          # descendant selector
doc.select("li.active")      # tag + class
doc.select("li:first")       # pseudo-class
```

Returns a `FoxyHtml` subtree or a `CollectionFoxyHtml`. See [CSS Selectors guide](../guides/css-selectors.md).

## Text and attribute methods

### `attr(name)`

Returns the value of attribute `name` from the **first node** in the list.

```python
link = doc.select("a")
link.attr("href")   # "/path/to/page"
```

### `texts()`

Returns a `list[str]` of all text-node contents (no whitespace collapsing).

```python
doc.select("p").texts()   # ["\n  Hello ", " world\n"]
```

### `joinedtexts()`

Joins all text nodes, collapses whitespace, strips leading/trailing spaces.

```python
doc.select("p").joinedtexts()   # "Hello world"
```

### `rebuild()`

Reconstructs the original HTML string from the token list.

```python
doc.select("nav").rebuild()   # '<nav id="menu">...</nav>'
```

## Transform methods

### `clean(translate_table={}, allow=['alt','src','href','title'])`

Returns a new `FoxyHtml` with all tags stripped down to their name plus the listed allowed attributes. See [HTML Sanitization guide](../guides/clean.md).

```python
safe = doc.clean()
safe = doc.clean(allow=["src", "alt"])
safe = doc.clean(translate_table={"b": "strong"})
```

### `foxycss(css)`

Applies indented `FoxyCss` rules and returns a structured result. See [FoxyCss guide](../guides/foxycss.md).

```python
result = doc.foxycss("""
ul
    li
        a@.attr('href')
""")
```

## id()

Returns the `id` attribute of the first node.

```python
doc.select("nav").id()   # "menu"
```

---

# CollectionFoxyHtml API

`CollectionFoxyHtml` wraps the results of `search()` — it holds multiple `FoxyHtml` subtrees. Inherits from `UserList`.

## Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `attr(name)` | `list[str \| None]` | Attribute `name` from each element |
| `search(*args, **kws)` | `CollectionFoxyHtml` | Runs `search()` on every element, flattens results |
| `select(css)` | `CollectionFoxyHtml` | Runs `select()` on every element |
| `texts()` | `list[list[str]]` | Text nodes from each element |
| `joinedtexts()` | `list[str]` | Joined text from each element |

```python
items = doc.search("li")

items.joinedtexts()          # ["One", "Two", "Three"]
items.attr("class")          # ["active", None, None]
items.search("a").attr("href")  # ["/", "/about", "/contact"]
```

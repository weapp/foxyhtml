# CSS Selectors

The `select(css)` method on `FoxyHtml` and `CollectionFoxyHtml` provides a CSS selector interface backed by [`CssSelector`](../api/selectors.md).

## Basic selectors

### Tag name

```python
doc.select("p")       # all <p> elements
doc.select("h1")      # all <h1> elements
doc.select("table")   # all <table> elements
```

### Class

```python
doc.select(".active")          # any tag with class="active"
doc.select(".nav-item")        # class with hyphen
```

### ID

```python
doc.select("#main")     # tag with id="main"
doc.select("#sidebar")
```

### Combining tag, class, and ID

```python
doc.select("li.active")         # <li class="active">
doc.select("a#logo")            # <a id="logo">
doc.select("div.card#featured") # <div class="card" id="featured">
```

---

## Descendant selector (space-separated)

A space between tokens means "search inside the previous result". Each token applies `search()` on the collection returned by the previous token.

```python
doc.select("ul li")          # <li> inside any <ul>
doc.select("nav ul li a")    # <a> inside <li> inside <ul> inside <nav>
doc.select("div.card p")     # <p> inside any <div class="card">
```

Note: this is a **descendant** selector (any depth), not a direct child selector. FoxyHTML does not support `>` (direct child).

---

## Pseudo-classes

Pseudo-classes filter the collection returned by the preceding selector token.

| Pseudo-class | Result |
|--------------|--------|
| `:first` | First element only (`r[0]`) |
| `:last` | Last element only (`r[-1]`) |
| `:even` | Elements at even indices: 0, 2, 4… |
| `:odd` | Elements at odd indices: 1, 3, 5… |

```python
doc.select("li:first")    # first <li>
doc.select("li:last")     # last <li>
doc.select("li:even")     # 1st, 3rd, 5th <li>
doc.select("li:odd")      # 2nd, 4th, 6th <li>
```

Pseudo-classes can be combined with tag, class, or ID:

```python
doc.select("li.item:first")   # first <li class="item">
doc.select("tr:odd")          # odd table rows (zebra stripe)
```

### Return type with pseudo-classes

- Without `:first` or `:last` → `CollectionFoxyHtml`
- With `:first` or `:last` → single `FoxyHtml` (or `None` if no match)
- With `:even` or `:odd` → `CollectionFoxyHtml` (may be empty)

---

## Practical examples

```python
html = """
<table>
  <tr><th>Name</th><th>Score</th></tr>
  <tr><td>Alice</td><td>95</td></tr>
  <tr><td>Bob</td><td>87</td></tr>
  <tr><td>Carol</td><td>92</td></tr>
</table>
"""
doc = FoxyHtml(html)

# All data rows (skip header)
data_rows = doc.select("tr:odd")

# First row
header = doc.select("tr:first")
print(header.joinedtexts())   # "Name Score"

# Last row
last = doc.select("tr:last")
print(last.joinedtexts())     # "Carol 92"

# All cell values
cells = doc.select("td")
print(cells.joinedtexts())    # ["Alice", "95", "Bob", "87", "Carol", "92"]
```

---

## Limitations

- Only one class name per token (no `li.a.b`)
- No `>` direct child combinator
- No `+` adjacent sibling combinator
- No `[attr=value]` attribute selectors
- No `:nth-child()` or `:not()`

For more complex extraction patterns, use [`foxycss()`](foxycss.md).

# FoxyCss — Indented Rules

`foxycss()` is a powerful extraction DSL that uses **indentation** to express descendant relationships and the **`@` operator** to apply Python transformations to matched elements.

## Basic usage

```python
result = doc.foxycss(css_rules)
```

The `css_rules` string uses newlines and indentation (any consistent indent — spaces or tabs) to build a selector tree.

---

## Indented selector syntax

Each line is a CSS selector. Child selectors are indented under their parent. The result mirrors the indentation structure.

### Single selector → value

```python
result = doc.foxycss("h1")
# Returns: FoxyHtml for the <h1> element
```

### Parent → children → list of results

```python
result = doc.foxycss("""
ul
    li
""")
# Returns: [FoxyHtml, FoxyHtml, FoxyHtml, …]  — one per <li>
```

---

## The `@` operator

Appended to a selector with `@`, a Python expression is evaluated on the matched element. The matched element is available as `t`.

```python
result = doc.foxycss("h1@.joinedtexts()")
# Returns: "Welcome"  (the text inside <h1>)
```

Any method call or attribute access on `t` works:

```python
# Get href from all links
result = doc.foxycss("""
ul
    li
        a@.attr('href')
""")
# Returns: ["/", "/about", "/contact"]
```

### Common `@` expressions

| Expression | What it does |
|------------|-------------|
| `@.joinedtexts()` | Text content, whitespace collapsed |
| `@.texts()` | Raw text node list |
| `@.attr('href')` | Value of `href` attribute |
| `@.attr('src')` | Value of `src` attribute |
| `@.rebuild()` | Raw HTML of the element |
| `@.id()` | Value of `id` attribute |

---

## Dict output with named keys

Use a line ending in `:` as a **dict key**. Its indented children become the value.

```python
result = doc.foxycss("""
ul
    li
        name:
            span.name@.joinedtexts()
        url:
            a@.attr('href')
""")
# Returns: [{"name": "Alice", "url": "/alice"}, {"name": "Bob", "url": "/bob"}]
```

The `:` suffix marks a line as a key label. The next indented block provides the value.

---

## Practical example: scraping a link list

```python
from foxyhtml import FoxyHtml

html = """
<nav>
  <ul>
    <li><a href="/" class="active">Home</a></li>
    <li><a href="/docs">Docs</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>
"""

doc = FoxyHtml(html)

# Extract all link texts
texts = doc.foxycss("""
ul
    li
        a@.joinedtexts()
""")
print(texts)   # ["Home", "Docs", "About"]

# Extract hrefs
hrefs = doc.foxycss("""
ul
    li
        a@.attr('href')
""")
print(hrefs)   # ["/", "/docs", "/about"]

# Extract as list of dicts
links = doc.foxycss("""
ul
    li
        text:
            a@.joinedtexts()
        href:
            a@.attr('href')
""")
print(links)
# [{"text": "Home", "href": "/"}, {"text": "Docs", "href": "/docs"}, ...]
```

---

## Comparison with `select()`

| Feature | `select()` | `foxycss()` |
|---------|-----------|------------|
| Syntax | Single-line CSS string | Multi-line indented rules |
| Transformations | None | `@` operator |
| Output | `FoxyHtml` / `CollectionFoxyHtml` | List, dict, or scalar |
| Named keys | No | Yes (`:` suffix) |
| Best for | Simple element access | Structured data extraction |

---

## Notes

- The `@` expression receives the matched element as `t` and must be a valid Python expression suffix (e.g. `.attr('href')` → `t.attr('href')`).
- If the `@` expression contains another `@`, it is replaced with `t` internally.
- Empty results propagate as `None` through transformations.

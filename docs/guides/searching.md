# Searching

FoxyHTML provides two search methods: `search()` for flat collection results and `isearch()` for a streaming generator with full subtree access.

## `search()` — flat scan

```python
results = doc.search(tagname=None, id=None, cls=None, fun=None)
# Returns: CollectionFoxyHtml
```

`search()` iterates through all nodes, collects matches via `isearch()`, and returns them as a `CollectionFoxyHtml` — a list of `FoxyHtml` subtrees.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `tagname` | `str` | Match tag name (case-insensitive) |
| `id` | `str` | Match `id` attribute |
| `cls` | `str` | Match a single CSS class name |
| `fun` | `callable` | Custom filter — receives a `Node`, truthy = include |

All parameters are optional. Provided parameters are combined with AND logic.

### Examples

```python
# By tag
doc.search("a")

# By class
doc.search(cls="highlight")

# By id
doc.search(id="main-nav")

# Combined
doc.search("li", cls="active")

# Custom filter: any element with a data-* attribute
doc.search(fun=lambda n: n.attr("data-value"))
```

---

## `isearch()` — generator with nesting

```python
for subtree in doc.isearch(tagname=None, id=None, cls=None, fun=None):
    # subtree is a FoxyHtml from opening tag to closing tag
```

`isearch()` is a generator that yields one `FoxyHtml` per matching element. It uses a depth counter `y` to track nesting, so each yielded value is the **complete subtree** — including all children.

### How the depth counter works

```
<ul>          ← match: y=1, start collecting
  <li>        ← same tagname, y=2
    text
  </li>       ← same tagname, y=1
  <li>        ← same tagname, y=2
    text
  </li>       ← same tagname, y=1
</ul>         ← closing ul: y=0, yield subtree
```

Only **top-level** elements are yielded — nested elements of the same tag type are included inside the parent subtree, not yielded separately.

### Example: nested lists

```python
html = """
<ul>
  <li>Item 1</li>
  <li>Item 2
    <ul>
      <li>Nested</li>
    </ul>
  </li>
</ul>
"""
doc = FoxyHtml(html)

# search() returns 3 li elements (flat scan returns all)
print(len(doc.search("li")))  # 3

# isearch("ul") yields 1 (only top-level ul)
for ul in doc.isearch("ul"):
    print(ul.joinedtexts())  # "Item 1 Item 2 Nested"
```

---

## Side-by-side comparison

```python
html = "<div><p>First</p><p>Second</p></div>"
doc = FoxyHtml(html)

# search(): returns CollectionFoxyHtml, all at once
paragraphs = doc.search("p")
print(len(paragraphs))          # 2
print(paragraphs.joinedtexts()) # ["First", "Second"]

# isearch(): generator, use in a loop
for p in doc.isearch("p"):
    print(p.joinedtexts())
# First
# Second
```

Use `search()` when you want to chain calls (`.attr()`, `.joinedtexts()`, etc.). Use `isearch()` when processing large documents and you want to avoid building a large list in memory.

---

## Chaining searches

`CollectionFoxyHtml.search()` runs `search()` on each element and flattens the results:

```python
doc.search("ul").search("li").joinedtexts()
# All li elements inside any ul, joined texts as a list
```

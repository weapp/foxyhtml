# HTML Sanitization

`clean()` strips all attributes from HTML tags except a safe allowlist, producing sanitized output suitable for display in contexts where you cannot trust the original HTML.

## Basic usage

```python
from foxyhtml import FoxyHtml

html = """<a href="/page" onclick="evil()" style="color:red">Click me</a>"""
doc = FoxyHtml(html)

safe = doc.clean()
print(safe.rebuild())
# <a href="/page">Click me</a>
```

Only allowed attributes are preserved. All others (`onclick`, `style`, `data-*`, etc.) are dropped.

---

## Default allowed attributes

```python
allow = ['alt', 'src', 'href', 'title']
```

These four attributes are kept by default:

| Attribute | Typical use |
|-----------|-------------|
| `alt` | Image alternative text |
| `src` | Image, script, iframe source |
| `href` | Link destination |
| `title` | Tooltip text |

---

## Customising allowed attributes

Pass a custom `allow` list:

```python
# Keep only src and alt (useful for image-only contexts)
safe = doc.clean(allow=["src", "alt"])

# Keep more attributes
safe = doc.clean(allow=["href", "src", "alt", "title", "class", "id"])
```

---

## Renaming tags

Use `translate_table` to rename tag names as part of the clean operation:

```python
safe = doc.clean(translate_table={"b": "strong", "i": "em"})
```

Old presentational tags (`<b>`, `<i>`) become semantic equivalents (`<strong>`, `<em>`).

You can also remove tags by mapping them to an empty string, though that only renames the tag — the content is still included.

---

## How it works

`clean()` calls `Node.clean()` on every node in the list and returns a new `FoxyHtml`. Non-tag nodes (text, comments) pass through unchanged.

For each tag node, it:

1. Reads the tag name from `node.extra[0]`
2. Applies `translate_table` to (optionally) rename the tag
3. Reads each attribute in `allow` via `node.attr(name)`
4. Reconstructs a minimal tag string: `<tagname attr1="val1" attr2="val2">`

Self-closing tags are handled correctly:

```python
doc = FoxyHtml('<img src="/logo.png" width="200" height="50" />')
print(doc.clean().rebuild())
# <img src="/logo.png"/>
```

---

## Full example

```python
from foxyhtml import FoxyHtml

unsafe = """
<div class="user-content" style="background: red">
  <script>alert('xss')</script>
  <p onclick="steal()">Visit <a href="https://example.com" target="_blank">this site</a></p>
  <img src="/img/photo.jpg" width="300" onerror="evil()"/>
</div>
"""

doc = FoxyHtml(unsafe)
safe = doc.clean()
print(safe.rebuild())
```

Output:

```html
<div>
  <script></script>
  <p>Visit <a href="https://example.com">this site</a></p>
  <img src="/img/photo.jpg"/>
</div>
```

Note: `clean()` only strips attributes — it does **not** remove dangerous tags like `<script>`. For full XSS protection, combine with tag filtering or use a dedicated HTML sanitizer library.

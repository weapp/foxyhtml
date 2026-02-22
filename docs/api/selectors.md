# Selectors API

## CssSelector

`CssSelector` parses a CSS selector string into a list of `(kws, modifiers)` pairs, one per space-separated token.

```python
from foxyhtml.css import CssSelector

sel = CssSelector("ul li.active:first")
print(sel.parsed)
# [({'tagname': 'ul'}, []), ({'tagname': 'li', 'cls': 'active'}, ['first'])]
```

### Supported syntax

| Syntax | Example | Maps to |
|--------|---------|---------|
| Tag name | `li` | `tagname="li"` |
| Class | `.active` | `cls="active"` |
| ID | `#main` | `id="main"` |
| Pseudo-class | `:first` | modifier `"first"` |
| Combination | `li.active#foo` | `tagname`, `cls`, `id` together |
| Descendant | `ul li` (space) | chained `search()` calls |

### Pseudo-classes

| Pseudo-class | Behaviour |
|--------------|-----------|
| `:first` | Keeps only the first match (`r[0]`) |
| `:last` | Keeps only the last match (`r[-1]`) |
| `:even` | Keeps elements at even indices (`r[::2]`) |
| `:odd` | Keeps elements at odd indices (`r[1::2]`) |

```python
doc.select("li:even")   # 1st, 3rd, 5th… list items
doc.select("li:last")   # last list item only
```

### Limitations

- Only a single class name per selector token is supported.
- No attribute selectors (`[attr=value]`).
- No `:nth-child()` or other complex pseudo-classes.

---

## FoxyCss

`FoxyCss` is a higher-level selector language that uses **indentation** to express descendant relationships and the `@` operator to apply Python transformations.

```python
from foxyhtml.css import FoxyCss

result = FoxyCss("""
ul
    li
        a@.attr('href')
""").apply(doc)
```

See the [FoxyCss guide](../guides/foxycss.md) for full documentation and examples.

### Constructor

```python
FoxyCss(css: str)
```

Parses the multi-line indented CSS string and builds an internal tree.

### `apply(fhtml)`

Applies the rule tree to a `FoxyHtml` document and returns a structured result (list, dict, or scalar depending on the rules).

```python
FoxyCss(rules).apply(doc)
```

### Internal helper: `foxy_css(css, fhtml)`

Module-level convenience wrapper:

```python
from foxyhtml.css import foxy_css

result = foxy_css("ul li", doc)
```

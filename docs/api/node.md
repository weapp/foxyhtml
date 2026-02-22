# Node API

## TypeNode

`TypeNode` is a namedtuple used as an enum to identify the type of each token.

```python
from foxyhtml import TypeNode

TypeNode.tag        # opening tag:  <div class="x">
TypeNode.singletag  # self-closing: <img src="…"/> or <br>
TypeNode.closetag   # closing tag:  </div>
TypeNode.notag      # text content between tags
TypeNode.comment    # HTML comment: <!-- … -->
TypeNode.other      # any other character not matched
```

Each value is simply the field name string (e.g. `TypeNode.tag == "tag"`).

---

## Node

`Node` is a namedtuple with three fields. It extends `_Node` to add helper methods.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | `str` | One of the `TypeNode` values |
| `content` | `str` | The raw HTML text of this token |
| `extra` | `tuple \| None` | Parsed metadata (see below) |

### `extra` contents

| Node type | `extra` value |
|-----------|--------------|
| `tag` | `(tagname, id, cls_list)` |
| `singletag` | `(tagname, id, cls_list)` |
| `closetag` | `(tagname,)` |
| `notag`, `comment`, `other` | `None` |

```python
node = list(FoxyHtml("<div id='x' class='a b'>"))[0]
node.type     # "tag"
node.content  # '<div id=\'x\' class=\'a b\'>'
node.extra    # ('div', 'x', ['a', 'b'])
```

### Methods

#### `istag()`

Returns `True` if the node is an opening or self-closing tag.

```python
node.istag()   # True for <div>, <img/>, <br>
```

#### `isclosetag()`

Returns `True` if the node is a closing or self-closing tag.

```python
node.isclosetag()   # True for </div>, <img/>
```

Note: `singletag` nodes return `True` for **both** `istag()` and `isclosetag()`.

#### `tagname()`

Returns the tag name string, or `None` for non-tag nodes.

```python
node.tagname()   # "div", "a", "img", …
```

#### `id()`

Returns the `id` attribute value for opening tags, or `None`.

```python
node.id()   # "menu", "logo", …
```

#### `attr(name)`

Returns the value of attribute `name`, or `None` if not present. Works on any tag node.

```python
node.attr("href")   # "/about"
node.attr("class")  # "nav active"
```

#### `clean(translate_table={}, allow=['alt','src','href','title'])`

Returns a new `Node` with all attributes stripped except those in `allow`. Optionally renames tags via `translate_table`.

```python
clean_node = node.clean()
clean_node = node.clean(allow=["src", "alt"])
clean_node = node.clean(translate_table={"b": "strong", "i": "em"})
```

`notag` nodes are returned unchanged.

---

## Inspecting nodes directly

You can iterate over a `FoxyHtml` to inspect individual tokens:

```python
doc = FoxyHtml("<p class='intro'>Hello <b>world</b></p>")
for node in doc:
    print(node.type, repr(node.content))
# tag       '<p class=\'intro\'>'
# notag     'Hello '
# tag       '<b>'
# notag     'world'
# closetag  '</b>'
# closetag  '</p>'
```

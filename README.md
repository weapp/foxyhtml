FoxyHTML
========

A HTML Parser written in Python

## Example

```python
import urllib2
from pprint import pprint
html = urllib2.urlopen("http://www.thetimes.co.uk").read()
parsed = FoxyHtml(html)

print "Way 1:"
results = parsed.search(cls="nib-inner")
for result in results:
    pprint(
        [result.joinedtexts() for result in result.search(tagname="li")])

print "Way 2:"
pprint(
    [result.joinedtexts() for result in parsed.foxycss(".nib-inner li")])
```

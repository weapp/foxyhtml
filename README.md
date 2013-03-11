FoxyHTML
========

A HTML Parser written in Python

## Example

```python
import urllib2
from pprint import pprint
html = urllib2.urlopen("http://www.thetimes.co.uk").read()
parsed = FoxyHtml(html)

print
print "Example1"
print "Way 1:"
results = parsed.search(cls="nib-inner")
for result in results:
    pprint(
        [result.joinedtexts() for result in result.search(tagname="li")])

print
print "Way 2:"
pprint(
    [result.joinedtexts() for result in parsed.foxycss(".nib-inner li")])

print
print "Example2"
pprint([dict(zip(["title", "body"], fields))
        for bricks in parsed.search(cls="brick-mpu")
        for brick in bricks.search(cls="brick-sixth")
        for fields in [brick.search(cls="f-hc").joinedtexts()]
        if all(fields)
        ])

print
print "Example3"
pprint([{
        'title': titles[0],
        'subtitile': titles[1],
        'body': brick.search(tagname="p").joinedtexts()
        }
        for bricks in parsed.search(cls="brick-arts")
        for brick in bricks.search(cls="brick-sixth")
        for titles in brick.search(cls="f-hc").texts()
        ])

print
print "Example4"
bricks = parsed.search(cls="brick-arts")
pprint(bricks.search(tagname="img").attr("src"))
print

print
print "Example5"
brick = bricks.search(cls="brick-sixth")[0]

print brick
print

print brick.rebuild()
print

print brick.clean().rebuild()
print
```

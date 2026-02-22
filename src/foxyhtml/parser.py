# -*- coding: utf-8 -*-
import re
from collections import namedtuple, UserList
from foxyhtml.css import FoxyCss, CollectionCSS, CssSelector

re_html = re.compile("""(</[a-zA-Z]+[^>]*>)                 #closetag
                        |(<[a-zA-Z]+(?:[^/>]|/[^>])*/>)     #singletag
                        |(<[a-zA-Z]+[^>]*>)                 #tag
                        |([^<]+)                            #notag
                        |(<![^>]*>)                         #comment
                        |(.)                                #other
                        """, re.DOTALL | re.X)


re_tag = re.compile("<([a-zA-Z]+[0-9]*)", re.DOTALL)
re_tag_id = re.compile(r"""id=(("[^"]*")|('[^']*')|[^\s>]+)""", re.DOTALL)
re_tag_cls = re.compile(r"""class=(("[^"]*")|('[^']*')|[^\s>]+)""", re.DOTALL)
re_closetag = re.compile("</([a-zA-Z]+[0-9]*)", re.DOTALL)
re_spaces = re.compile(r"\s+")

singles = ['meta', 'img', 'link', 'input', 'area', 'base', 'col', 'br', 'hr']
allow = ['alt', 'src', 'href', 'title']
inlineTags = ['a', 'abbr', 'acronym', 'b', 'br', 'code', 'em', 'font', 'i',
              'img', 'ins', 'kbd', 'map', 'samp', 'small', 'span', 'strong',
              'sub', 'sup', 'textarea']


def re_attr(name):
    expr = r"""%s=(("[^"]*")|('[^']*')|[^\s>]+)"""
    return re.compile(expr % name, re.DOTALL | re.IGNORECASE)


def get_attr(name):
    if name not in get_attr.regexps:
        get_attr.regexps[name] = re_attr(name)
    return get_attr.regexps[name]
get_attr.regexps = {}

Type_node_attrs = 'tag singletag closetag notag comment other'
TypeNode = namedtuple('TypeNode', Type_node_attrs)\
    ._make(Type_node_attrs.split(' '))
_Node = namedtuple('Node', 'type content extra')


class CollectionFoxyHtml(UserList, CollectionCSS):
    def attr(self, attr):
        return [node.attr(attr) for node in self if node]

    def search(self, *args, **kws):
        return CollectionFoxyHtml([t for node in self
                                   for t in node.search(*args, **kws)])

    def texts(self):
        return [node.texts() for node in self]

    def joinedtexts(self):
        return [node.joinedtexts() for node in self if node]

    def select(self, css):
        t = CollectionFoxyHtml([node.select(css) for node in self])
        return t
        if len(self) == 1:
            return t[0]
        else:
            return t


class Node(_Node):
    def attr(self, attr):
        tag = self.content
        value = get_attr(attr).search(tag)
        value = value and value.group(1).strip('"').strip("'")
        return value

    def istag(self):
        return self.type in (TypeNode.tag, TypeNode.singletag)

    def isclosetag(self):
        return self.type in (TypeNode.closetag, TypeNode.singletag)

    def tagname(self):
        if self.istag() or self.isclosetag():
            return self.extra[0]

    def id(self):
        if self.istag():
            return self.extra[1]

    def clean(self, translate_table={}, allow=allow):
        if self.type in ("closetag", "tag", "singletag"):
            name = self.extra[0].lower()
            slash1 = "" if self.istag() else "/"
            slash2 = "/" if self.istag() and self.isclosetag() else ""
            for attr_name in allow:
                attr = self.attr(attr_name)
                if attr:
                    slash2 = " %s=\"%s\"%s" % (attr_name, attr, slash2)
            name = translate_table.get(name, name)
            content = "<%s%s%s>" % (slash1, name, slash2)
            self = type(self)(self.type, content, (name, None, []))
        return self


def _parseNode(closetag, singletag, tag, notag, comment, other):
    if tag:
        tagname = re_tag.search(tag).group(1)
        id = re_tag_id.search(tag)
        id = id and id.group(1).strip('"').strip("'")
        cls = re_tag_cls.search(tag)
        cls = cls and cls.group(1).strip('"').strip("'").split() or []
        if tagname in singles:
            return Node(TypeNode.singletag, tag, (tagname, id, cls))
        else:
            return Node(TypeNode.tag, tag, (tagname, id, cls))
    elif singletag:
        tagname = re_tag.search(singletag).group(1)
        id = re_tag_id.search(singletag)
        id = id and id.group(1).strip('"').strip("'")
        cls = re_tag_cls.search(singletag)
        cls = cls and cls.group(1).strip('"').strip("'").split() or []
        return Node(TypeNode.singletag, singletag, (tagname, id, cls))
    elif closetag:
        closetagname = re_closetag.search(closetag).group(1)
        return Node(TypeNode.closetag, closetag, (closetagname,))
    elif notag:
        return Node(TypeNode.notag, notag, None)
    elif comment:
        return Node(TypeNode.notag, comment, None)
    elif other:
        return Node(TypeNode.notag, other, None)


class FoxyHtml(list):
    def __init__(self, html=None):
        if html is None:
            list.__init__(self)
        elif isinstance(html, str):
            list.__init__(
                self, [_parseNode(*node) for node in re_html.findall(html)])
        elif isinstance(html, bytes):
            FoxyHtml.__init__(self, html.decode('utf-8'))
        elif hasattr(html, 'read'):
            FoxyHtml.__init__(self, html.read())
        else:
            list.__init__(self, list(html))

    def _select(self, sel):
        r = self
        for kws, modif in sel.parsed:
            r = r.search(**kws)
            for m in modif:
                if m == "first":
                    r = r[0] if r else None
                elif m == "even":
                    r = CollectionFoxyHtml(r[::2])
                elif m == "odd":
                    r = CollectionFoxyHtml(r[1::2])
                elif m == "last":
                    r = r[-1] if r else None
        return r

    def select(self, item):
        sel = CssSelector(item)
        return self._select(sel)

    def clean(self, translate_table={}, allow=allow):
        return FoxyHtml(node.clean(translate_table, allow) for node in self)

    def foxycss(self, css):
        return FoxyCss(css).apply(self)

    def isearch(self, tagname=None, id=None, cls=None, fun=None, p=False):
        tagname = tagname and tagname.lower()
        y = 0
        r = []
        ctagname = None
        for node in self:
            if not y and node.istag() and \
                (not tagname or node.extra[0] == tagname) and \
                (not id or node.extra[1] == id) and \
                (not cls or cls in node.extra[2]) and \
                    (not fun or fun(node)):
                ctagname = node.extra[0]
                y += 1
            elif y and node.istag() and node.extra[0] == ctagname:
                y += 1

            if y > 0:
                r.append(node)

            if y > 0 and node.isclosetag() and node.extra[0] == ctagname:
                y -= 1

            if r and not y:
                yield FoxyHtml(r)
                r = []
                ctagname = None

    def search(self, tagname=None, id=None, cls=None, **kws):
        return CollectionFoxyHtml(self.isearch(tagname, id, cls, **kws))

    def rebuild(self):
        return "".join(node.content for node in self)

    def texts(self):
        return [node.content for node in self if node.type == TypeNode.notag]

    def joinedtexts(self):
        text = "".join(
            self.texts()).replace("\r", ' ').replace("\n", ' ').strip()
        return re_spaces.sub(' ', text)

    def __repr__(self):
        return repr(self.rebuild())

    def attr(self, name):
        return self[0].attr(name)

    def id(self):
        return self[0].id()

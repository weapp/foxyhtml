# -*- coding: utf-8 -*-
import re
from collections import namedtuple
from UserList import UserList
from foxycss import FoxyCss, CollectionCSS, CssSelector

#(tag and re.search('<([a-zA-Z]+)', tag).group(1)) or (closetag and re.search('</([a-zA-Z]+)', closetag).group(1) or '').lower() )

re_html = re.compile("""(</[a-zA-Z]+[^>]*>)                 #closetag
                        |(<[a-zA-Z]+(?:[^/>]|/[^>])*/>)      #singletag
                        |(<[a-zA-Z]+[^>]*>)                 #tag
                        |([^<]+)                            #notag
                        |(<![^>]*>)                         #comment
                        |(.)                                #other
                        """, re.DOTALL | re.X)


re_tag = re.compile("<([a-zA-Z]+[0-9]*)", re.DOTALL)
re_tag_id = re.compile("""id=(("[^"]*")|('[^']*')|[^\s>]+)""", re.DOTALL)
re_tag_cls = re.compile("""class=(("[^"]*")|('[^']*')|[^\s>]+)""", re.DOTALL)
re_closetag = re.compile("</([a-zA-Z]+[0-9]*)", re.DOTALL)
re_spaces = re.compile("\s+")

def get_attr(name):
    if name not in get_attr.regexps:
        get_attr.regexps[name] = re.compile("""%s=(("[^"]*")|('[^']*')|[^\s>]+)""" % name, re.DOTALL | re.IGNORECASE)
    return get_attr.regexps[name]
get_attr.regexps = {}

TypeNode = namedtuple('TypeNode', 'tag singletag closetag notag comment other')._make('tag singletag closetag notag comment other'.split(' '))
_Node = namedtuple('Node', 'type content extra')

class CollectionFoxyHtml(UserList, CollectionCSS):
    def attr(self, attr):
        return CollectionFoxyHtml([value.attr(attr) for value in self if value])

    def search(self, *args, **kws):
        return CollectionFoxyHtml([t for elem in self for t in elem.search(*args, **kws)])
    
    def texts(self):
        return [elem.texts() for elem in self]
    
    def joinedtexts(self):
        return [elem.joinedtexts() for elem in self if elem]
    
    def select(self, css):
        t = CollectionFoxyHtml([elem.select(css) for elem in self])
        return t
        if len(self)==1:
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
            
    def clean(self, translate_table={}):
      if self.type in ("closetag", "tag"):
        #print self.extra[0], self.extra
        name = self.extra[0]
        slash1 = "" if self.istag() else "/"
        slash2 = " /" if self.istag() and self.isclosetag() else ""
        src = self.attr("src")
        if src:
          slash2 = " src=\"%s\"%s" % (src, slash2)
        href = self.attr("href")
        if href:
          slash2 = " href=\"%s\"%s" % (href, slash2)
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
        elif isinstance(html, basestring):
            if isinstance(html, unicode):
                pass
            else:
                if 'utf-8' in html:
                    html = unicode(html, 'utf-8')
            list.__init__(self, [_parseNode(*node) for node in re_html.findall(html)])
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
        '''
        r = self
        css = item.split(' ')
        for c in css:
            modif = []
            kws = {}
            for arg in re.findall("([a-zA-Z0-9]+)|\.([a-zA-Z0-9]+)|\#([a-zA-Z0-9]+)|\:([a-zA-Z0-9]+)", c):
                if arg[0]:
                    kws["tagname"] = arg[0]
                elif arg[1]:
                    kws["cls"] = arg[1]
                elif arg[2]:
                    kws["id"] = arg[2]
                elif arg[3]:
                    modif.append(arg[3])
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
        '''

    def clean(self, translate_table={}):
      return FoxyHtml((process(node, translate_table) for node in html))
    
    def foxycss(self, css):
        return FoxyCss(css).apply(self)

    def isearch(self, tagname=None, id=None, cls=None, fun=None, p=False):
        #p = True
        tagname = tagname and tagname.lower()
        y = 0
        r = []
        if p: print "***", tagname, id, cls, fun
        ctagname = None
        for node in self:#[1:-1]:
            if p: print node
            if p: print "...*...", y, node.istag() ,\
                node.istag()  and (not tagname or node.extra[0] == tagname) ,\
                node.istag()  and (not id or node.extra[1] == id) ,\
                node.istag()  and (not cls or cls in node.extra[2])
                
            #el orden de los if es importante para que devuelva el primer y el ultimo nodo
            if not y and node.istag() and \
                (not tagname or node.extra[0] == tagname) and \
                (not id or node.extra[1] == id) and \
                (not cls or cls in node.extra[2]) and \
                (not fun or fun(node)):
                # guardamos porque pudiera ser que el parametro tagname fuera None
                ctagname = node.extra[0]
                y += 1
                if p: print "++level", tagname
            elif y and node.istag() and node.extra[0] == ctagname:
                y += 1
                if p: print "++level"
            
            if y>0:
                r.append(node)
            
            
            if p: print "--level?", y, node.isclosetag(), node.extra
            if y>0 and node.isclosetag() and node.extra[0] == ctagname:
                y -= 1
                if p: print "--level"
            
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
        text = "".join(self.texts()).replace("\r",' ').replace("\n",' ').strip() 
        return re_spaces.sub( ' ', text)
    
    def __repr__(self):
        return repr(self.rebuild())
        
    def attr(self, name):
        return self[0].attr(name)

    def id(self):
        return self[0].id()

    
def main(html):
    import urllib2
    from pprint import pprint
    html = urllib2.urlopen("http://www.thetimes.co.uk").read()
    parsed = FoxyHtml(html)
    
    print "Way 1:"
    results = parsed.search(cls="nib-inner")
    for result in results:
        pprint([result.joinedtexts() for result in result.search(tagname="li")])
    
    print "Way 2:"
    pprint([result.joinedtexts() for result in parsed.foxycss(".nib-inner li")])
    


if __name__ == "__main__":
    main("")
import re
class CollectionCSS:
    pass

class CssSelector:
    def __init__(self, item):
        self.parsed = []
        css = item.split(' ')
        for c in css:
            modif = []
            kws = {}
            for arg in re.findall("([a-zA-Z0-9\-\_]+)|\.([a-zA-Z0-9\-\_]+)|\#([a-zA-Z0-9\-\_]+)|\:([a-zA-Z0-9\-\_]+)", c):
                if arg[0]:
                    kws["tagname"] = arg[0]
                elif arg[1]:
                    kws["cls"] = arg[1]
                elif arg[2]:
                    kws["id"] = arg[2]
                elif arg[3]:
                    modif.append(arg[3])
                self.parsed.append((kws, modif))
    
    def __str__(self):
        return str(self.parsed)
        
    def __repr__(self):
        return repr(self.parsed)
    
class FoxyCss:
    def __init__(self, css):
        self.tree = FoxyCss.proccess(
                        FoxyCss.tree(
                            [FoxyCss.parse_line(line) for line in
                                [line for line in 
                                    css.replace('\r', '\n').split('\n') if line.strip()
                                ]
                            ]
                        )
                    )

    def apply(self, fhtml):
        return FoxyCss._apply(self.tree, fhtml)

    @staticmethod
    def parse_line(line):
        stripped = line.lstrip()
        ident = (len(line) - len(stripped))# / 4
        stripped = stripped.rstrip()
        colon = stripped.endswith(':')
        if colon:
            stripped = stripped.rstrip(':')
        
        '''
        parentheses = stripped.endswith(')')
        if parentheses:
            stripped = stripped.rstrip(')')
            stripped, parentheses = stripped.rsplit('(', 1)
            stripped = stripped.strip()
        '''
        parentheses = '@' in stripped
        if parentheses:
            stripped, parentheses = stripped.split('@', 1)
            stripped = stripped.strip()
            parentheses = eval('lambda t:(t%s) if t is not None else None' % parentheses.replace('@', 't'))
            
        return ident, colon, stripped if colon else CssSelector(stripped), parentheses
        
    @staticmethod
    def tree(parsed_css):
        t = []
        while parsed_css:
            parent = parsed_css.pop(0)
            childs = []
            while parsed_css and parent[0] != parsed_css[0][0]:
                childs.append(parsed_css.pop(0))
            t.append((parent, FoxyCss.tree(childs)))
        return t

    @staticmethod
    def proccess(t):
        f = {}
        l = []
        for parent, childs in t:
            ident, iskey, tag, attr = parent
            if iskey:
                #print ident, tag, childs
                f[tag] = FoxyCss.proccess(childs)
            else:
                if childs:
                    l.append((tag, FoxyCss.proccess(childs)))
                else:
                    l.append((tag, attr))
        return f or l or None
    
    @staticmethod
    def _apply(tree, fhtml):
        r = None
        if isinstance(tree, dict):
            r = {k: FoxyCss._apply(v, fhtml) for k, v in tree.iteritems()}
        elif isinstance(tree, list):
            r = []
            for item in tree:
                t = fhtml._select(item[0])
                if isinstance(item, tuple) and isinstance(item[1], (list, dict)): #codigo con hijos
                    ks = item[1].keys()
                    if ks == ['$value', '$key'] or ks == ['$key', '$value']:
                        t = {(FoxyCss._apply(item[1]['$key'], it)):(FoxyCss._apply(item[1]['$value'], it)) for it in t}
                    else:
                        t = [FoxyCss._apply(item[1], it) for it in t] if isinstance(t, CollectionCSS) else FoxyCss._apply(item[1], t)
                elif item[1]: #codigo tras la arroba
                        #t = eval('(t%s) if t is not None else None' % item[1].replace('@', 't'))
                        t = item[1](t)
                r.append(t)
            if len(tree) == 1:
                r = r[0]
        else:
            print tree
            
        
        return r
    
    def __str__(self):
        return str(self.tree)
        
    def __repr__(self):
        return repr(self.tree)

    
def foxy_css(css, fhtml):
    return FoxyCss(css).apply(fhtml)
    
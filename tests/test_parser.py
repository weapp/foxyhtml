"""Tests for foxyhtml.parser — FoxyHtml, Node, CollectionFoxyHtml."""
import io
import pytest
from foxyhtml import FoxyHtml, CollectionFoxyHtml, Node, TypeNode


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_html():
    return FoxyHtml("""
        <div id="main" class="wrapper">
            <p class="intro">Hello world</p>
            <ul class="menu">
                <li>Item 1</li>
                <li>Item 2</li>
                <li class="active">Item 3</li>
            </ul>
            <img src="photo.jpg" alt="A photo" />
        </div>
    """)


@pytest.fixture
def nested_html():
    return FoxyHtml("""
        <div class="outer">
            <div class="inner">
                <span>Text</span>
            </div>
        </div>
    """)


# ---------------------------------------------------------------------------
# FoxyHtml construction
# ---------------------------------------------------------------------------

class TestFoxyHtmlConstruction:
    def test_from_string(self):
        parsed = FoxyHtml("<p>Hello</p>")
        assert len(parsed) > 0

    def test_from_bytes_utf8(self):
        parsed = FoxyHtml(b"<p>Hello</p>")
        assert len(parsed) > 0

    def test_from_bytes_with_unicode(self):
        parsed = FoxyHtml("<p>Ñoño</p>".encode("utf-8"))
        assert "Ñoño" in parsed.rebuild()

    def test_from_file_like(self):
        f = io.StringIO("<p>Hello</p>")
        parsed = FoxyHtml(f)
        assert len(parsed) > 0

    def test_from_none(self):
        parsed = FoxyHtml()
        assert list(parsed) == []

    def test_from_iterable(self, simple_html):
        nodes = list(simple_html)
        copy = FoxyHtml(nodes)
        assert copy.rebuild() == simple_html.rebuild()


# ---------------------------------------------------------------------------
# rebuild
# ---------------------------------------------------------------------------

class TestRebuild:
    def test_roundtrip(self):
        html = "<div><p>Hello</p></div>"
        assert FoxyHtml(html).rebuild() == html

    def test_rebuild_with_attributes(self):
        html = '<a href="http://example.com">link</a>'
        assert FoxyHtml(html).rebuild() == html

    def test_rebuild_self_closing(self):
        html = '<img src="x.jpg" />'
        assert FoxyHtml(html).rebuild() == html


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

class TestSearch:
    def test_search_by_tagname(self, simple_html):
        results = simple_html.search(tagname="li")
        assert len(results) == 3

    def test_search_by_cls(self, simple_html):
        results = simple_html.search(cls="intro")
        assert len(results) == 1

    def test_search_by_id(self, simple_html):
        results = simple_html.search(id="main")
        assert len(results) == 1

    def test_search_by_tagname_and_cls(self, simple_html):
        results = simple_html.search(tagname="li", cls="active")
        assert len(results) == 1

    def test_search_returns_collection(self, simple_html):
        assert isinstance(simple_html.search(tagname="li"), CollectionFoxyHtml)

    def test_search_no_match(self, simple_html):
        results = simple_html.search(tagname="table")
        assert len(results) == 0

    def test_search_content_integrity(self, simple_html):
        li = simple_html.search(tagname="li")
        assert li[0].joinedtexts() == "Item 1"
        assert li[1].joinedtexts() == "Item 2"
        assert li[2].joinedtexts() == "Item 3"


# ---------------------------------------------------------------------------
# texts / joinedtexts
# ---------------------------------------------------------------------------

class TestTexts:
    def test_texts_returns_list(self, simple_html):
        p = simple_html.search(cls="intro")
        texts = p[0].texts()
        assert isinstance(texts, list)
        assert "Hello world" in texts

    def test_joinedtexts_strips_whitespace(self):
        parsed = FoxyHtml("<p>  Hello   world  </p>")
        assert parsed.search(tagname="p")[0].joinedtexts() == "Hello world"

    def test_joinedtexts_collapses_newlines(self):
        parsed = FoxyHtml("<p>Line 1\nLine 2</p>")
        result = parsed.search(tagname="p")[0].joinedtexts()
        assert "\n" not in result
        assert "Line 1" in result
        assert "Line 2" in result


# ---------------------------------------------------------------------------
# attr
# ---------------------------------------------------------------------------

class TestAttr:
    def test_attr_double_quotes(self, simple_html):
        img = simple_html.search(tagname="img")
        assert img[0].attr("src") == "photo.jpg"

    def test_attr_alt(self, simple_html):
        img = simple_html.search(tagname="img")
        assert img[0].attr("alt") == "A photo"

    def test_attr_missing(self, simple_html):
        p = simple_html.search(tagname="p")
        assert p[0].attr("href") is None

    def test_attr_on_collection(self, simple_html):
        imgs = simple_html.search(tagname="img")
        srcs = imgs.attr("src")
        assert srcs == ["photo.jpg"]

    def test_attr_id(self, simple_html):
        div = simple_html.search(tagname="div")
        assert div[0].attr("id") == "main"


# ---------------------------------------------------------------------------
# select (CSS selectors)
# ---------------------------------------------------------------------------

class TestSelect:
    def test_select_by_tag(self, simple_html):
        result = simple_html.select("li")
        assert len(result) == 3

    def test_select_by_class(self, simple_html):
        result = simple_html.select(".intro")
        assert result[0].joinedtexts() == "Hello world"

    def test_select_by_id(self, simple_html):
        result = simple_html.select("#main")
        assert len(result) == 1

    def test_select_descendant(self, simple_html):
        result = simple_html.select("ul li")
        assert len(result) == 3

    def test_select_first(self, simple_html):
        result = simple_html.select("li:first")
        assert result.joinedtexts() == "Item 1"

    def test_select_last(self, simple_html):
        result = simple_html.select("li:last")
        assert result.joinedtexts() == "Item 3"

    def test_select_even(self, simple_html):
        result = simple_html.select("li:even")
        assert len(result) == 2  # indices 0, 2

    def test_select_odd(self, simple_html):
        result = simple_html.select("li:odd")
        assert len(result) == 1  # index 1


# ---------------------------------------------------------------------------
# foxycss
# ---------------------------------------------------------------------------

class TestFoxyCss:
    def test_foxycss_simple(self, simple_html):
        result = simple_html.foxycss(".menu li")
        assert len(result) == 3

    def test_foxycss_text_transform(self, simple_html):
        # @ applies to the CollectionFoxyHtml; joinedtexts() is a valid method
        result = simple_html.foxycss(".menu li@.joinedtexts()")
        assert result == ["Item 1", "Item 2", "Item 3"]

    def test_foxycss_nested(self, nested_html):
        result = nested_html.foxycss(".outer .inner")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Node methods
# ---------------------------------------------------------------------------

class TestNode:
    def test_node_istag(self):
        parsed = FoxyHtml("<p>text</p>")
        tags = [n for n in parsed if n.istag()]
        assert len(tags) == 1
        assert tags[0].extra[0] == "p"

    def test_node_isclosetag(self):
        parsed = FoxyHtml("<p>text</p>")
        closetags = [n for n in parsed if n.isclosetag() and n.type == TypeNode.closetag]
        assert len(closetags) == 1

    def test_node_tagname(self):
        parsed = FoxyHtml("<div>x</div>")
        tag = next(n for n in parsed if n.istag())
        assert tag.tagname() == "div"

    def test_node_id(self):
        parsed = FoxyHtml('<div id="foo">x</div>')
        tag = next(n for n in parsed if n.istag())
        assert tag.id() == "foo"

    def test_singletag_parsed_as_singletag(self):
        parsed = FoxyHtml('<img src="x.jpg" />')
        tag = next(n for n in parsed if n.type == TypeNode.singletag)
        assert tag.tagname() == "img"

    def test_known_singles_are_singletag(self):
        """Tags like <br>, <hr>, <meta> are treated as singletags."""
        parsed = FoxyHtml("<br>")
        tag = next(n for n in parsed if n.type in (TypeNode.tag, TypeNode.singletag))
        assert tag.type == TypeNode.singletag

    def test_node_clean_strips_unknown_attrs(self):
        parsed = FoxyHtml('<a href="http://example.com" onclick="evil()">link</a>')
        cleaned = parsed.clean()
        rebuilt = cleaned.rebuild()
        assert "onclick" not in rebuilt
        assert 'href="http://example.com"' in rebuilt


# ---------------------------------------------------------------------------
# CollectionFoxyHtml
# ---------------------------------------------------------------------------

class TestCollectionFoxyHtml:
    def test_collection_search(self, simple_html):
        uls = simple_html.search(tagname="ul")
        items = uls.search(tagname="li")
        assert len(items) == 3

    def test_collection_texts(self, simple_html):
        items = simple_html.search(tagname="li")
        texts = items.texts()
        assert len(texts) == 3

    def test_collection_joinedtexts(self, simple_html):
        items = simple_html.search(tagname="li")
        joined = items.joinedtexts()
        assert "Item 1" in joined

    def test_collection_attr(self, simple_html):
        imgs = simple_html.search(tagname="img")
        srcs = imgs.attr("src")
        assert srcs == ["photo.jpg"]

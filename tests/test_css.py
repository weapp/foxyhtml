"""Tests for foxyhtml.css — CssSelector and FoxyCss."""
import pytest
from foxyhtml.css import CssSelector, FoxyCss
from foxyhtml import FoxyHtml


# ---------------------------------------------------------------------------
# CssSelector parsing
# ---------------------------------------------------------------------------

class TestCssSelector:
    def test_parse_tagname(self):
        sel = CssSelector("div")
        kws, modif = sel.parsed[0]
        assert kws.get("tagname") == "div"

    def test_parse_class(self):
        sel = CssSelector(".active")
        kws, modif = sel.parsed[0]
        assert kws.get("cls") == "active"

    def test_parse_id(self):
        sel = CssSelector("#main")
        kws, modif = sel.parsed[0]
        assert kws.get("id") == "main"

    def test_parse_pseudo_first(self):
        sel = CssSelector("li:first")
        _, modif = sel.parsed[-1]
        assert "first" in modif

    def test_parse_pseudo_last(self):
        sel = CssSelector("li:last")
        _, modif = sel.parsed[-1]
        assert "last" in modif

    def test_parse_tag_and_class(self):
        sel = CssSelector("li.active")
        kws_list = [kws for kws, _ in sel.parsed]
        tags = [k.get("tagname") for k in kws_list if "tagname" in k]
        classes = [k.get("cls") for k in kws_list if "cls" in k]
        assert "li" in tags
        assert "active" in classes

    def test_repr(self):
        sel = CssSelector("div")
        assert "div" in repr(sel)


# ---------------------------------------------------------------------------
# FoxyCss.parse_line
# ---------------------------------------------------------------------------

class TestFoxyCssParseInput:
    def test_parse_simple_selector(self):
        ident, colon, sel, attr = FoxyCss.parse_line("  .menu")
        assert ident == 2
        assert colon is False
        assert isinstance(sel, CssSelector)

    def test_parse_colon_key(self):
        ident, colon, sel, attr = FoxyCss.parse_line("title:")
        assert colon is True
        assert sel == "title"

    def test_parse_at_transform(self):
        ident, colon, sel, attr = FoxyCss.parse_line(".menu li@.upper()")
        assert callable(attr)
        assert attr("hello") == "HELLO"

    def test_at_transform_none_safe(self):
        _, _, _, attr = FoxyCss.parse_line("li@.upper()")
        assert attr(None) is None


# ---------------------------------------------------------------------------
# FoxyCss.apply — integration with FoxyHtml
# ---------------------------------------------------------------------------

@pytest.fixture
def html():
    return FoxyHtml("""
        <ul class="menu">
            <li class="item">Alpha</li>
            <li class="item">Beta</li>
            <li class="item active">Gamma</li>
        </ul>
        <div id="header"><h1>Title</h1></div>
    """)


class TestFoxyCssApply:
    def test_simple_class_selector(self, html):
        result = html.foxycss(".menu li")
        assert len(result) == 3

    def test_text_via_at(self, html):
        # @ applies to the CollectionFoxyHtml; use collection methods
        result = html.foxycss(".menu li@.joinedtexts()")
        assert result == ["Alpha", "Beta", "Gamma"]

    def test_texts_via_at(self, html):
        # texts() on CollectionFoxyHtml returns a list of lists
        result = html.foxycss(".menu li@.texts()")
        flat = [t.strip() for texts in result for t in texts if t.strip()]
        assert flat == ["Alpha", "Beta", "Gamma"]

    def test_id_selector(self, html):
        result = html.foxycss("#header h1")
        assert len(result) == 1
        assert result[0].joinedtexts() == "Title"

    def test_nested_selectors(self):
        parsed = FoxyHtml("""
            <div class="outer">
                <div class="inner">
                    <p>Text</p>
                </div>
            </div>
        """)
        result = parsed.foxycss(".outer .inner p")
        assert len(result) == 1
        assert result[0].joinedtexts() == "Text"

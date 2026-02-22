---
hide:
  - navigation
  - toc
---

<section class="mdx-perf">

<h2>Faster than BeautifulSoup. Half the memory.</h2>

<p>Most Python scrapers reach for BeautifulSoup first. FoxyHTML parses twice as fast,
uses half the memory — and needs nothing but Python.</p>

<div class="mdx-stats">
  <div class="mdx-stat">
    <span class="mdx-stat__value">2×</span>
    <span class="mdx-stat__label">faster to parse than BeautifulSoup</span>
  </div>
  <div class="mdx-stat">
    <span class="mdx-stat__value">×1.4</span>
    <span class="mdx-stat__label">faster to query real-world noisy pages</span>
  </div>
  <div class="mdx-stat">
    <span class="mdx-stat__value">½</span>
    <span class="mdx-stat__label">the memory footprint of BeautifulSoup</span>
  </div>
</div>

<div class="mdx-bars">
  <p class="mdx-bars__title">Memory used to parse a 1.4 MB Wikipedia page</p>

  <div class="mdx-bar">
    <span class="mdx-bar__lib mdx-bar__lib--highlight">foxyhtml</span>
    <div class="mdx-bar__track">
      <div class="mdx-bar__fill mdx-bar__fill--foxy" style="width:55%"></div>
    </div>
    <span class="mdx-bar__value mdx-bar__value--highlight">16.9 MB</span>
  </div>

  <div class="mdx-bar">
    <span class="mdx-bar__lib">lxml.html</span>
    <div class="mdx-bar__track">
      <div class="mdx-bar__fill mdx-bar__fill--lxml" style="width:63%"></div>
    </div>
    <span class="mdx-bar__value">19.4 MB</span>
  </div>

  <div class="mdx-bar">
    <span class="mdx-bar__lib">selectolax</span>
    <div class="mdx-bar__track">
      <div class="mdx-bar__fill mdx-bar__fill--selectolax" style="width:68%"></div>
    </div>
    <span class="mdx-bar__value">20.9 MB</span>
  </div>

  <div class="mdx-bar">
    <span class="mdx-bar__lib">bs4 + html.parser</span>
    <div class="mdx-bar__track">
      <div class="mdx-bar__fill mdx-bar__fill--bs4" style="width:95%"></div>
    </div>
    <span class="mdx-bar__value">29.4 MB</span>
  </div>

  <div class="mdx-bar">
    <span class="mdx-bar__lib">bs4 + lxml</span>
    <div class="mdx-bar__track">
      <div class="mdx-bar__fill mdx-bar__fill--bs4" style="width:100%"></div>
    </div>
    <span class="mdx-bar__value">30.9 MB</span>
  </div>

  <p class="mdx-bars__caption">
    Measured on a real 1.4 MB Wikipedia page. Lower is better.
    <a href="benchmarks/">Full benchmarks &rarr;</a>
  </p>
</div>

</section>

<h2 class="mdx-features-title">Everything you need. Nothing you don't.</h2>
<p class="mdx-features-subtitle">
  If you know CSS selectors, you know how to use FoxyHTML. No new concepts,
  no configuration, no dependency tree to untangle.
</p>

<div class="grid cards" markdown>

-   :material-package-variant-closed:{ .lg .middle } **Zero dependencies**

    ---

    Pure Python. No `lxml` to compile, no `beautifulsoup4` to pin, no
    binary wheels to worry about. `pip install foxyhtml` and you're done.

    [:octicons-arrow-right-24: Quick install](getting-started.md)

-   :material-magnify:{ .lg .middle } **jQuery-like API**

    ---

    `search()`, `select()`, `attr()`, `joinedtexts()` — an interface designed
    to feel natural if you've ever written a jQuery selector.

    [:octicons-arrow-right-24: Searching guide](guides/searching.md)

-   :material-code-tags:{ .lg .middle } **CSS selectors**

    ---

    Tag, `.class`, `#id`, descendant chains and pseudo-classes
    (`:first`, `:last`, `:even`, `:odd`) — all in one compact call.

    [:octicons-arrow-right-24: CSS selector syntax](guides/css-selectors.md)

-   :material-table-edit:{ .lg .middle } **Structured extraction**

    ---

    `foxycss()` maps indented selector rules to Python dicts and lists.
    Extract entire data structures from a page in a single expression.

    [:octicons-arrow-right-24: FoxyCss guide](guides/foxycss.md)

-   :material-shield-check:{ .lg .middle } **HTML sanitization**

    ---

    Strip untrusted markup down to a safe allowlist of tags and attributes
    with a single `clean()` call.

    [:octicons-arrow-right-24: Sanitization guide](guides/clean.md)

-   :material-language-python:{ .lg .middle } **Runs everywhere**

    ---

    Tested on Python 3.8 through 3.12+. Works in AWS Lambda, Docker scratch
    images, restricted CI environments — anywhere a pure Python package can run.

    [:octicons-arrow-right-24: API reference](api/foxyhtml.md)

</div>

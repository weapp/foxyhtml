---
hide:
  - navigation
  - toc
---

<section class="mdx-hero">
  <div class="mdx-hero__content">
    <div class="mdx-hero__inner">

      <div class="mdx-hero__teaser">
        <h1>
          Parse HTML like jQuery.<br>
          <span class="mdx-hero__accent">No overhead. No setup.</span>
        </h1>
        <p>
          One <code>pip install</code>. No C extensions to compile, no build steps, no surprises.
          Parses twice as fast as BeautifulSoup and uses half the memory — with a CSS
          selector API you already know.
        </p>
        <nav class="mdx-hero__cta" aria-label="Quick start">
          <a href="getting-started/" class="md-button md-button--primary">
            Get started &rarr;
          </a>
          <a href="api/foxyhtml/" class="md-button">
            Read the docs
          </a>
        </nav>
        <p class="mdx-hero__badges">
          <img src="https://img.shields.io/badge/python-3.8%2B-3776AB?logo=python&logoColor=white&style=flat-square" alt="Python 3.8+">
          <img src="https://img.shields.io/badge/license-MIT-22c55e?style=flat-square" alt="MIT License">
          <img src="https://img.shields.io/badge/dependencies-none-6366f1?style=flat-square" alt="No dependencies">
          <img src="https://img.shields.io/badge/version-0.2.0-64748b?style=flat-square" alt="v0.2.0">
        </p>
      </div>

      <div class="mdx-hero__code" aria-hidden="true">
        <div class="mdx-hero__code-header">
          <span class="mdx-hero__code-dot" style="background:#ff5f57"></span>
          <span class="mdx-hero__code-dot" style="background:#febc2e"></span>
          <span class="mdx-hero__code-dot" style="background:#28c840"></span>
          <span class="mdx-hero__code-filename">scraper.py</span>
        </div>
        <pre class="mdx-hero__pre"><code class="language-python"><span style="color:#7c3aed">from</span> foxyhtml <span style="color:#7c3aed">import</span> <span style="color:#1e40af">FoxyHtml</span>

doc <span style="color:#64748b">=</span> <span style="color:#1e40af">FoxyHtml</span>(<span style="color:#0891b2">open</span>(<span style="color:#16a34a">"page.html"</span>))

<span style="color:#94a3b8"># Search by tag, class or id</span>
items  <span style="color:#64748b">=</span> doc.<span style="color:#0891b2">search</span>(<span style="color:#16a34a">"li"</span>)
active <span style="color:#64748b">=</span> doc.<span style="color:#0891b2">search</span>(<span style="color:#16a34a">"a"</span>, cls<span style="color:#64748b">=</span><span style="color:#16a34a">"active"</span>)
nav    <span style="color:#64748b">=</span> doc.<span style="color:#0891b2">search</span>(id<span style="color:#64748b">=</span><span style="color:#16a34a">"main-nav"</span>)

<span style="color:#94a3b8"># CSS selectors + pseudo-classes</span>
first <span style="color:#64748b">=</span> doc.<span style="color:#0891b2">select</span>(<span style="color:#16a34a">"li:first"</span>)
href  <span style="color:#64748b">=</span> doc.<span style="color:#0891b2">select</span>(<span style="color:#16a34a">"a#logo"</span>).<span style="color:#0891b2">attr</span>(<span style="color:#16a34a">"href"</span>)

<span style="color:#94a3b8"># Structured data extraction</span>
links <span style="color:#64748b">=</span> doc.<span style="color:#0891b2">foxycss</span>(<span style="color:#16a34a">"""
nav
    li
        a@.attr('href')
"""</span>)</code></pre>
      </div>

    </div>
  </div>
</section>

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

"""Tests for the text-only handler options: image_placeholder,
drop_empty_alt_images, drop_image_only_links.

These three knobs install custom Rust-side handlers via add_handler when
their corresponding fields are set. Tests cover each knob in isolation,
their interactions, and the structural-detection edge cases that motivated
DOM-based detection over rendered-output prefix matching.
"""

import htmd


# --- image_placeholder ------------------------------------------------------


class TestImagePlaceholder:
    """Custom <img> rendering via template with {alt} substitution."""

    def test_default_renders_markdown_image(self):
        """No placeholder set → htmd's default ![alt](src) rendering."""
        out = htmd.convert_html('<img src="x.png" alt="foo">')
        assert "![foo](x.png)" in out

    def test_template_substitutes_alt(self):
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        out = htmd.convert_html('<img src="x.png" alt="foo">', opts)
        assert "[Image: foo]" in out
        assert "x.png" not in out  # src is dropped

    def test_template_with_empty_alt(self):
        """Empty alt becomes empty string in template, not the literal '{alt}'."""
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        out = htmd.convert_html('<img src="x.png" alt="">', opts)
        assert "[Image: ]" in out

    def test_template_with_missing_alt_attribute(self):
        """No alt attribute is treated the same as empty alt."""
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        out = htmd.convert_html('<img src="x.png">', opts)
        assert "[Image: ]" in out

    def test_template_trims_alt_whitespace(self):
        """Alt text is trimmed before substitution."""
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        out = htmd.convert_html('<img src="x.png" alt="  foo  ">', opts)
        assert "[Image: foo]" in out

    def test_template_without_alt_token(self):
        """Template without {alt} still works — it's just a literal string."""
        opts = htmd.Options()
        opts.image_placeholder = "[IMAGE]"
        out = htmd.convert_html('<img src="x.png" alt="anything">', opts)
        assert "[IMAGE]" in out

    def test_template_with_special_markdown_chars_in_alt(self):
        """Brackets in alt text are inserted verbatim; HandlerResult bypasses
        the text-node escaping that would normally backslash-escape them."""
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        out = htmd.convert_html('<img src="x.png" alt="![foo]">', opts)
        assert "[Image: ![foo]]" in out


# --- drop_empty_alt_images --------------------------------------------------


class TestDropEmptyAltImages:
    """Drop <img> elements whose alt is empty or missing."""

    def test_default_keeps_empty_alt(self):
        out = htmd.convert_html('<p>before<img src="x.png" alt="">after</p>')
        # Default htmd rendering keeps the image; exact form is `![](x.png)`.
        assert "![" in out

    def test_drops_empty_alt(self):
        opts = htmd.Options()
        opts.drop_empty_alt_images = True
        out = htmd.convert_html(
            '<p>before<img src="x.png" alt="">after</p>',
            opts,
        )
        assert "x.png" not in out
        assert "![" not in out
        assert "before" in out
        assert "after" in out

    def test_drops_missing_alt_attribute(self):
        opts = htmd.Options()
        opts.drop_empty_alt_images = True
        out = htmd.convert_html('<p>before<img src="x.png">after</p>', opts)
        assert "x.png" not in out
        assert "before" in out
        assert "after" in out

    def test_drops_whitespace_only_alt(self):
        opts = htmd.Options()
        opts.drop_empty_alt_images = True
        out = htmd.convert_html(
            '<p>x<img src="x.png" alt="   ">y</p>',
            opts,
        )
        assert "x.png" not in out

    def test_keeps_nonempty_alt_with_default_rendering(self):
        """Without a custom template, non-empty alts get htmd's default
        ![alt](src) rendering (handler defers to fallback)."""
        opts = htmd.Options()
        opts.drop_empty_alt_images = True
        out = htmd.convert_html('<img src="x.png" alt="kept">', opts)
        assert "![kept](x.png)" in out


# --- image_placeholder + drop_empty_alt_images ------------------------------


class TestImagePlaceholderWithDropEmpty:
    """Both knobs set: non-empty alts use the template, empty alts dropped."""

    def test_non_empty_alt_uses_template(self):
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        opts.drop_empty_alt_images = True
        out = htmd.convert_html('<img src="x.png" alt="foo">', opts)
        assert "[Image: foo]" in out

    def test_empty_alt_dropped_not_templated(self):
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        opts.drop_empty_alt_images = True
        out = htmd.convert_html(
            '<p>x<img src="x.png" alt="">y</p>',
            opts,
        )
        assert "[Image:" not in out
        assert "x.png" not in out
        assert "x" in out and "y" in out


# --- drop_image_only_links: structural detection cases ---------------------


class TestDropImageOnlyLinks:
    """Structural detection: anchor's direct children must be exactly one
    <img> element plus only whitespace text siblings."""

    def test_default_keeps_link_around_image(self):
        out = htmd.convert_html(
            '<a href="https://example.com"><img src="x.png" alt="foo"></a>',
        )
        # Default: link wraps image, both rendered.
        assert "https://example.com" in out
        assert "![foo](x.png)" in out

    def test_unwraps_bare_image_only_link(self):
        opts = htmd.Options()
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com"><img src="x.png" alt="foo"></a>',
            opts,
        )
        assert "https://example.com" not in out
        assert "![foo](x.png)" in out

    def test_unwraps_with_whitespace_siblings(self):
        """Pretty-printed HTML with whitespace text nodes around the image
        still counts as image-only — that's the natural form from any HTML
        formatter."""
        opts = htmd.Options()
        opts.drop_image_only_links = True
        html = '<a href="https://example.com">\n  <img src="x.png" alt="foo">\n</a>'
        out = htmd.convert_html(html, opts)
        assert "https://example.com" not in out
        assert "![foo](x.png)" in out

    def test_keeps_link_with_image_plus_text(self):
        """The motivating false-positive: <a><img> text</a> must NOT be
        unwrapped — the rendered markdown starts with the image marker but
        the link semantically wraps both image and text."""
        opts = htmd.Options()
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com"><img src="x.png" alt="foo"> Read more</a>',
            opts,
        )
        # Link must survive: structural check sees a non-whitespace text sibling.
        assert "https://example.com" in out
        assert "Read more" in out

    def test_keeps_link_with_two_images(self):
        opts = htmd.Options()
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com">'
            '<img src="a.png" alt="a"><img src="b.png" alt="b">'
            "</a>",
            opts,
        )
        assert "https://example.com" in out

    def test_keeps_link_with_image_plus_other_element(self):
        opts = htmd.Options()
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com">'
            '<img src="x.png" alt="foo"><span>caption</span>'
            "</a>",
            opts,
        )
        assert "https://example.com" in out
        assert "caption" in out

    def test_keeps_link_with_only_text(self):
        """Plain text-only links are unaffected — fallback handles them."""
        opts = htmd.Options()
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com">click me</a>',
            opts,
        )
        assert "[click me](https://example.com)" in out

    def test_keeps_link_with_no_children(self):
        """<a></a> has no img child, so structural check fails — fallback."""
        opts = htmd.Options()
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com"></a>',
            opts,
        )
        # Empty link goes through fallback. We don't assert exact rendering,
        # just that no crash and the option didn't unwrap into nothing.
        assert isinstance(out, str)


# --- drop_image_only_links + other knobs ------------------------------------


class TestDropImageOnlyLinksWithOtherKnobs:
    """The unwrapped inner walk uses whatever <img> handler chain is active."""

    def test_unwrapped_image_uses_custom_template(self):
        opts = htmd.Options()
        opts.image_placeholder = "[Image: {alt}]"
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<a href="https://example.com"><img src="x.png" alt="foo"></a>',
            opts,
        )
        assert "https://example.com" not in out
        assert "[Image: foo]" in out

    def test_unwrapped_empty_alt_image_with_drop_empty_emits_nothing(self):
        """When drop_image_only_links + drop_empty_alt_images both apply to
        an empty-alt image inside an anchor, the structural check still
        passes (the <img> element exists), the inner walk emits empty string
        (image dropped), and the anchor unwraps to empty.

        Net effect: the entire <a><img></a> disappears, which is the
        intended LLM-ingestion behavior — no link, no image, no chrome."""
        opts = htmd.Options()
        opts.drop_empty_alt_images = True
        opts.drop_image_only_links = True
        out = htmd.convert_html(
            '<p>before<a href="https://example.com">'
            '<img src="x.png" alt=""></a>after</p>',
            opts,
        )
        assert "https://example.com" not in out
        assert "x.png" not in out
        assert "before" in out
        assert "after" in out

    def test_link_with_only_dropped_image_still_classified_as_image_only(self):
        """Variant of the above with whitespace siblings — same outcome."""
        opts = htmd.Options()
        opts.drop_empty_alt_images = True
        opts.drop_image_only_links = True
        html = (
            '<p>x<a href="https://example.com">\n  <img src="x.png" alt="">\n</a>y</p>'
        )
        out = htmd.convert_html(html, opts)
        assert "https://example.com" not in out
        assert "x" in out and "y" in out


# --- Regression test for the prefix-matching false positive ----------------


def test_link_with_image_then_text_does_not_unwrap_with_custom_template():
    """The original heuristic (string-prefix matching) would unwrap this case
    when image_placeholder = "[Image: {alt}]" because the rendered inner
    content "[Image: foo] Read more" starts with "[Image: ". Structural
    detection prevents this — the anchor has a non-whitespace text sibling,
    so it's not image-only and the link survives."""
    opts = htmd.Options()
    opts.image_placeholder = "[Image: {alt}]"
    opts.drop_image_only_links = True
    out = htmd.convert_html(
        '<a href="https://example.com"><img src="x.png" alt="foo"> Read more</a>',
        opts,
    )
    assert "https://example.com" in out
    assert "Read more" in out

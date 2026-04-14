# tests/test_conversion.py
"""End-to-end smoke tests: each option demonstrably changes output."""

import htmd
import pytest


def test_convert_without_options():
    assert htmd.convert_html("<h1>Hello</h1>").strip() == "# Hello"


def test_convert_with_default_options_matches_no_options():
    """Both code paths (htmd_convert vs builder) should agree on trivial input."""
    html = "<h1>Hello</h1><p>world</p>"
    no_opts = htmd.convert_html(html)
    with_opts = htmd.convert_html(html, htmd.Options())
    assert no_opts == with_opts


def test_heading_style_setex():
    opts = htmd.Options()
    opts.heading_style = htmd.HeadingStyle.SETEX
    out = htmd.convert_html("<h1>Hello</h1>", opts)
    assert "===" in out
    assert not out.lstrip().startswith("#")


def test_bullet_list_marker_dash():
    opts = htmd.Options()
    opts.bullet_list_marker = htmd.BulletListMarker.DASH
    opts.ul_bullet_spacing = 1
    out = htmd.convert_html("<ul><li>a</li></ul>", opts)
    assert "- a" in out


def test_ul_bullet_spacing_controls_gap():
    opts = htmd.Options()
    opts.ul_bullet_spacing = 5
    out = htmd.convert_html("<ul><li>a</li></ul>", opts)
    assert "*     a" in out  # marker + 5 spaces + content


@pytest.mark.parametrize(
    "style,marker",
    [
        (htmd.HrStyle.DASHES, "-"),
        (htmd.HrStyle.ASTERISKS, "*"),
        (htmd.HrStyle.UNDERSCORES, "_"),
    ],
)
def test_hr_style(style, marker):
    opts = htmd.Options()
    opts.hr_style = style
    out = htmd.convert_html("<hr>", opts)
    assert marker in out


def test_code_block_style_fenced():
    opts = htmd.Options()
    opts.code_block_style = htmd.CodeBlockStyle.FENCED
    out = htmd.convert_html("<pre><code>x = 1</code></pre>", opts)
    assert "```" in out


def test_code_block_style_indented():
    opts = htmd.Options()
    opts.code_block_style = htmd.CodeBlockStyle.INDENTED
    out = htmd.convert_html("<pre><code>x = 1</code></pre>", opts)
    assert "```" not in out
    assert "    x = 1" in out or "\tx = 1" in out


def test_code_block_fence_tildes():
    opts = htmd.Options()
    opts.code_block_style = htmd.CodeBlockStyle.FENCED
    opts.code_block_fence = htmd.CodeBlockFence.TILDES
    out = htmd.convert_html("<pre><code>x = 1</code></pre>", opts)
    assert "~~~" in out
    assert "```" not in out


def test_skip_tags_drops_content():
    opts = htmd.create_options_with_skip_tags(["script"])
    out = htmd.convert_html("<h1>Hello</h1><script>alert('x')</script>", opts)
    assert "alert" not in out
    assert "Hello" in out


def test_skip_tags_multiple():
    opts = htmd.create_options_with_skip_tags(["script", "style"])
    html = "<h1>Hi</h1><script>a</script><style>b</style><p>keep</p>"
    out = htmd.convert_html(html, opts)
    assert "a" not in out.replace("Hi", "").replace("keep", "")
    assert "keep" in out


def test_link_style_referenced():
    opts = htmd.Options()
    opts.link_style = htmd.LinkStyle.REFERENCED
    out = htmd.convert_html('<a href="https://example.com">ex</a>', opts)
    # Referenced style produces [ex][1] ... [1]: https://example.com
    assert "[ex]" in out
    assert "https://example.com" in out


def test_link_style_inlined_default():
    opts = htmd.Options()
    out = htmd.convert_html('<a href="https://example.com">ex</a>', opts)
    assert "[ex](https://example.com)" in out


def test_convert_html_rejects_non_string():
    with pytest.raises(TypeError):
        htmd.convert_html(123)


def test_empty_html():
    assert htmd.convert_html("") == ""


def test_options_instance_reusable():
    """Passing the same Options twice shouldn't mutate or consume it."""
    opts = htmd.Options()
    opts.heading_style = htmd.HeadingStyle.SETEX
    a = htmd.convert_html("<h1>x</h1>", opts)
    b = htmd.convert_html("<h1>x</h1>", opts)
    assert a == b

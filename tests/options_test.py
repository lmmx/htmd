# tests/test_options.py
"""Options construction, defaults, and attribute round-tripping."""

import htmd
import pytest

EXPECTED_DEFAULTS = {
    "heading_style": "atx",
    "hr_style": "asterisks",
    "br_style": "two_spaces",
    "link_style": "inlined",
    "link_reference_style": "full",
    "code_block_style": "fenced",
    "code_block_fence": "backticks",
    "bullet_list_marker": "asterisk",
    "ul_bullet_spacing": 3,
    "ol_number_spacing": 2,
    "preformatted_code": False,
    "translation_mode": "pure",
    "image_placeholder": None,
    "drop_empty_alt_images": False,
    "drop_image_only_links": False,
}


@pytest.fixture
def opts():
    return htmd.Options()


@pytest.mark.parametrize("attr,expected", list(EXPECTED_DEFAULTS.items()))
def test_default_values(opts, attr, expected):
    assert getattr(opts, attr) == expected


def test_default_skip_tags_empty(opts):
    assert opts.skip_tags == []


@pytest.mark.parametrize(
    "attr,value",
    [
        ("heading_style", "setex"),
        ("hr_style", "dashes"),
        ("br_style", "backslash"),
        ("link_style", "referenced"),
        ("link_reference_style", "collapsed"),
        ("code_block_style", "indented"),
        ("code_block_fence", "tildes"),
        ("bullet_list_marker", "dash"),
        ("translation_mode", "faithful"),
        ("ul_bullet_spacing", 4),
        ("ol_number_spacing", 3),
        ("preformatted_code", True),
        ("skip_tags", ["script", "style"]),
        ("image_placeholder", "[Image: {alt}]"),
        ("image_placeholder", None),
        ("drop_empty_alt_images", True),
        ("drop_image_only_links", True),
    ],
)
def test_attribute_roundtrip(opts, attr, value):
    setattr(opts, attr, value)
    assert getattr(opts, attr) == value


@pytest.mark.parametrize("bad_value", [-1, 256, 1000])
def test_u8_field_rejects_out_of_range(opts, bad_value):
    with pytest.raises(OverflowError):
        opts.ul_bullet_spacing = bad_value
    with pytest.raises(OverflowError):
        opts.ol_number_spacing = bad_value


def test_create_options_with_skip_tags():
    opts = htmd.create_options_with_skip_tags(["script", "style"])
    assert opts.skip_tags == ["script", "style"]
    # Other fields should match defaults
    assert opts.heading_style == "atx"


def test_create_options_with_empty_skip_tags():
    opts = htmd.create_options_with_skip_tags([])
    assert opts.skip_tags == []


class TestUnknownEnumStrings:
    """Pin the silent-fallback behavior: unrecognized strings currently fall
    through to the default variant rather than erroring. If this ever changes,
    these tests will tell you. Remove/invert them if you change the policy."""

    def test_unknown_heading_style_falls_back_to_atx(self):
        opts = htmd.Options()
        opts.heading_style = "banana"
        # ATX produces `# heading`, SETEX produces `heading\n=======`
        out = htmd.convert_html("<h1>hi</h1>", opts)
        assert out.startswith("#")

    def test_unknown_bullet_marker_falls_back_to_asterisk(self):
        opts = htmd.Options()
        opts.bullet_list_marker = "squiggle"
        out = htmd.convert_html("<ul><li>x</li></ul>", opts)
        assert "*" in out

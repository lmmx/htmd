# tests/test_constants.py
"""Enum constants and module surface."""

import pytest
import htmd

EXPECTED_CONSTANTS = {
    "HeadingStyle": {"ATX": "atx", "SETEX": "setex"},
    "HrStyle": {
        "DASHES": "dashes",
        "ASTERISKS": "asterisks",
        "UNDERSCORES": "underscores",
    },
    "BrStyle": {"TWO_SPACES": "two_spaces", "BACKSLASH": "backslash"},
    "LinkStyle": {
        "INLINED": "inlined",
        "INLINED_PREFER_AUTOLINKS": "inlined_prefer_autolinks",
        "REFERENCED": "referenced",
    },
    "LinkReferenceStyle": {
        "FULL": "full",
        "COLLAPSED": "collapsed",
        "SHORTCUT": "shortcut",
    },
    "CodeBlockStyle": {"INDENTED": "indented", "FENCED": "fenced"},
    "CodeBlockFence": {"TILDES": "tildes", "BACKTICKS": "backticks"},
    "BulletListMarker": {"ASTERISK": "asterisk", "DASH": "dash"},
    "TranslationMode": {"PURE": "pure", "FAITHFUL": "faithful"},
}


@pytest.mark.parametrize(
    "enum_name,member,expected",
    [
        (enum_name, member, expected)
        for enum_name, members in EXPECTED_CONSTANTS.items()
        for member, expected in members.items()
    ],
)
def test_enum_constants_match_rust_match_arms(enum_name, member, expected):
    """Every Python-side enum string must match the literal in the Rust match arms.
    If this breaks, conversion silently falls through to the default variant."""
    enum_obj = getattr(htmd, enum_name)
    assert getattr(enum_obj, member) == expected


def test_all_contains_documented_names():
    expected = {
        "convert_html",
        "create_options_with_skip_tags",
        "Options",
        "HeadingStyle",
        "HrStyle",
        "BrStyle",
        "LinkStyle",
        "LinkReferenceStyle",
        "CodeBlockStyle",
        "CodeBlockFence",
        "BulletListMarker",
        "TranslationMode",
    }
    assert set(htmd.__all__) == expected


def test_top_level_exports_exist():
    for name in htmd.__all__:
        assert hasattr(htmd, name), f"htmd.{name} missing"

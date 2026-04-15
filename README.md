# htmd-py

<!-- [![downloads](https://static.pepy.tech/badge/htmd-py/month)](https://pepy.tech/project/htmd-py) -->
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![PyPI](https://img.shields.io/pypi/v/htmd-py.svg)](https://pypi.org/project/htmd-py)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/htmd-py.svg)](https://pypi.org/project/htmd-py)
[![License](https://img.shields.io/pypi/l/htmd-py.svg)](https://pypi.python.org/pypi/htmd-py)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/lmmx/htmd/master.svg)](https://results.pre-commit.ci/latest/github/lmmx/htmd/master)

Python bindings for the [htmd](https://github.com/letmutex/htmd) Rust library, a fast HTML to Markdown converter.

## Installation

```bash
pip install htmd-py
```

### Requirements

- Python 3.9+

### Options

You can customise the HTML to Markdown conversion with the following options:

- `heading_style`: Style for headings (values from `htmd.HeadingStyle`)
- `hr_style`: Style for horizontal rules (values from `htmd.HrStyle`)
- `br_style`: Style for line breaks (values from `htmd.BrStyle`)
- `link_style`: Style for links (values from `htmd.LinkStyle`)
- `link_reference_style`: Style for referenced links (values from `htmd.LinkReferenceStyle`)
- `code_block_style`: Style for code blocks (values from `htmd.CodeBlockStyle`)
- `code_block_fence`: Fence style for code blocks (values from `htmd.CodeBlockFence`)
- `bullet_list_marker`: Marker for unordered lists (values from `htmd.BulletListMarker`)
- `ul_bullet_spacing`: Number of spaces between the bullet character and the content in unordered lists (integer, `u8`)
- `ol_number_spacing`: Number of spaces between the period and the content in ordered lists (integer, `u8`)
- `preformatted_code`: Whether to preserve whitespace in inline code (boolean)
- `translation_mode`: How faithfully to preserve source HTML (values from `htmd.TranslationMode`)
- `skip_tags`: List of HTML tags to skip during conversion (list of strings)
- <sup>†</sup>`image_placeholder`: Optional template string for `<img>` elements; `{alt}` is substituted for the alt attribute (`Optional[str]`)
- <sup>†</sup>`drop_empty_alt_images`: Drop `<img>` with empty or missing alt (boolean)
- <sup>†</sup>`drop_image_only_links`: Unwrap `<a>` whose only element child is an `<img>` (boolean)

 <sup>†</sup> _These options are in htmd-py, not part of the htmd crate's `Options`._

All options are exposed in a simple manner:

```py
import htmd

# Simple conversion with default options
markdown = htmd.convert_html("<h1>Hello World</h1>")
print(markdown)  # "# Hello World"

# Using custom options
options = htmd.Options()
options.heading_style = htmd.HeadingStyle.SETEX
options.bullet_list_marker = htmd.BulletListMarker.DASH
markdown = htmd.convert_html("<h1>Hello World</h1><ul><li>Item 1</li></ul>", options)
print(markdown)

# Skip specific HTML tags
options = htmd.create_options_with_skip_tags(["script", "style"])
markdown = htmd.convert_html("<h1>Hello</h1><script>alert('Hi');</script>", options)
print(markdown)  # "# Hello" (script tag is skipped)
```

Refer to the [htmd docs](https://docs.rs/htmd/latest/htmd/options/struct.Options.html) for all available options.

### Available Constants

The module provides enumeration-like objects for all option values:

```python
import htmd

# HeadingStyle
htmd.HeadingStyle.ATX       # "atx"
htmd.HeadingStyle.SETEX     # "setex"

# HrStyle
htmd.HrStyle.DASHES         # "dashes"
htmd.HrStyle.ASTERISKS      # "asterisks"
htmd.HrStyle.UNDERSCORES    # "underscores"

# BrStyle
htmd.BrStyle.TWO_SPACES     # "two_spaces"
htmd.BrStyle.BACKSLASH      # "backslash"

# LinkStyle
htmd.LinkStyle.INLINED                   # "inlined"
htmd.LinkStyle.INLINED_PREFER_AUTOLINKS  # "inlined_prefer_autolinks"
htmd.LinkStyle.REFERENCED                # "referenced"

# LinkReferenceStyle
htmd.LinkReferenceStyle.FULL       # "full"
htmd.LinkReferenceStyle.COLLAPSED  # "collapsed"
htmd.LinkReferenceStyle.SHORTCUT   # "shortcut"

# CodeBlockStyle
htmd.CodeBlockStyle.INDENTED  # "indented"
htmd.CodeBlockStyle.FENCED    # "fenced"

# CodeBlockFence
htmd.CodeBlockFence.TILDES    # "tildes"
htmd.CodeBlockFence.BACKTICKS # "backticks"

# BulletListMarker
htmd.BulletListMarker.ASTERISK  # "asterisk"
htmd.BulletListMarker.DASH      # "dash"

# TranslationMode
htmd.TranslationMode.PURE       # "pure"
htmd.TranslationMode.FAITHFUL   # "faithful"
```

`ul_bullet_spacing` and `ol_number_spacing` are plain integers rather than enum-like constants — any value in the `u8` range (0–255) is valid.

## Benchmarks

Tested with small (12 lines) and medium (1000 lines) markdown strings

- vs. [markdownify](https://pypi.org/project/markdownify): 10x (S) - 30x (M) faster

## Contributing

Maintained by [lmmx](https://github.com/lmmx). Contributions welcome!

1. **Issues & Discussions**: Please open a GitHub issue or discussion for bugs, feature requests, or questions.
2. **Pull Requests**: PRs are welcome!
   - Install the dev extra (e.g. with [uv](https://docs.astral.sh/uv/): `uv pip install -e .[dev]`)
   - Run tests (when available) and include updates to docs or examples if relevant.
   - If reporting a bug, please include the version and the error message/traceback if available.

## Credits

- [htmd](https://github.com/letmutex/htmd) - The underlying Rust library
- Inspired by [comrak](https://github.com/lmmx/comrak) - Python bindings for Comrak, a fast Markdown to HTML converter.

## License

Licensed under the Apache License, Version 2.0.

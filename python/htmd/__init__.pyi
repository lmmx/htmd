from typing import Optional, Sequence

class Options:
    """
    Python class that mirrors htmd's `Options`
    """

    heading_style: str
    hr_style: str
    br_style: str
    link_style: str
    link_reference_style: str
    code_block_style: str
    code_block_fence: str
    bullet_list_marker: str
    preformatted_code: bool
    skip_tags: list[str]

def convert_html(html: str, options: Optional[Options] = None) -> str:
    """
    Convert an HTML string to Markdown, with optional options.
    """

def create_options_with_skip_tags(tags: Sequence[str]) -> Options:
    """
    Create options configured to skip specific HTML tags during conversion.
    """

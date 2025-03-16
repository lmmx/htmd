use pyo3::prelude::*;

use htmd_lib::options::{
    BrStyle as HtmdBrStyle, BulletListMarker as HtmdBulletListMarker,
    CodeBlockFence as HtmdCodeBlockFence, CodeBlockStyle as HtmdCodeBlockStyle,
    HeadingStyle as HtmdHeadingStyle, HrStyle as HtmdHrStyle,
    LinkReferenceStyle as HtmdLinkReferenceStyle, LinkStyle as HtmdLinkStyle,
    Options as HtmdOptions,
};
use htmd_lib::HtmlToMarkdownBuilder;

/// Python class that mirrors htmd's `Options`
#[pyclass(name = "Options")]
#[derive(Clone)]
pub struct PyOptions {
    #[pyo3(get, set)]
    pub heading_style: String,
    #[pyo3(get, set)]
    pub hr_style: String,
    #[pyo3(get, set)]
    pub br_style: String,
    #[pyo3(get, set)]
    pub link_style: String,
    #[pyo3(get, set)]
    pub link_reference_style: String,
    #[pyo3(get, set)]
    pub code_block_style: String,
    #[pyo3(get, set)]
    pub code_block_fence: String,
    #[pyo3(get, set)]
    pub bullet_list_marker: String,
    #[pyo3(get, set)]
    pub preformatted_code: bool,

    // Special attributes that don't map directly to HtmdOptions
    #[pyo3(get, set)]
    pub skip_tags: Vec<String>,
}

impl PyOptions {
    /// Convert PyOptions to HtmdOptions
    pub fn to_htmd_options(&self) -> HtmdOptions {
        let heading_style = match self.heading_style.as_str() {
            "setex" => HtmdHeadingStyle::Setex,
            _ => HtmdHeadingStyle::Atx,
        };

        let hr_style = match self.hr_style.as_str() {
            "dashes" => HtmdHrStyle::Dashes,
            "underscores" => HtmdHrStyle::Underscores,
            _ => HtmdHrStyle::Asterisks,
        };

        let br_style = match self.br_style.as_str() {
            "backslash" => HtmdBrStyle::Backslash,
            _ => HtmdBrStyle::TwoSpaces,
        };

        let link_style = match self.link_style.as_str() {
            "referenced" => HtmdLinkStyle::Referenced,
            _ => HtmdLinkStyle::Inlined,
        };

        let link_reference_style = match self.link_reference_style.as_str() {
            "collapsed" => HtmdLinkReferenceStyle::Collapsed,
            "shortcut" => HtmdLinkReferenceStyle::Shortcut,
            _ => HtmdLinkReferenceStyle::Full,
        };

        let code_block_style = match self.code_block_style.as_str() {
            "indented" => HtmdCodeBlockStyle::Indented,
            _ => HtmdCodeBlockStyle::Fenced,
        };

        let code_block_fence = match self.code_block_fence.as_str() {
            "tildes" => HtmdCodeBlockFence::Tildes,
            _ => HtmdCodeBlockFence::Backticks,
        };

        let bullet_list_marker = match self.bullet_list_marker.as_str() {
            "dash" => HtmdBulletListMarker::Dash,
            _ => HtmdBulletListMarker::Asterisk,
        };

        HtmdOptions {
            heading_style,
            hr_style,
            br_style,
            link_style,
            link_reference_style,
            code_block_style,
            code_block_fence,
            bullet_list_marker,
            preformatted_code: self.preformatted_code,
        }
    }

    /// Apply the options to an HtmlToMarkdownBuilder
    pub fn apply_to_builder(&self, builder: HtmlToMarkdownBuilder) -> HtmlToMarkdownBuilder {
        let mut builder = builder.options(self.to_htmd_options());

        // Apply skip_tags if any
        if !self.skip_tags.is_empty() {
            let skip_tags: Vec<&str> = self.skip_tags.iter().map(|s| s.as_str()).collect();
            builder = builder.skip_tags(skip_tags);
        }

        builder
    }
}

#[pymethods]
impl PyOptions {
    #[new]
    pub fn new() -> Self {
        let defaults = HtmdOptions::default();

        Self {
            heading_style: match defaults.heading_style {
                HtmdHeadingStyle::Atx => "atx".to_string(),
                HtmdHeadingStyle::Setex => "setex".to_string(),
            },

            hr_style: match defaults.hr_style {
                HtmdHrStyle::Dashes => "dashes".to_string(),
                HtmdHrStyle::Asterisks => "asterisks".to_string(),
                HtmdHrStyle::Underscores => "underscores".to_string(),
            },

            br_style: match defaults.br_style {
                HtmdBrStyle::TwoSpaces => "two_spaces".to_string(),
                HtmdBrStyle::Backslash => "backslash".to_string(),
            },

            link_style: match defaults.link_style {
                HtmdLinkStyle::Inlined => "inlined".to_string(),
                HtmdLinkStyle::Referenced => "referenced".to_string(),
            },

            link_reference_style: match defaults.link_reference_style {
                HtmdLinkReferenceStyle::Full => "full".to_string(),
                HtmdLinkReferenceStyle::Collapsed => "collapsed".to_string(),
                HtmdLinkReferenceStyle::Shortcut => "shortcut".to_string(),
            },

            code_block_style: match defaults.code_block_style {
                HtmdCodeBlockStyle::Indented => "indented".to_string(),
                HtmdCodeBlockStyle::Fenced => "fenced".to_string(),
            },

            code_block_fence: match defaults.code_block_fence {
                HtmdCodeBlockFence::Tildes => "tildes".to_string(),
                HtmdCodeBlockFence::Backticks => "backticks".to_string(),
            },

            bullet_list_marker: match defaults.bullet_list_marker {
                HtmdBulletListMarker::Asterisk => "asterisk".to_string(),
                HtmdBulletListMarker::Dash => "dash".to_string(),
            },

            preformatted_code: defaults.preformatted_code,

            // Special attributes
            skip_tags: Vec::new(),
        }
    }
}

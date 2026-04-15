use std::rc::Rc;

use pyo3::prelude::*;

use htmd_lib::element_handler::{HandlerResult, Handlers};
use htmd_lib::options::{
    BrStyle as HtmdBrStyle, BulletListMarker as HtmdBulletListMarker,
    CodeBlockFence as HtmdCodeBlockFence, CodeBlockStyle as HtmdCodeBlockStyle,
    HeadingStyle as HtmdHeadingStyle, HrStyle as HtmdHrStyle,
    LinkReferenceStyle as HtmdLinkReferenceStyle, LinkStyle as HtmdLinkStyle,
    Options as HtmdOptions, TranslationMode as HtmdTranslationMode,
};
use htmd_lib::{Element, HtmlToMarkdownBuilder};
use markup5ever_rcdom::{Node, NodeData};

/// True if `node`'s direct children are exactly one `<img>` element, with
/// any other children being whitespace-only text nodes. Comments, doctype,
/// and processing instructions are ignored.
fn is_image_only_anchor(node: &Rc<Node>) -> bool {
    let children = node.children.borrow();
    let mut saw_image = false;
    for child in children.iter() {
        match &child.data {
            NodeData::Text { contents } => {
                if !contents.borrow().chars().all(char::is_whitespace) {
                    return false;
                }
            }
            NodeData::Element { name, .. } => {
                if &*name.local != "img" {
                    return false;
                }
                if saw_image {
                    return false;
                }
                saw_image = true;
            }
            _ => {}
        }
    }
    saw_image
}

/// Python class that mirrors htmd's `Options`
#[pyclass(name = "Options", from_py_object)]
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
    pub ul_bullet_spacing: u8,
    #[pyo3(get, set)]
    pub ol_number_spacing: u8,
    #[pyo3(get, set)]
    pub preformatted_code: bool,
    #[pyo3(get, set)]
    pub translation_mode: String,

    // Special attributes that don't map directly to HtmdOptions
    #[pyo3(get, set)]
    pub skip_tags: Vec<String>,

    /// Custom image replacement template. When set, `<img>` elements are
    /// replaced with this string, with `{alt}` substituted for the alt
    /// attribute's value. When `None`, htmd's default `![alt](src)`
    /// rendering is used.
    #[pyo3(get, set)]
    pub image_placeholder: Option<String>,

    /// When true, `<img>` elements whose alt attribute is empty or missing
    /// are dropped from the output. Composes with `image_placeholder`:
    /// non-empty alts use the template, empty alts are dropped.
    #[pyo3(get, set)]
    pub drop_empty_alt_images: bool,

    /// When true, `<a>` elements whose only element child is an `<img>`
    /// (with optional whitespace-only text siblings) are unwrapped: the
    /// inner image render is emitted without the surrounding link.
    #[pyo3(get, set)]
    pub drop_image_only_links: bool,
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
            "inlined_prefer_autolinks" => HtmdLinkStyle::InlinedPreferAutolinks,
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

        let translation_mode = match self.translation_mode.as_str() {
            "faithful" => HtmdTranslationMode::Faithful,
            _ => HtmdTranslationMode::Pure,
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
            ul_bullet_spacing: self.ul_bullet_spacing,
            ol_number_spacing: self.ol_number_spacing,
            preformatted_code: self.preformatted_code,
            translation_mode,
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

        // Install custom <img> handler if image_placeholder or drop_empty_alt_images is set.
        let wants_img_handler =
            self.image_placeholder.is_some() || self.drop_empty_alt_images;
        if wants_img_handler {
            let template = self.image_placeholder.clone();
            let drop_empty = self.drop_empty_alt_images;
            builder = builder.add_handler(
                vec!["img"],
                move |handlers: &dyn Handlers, element: Element| -> Option<HandlerResult> {
                    let alt = element
                        .attrs
                        .iter()
                        .find(|a| &*a.name.local == "alt")
                        .map(|a| a.value.to_string())
                        .unwrap_or_default();
                    let alt_trimmed = alt.trim();

                    if alt_trimmed.is_empty() && drop_empty {
                        return Some(HandlerResult::from(String::new()));
                    }

                    if let Some(ref t) = template {
                        let replaced = t.replace("{alt}", alt_trimmed);
                        return Some(HandlerResult::from(replaced));
                    }

                    handlers.fallback(element)
                },
            );
        }

        // Install custom <a> handler that unwraps image-only links.
        if self.drop_image_only_links {
            builder = builder.add_handler(
                vec!["a"],
                move |handlers: &dyn Handlers, element: Element| -> Option<HandlerResult> {
                    if is_image_only_anchor(element.node) {
                        let inner = handlers.walk_children(element.node);
                        return Some(HandlerResult::from(inner.content));
                    }
                    handlers.fallback(element)
                },
            );
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
                HtmdLinkStyle::InlinedPreferAutolinks => "inlined_prefer_autolinks".to_string(),
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

            ul_bullet_spacing: defaults.ul_bullet_spacing,
            ol_number_spacing: defaults.ol_number_spacing,

            preformatted_code: defaults.preformatted_code,

            translation_mode: match defaults.translation_mode {
                HtmdTranslationMode::Pure => "pure".to_string(),
                HtmdTranslationMode::Faithful => "faithful".to_string(),
            },

            // Special attributes
            skip_tags: Vec::new(),

            // Text-only handler options
            image_placeholder: None,
            drop_empty_alt_images: false,
            drop_image_only_links: false,
        }
    }
}

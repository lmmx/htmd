use pyo3::prelude::*;

use htmd_lib::convert as htmd_convert;
use htmd_lib::HtmlToMarkdown;
use pyo3_stub_gen::{define_stub_info_gatherer, derive::gen_stub_pyfunction};

// Import the Python option classes we defined
mod options;
use options::PyOptions;

/// Convert an HTML string to Markdown, with optional options.
#[gen_stub_pyfunction]
#[pyfunction(signature=(html, options=None))]
fn convert_html(html: &str, options: Option<PyOptions>) -> PyResult<String> {
    if let Some(py_opts) = options {
        let builder = HtmlToMarkdown::builder();
        let builder = py_opts.apply_to_builder(builder);

        let converter = builder.build();
        match converter.convert(html) {
            Ok(markdown) => Ok(markdown),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Conversion error: {}",
                e
            ))),
        }
    } else {
        // Use default options
        match htmd_convert(html) {
            Ok(markdown) => Ok(markdown),
            Err(e) => Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(format!(
                "Conversion error: {}",
                e
            ))),
        }
    }
}

/// Create options configured to skip specific HTML tags during conversion.
#[gen_stub_pyfunction]
#[pyfunction]
fn create_options_with_skip_tags(tags: Vec<String>) -> PyResult<PyOptions> {
    let mut options = PyOptions::new();
    options.skip_tags = tags;
    Ok(options)
}

#[pymodule]
fn htmd(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Expose the functions
    m.add_function(wrap_pyfunction!(convert_html, m)?)?;
    m.add_function(wrap_pyfunction!(create_options_with_skip_tags, m)?)?;

    // Expose the classes
    m.add_class::<PyOptions>()?;

    // Add enum constants for HeadingStyle
    let heading_style = PyModule::new(m.py(), "HeadingStyle")?;
    heading_style.setattr("ATX", "atx")?;
    heading_style.setattr("SETEX", "setex")?;
    m.setattr("HeadingStyle", heading_style)?;

    // Add enum constants for HrStyle
    let hr_style = PyModule::new(m.py(), "HrStyle")?;
    hr_style.setattr("DASHES", "dashes")?;
    hr_style.setattr("ASTERISKS", "asterisks")?;
    hr_style.setattr("UNDERSCORES", "underscores")?;
    m.setattr("HrStyle", hr_style)?;

    // Add enum constants for BrStyle
    let br_style = PyModule::new(m.py(), "BrStyle")?;
    br_style.setattr("TWO_SPACES", "two_spaces")?;
    br_style.setattr("BACKSLASH", "backslash")?;
    m.setattr("BrStyle", br_style)?;

    // Add enum constants for LinkStyle
    let link_style = PyModule::new(m.py(), "LinkStyle")?;
    link_style.setattr("INLINED", "inlined")?;
    link_style.setattr("REFERENCED", "referenced")?;
    m.setattr("LinkStyle", link_style)?;

    // Add enum constants for LinkReferenceStyle
    let link_reference_style = PyModule::new(m.py(), "LinkReferenceStyle")?;
    link_reference_style.setattr("FULL", "full")?;
    link_reference_style.setattr("COLLAPSED", "collapsed")?;
    link_reference_style.setattr("SHORTCUT", "shortcut")?;
    m.setattr("LinkReferenceStyle", link_reference_style)?;

    // Add enum constants for CodeBlockStyle
    let code_block_style = PyModule::new(m.py(), "CodeBlockStyle")?;
    code_block_style.setattr("INDENTED", "indented")?;
    code_block_style.setattr("FENCED", "fenced")?;
    m.setattr("CodeBlockStyle", code_block_style)?;

    // Add enum constants for CodeBlockFence
    let code_block_fence = PyModule::new(m.py(), "CodeBlockFence")?;
    code_block_fence.setattr("TILDES", "tildes")?;
    code_block_fence.setattr("BACKTICKS", "backticks")?;
    m.setattr("CodeBlockFence", code_block_fence)?;

    // Add enum constants for BulletListMarker
    let bullet_list_marker = PyModule::new(m.py(), "BulletListMarker")?;
    bullet_list_marker.setattr("ASTERISK", "asterisk")?;
    bullet_list_marker.setattr("DASH", "dash")?;
    m.setattr("BulletListMarker", bullet_list_marker)?;

    Ok(())
}

define_stub_info_gatherer!(stub_info);

use pyo3_stub_gen::Result;

fn main() -> Result<()> {
    let stub = htmd::stub_info()?;
    stub.generate()?;
    Ok(())
}

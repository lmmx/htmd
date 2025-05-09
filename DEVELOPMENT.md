## Release process

- `pre-commit run all-files`
- `maturin develop --release`
- `git push`
- `gh run download -p wheel*`
- `mv wheel*/* dist/ && rm -rf wheel* && pdm publish --no-build`

## Generate type stub (.pyi)

```
cargo run --bin stub_gen
mv ./htmd-py.pyi ./htmd.pyi

# Manual formatting and fine-tuning
```

## Trouble Shooting

#### link error for python3.13

```
  = note: mold: fatal: library not found: python3.13
          clang: error: linker command failed with exit code 1 (use -v to see invocation)
```

You should install Python3.13's shared libraries. On ubuntu:

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get install python3.13-dev
```

#### ModuleNotFoundError: No module named 'msvcrt'

You can just `uv venv`.

If this error occurs in IDE, you need to set ./.cargo/config.toml like the following:

```
[env]
PYO3_PYTHON = "YOUR_WORKSPACE/htmd/.venv/bin/python"
```

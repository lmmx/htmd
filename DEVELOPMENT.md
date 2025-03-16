## Release process

- `pre-commit run all-files`
- `maturin develop --release`
- `git push`
- `gh run download -p wheel*`
- `mv wheel*/* dist/ && rm -rf wheel* && pdm publish --no-build`

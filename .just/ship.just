# Release a new version, pass --help for options to `uv version --bump`
release bump_level="patch":
    #!/usr/bin/env -S echo-comment --shell-flags="-e" --color bright-green

    ## Exit early if help was requested
    if [[ "{{ bump_level }}" == "--help" ]]; then
        uv version --help
        exit 0
    fi

    # 📈 Bump the version in pyproject.toml (patch/minor/major: {{ bump_level }})
    uv version --frozen --bump {{ bump_level }}

    # 📦 Stage all changes (including the version bump)
    git add --all

    # 🔄 Create a temporary commit to capture the new version
    git commit -m "chore(temp): version check"

    # ✂️  Extract the new version number that was just set, undo the commit
    new_version=$(uv version --short)
    git reset --soft HEAD~1

    # 🦀 Sync the same version into Cargo.toml
    cargo set-version "$new_version"

    # ✅ Stage everything again and create the real release commit
    git add --all
    git commit -m "chore(release): bump 🐍🦀 -> v$new_version"

    # 🏷️ Create the git tag for this release
    git tag -a "v$new_version" -m "Release v$new_version"

    branch_name=$(git rev-parse --abbrev-ref HEAD);
    # 🚀 Push the release commit to $branch_name
    git push origin $branch_name

    # 🚀 Push the commit tag to the remote
    git push origin "v$new_version"

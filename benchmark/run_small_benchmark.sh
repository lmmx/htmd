(
    cd hello_world_x1000 && \
    hyperfine \
        'python htmd_bench.py' -n baseline \
        'python markdownify_bench.py' -n markdownify \
        --warmup 5
)

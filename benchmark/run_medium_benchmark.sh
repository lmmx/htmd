(
    cd turndown_test_index_x10 && \
    curl -sOL https://raw.githubusercontent.com/letmutex/htmd/main/tests/html/turndown_test_index.html && \
    hyperfine \
        'python htmd_bench.py' -n baseline \
        'python markdownify_bench.py' -n markdownify \
        --warmup 5
    rm turndown_test_index.html
)

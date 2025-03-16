from pathlib import Path

import htmd

HTML_TEXT = (Path(__file__).parent / "turndown_test_index.html").read_text()


def main():
    N = 10
    for _ in range(N):
        _ = htmd.convert_html(HTML_TEXT)


if __name__ == "__main__":
    main()

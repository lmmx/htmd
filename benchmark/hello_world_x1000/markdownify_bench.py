import markdownify

HTML_TEXT = """<html><head></head>
<body>
<h1>Example</h1>
<p>This is <em>bold</em> text with <a href="https://example.com">a link</a>.
<p>And some list:
<ul>
<li>item1</li>
<li>item2</li>
</ul>
<p>The end.</p>
</body>
</html>
"""


def main():
    N = 1000
    for _ in range(N):
        _ = markdownify.markdownify(HTML_TEXT)


if __name__ == "__main__":
    main()

import sys
import os

# Ensure we can import from lib
sys.path.append(os.getcwd())

from lib.scrape.optimize_html import extract_text_and_links

def test_extract_text_and_links():
    # Test 1: HTML with links
    html_with_links = """
    <html>
        <head>
            <title>Test</title>
            <script>console.log('bad');</script>
            <style>.bad { color: red; }</style>
        </head>
        <body>
            <h1>Welcome</h1>
            <p>Visit our <a href="https://example.com">website</a> for more info.</p>
            <p>Contact us at <a href="mailto:info@example.com">info@example.com</a></p>
            <a href="/page">Link with text</a>
            <script>alert('bad inside body');</script>
            <footer>Footer content</footer>
        </body>
    </html>
    """
    result = extract_text_and_links(html_with_links)
    print("--- Test 1 Result ---")
    print(result)
    print()
    assert "Welcome" in result
    assert "[website](https://example.com)" in result
    assert "[info@example.com](mailto:info@example.com)" in result
    assert "[Link with text](/page)" in result or "Link with text" in result
    # Ensure script content was removed
    assert "console.log" not in result
    assert "alert" not in result
    
    # Test 2: HTML without links
    html_no_links = """
    <html>
        <body>
            <h1>Title</h1>
            <p>Just plain text content.</p>
        </body>
    </html>
    """
    result2 = extract_text_and_links(html_no_links)
    print("--- Test 2 Result ---")
    print(result2)
    print()
    assert "Title" in result2
    assert "Just plain text content." in result2

    # Test 3: Link without href
    html_no_href = """
    <body>
        <a>Link without href</a>
        <p>Normal text</p>
    </body>
    """
    result3 = extract_text_and_links(html_no_href)
    print("--- Test 3 Result ---")
    print(result3)
    print()
    assert "Link without href" in result3
    assert "Normal text" in result3

    # Test 4: Multiple links in a paragraph
    html_multi_links = """
    <body>
        <p>Check <a href="/home">home</a> and <a href="/about">about</a> pages.</p>
    </body>
    """
    result4 = extract_text_and_links(html_multi_links)
    print("--- Test 4 Result ---")
    print(result4)
    print()
    assert "[home](/home)" in result4
    assert "[about](/about)" in result4

    print("\n✓ ALL TESTS PASSED")

if __name__ == "__main__":
    try:
        test_extract_text_and_links()
    except ImportError as e:
        print(f"ImportError: {e}")
        print("Please ensure beautifulsoup4 and lxml are installed.")
    except AssertionError as e:
        print(f"✗ Assertion failed: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()

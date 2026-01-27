import sys
import os
sys.path.append(os.getcwd())

from lib.scrape.optimize_html import extract_text_and_links

html = """
<html>
    <body>
        <p>Visit our <a href="https://example.com">website</a> for more.</p>
    </body>
</html>
"""

result = extract_text_and_links(html)
print("Result:")
print(repr(result))
print("\nFormatted:")
print(result)

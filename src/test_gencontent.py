import unittest
from gencontent import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_simple(self):
        markdown = "# Hello"
        self.assertEqual(extract_title(markdown), "Hello")
    
    def test_extract_title_with_whitespace(self):
        markdown = "#   Hello World   "
        self.assertEqual(extract_title(markdown), "Hello World")
    
    def test_extract_title_multiline(self):
        markdown = "# My Title\n\nSome content here"
        self.assertEqual(extract_title(markdown), "My Title")
    
    def test_extract_title_with_leading_newlines(self):
        markdown = "\n\n# My Title\n\nContent"
        self.assertEqual(extract_title(markdown), "My Title")
    
    def test_extract_title_h2_not_h1(self):
        markdown = "## This is h2\n# This is h1"
        self.assertEqual(extract_title(markdown), "This is h1")
    
    def test_extract_title_no_h1_raises_exception(self):
        markdown = "## This is h2\n\nSome content"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")
    
    def test_extract_title_empty_string_raises_exception(self):
        markdown = ""
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")
    
    def test_extract_title_only_paragraph_raises_exception(self):
        markdown = "This is just a paragraph"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")
    
    def test_extract_title_hash_without_space_not_h1(self):
        markdown = "#Not an h1"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")
    
    def test_extract_title_multiple_hashes_not_h1(self):
        markdown = "## This is h2"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No h1 header found in markdown")

    def test_eq(self):
        actual = extract_title("# This is a title")
        self.assertEqual(actual, "This is a title")

    def test_eq_double(self):
        actual = extract_title(
            """
# This is a title

# This is a second title that should be ignored
"""
        )
        self.assertEqual(actual, "This is a title")

    def test_eq_long(self):
        actual = extract_title(
            """
# title

this is a bunch

of text

- and
- a
- list
"""
        )
        self.assertEqual(actual, "title")

    def test_none(self):
        try:
            extract_title(
                """
no title
"""
            )
            self.fail("Should have raised an exception")
        except Exception as e:
            pass        


if __name__ == "__main__":
    unittest.main()

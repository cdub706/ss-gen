"""
Text Node Representation and Conversion

This module defines TextNode, which represents a piece of text with formatting
information (bold, italic, code, links, images). TextNodes are used as an
intermediate representation during markdown parsing before conversion to HTML.

The workflow: Markdown text -> TextNodes -> HTMLNodes -> HTML string
"""
from enum import Enum
from pydoc import text
from htmlnode import LeafNode

class TextType(Enum):
    """
    Enumeration of text formatting types supported in markdown.
    
    These correspond to different inline markdown elements:
    - TEXT: Plain unformatted text
    - BOLD: Bold text (**text**)
    - ITALIC: Italic text (_text_)
    - CODE: Inline code (`text`)
    - LINK: Hyperlink ([text](url))
    - IMAGE: Image (![alt](url))
    """
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    """
    Represents a segment of text with its formatting type.
    
    TextNodes are created during inline markdown parsing and serve as an
    intermediate representation before conversion to HTML. They preserve
    both the text content and its semantic meaning (bold, link, etc.).
    
    Attributes:
        text: The text content (for images, this is the alt text)
        text_type: A TextType enum indicating the formatting type
        url: Optional URL for links and images
    """
    def __init__(self, text, text_type, url=None):
        """
        Initialize a TextNode.
        
        Args:
            text: The text content string
            text_type: A TextType enum value indicating the formatting type
            url: Optional URL string (required for LINK and IMAGE types)
        """
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        """
        Equality comparison for TextNodes.
        
        Two TextNodes are equal if they have the same text, text_type, and url.
        Used primarily for testing and debugging.
        """
        return (
            isinstance(other, TextNode)
            and self.text == other.text 
            and self.text_type == other.text_type 
            and self.url == other.url
        )

    def __repr__(self):
        """String representation for debugging purposes."""
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
    """
    Converts a TextNode to its corresponding HTMLNode (LeafNode) representation.
    
    This function maps each TextType to its appropriate HTML tag:
    - TEXT -> plain text (no tag)
    - BOLD -> <b> tag
    - ITALIC -> <i> tag
    - CODE -> <code> tag
    - LINK -> <a> tag with href attribute
    - IMAGE -> <img> tag with src and alt attributes
    
    Args:
        text_node: The TextNode to convert
    
    Returns:
        LeafNode: An HTMLNode representing the text with appropriate HTML formatting
    
    Raises:
        ValueError: If the TextType is not recognized
    
    Example:
        TextNode("Hello", TextType.BOLD) -> LeafNode("b", "Hello")
        TextNode("Click", TextType.LINK, "/page") -> LeafNode("a", "Click", {"href": "/page"})
    """
    match text_node.text_type:
        case TextType.TEXT:
            # Plain text has no HTML tag
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            # Bold text uses <b> tag
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            # Italic text uses <i> tag
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            # Inline code uses <code> tag
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            # Links use <a> tag with href attribute
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            # Images use <img> tag with src and alt attributes
            # The text content becomes the alt text, url becomes the src
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})            
        case _:
            raise ValueError(f"invalid text type: {text_node.text_type}")

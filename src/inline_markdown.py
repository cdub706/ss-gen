"""
Inline Markdown Parsing Module

This module handles parsing inline markdown formatting within text blocks.
It processes elements like bold (**text**), italic (_text_), code (`text`),
links ([text](url)), and images (![alt](url)).

The parsing process works by splitting text nodes at delimiters and creating
new TextNodes with appropriate types. The order of processing is important
to handle nested and overlapping markdown syntax correctly.
"""
import re
from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Splits TextNodes at delimiter boundaries and creates new TextNodes with formatting.
    
    This function is used to parse bold (**text**), italic (_text_), and code (`text`)
    markdown syntax. It works by:
    1. Splitting each text node at the delimiter
    2. Alternating between plain text (even indices) and formatted text (odd indices)
    3. Creating new TextNodes with the appropriate text type
    
    Args:
        old_nodes: List of TextNodes to process (only TEXT nodes are split)
        delimiter: String delimiter to split on (e.g., "**" for bold, "_" for italic, "`" for code)
        text_type: TextType enum value to assign to delimited sections (e.g., TextType.BOLD)
    
    Returns:
        list: New list of TextNodes with formatting applied
    
    Raises:
        ValueError: If the delimiter is not properly closed (odd number of delimiters)
    
    Example:
        Input:  [TextNode("This is **bold** text", TextType.TEXT)], delimiter="**", TextType.BOLD
        Output: [TextNode("This is ", TextType.TEXT), TextNode("bold", TextType.BOLD), 
                 TextNode(" text", TextType.TEXT)]
    
    Note:
        Nodes that are not TextType.TEXT are passed through unchanged.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # Only process TEXT nodes - other types are already formatted and should pass through
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        # If text is empty, preserve it as-is
        if old_node.text == "":
            new_nodes.append(old_node)
            continue

        # Split the text at delimiter boundaries
        split_nodes = []
        sections = old_node.text.split(delimiter)
        
        # Validate delimiter pairing: must have odd number of sections
        # (even sections means unclosed delimiter: "text**bold")
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        
        # Alternate between plain text (even indices) and formatted text (odd indices)
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                # Even indices are plain text (outside delimiters)
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                # Odd indices are formatted text (inside delimiters)
                split_nodes.append(TextNode(sections[i], text_type))
        
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text):
    """
    Extracts all markdown image syntax from text using regex.
    
    Finds all patterns matching ![alt text](url) format.
    
    Args:
        text: String to search for image markdown
    
    Returns:
        list: List of tuples (alt_text, url) for each image found
    
    Example:
        Input:  'Text ![alt](image.png) more text'
        Output: [('alt', 'image.png')]
    """
    # Regex pattern: !\[...\]\(...\)
    # - !\[ matches literal '!['
    # - ([^\]]+) captures alt text (one or more non-] characters)
    # - \]\( matches literal ']('
    # - ([^\)]+) captures URL (one or more non-) characters)
    # - \) matches literal ')'
    pattern = r"!\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    """
    Extracts all markdown link syntax from text using regex.
    
    Finds all patterns matching [text](url) format (but not images).
    
    Args:
        text: String to search for link markdown
    
    Returns:
        list: List of tuples (link_text, url) for each link found
    
    Example:
        Input:  'Text [link](url.com) more text'
        Output: [('link', 'url.com')]
    """
    # Regex pattern: \[...\]\(...\)
    # Similar to images but without the ! prefix
    pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    """
    Splits TextNodes to extract markdown images (![alt](url)) and create IMAGE TextNodes.
    
    This function processes images before links because images have a '!' prefix.
    It preserves text before, between, and after images as separate TEXT nodes.
    
    Args:
        old_nodes: List of TextNodes to process (only TEXT nodes are examined)
    
    Returns:
        list: New list of TextNodes with IMAGE nodes inserted where images are found
    
    Example:
        Input:  [TextNode("Text ![alt](img.png) more", TextType.TEXT)]
        Output: [TextNode("Text ", TextType.TEXT), 
                 TextNode("alt", TextType.IMAGE, "img.png"),
                 TextNode(" more", TextType.TEXT)]
    
    Note:
        Nodes that are not TextType.TEXT are passed through unchanged.
        Uses regex finditer to preserve position information for splitting text.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # Only process TEXT nodes - other types are already processed
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        # Pattern matches ![alt](url) format
        pattern = r"!\[([^\]]+)\]\(([^\)]+)\)"
        # Use finditer to get match positions for splitting
        matches = list(re.finditer(pattern, text))
        
        # If no images found, pass through the node unchanged
        if not matches:
            new_nodes.append(old_node)
            continue
        
        # Build new nodes by splitting text around image matches
        split_nodes = []
        last_end = 0  # Track position in text for splitting
        
        for match in matches:
            # Add any text that appears before this image match
            if match.start() > last_end:
                text_before = text[last_end:match.start()]
                if text_before:
                    split_nodes.append(TextNode(text_before, TextType.TEXT))
            
            # Create an IMAGE TextNode from the match
            # Group 1 is alt text, Group 2 is URL
            alt_text = match.group(1)
            url = match.group(2)
            split_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            # Update position to after this match
            last_end = match.end()
        
        # Add any remaining text after the last image
        if last_end < len(text):
            text_after = text[last_end:]
            if text_after:
                split_nodes.append(TextNode(text_after, TextType.TEXT))
        
        new_nodes.extend(split_nodes)
    
    return new_nodes


def split_nodes_link(old_nodes):
    """
    Splits TextNodes to extract markdown links ([text](url)) and create LINK TextNodes.
    
    This function processes links after images using a negative lookbehind to ensure
    it doesn't match images (which start with !). It preserves text before, between,
    and after links as separate TEXT nodes.
    
    Args:
        old_nodes: List of TextNodes to process (only TEXT nodes are examined)
    
    Returns:
        list: New list of TextNodes with LINK nodes inserted where links are found
    
    Example:
        Input:  [TextNode("Text [link](url.com) more", TextType.TEXT)]
        Output: [TextNode("Text ", TextType.TEXT),
                 TextNode("link", TextType.LINK, "url.com"),
                 TextNode(" more", TextType.TEXT)]
    
    Note:
        Nodes that are not TextType.TEXT are passed through unchanged.
        The regex uses negative lookbehind (?<!!) to avoid matching images.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # Only process TEXT nodes - other types are already processed
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        # Pattern matches [text](url) but NOT ![text](url) (images)
        # (?<!!) is a negative lookbehind ensuring no '!' before '['
        pattern = r"(?<!!)\[([^\]]+)\]\(([^\)]+)\)"
        matches = list(re.finditer(pattern, text))
        
        # If no links found, pass through the node unchanged
        if not matches:
            new_nodes.append(old_node)
            continue
        
        # Build new nodes by splitting text around link matches
        split_nodes = []
        last_end = 0  # Track position in text for splitting
        
        for match in matches:
            # Add any text that appears before this link match
            if match.start() > last_end:
                text_before = text[last_end:match.start()]
                if text_before:
                    split_nodes.append(TextNode(text_before, TextType.TEXT))
            
            # Create a LINK TextNode from the match
            # Group 1 is link text, Group 2 is URL
            link_text = match.group(1)
            url = match.group(2)
            split_nodes.append(TextNode(link_text, TextType.LINK, url))
            
            # Update position to after this match
            last_end = match.end()
        
        # Add any remaining text after the last link
        if last_end < len(text):
            text_after = text[last_end:]
            if text_after:
                split_nodes.append(TextNode(text_after, TextType.TEXT))
        
        new_nodes.extend(split_nodes)
    
    return new_nodes


def text_to_textnodes(text):
    """
    Converts plain text with inline markdown syntax into a list of formatted TextNodes.
    
    This is the main entry point for inline markdown parsing. It processes text
    through multiple parsing stages in a specific order to handle nested and
    overlapping markdown syntax correctly.
    
    Processing order matters:
    1. Images first (they have unique ! prefix)
    2. Links second (uses negative lookbehind to exclude images)
    3. Bold (uses ** delimiter)
    4. Italic (uses _ delimiter) 
    5. Code (uses ` delimiter)
    
    This order ensures that more complex syntax is handled before simpler delimiters,
    preventing conflicts (e.g., images are processed before links which share [](url) syntax).
    
    Args:
        text: Plain text string containing inline markdown syntax
    
    Returns:
        list: List of TextNodes representing the text with formatting applied
    
    Example:
        Input:  'This is **bold** and has a [link](url.com)'
        Output: [TextNode('This is ', TextType.TEXT),
                 TextNode('bold', TextType.BOLD),
                 TextNode(' and has a ', TextType.TEXT),
                 TextNode('link', TextType.LINK, 'url.com')]
    """
    # Start with a single TextNode containing the entire text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Process images first - they have unique ! prefix, must be handled before links
    # This prevents links from matching image syntax
    nodes = split_nodes_image(nodes)
    
    # Process links second - uses negative lookbehind to avoid matching images
    # Images and links share [...] syntax, so order matters
    nodes = split_nodes_link(nodes)
    
    # Process bold text (**text**) - double asterisk delimiter
    # Bold is processed before italic to handle potential conflicts
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    
    # Process italic text (_text_) - underscore delimiter
    # Processed after bold because bold uses ** (two characters)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    
    # Process inline code (`text`) - backtick delimiter
    # Processed last as it's less likely to conflict with other syntax
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes    
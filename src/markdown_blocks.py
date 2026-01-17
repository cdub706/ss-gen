"""
Block-Level Markdown Parsing Module

This module handles parsing markdown at the block level (paragraphs, headings,
code blocks, quotes, lists). It splits markdown into blocks separated by blank
lines, identifies each block's type, and converts them to HTML nodes.

The parsing process:
1. Split markdown into blocks (separated by double newlines)
2. Identify each block's type (heading, code, quote, list, paragraph)
3. Convert each block to HTML nodes (which may contain inline formatting)

This works in conjunction with inline_markdown.py which handles formatting
within blocks (bold, italic, links, etc.).
"""
from enum import Enum
from htmlnode import ParentNode, LeafNode
from inline_markdown import text_to_textnodes
from textnode import text_node_to_html_node, TextNode, TextType

class BlockType(Enum):
    """
    Enumeration of markdown block types.
    
    Each type corresponds to a specific markdown syntax:
    - PARAGRAPH: Plain text blocks (default)
    - HEADING: Headings (# through ######)
    - CODE: Code blocks (```code```)
    - QUOTE: Blockquotes (> text)
    - UNORDERED_LIST: Bulleted lists (- item)
    - ORDERED_LIST: Numbered lists (1. item)
    """
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown):
    """
    Splits markdown text into individual blocks separated by blank lines.
    
    Markdown blocks are separated by double newlines (\n\n). This function
    splits the document at these boundaries and returns a list of block strings.
    
    Args:
        markdown: Complete markdown document as a string
    
    Returns:
        list: List of block strings (each block is stripped of leading/trailing whitespace)
    
    Example:
        Input:  "# Heading\\n\\nParagraph text.\\n\\n- List item"
        Output: ["# Heading", "Paragraph text.", "- List item"]
    """
    # Split markdown at double newlines (block separators)
    blocks = markdown.split("\n\n")
    
    # Filter out empty blocks and strip whitespace from each block
    result = []
    for block in blocks:
        stripped = block.strip()
        if stripped:  # Only add non-empty blocks
            result.append(stripped)
    
    return result

def block_to_block_type(block):
    """
    Identifies the type of a markdown block by examining its syntax.
    
    This function determines the block type by checking for specific markdown
    patterns in order of precedence. The order matters because some patterns
    can overlap (e.g., a heading could theoretically match list syntax).
    
    Block type detection order:
    1. Headings (# through ######)
    2. Code blocks (```)
    3. Quotes (>)
    4. Unordered lists (-)
    5. Ordered lists (1., 2., etc.)
    6. Paragraphs (default/fallback)
    
    Args:
        block: A single markdown block string to analyze
    
    Returns:
        BlockType: The identified block type enum value
    
    Example:
        Input:  "# Heading"
        Output: BlockType.HEADING
        
        Input:  "- Item 1\\n- Item 2"
        Output: BlockType.UNORDERED_LIST
    """
    lines = block.split("\n")
    
    # Check for heading: starts with 1-6 # characters followed by a space
    # Format: # Heading, ## Heading, etc. (up to ######)
    if block.startswith("#"):
        hash_count = 0
        # Count consecutive # characters at the start
        for char in block:
            if char == "#":
                hash_count += 1
            else:
                break
        # Validate: must be 1-6 hashes, followed by a space (not empty or 7+ hashes)
        if hash_count >= 1 and hash_count <= 6 and len(block) > hash_count and block[hash_count] == " ":
            return BlockType.HEADING
    
    # Check for code block: starts and ends with ```
    # Format: ```\\ncode\\n```
    if block.startswith("```") and block.endswith("```"):
        # Validate that it starts with ``` followed by a newline
        # This distinguishes code blocks from inline code
        if len(block) > 3 and block[3] == "\n":
            return BlockType.CODE
    
    # Check for quote block: every non-empty line starts with ">"
    # Format: > Quote text\\n> More quote text
    # Must have at least one line with "> " (with space) to be a valid quote
    if lines:
        has_quote_marker = False
        is_quote = True
        for line in lines:
            stripped = line.strip()
            if stripped:  # Only check non-empty lines
                if line.startswith("> "):
                    # Valid quote marker with space
                    has_quote_marker = True
                elif not line.startswith(">"):
                    # Line doesn't start with > - not a quote block
                    is_quote = False
                    break
        # Quote blocks must have at least one line with proper "> " syntax
        if is_quote and has_quote_marker:
            return BlockType.QUOTE
    
    # Check for unordered list: every non-empty line starts with "- "
    # Format: - Item 1\\n- Item 2
    if lines and all(line.startswith("- ") for line in lines if line.strip()):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list: lines start with "1. ", "2. ", "3. ", etc.
    # Format: 1. First item\\n2. Second item\\n3. Third item
    # Must start at 1 and increment sequentially
    if lines:
        is_ordered = True
        expected_num = 1
        for line in lines:
            if not line.strip():
                # Skip empty lines in ordered lists
                continue
            # Check if line starts with the expected number followed by ". "
            if not line.startswith(f"{expected_num}. "):
                is_ordered = False
                break
            expected_num += 1
        
        # At least one numbered line must match (expected_num > 1)
        if is_ordered and expected_num > 1:
            return BlockType.ORDERED_LIST
    
    # Default to paragraph if no other type matches
    return BlockType.PARAGRAPH


def text_to_children(text):
    """
    Converts text with inline markdown formatting to a list of HTMLNodes.
    
    This is a helper function that bridges inline markdown parsing (text_to_textnodes)
    and HTML generation (text_node_to_html_node). It processes inline formatting
    like bold, italic, links, and images within block text.
    
    Args:
        text: Text string that may contain inline markdown syntax
    
    Returns:
        list: List of HTMLNodes (LeafNodes) representing the formatted text
    
    Example:
        Input:  "This is **bold** text"
        Output: [LeafNode(None, "This is "), LeafNode("b", "bold"), LeafNode(None, " text")]
    """
    # Parse inline markdown into TextNodes
    text_nodes = text_to_textnodes(text)
    # Convert each TextNode to its corresponding HTMLNode
    html_nodes = []
    for text_node in text_nodes:
        html_nodes.append(text_node_to_html_node(text_node))
    return html_nodes


def heading_to_html_node(block):
    """
    Converts a heading block to an HTMLNode (h1 through h6).
    
    Extracts the heading level from the number of # characters and the
    heading text, then processes any inline markdown within the heading.
    
    Args:
        block: Heading block string (e.g., "## My Heading")
    
    Returns:
        ParentNode: HTMLNode with tag h1-h6 containing formatted text children
    
    Example:
        Input:  "## My Heading"
        Output: ParentNode("h2", [LeafNode(...)])  # with formatted children
    """
    # Extract heading level by counting consecutive # characters
    hash_count = 0
    for char in block:
        if char == "#":
            hash_count += 1
        else:
            break
    
    # Extract text after the hashes and space (e.g., "## Heading" -> "Heading")
    text = block[hash_count + 1:].strip()
    # Process inline markdown in the heading text
    children = text_to_children(text)
    # Create heading tag (h1, h2, ..., h6)
    return ParentNode(f"h{hash_count}", children)


def code_to_html_node(block):
    """
    Converts a code block to an HTMLNode wrapped in <pre><code> tags.
    
    Code blocks are special: they do NOT process inline markdown formatting.
    The code content is treated as literal text to preserve code formatting,
    syntax highlighting indicators, and special characters.
    
    Args:
        block: Code block string (e.g., "```\\ncode here\\n```")
    
    Returns:
        ParentNode: HTMLNode with structure <pre><code>content</code></pre>
    
    Example:
        Input:  "```\\npython\\nprint('hello')\\n```"
        Output: ParentNode("pre", [ParentNode("code", [LeafNode(...)])])
    
    Note:
        The code content is extracted by removing the opening "```\\n" (4 chars)
        and closing "```" (3 chars) from the block.
    """
    # Extract content between ``` and ```
    # Remove the opening ```\n (4 characters) and closing ``` (3 characters)
    content = block[4:-3]
    # Create a plain text node (no inline markdown parsing for code blocks)
    text_node = TextNode(content, TextType.TEXT)
    code_node = text_node_to_html_node(text_node)
    # Wrap code in <pre><code> tags for proper HTML formatting
    return ParentNode("pre", [ParentNode("code", [code_node])])


def quote_to_html_node(block):
    """
    Converts a quote block to an HTMLNode wrapped in <blockquote> tags.
    
    Removes the ">" markers from each line of the quote block and processes
    any inline markdown formatting within the quote text.
    
    Args:
        block: Quote block string (e.g., "> Quote text\\n> More text")
    
    Returns:
        ParentNode: HTMLNode with tag "blockquote" containing formatted text children
    
    Example:
        Input:  "> This is a **quote**\\n> with multiple lines"
        Output: ParentNode("blockquote", [LeafNode(...)])  # with formatted children
    
    Note:
        Lines starting with "> " have the prefix removed. Lines starting with just ">"
        (without space) are treated as empty lines.
    """
    lines = block.split("\n")
    # Remove ">" or "> " prefix from each line and preserve the structure
    text_lines = []
    for line in lines:
        if line.startswith("> "):
            # Standard quote line: remove "> " prefix (2 characters)
            text_lines.append(line[2:])
        elif line.startswith(">"):
            # Line is just ">" or ">" followed by whitespace - treat as empty line
            text_lines.append("")
        elif line.strip():
            # Line without > prefix (shouldn't happen in valid quotes, but handle gracefully)
            text_lines.append(line)
    
    # Join lines back together and process inline markdown
    text = "\n".join(text_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    """
    Converts an unordered list block to an HTMLNode wrapped in <ul> tags.
    
    Each line starting with "- " becomes a list item (<li>). Inline markdown
    formatting within list items is processed.
    
    Args:
        block: Unordered list block string (e.g., "- Item 1\\n- Item 2")
    
    Returns:
        ParentNode: HTMLNode with tag "ul" containing "li" children
    
    Example:
        Input:  "- First **item**\\n- Second item"
        Output: ParentNode("ul", [ParentNode("li", [...]), ParentNode("li", [...])])
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        if line.startswith("- "):
            # Extract item text by removing "- " prefix (2 characters)
            item_text = line[2:].strip()
            # Process inline markdown in the item text
            children = text_to_children(item_text)
            # Create list item node
            list_items.append(ParentNode("li", children))
    
    # Wrap all items in <ul> tag
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    """
    Converts an ordered list block to an HTMLNode wrapped in <ol> tags.
    
    Each line starting with "number. " (1., 2., 3., etc.) becomes a list item.
    The number prefix is removed, and inline markdown formatting within items
    is processed.
    
    Args:
        block: Ordered list block string (e.g., "1. First\\n2. Second")
    
    Returns:
        ParentNode: HTMLNode with tag "ol" containing "li" children
    
    Example:
        Input:  "1. First *item*\\n2. Second item"
        Output: ParentNode("ol", [ParentNode("li", [...]), ParentNode("li", [...])])
    
    Note:
        The number prefix is removed by splitting on ". " and taking the second part.
        This handles any number (1. through N.) without needing to parse the number.
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Find the first ". " to remove the number prefix (e.g., "1. ", "2. ")
        if ". " in line:
            # Split on ". " and take everything after it as the item text
            item_text = line.split(". ", 1)[1].strip()
            # Process inline markdown in the item text
            children = text_to_children(item_text)
            # Create list item node
            list_items.append(ParentNode("li", children))
    
    # Wrap all items in <ol> tag
    return ParentNode("ol", list_items)


def paragraph_to_html_node(block):
    """
    Converts a paragraph block to an HTMLNode wrapped in <p> tags.
    
    Paragraphs are the default block type. Newlines within a paragraph are
    converted to spaces (HTML paragraphs are single-line blocks). Inline
    markdown formatting within paragraphs is processed.
    
    Args:
        block: Paragraph block string (plain text, possibly with newlines)
    
    Returns:
        ParentNode: HTMLNode with tag "p" containing formatted text children
    
    Example:
        Input:  "This is a paragraph with **bold** text"
        Output: ParentNode("p", [LeafNode(...)])  # with formatted children
    """
    # Replace newlines with spaces for paragraph text
    # HTML paragraphs don't preserve line breaks within the paragraph
    text = block.replace("\n", " ")
    # Process inline markdown in the paragraph text
    children = text_to_children(text)
    return ParentNode("p", children)


def markdown_to_html_node(markdown):
    """
    Converts a complete markdown document into a single HTMLNode tree.
    
    This is the main entry point for markdown-to-HTML conversion. It processes
    the document in stages:
    1. Splits the markdown into blocks
    2. Identifies each block's type
    3. Converts each block to HTML nodes (which includes inline formatting)
    4. Wraps all blocks in a root <div> node
    
    Args:
        markdown: Complete markdown document as a string
    
    Returns:
        ParentNode: Root HTMLNode containing all blocks as children, wrapped in <div>
    
    Example:
        Input:  "# Heading\\n\\nParagraph with **bold**.\\n\\n- List item"
        Output: ParentNode("div", [
            ParentNode("h1", [...]),      # heading
            ParentNode("p", [...]),       # paragraph
            ParentNode("ul", [...]),      # list
        ])
    
    Note:
        Each block is processed independently. Inline markdown within blocks
        is handled by the individual block conversion functions.
    """
    # Step 1: Split markdown into individual blocks
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    
    # Step 2: Convert each block to HTML based on its type
    for block in blocks:
        # Identify the block type
        block_type = block_to_block_type(block)
        
        # Convert block to HTML node based on type
        if block_type == BlockType.HEADING:
            html_nodes.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            html_nodes.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            html_nodes.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            html_nodes.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            html_nodes.append(ordered_list_to_html_node(block))
        else:  # PARAGRAPH (default/fallback)
            html_nodes.append(paragraph_to_html_node(block))
    
    # Step 3: Wrap all blocks in a root <div> node
    return ParentNode("div", html_nodes)
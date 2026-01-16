from enum import Enum
from htmlnode import ParentNode, LeafNode
from inline_markdown import text_to_textnodes
from textnode import text_node_to_html_node, TextNode, TextType

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown):
    blocks = markdown.split("\n\n")
    
    result = []
    for block in blocks:
        stripped = block.strip()
        if stripped:  # Only add non-empty blocks
            result.append(stripped)
    
    return result

def block_to_block_type(block):
    lines = block.split("\n")
    
    # Check for heading (1-6 # characters followed by space)
    if block.startswith("#"):
        hash_count = 0
        for char in block:
            if char == "#":
                hash_count += 1
            else:
                break
        if hash_count >= 1 and hash_count <= 6 and len(block) > hash_count and block[hash_count] == " ":
            return BlockType.HEADING
    
    # Check for code block (starts with 3 backticks and newline, ends with 3 backticks)
    if block.startswith("```") and block.endswith("```"):
        # Check if it starts with ```\n (3 backticks followed by newline)
        if len(block) > 3 and block[3] == "\n":
            return BlockType.CODE
    
    # Check for quote block (every non-empty line starts with ">")
    # Must have at least one line with "> " (with space) to be a quote
    if lines:
        has_quote_marker = False
        is_quote = True
        for line in lines:
            stripped = line.strip()
            if stripped:
                if line.startswith("> "):
                    has_quote_marker = True
                elif not line.startswith(">"):
                    is_quote = False
                    break
        if is_quote and has_quote_marker:
            return BlockType.QUOTE
    
    # Check for unordered list (every line starts with "- ")
    if lines and all(line.startswith("- ") for line in lines if line.strip()):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (every line starts with number. and space, starting at 1)
    if lines:
        is_ordered = True
        expected_num = 1
        for line in lines:
            if not line.strip():
                continue
            # Check if line starts with "number. "
            if not line.startswith(f"{expected_num}. "):
                is_ordered = False
                break
            expected_num += 1
        
        if is_ordered and expected_num > 1:  # At least one line matched
            return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def text_to_children(text):
    """Convert text with inline markdown to a list of HTMLNodes."""
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_nodes.append(text_node_to_html_node(text_node))
    return html_nodes


def heading_to_html_node(block):
    """Convert a heading block to an HTMLNode."""
    # Extract heading level and text
    hash_count = 0
    for char in block:
        if char == "#":
            hash_count += 1
        else:
            break
    
    # Get text after the hashes and space
    text = block[hash_count + 1:].strip()
    children = text_to_children(text)
    return ParentNode(f"h{hash_count}", children)


def code_to_html_node(block):
    """Convert a code block to an HTMLNode. Special case: no inline parsing."""
    # Extract content between ``` and ```
    # Remove the opening ```\n and closing ```
    content = block[4:-3]  # Remove ```\n at start and ``` at end
    # Create a TextNode and convert it (no inline parsing)
    text_node = TextNode(content, TextType.TEXT)
    code_node = text_node_to_html_node(text_node)
    # Wrap in <pre><code>
    return ParentNode("pre", [ParentNode("code", [code_node])])


def quote_to_html_node(block):
    """Convert a quote block to an HTMLNode."""
    lines = block.split("\n")
    # Remove ">" or "> " prefix from each line and join with newlines
    text_lines = []
    for line in lines:
        if line.startswith("> "):
            text_lines.append(line[2:])
        elif line.startswith(">"):
            # Line is just ">" or ">" followed by whitespace - treat as empty line
            text_lines.append("")
        elif line.strip():
            text_lines.append(line)
    
    text = "\n".join(text_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    """Convert an unordered list block to an HTMLNode."""
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        if line.startswith("- "):
            item_text = line[2:].strip()
            children = text_to_children(item_text)
            list_items.append(ParentNode("li", children))
    
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    """Convert an ordered list block to an HTMLNode."""
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Find the first ". " to remove the number prefix
        if ". " in line:
            item_text = line.split(". ", 1)[1].strip()
            children = text_to_children(item_text)
            list_items.append(ParentNode("li", children))
    
    return ParentNode("ol", list_items)


def paragraph_to_html_node(block):
    """Convert a paragraph block to an HTMLNode."""
    # Replace newlines with spaces for paragraph text
    text = block.replace("\n", " ")
    children = text_to_children(text)
    return ParentNode("p", children)


def markdown_to_html_node(markdown):
    """Convert a full markdown document into a single parent HTMLNode."""
    blocks = markdown_to_blocks(markdown)
    html_nodes = []
    
    for block in blocks:
        block_type = block_to_block_type(block)
        
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
        else:  # PARAGRAPH
            html_nodes.append(paragraph_to_html_node(block))
    
    return ParentNode("div", html_nodes)
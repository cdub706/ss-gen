import re
from textnode import TextNode, TextType


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        # If text is empty, preserve it
        if old_node.text == "":
            new_nodes.append(old_node)
            continue

        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.TEXT))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes


def extract_markdown_images(text):
    pattern = r"!\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    matches = re.findall(pattern, text)
    return matches


def split_nodes_image(old_nodes):
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        pattern = r"!\[([^\]]+)\]\(([^\)]+)\)"
        matches = list(re.finditer(pattern, text))
        
        if not matches:
            new_nodes.append(old_node)
            continue
        
        split_nodes = []
        last_end = 0
        
        for match in matches:
            # Add text before the match
            if match.start() > last_end:
                text_before = text[last_end:match.start()]
                if text_before:
                    split_nodes.append(TextNode(text_before, TextType.TEXT))
            
            # Add the image node
            alt_text = match.group(1)
            url = match.group(2)
            split_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            
            last_end = match.end()
        
        # Add remaining text after the last match
        if last_end < len(text):
            text_after = text[last_end:]
            if text_after:
                split_nodes.append(TextNode(text_after, TextType.TEXT))
        
        new_nodes.extend(split_nodes)
    
    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        pattern = r"(?<!!)\[([^\]]+)\]\(([^\)]+)\)"
        matches = list(re.finditer(pattern, text))
        
        if not matches:
            new_nodes.append(old_node)
            continue
        
        split_nodes = []
        last_end = 0
        
        for match in matches:
            # Add text before the match
            if match.start() > last_end:
                text_before = text[last_end:match.start()]
                if text_before:
                    split_nodes.append(TextNode(text_before, TextType.TEXT))
            
            # Add the link node
            link_text = match.group(1)
            url = match.group(2)
            split_nodes.append(TextNode(link_text, TextType.LINK, url))
            
            last_end = match.end()
        
        # Add remaining text after the last match
        if last_end < len(text):
            text_after = text[last_end:]
            if text_after:
                split_nodes.append(TextNode(text_after, TextType.TEXT))
        
        new_nodes.extend(split_nodes)
    
    return new_nodes


def text_to_textnodes(text):
    # Start with a single TextNode containing the entire text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Process images first (they have ! prefix)
    nodes = split_nodes_image(nodes)
    
    # Process links second (they use [...] syntax but not images)
    nodes = split_nodes_link(nodes)
    
    # Process bold text (**text**)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    
    # Process italic text (_text_)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    
    # Process code blocks (`text`)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes    
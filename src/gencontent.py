import os
from markdown_blocks import markdown_to_html_node


def extract_title(markdown):
    lines = markdown.split("\n")
    
    for line in lines:
        stripped = line.strip()
        # Check if line starts with exactly one # followed by a space
        if stripped.startswith("# ") and not stripped.startswith("##"):
            # Extract title: remove "# " and strip whitespace
            title = stripped[2:].strip()
            return title
    
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    title = extract_title(markdown_content)
    
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(final_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    # Walk through the content directory recursively
    for root, dirs, files in os.walk(dir_path_content):
        for file in files:
            # Only process markdown files
            if file.endswith(".md"):
                # Get the full path to the markdown file
                markdown_path = os.path.join(root, file)
                
                # Calculate the relative path from content directory
                rel_path = os.path.relpath(markdown_path, dir_path_content)
                
                # Convert .md to .html and create destination path
                rel_html_path = rel_path.replace(".md", ".html")
                dest_path = os.path.join(dest_dir_path, rel_html_path)
                
                # Generate the page
                generate_page(markdown_path, template_path, dest_path)


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
    
    # No h1 header found
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read markdown file
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Read template file
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Create destination directory if it doesn't exist
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the final HTML file
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(final_html)

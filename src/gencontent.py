"""
Content Generation Module

This module handles converting markdown files to HTML pages by:
1. Reading markdown content and extracting the title
2. Converting markdown to HTML using the markdown parser
3. Injecting the content into the HTML template
4. Adjusting asset paths for deployment (basepath support)
"""
import os
from markdown_blocks import markdown_to_html_node


def extract_title(markdown):
    """
    Extracts the page title from the first H1 heading (# Title) in markdown.
    
    The title is used for the HTML <title> tag and page metadata.
    An H1 heading is identified by exactly one '#' followed by a space.
    
    Args:
        markdown: The markdown content string to extract the title from
    
    Returns:
        str: The title text (without the # prefix)
    
    Raises:
        ValueError: If no H1 heading is found in the markdown
    
    Example:
        Input:  "# My Page Title\\nContent here..."
        Output: "My Page Title"
    """
    lines = markdown.split("\n")
    
    for line in lines:
        stripped = line.strip()
        # Check if line starts with exactly one # followed by a space
        # Must check for "##" to avoid matching H2+ headings
        if stripped.startswith("# ") and not stripped.startswith("##"):
            # Extract title: remove "# " prefix and strip any remaining whitespace
            title = stripped[2:].strip()
            return title
    
    raise ValueError("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path, basepath):
    """
    Generates a single HTML page from a markdown file.
    
    This function performs the complete conversion process:
    1. Reads the markdown source file
    2. Converts markdown to HTML
    3. Extracts the page title
    4. Injects title and content into the template
    5. Adjusts asset paths (href/src) for the deployment basepath
    6. Writes the final HTML to the destination path
    
    Args:
        from_path: Path to the source markdown file
        template_path: Path to the HTML template file
        dest_path: Destination path where the HTML file will be written
        basepath: Base path prefix for asset URLs (e.g., "/ss-gen/" or "/")
    
    The basepath is prepended to all absolute paths (starting with "/") in href
    and src attributes, allowing the site to be deployed in subdirectories.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown source file
    with open(from_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Read the HTML template file
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()
    
    # Convert markdown to HTML using the markdown parser
    # This returns a tree of HTMLNode objects representing the document structure
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract the page title from the first H1 heading
    title = extract_title(markdown_content)
    
    # Inject the title and content into the template
    # The template uses {{ Title }} and {{ Content }} as placeholders
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Adjust asset paths for deployment basepath
    # This allows the site to work when deployed to a subdirectory (e.g., GitHub Pages)
    # Example: href="/images/logo.png" becomes href="/ss-gen/images/logo.png"
    final_html = final_html.replace('href="/', f'href="{basepath}')
    final_html = final_html.replace('src="/', f'src="{basepath}')
    
    # Ensure the destination directory exists before writing the file
    # This handles nested directory structures (e.g., blog/post/index.html)
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Write the final HTML to the destination file
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(final_html)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    """
    Recursively processes all markdown files in the content directory.
    
    This function walks through the entire content directory tree and converts
    each .md file to an .html file, preserving the directory structure in the
    output. For example:
    - content/blog/post.md -> docs/blog/post.html
    - content/about/index.md -> docs/about/index.html
    
    Args:
        dir_path_content: Root directory containing markdown source files
        template_path: Path to the HTML template file
        dest_dir_path: Root directory where HTML files will be generated
        basepath: Base path prefix for asset URLs in generated HTML
    """
    # Walk through the content directory recursively
    # This visits all subdirectories and files
    for root, dirs, files in os.walk(dir_path_content):
        for file in files:
            # Only process markdown files (ignore other file types)
            if file.endswith(".md"):
                # Get the full absolute path to the markdown file
                markdown_path = os.path.join(root, file)
                
                # Calculate the relative path from the content root directory
                # This preserves the nested directory structure
                rel_path = os.path.relpath(markdown_path, dir_path_content)
                
                # Convert .md extension to .html and create the destination path
                # This maintains the same directory structure in the output
                rel_html_path = rel_path.replace(".md", ".html")
                dest_path = os.path.join(dest_dir_path, rel_html_path)
                
                # Generate the HTML page from the markdown file
                generate_page(markdown_path, template_path, dest_path, basepath)


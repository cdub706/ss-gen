"""
Static Site Generator - Main Entry Point

This module orchestrates the entire static site generation process:
1. Cleans the output directory
2. Copies static assets (CSS, images) to the output directory
3. Converts all markdown files to HTML pages using the template
"""
import os, shutil, sys
from copystatic import copy_directory
from gencontent import generate_pages_recursive

# Directory paths for the static site generation process
dir_path_static = "./static"      # Source directory for static assets (CSS, images)
dir_path_public = "./docs"        # Output directory where the final HTML site is generated
dir_path_content = "./content"    # Source directory containing markdown content files
template_path = "./template.html" # HTML template file used to wrap generated content

def main():
    """
    Main function that drives the static site generation process.
    
    Workflow:
    1. Accepts an optional basepath argument (e.g., "/ss-gen/") for asset paths
    2. Deletes the existing output directory to ensure a clean build
    3. Copies all static assets from static/ to docs/
    4. Recursively processes all .md files in content/ and generates HTML pages
    """
    # Get basepath from CLI argument, default to "/" for root-level deployment
    # The basepath is used to adjust href/src paths in generated HTML (e.g., for GitHub Pages)
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    
    # Step 1: Clean the output directory for a fresh build
    print("Deleting docs directory...")
    if os.path.exists(dir_path_public):
        shutil.rmtree(dir_path_public)

    # Step 2: Copy static assets (CSS, images, etc.) to the output directory
    # This preserves the directory structure from static/ to docs/
    print("Copying static files to docs directory...")
    copy_directory(dir_path_static, dir_path_public)
    
    # Step 3: Convert all markdown files to HTML pages
    # This recursively processes the content directory and generates HTML files
    # in the same directory structure within docs/
    print("Generating content...")
    generate_pages_recursive(dir_path_content, template_path, dir_path_public, basepath)

if __name__ == "__main__":
    main()
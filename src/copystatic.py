"""
Static File Copying Module

This module handles copying static assets (CSS, images, etc.) from the source
directory to the output directory, preserving the directory structure.
"""
import os
import shutil

def copy_directory(src_dir, dest_dir):
    """
    Recursively copies all files and directories from src_dir to dest_dir.
    
    This function ensures that static assets like CSS files and images are
    available in the output directory at the correct paths. The destination
    directory is cleaned before copying to ensure no stale files remain.
    
    Args:
        src_dir: Source directory containing static assets to copy
        dest_dir: Destination directory where files will be copied to
    
    Note:
        The destination directory is completely removed and recreated to
        ensure a clean copy without orphaned files from previous builds.
    """
    # Validate that the source directory exists before attempting to copy
    if not os.path.exists(src_dir):
        print(f"Error: Source directory '{src_dir}' does not exist")
        return
    
    # Clean the destination directory if it exists to ensure a fresh copy
    # This removes any files that may have been deleted from the source
    if os.path.exists(dest_dir):
        print(f"Cleaning destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create the destination directory structure
    os.mkdir(dest_dir)
    print(f"Created destination directory: {dest_dir}")
    
    def copy_recursive(src, dest):
        """
        Internal recursive function that copies files and directories.
        
        For each item in the source directory:
        - If it's a file: copy it directly to the destination
        - If it's a directory: create it in the destination and recurse into it
        
        Args:
            src: Current source path (file or directory)
            dest: Current destination path (file or directory)
        """
        # List all items (files and directories) in the current source directory
        items = os.listdir(src)
        
        for item in items:
            src_path = os.path.join(src, item)
            dest_path = os.path.join(dest, item)
            
            if os.path.isfile(src_path):
                # Copy individual files directly
                shutil.copy(src_path, dest_path)
                print(f"Copied file: {src_path} -> {dest_path}")
            else:
                # Create the destination directory and recurse into it
                # This preserves the nested directory structure from static/
                os.mkdir(dest_path)
                print(f"Created directory: {dest_path}")
                copy_recursive(src_path, dest_path)
    
    # Initiate the recursive copying process starting from the root directories
    copy_recursive(src_dir, dest_dir)
    print(f"Finished copying from {src_dir} to {dest_dir}")
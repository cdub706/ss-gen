import os
import shutil

def copy_directory(src_dir, dest_dir):
    # Check if source directory exists
    if not os.path.exists(src_dir):
        print(f"Error: Source directory '{src_dir}' does not exist")
        return
    
    # Delete all contents of destination directory if it exists
    if os.path.exists(dest_dir):
        print(f"Cleaning destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Create the destination directory
    os.mkdir(dest_dir)
    print(f"Created destination directory: {dest_dir}")
    
    def copy_recursive(src, dest):
        # List all items in source directory
        items = os.listdir(src)
        
        for item in items:
            src_path = os.path.join(src, item)
            dest_path = os.path.join(dest, item)
            
            if os.path.isfile(src_path):
                # Copy file
                shutil.copy(src_path, dest_path)
                print(f"Copied file: {src_path} -> {dest_path}")
            else:
                # It's a directory, create it and recurse
                os.mkdir(dest_path)
                print(f"Created directory: {dest_path}")
                copy_recursive(src_path, dest_path)
    
    # Start the recursive copy
    copy_recursive(src_dir, dest_dir)
    print(f"Finished copying from {src_dir} to {dest_dir}")
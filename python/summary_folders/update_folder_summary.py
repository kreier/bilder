import os
import sys
import csv
import pandas as pd
from openpyxl.utils import get_column_letter

def parse_folders(target_dir):
    """
    Parses the target directory and generates two reports:
    1. Detailed Report: Recursive stats for folders up to depth 2.
    2. Summary Report: Recursive stats for immediate children (depth 1).
    """
    target_dir = os.path.abspath(target_dir)
    
    if not os.path.isdir(target_dir):
        print(f"Error: {target_dir} is not a valid directory.")
        return

    print(f"Recursively analyzing directory: {target_dir}")

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tiff']
    
    # 1. Collect 'Flat' stats for EVERY directory in the tree
    flat_stats = {} # path -> {bytes, images, other, immediate_dirs_count}
    
    for root, dirs, files in os.walk(target_dir):
        b, img, oth = 0, 0, 0
        for f in files:
            fp = os.path.join(root, f)
            try:
                sz = os.path.getsize(fp)
                b += sz
                _, ext = os.path.splitext(f)
                if ext.lower() in image_extensions:
                    img += 1
                else:
                    oth += 1
            except (OSError, PermissionError):
                continue
        flat_stats[root] = {'b': b, 'img': img, 'oth': oth, 'dir_count': len(dirs)}

    # 2. Helper to get recursive stats for any path
    def get_recursive_stats(start_path):
        rb, rimg, roth, rsubs = 0, 0, 0, 0
        for path, stats in flat_stats.items():
            # If path is start_path or a subdirectory of start_path
            if path == start_path or path.startswith(start_path + os.sep):
                rb += stats['b']
                rimg += stats['img']
                roth += stats['oth']
                if path != start_path:
                    rsubs += 1
        return rb, rimg, roth, rsubs

    # 3. Build Detailed Data (Recursive, Depth <= 2)
    detail_data = []
    COL_PATH, COL_SIZE, COL_SIZE_MB, COL_IMAGES, COL_OTHER, COL_SUBS = "Folder Path", "Size (Bytes)", "Size (MB)", "Image Files", "Other Files", "Subfolders"

    # To maintain order and find depths, we iterate through the keys sorted by path
    for path in sorted(flat_stats.keys()):
        rel_path = os.path.relpath(path, target_dir)
        depth = 0 if rel_path == "." else rel_path.replace(os.sep, '/').count('/') + 1
        
        if depth <= 2:
            rb, rimg, roth, rsubs = get_recursive_stats(path)
            display_path = "./" if rel_path == "." else rel_path
            detail_data.append({
                COL_PATH: display_path,
                COL_SIZE: rb,
                COL_SIZE_MB: round(rb / (1024 * 1024), 2),
                COL_IMAGES: rimg,
                COL_OTHER: roth,
                COL_SUBS: rsubs
            })

    # 4. Build Summary Data (Recursive, Immediate Children Only)
    summary_data = []
    S_NAME, S_MB, S_FILES, S_SUBS = "Folder Name", "Size (MB)", "Number of Files", "Number of Subfolders"
    
    # Target immediate children
    try:
        children = [os.path.join(target_dir, d) for d in os.listdir(target_dir) if os.path.isdir(os.path.join(target_dir, d))]
        for child_path in sorted(children):
            rb, rimg, roth, rsubs = get_recursive_stats(child_path)
            summary_data.append({
                S_NAME: os.path.basename(child_path),
                S_MB: round(rb / (1024 * 1024), 2),
                S_FILES: rimg + roth,
                S_SUBS: rsubs
            })
    except PermissionError:
        print("Warning: Could not list children for summary due to permissions.")

    # 5. Export Logic
    def save_report(df, base_filename, sheet_name):
        csv_fn = f"{base_filename}.csv"
        excel_fn = f"{base_filename}.xlsx"
        
        df.to_csv(csv_fn, index=False)
        print(f"Generated: {csv_fn}")
        
        try:
            with pd.ExcelWriter(excel_fn, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name=sheet_name)
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(df.columns):
                    max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4
                    worksheet.column_dimensions[get_column_letter(i + 1)].width = max_len
            print(f"Generated: {excel_fn}")
        except Exception as e:
            print(f"Excel export failed for {excel_fn}: {e}")

    # Process Reports
    if detail_data:
        save_report(pd.DataFrame(detail_data), "folder_detail", "Folder Detail")
    
    if summary_data:
        save_report(pd.DataFrame(summary_data), "folder_summary", "Folder Summary")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    parse_folders(target)

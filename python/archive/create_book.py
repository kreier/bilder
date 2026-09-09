import os
import csv

def list_folders_files_and_size(directory):
    folders_info = {}
    for name in os.listdir(directory):
        folder_path = os.path.join(directory, name)
        if os.path.isdir(folder_path):
            subfolders = [sub for sub in os.walk(folder_path)][1:]
            file_count = 0
            total_size = 0
            for root, dirs, files in os.walk(folder_path):
                file_count += len(files)
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
            folders_info[name] = {
                "subfolder_count": len(subfolders),
                "file_count": file_count,
                "total_size": total_size,
                "total_size_bytes": total_size
            }
    return folders_info

def size_format(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

current_directory = os.getcwd()
folders_info = list_folders_files_and_size(current_directory)

csv_file = "folder_info.csv"
# with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
#     writer = csv.writer(file)
#     writer.writerow(["Folder", "Subfolder Count", "File Count", "Total Size", "Total Size (Bytes)"])
#     for folder, info in folders_info.items():
#         size_str = size_format(info["total_size"])
#         writer.writerow([folder, info['subfolder_count'], info['file_count'], size_str, info['total_size_bytes']])

print(f"Results exported to {csv_file}")
print(folders_info)

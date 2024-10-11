import os

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
                "total_size": total_size
            }
    return folders_info

def size_format(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

current_directory = os.getcwd()
folders_info = list_folders_files_and_size(current_directory)

print("Folders, their subfolder counts, file counts, and total sizes in the current directory:")
for folder, info in folders_info.items():
    size_str = size_format(info["total_size"])
    print(f"{folder}: {info['subfolder_count']} subfolders, {info['file_count']} files, {size_str}")

import os

def list_folders_and_subfolders(directory):
    folders_info = {}
    for name in os.listdir(directory):
        folder_path = os.path.join(directory, name)
        if os.path.isdir(folder_path):
            subfolders = [sub for sub in os.walk(folder_path)][1:]
            folders_info[name] = len(subfolders)
    return folders_info

current_directory = os.getcwd()
folders_info = list_folders_and_subfolders(current_directory)

print("Folders and their subfolder counts in the current directory:")
for folder, subfolder_count in folders_info.items():
    print(f"{folder}: {subfolder_count} subfolders")

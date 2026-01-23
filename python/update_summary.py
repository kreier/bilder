import os
import csv
import pandas as pd

def get_folder_info(base_path):
    folder_data = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            folder_size = 0
            num_pictures = 0
            num_other_files = 0
            num_subfolders = 0

            for root, dirs, files in os.walk(item_path):
                num_subfolders += len(dirs)
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        folder_size += os.path.getsize(file_path)
                    except OSError:
                        continue
                    
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp')):
                        num_pictures += 1
                    else:
                        num_other_files += 1

            folder_data.append([item, folder_size, num_pictures, num_other_files, num_subfolders])
    return folder_data

def write_to_csv_and_excel(data, csv_file="pictures_summary.csv", excel_file="pictures_summary.xlsx"):
    headers = ["Folder Name", "Size (bytes)", "Number of Pictures", "Number of Other Files", "Number of Subfolders"]
    
    # Write CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(data)
    
    # Write Excel using pandas
    df = pd.DataFrame(data, columns=headers)
    df.to_excel(excel_file, index=False)

if __name__ == "__main__":
    base_path = os.getcwd()
    folder_info = get_folder_info(base_path)
    write_to_csv_and_excel(folder_info)
    print("Reports generated: pictures_summary.csv and pictures_summary.xlsx")

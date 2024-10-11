# Bilder

Support tool to organize and categorize my image collection.

## Rationale

I store my images sorted by years, with a folder for each year. Inside these folders there are subfolders for each event. The name style of these subfolders is `MMDD_Description_of_the_Event`. The pictures of a visit to Shanghai on the first of August in 2024 would therefore be in the folder `/2024/0801_Shanghai/`.

The goal for the `investigate.py` app is therefore to scan the folders with the years, and create a `.csv` file with colums for all folders, the number of subfolders, number of files, and total size of the folder.

A later `investigate_events.py` will be more verbose about the events. Since the folder name structure is defined the events can be named (with removing the _ characters) and the correct month and day of the event.

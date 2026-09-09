import os
from glob import glob

photo_dir = "/path/to/icloud/photos"
photos = glob(os.path.join(photo_dir, "*.jpg"))

for photo in photos:
    print(photo)


from PIL import Image
from PIL.ExifTags import TAGS

image = Image.open("example.jpg")
exif_data = image._getexif()

if exif_data:
    for tag, value in exif_data.items():
        tag_name = TAGS.get(tag, tag)
        print(f"{tag_name}: {value}")


import exifread

with open("example.jpg", "rb") as f:
    tags = exifread.process_file(f)

for tag in tags.keys():
    print(f"{tag}: {tags[tag]}")


from datetime import datetime

date_taken = exif_data.get(36867)  # DateTimeOriginal
if date_taken:
    dt = datetime.strptime(date_taken, "%Y:%m:%d %H:%M:%S")
    print("Photo taken on:", dt)

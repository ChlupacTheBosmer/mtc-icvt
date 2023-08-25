from modules.utility.validator import validate_folders
from mtc_crop import mtcCrop
import sys
import os

def retrieve_args():
    batch_folder_path = None
    if os.path.isdir(sys.argv[1]):
        batch_folder_path = sys.argv[1] if len(sys.argv) > 1 else None
    print("Batch folder path:", batch_folder_path)
    return batch_folder_path

if __name__ == "__main__":

    # Retrieve arguments: Path to the batch folder
    batch_folder_path = retrieve_args()

    # Get only validated sub-folders which contain videos and a json save file
    video_folder_paths = validate_folders(batch_folder_path)

    # For every video folder open a separate cropper instance (PARA)
    for i, video_folder_path in enumerate(video_folder_paths):
        cropper = mtcCrop(video_folder_path, os.path.join(video_folder_path, "output"))

    #
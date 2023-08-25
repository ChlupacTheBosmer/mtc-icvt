import os

def delete_picture_files(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)

        for file in files:
            # Check if the file has a picture extension
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                file_path = os.path.join(folder_path, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

        print("Picture files deleted successfully.")

        return True

    except Exception as e:
        print("An error occurred:", e)

        return False

def delete_video_files(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(folder_path)

        for file in files:
            # Check if the file has a video extension
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                file_path = os.path.join(folder_path, file)
                os.remove(file_path)
                print(f"Deleted: {file_path}")

        print("Video files deleted successfully.")

        return True

    except Exception as e:
        print("An error occurred:", e)

        return False

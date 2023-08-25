import os

def validate_folders(root_folder):
    valid_subfolders = []

    for foldername, subfolders, filenames in os.walk(root_folder):
        if subfolders:
            has_video = False
            has_json = False

            for filename in filenames:
                if filename.endswith('.mp4') or filename.endswith('.avi'):
                    has_video = True
                if filename.endswith('.json'):
                    has_json = True

            if has_video and has_json:
                valid_subfolders.append(foldername)

            print(f"Subfolder: {foldername}")
            print(f"Has Video: {has_video}")
            print(f"Has JSON: {has_json}")
            print("")

    return valid_subfolders

def generator_has_elements(generator):
    try:
        # Try to iterate over the generator
        next(generator)
        return True  # Generator has elements
    except StopIteration:
        return False  # Generator is empty

if __name__ == '__main__':
    root_folder = "../.."
    valid_subfolders = validate_folders(root_folder)

    print("Valid Subfolders:")
    for folder in valid_subfolders:
        print(folder)
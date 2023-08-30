# Import ICVT components
from modules.base.icvt import AppAncestor
from modules.utility import utils
from modules.video import video_passive
from modules.crop import crop
from modules.database import sqlite_data
from modules.video import construct_video
from modules.utility import validator
from modules.yolo.yolo_video_od_simple import detect_visitors_on_video

# Part of python modules
import configparser
import json
import os
import cv2
import datetime
import cProfile

class mtcCrop(AppAncestor):
    def __init__(self, video_folder_path, output_folder_path):

        # Print the current time in default format (including date and microseconds)
        print("Start Time:", datetime.datetime.now())

        # Define logger
        self.logger = self.log_define()

        # First log
        self.logger.info("Initializing mtcCropE - Metacentrum Crop Engine class...")

        # Create config and read file
        self.config = self.config_create()
        self.config_read()

        # Define variables

        # Obsolete but neccessary
        self.default_label_category = 0
        self.randomize = 0
        self.scanned_folders = []
        self.dir_hierarchy = False
        self.loaded = False
        self.crop_mode: int = 3
        self.frames_per_visit = 0
        self.auto = 0
        self.frames = []
        self.modified_frames = []
        self.button_images = []
        self.buttons = []
        self.gui_imgs = []
        self.main_window = None

        # In active use
        self.video_filepaths = []
        self.points_of_interest_entry = []
        self.cap = None
        self.image_details_dict = {}
        self.frame_metadata_database = None
        self.visit_index = 0

        # Assign folders
        # TODO: Decide how the folder paths will be defined (via a file / string passed as arg)
        self.output_folder = output_folder_path
        self.video_folder_path = video_folder_path

        # Construct ROI data
        # TODO: Move to crop.py both here and in iccs.py
        self.reload_roi_entries()

        # Create output folders
        utils.create_dir(self.output_folder)
        if self.whole_frame > 0:
            utils.create_dir(os.path.join(self.output_folder, "whole frames"))

        # Load video files
        self.load_videos()

        # Load the save file
        self.load_progress()

        # Simply run YOLO on every video
        # self.frame_metadata_database = self.create_frame_database()
        # frame_number = 0
        # for i, video_filepath in enumerate(self.video_filepaths):
        #     detection_metadata = detect_visitors_on_video(video_filepath, os.path.join('resources', 'yolo', 'best.pt'))
        #     for dict in detection_metadata:
        #         frame_number += 1


        # # Run the crop engine
        self.crop_engine()

        # Print the current time in default format (including date and microseconds)
        print("End Time:", datetime.datetime.now())


        # script_path = os.path.join("modules", "database", "query_get_unique_values_of_roi.sql")
        # result = self.frame_metadata_database.execute_sql_script(script_path)
        # for i, roi_number in enumerate(result):
        #     print(roi_number[0])
        #     query_params = (roi_number[0],)
        #     script_path = os.path.join("modules", "database", "query_get_frame_paths_by_roi.sql")
        #     frame_paths = self.frame_metadata_database.execute_sql_script(script_path, query_params)
        #     video_generated, video_file_path = construct_video.create_video_from_frames(frame_paths, f"video_od_{roi_number[0]}.mp4")


    def get_valid_folder(self, folder_name):
        while True:
            folder_path = input(f'Enter the path to your {folder_name} folder. Make sure it is correct. Do not use quotes: ')

            # Check if the path exists and is a directory
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                return folder_path
            else:
                print("Invalid path. Please provide a valid directory path.")

    def config_create(self):
        # Set default values
        config = configparser.ConfigParser()
        config['Crop settings'] = {
            'crop_interval_frames': '30',
            'yolo_processing': '0',
            'yolo_conf': '0.25',
            'export_whole_frame': '0',
            'export_crops': '1',
            'crop_size': '640',
            'random_offset_range': '100',
            'filename_prefix': ''
        }

        # Check if settings_crop.ini exists, and create it with default values if not
        if not os.path.exists('settings_mtc_crop.ini'):
            with open('settings_mtc_crop.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        return config

    def config_read(self):

        # Define logger
        self.logger.debug('Running function config_read()')

        try:
            # Read settings from settings_crop.ini
            self.config.read('settings_mtc_crop.ini', encoding='utf-8')

            # Get crop values from config
            self.frame_skip = int(self.config['Crop settings'].get('crop_interval_frames', '30').strip())
            self.yolo_processing = int(self.config['Crop settings'].get('yolo_processing', '0').strip())
            self.yolo_conf = float(self.config['Crop settings'].get('yolo_conf', '0.25').strip())
            self.whole_frame = int(self.config['Crop settings'].get('export_whole_frame', '0').strip())
            self.cropped_frames = int(self.config['Crop settings'].get('export_crops', '1').strip())
            self.crop_size = int(self.config['Crop settings'].get('crop_size', '640').strip())
            self.offset_range = int(self.config['Crop settings'].get('random_offset_range', '100').strip())
            self.prefix = self.config['Crop settings'].get('filename_prefix', '').strip()

        except ValueError:
            self.logger.warning('Invalid folder/file path or crop settings found in settings_crop.ini')

    def config_write(self):

        # Define logger
        self.logger.debug("Running function config_write()")
        config = self.config
        config.read('settings_mtc_crop.ini')

        # Update values in the config file
        config.set('Crop settings', 'crop_interval_frames', str(self.frame_skip))
        config.set('Crop settings', 'yolo_processing', str(self.yolo_processing))
        config.set('Crop settings', 'yolo_conf', str(self.yolo_conf))
        config.set('Crop settings', 'export_whole_frame', str(self.whole_frame))
        config.set('Crop settings', 'export_crops', str(self.cropped_frames))
        config.set('Crop settings', 'crop_size', str(self.crop_size))
        config.set('Crop settings', 'random_offset_range', str(self.offset_range))
        config.set('Crop settings', 'filename_prefix', str(self.prefix))

        # Save changes to the config file
        with open('settings_mtc_crop.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)

    def reload_roi_entries(self):
        self.logger.debug('Running function reload_points_of_interest()')

        # Clear the array of POIs and reconstruct it with empty lists.
        self.points_of_interest_entry.clear()
        self.points_of_interest_entry = [[[], filepath] for filepath in self.video_filepaths]

    # TODO: Modify so that only video names are loaded. After all the script is supplied the folder with the videos,
    #  therefore, it doesn't need to have a full path in the save file. It only creates issues.
    def load_progress(self):

        # Define logger
        self.logger.debug(f"Running function load_progress()")

        # Confirm with the user if they want to load the settings
        result = str(input("Do you want to load settings? This will overwrite any unsaved progress. (y/n):"))

        if result == "y":

            # Call the function to get a valid output folder
            save_file_folder = self.video_folder_path

            if utils.check_path(save_file_folder, 0):

                # Create an in-memory file object
                filepath = os.path.join(save_file_folder, 'crop_information.json')
                if os.path.isfile(filepath):
                    try:
                        if self.main_window.winfo_exists():
                            self.main_window.destroy()
                    except:
                        self.logger.debug("Error: Unexpected, window destroyed before reference.")
                    self.points_of_interest_entry = []
                    with open(filepath, "r") as json_file:
                        data_combined = json.load(json_file)

                        # Restore data from dictionary
                        self.auto = (data_combined["auto_processing"])
                        data_matched = data_combined["video_data"]
                        self.points_of_interest_entry = [item for item in data_matched.values()]
                        video_filepaths_new = [item[1] for item in data_matched.values()]

                    # Compare the loaded and the currently found video filepaths.
                    set1 = set({os.path.basename(filepath) for filepath in video_filepaths_new})
                    print(set1)
                    set2 = set({os.path.basename(filepath) for filepath in self.video_filepaths})
                    print(set2)
                    if not set1 == set2:
                        print("The contents of the video folder have changed since the save has been made. "
                              "Cannot load the progress. Please start over.")
                        self.reload_roi_entries()
                    else:
                        self.video_filepaths = []
                        prefix = save_file_folder

                        # Create a new list with modified base names
                        self.video_filepaths = [os.path.join(prefix, os.path.basename(path)) for path in video_filepaths_new]
                        print(self.video_filepaths)
                else:
                    print("There are no save files in the current directory.")
            else:
                print("Invalid video folder path")

    def create_frame_database(self):

        database_path = os.path.join(self.video_folder_path, "frame_metadata.db")
        frame_metadata_database = sqlite_data.frameDatabase(database_path)

        return frame_metadata_database

    # TODO: Modify
    def crop_engine(self):

        # Define logger
        self.logger.debug("Running function crop_engine()")

        # Define variables
        self.image_details_dict = {}

        # Ask to confirm whether the process should begin
        # Confirm with the user if they want to load the settings
        result = str(input("Do you want to start the cropping process? (y/n):"))

        if result == "y":
            self.logger.info("Initializing the cropping engine...")

            # Check if some ROIs were selected
            if len(self.points_of_interest_entry[0][0]) == 0:
                print("No regions of interest selected. Please select at least one ROI.")
                return

            # Define arrays
            valid_annotations_array = []
            valid_annotation_data_entry = []

            # Close window and start cropping
            self.logger.debug(f"Start cropping on the following videos: {self.video_filepaths}")

            # Check validity of paths
            video_ok = utils.check_path(self.video_folder_path, 0)
            if not video_ok:
                print(f"Unspecified path to a video folder.")
                return

            # Create database of frame metadata
            self.frame_metadata_database = self.create_frame_database()

            # The whole frame settings is artificially altered to allow for whole frame generation - messy
            orig_wf = self.whole_frame
            self.whole_frame = 0

            # Starting from the second frame of every video frames are generated. (could PARA)
            for i, video_filepath in enumerate(self.video_filepaths):

                self.video_file_object = video_passive.VideoFilePassive(video_filepath)
                total_frames = self.video_file_object.total_frames
                visit_duration = total_frames // self.video_file_object.fps
                frame_number_start = 1

                # TODO: Make this work so that the roi gets paired reliably to the video
                # try:
                #     roi_index = next(
                #         ix for ix, sublist in enumerate(self.points_of_interest_entry) if sublist[1] == video_filepath)
                # except StopIteration:
                #     roi_index = 0
                #     self.logger.warning("No ROI entry found for a video file. Defaults to index 0")

                # Define a video writer and variables
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                frame_size = None
                video_writers = {}
                entry_skeleton = [self.video_file_object.recording_identifier, self.video_file_object.timestamp]

                # Generator will contain a cropped frame from the video and should be processed further
                frame_generator = crop.generate_frames(self, self.video_file_object,
                                                       self.points_of_interest_entry[i][0], frame_number_start,
                                                       visit_duration, frames_to_skip=self.frame_skip, name_prefix=self.prefix)

                for frame in frame_generator:
                    img = frame.frame

                    # Whenever a frame with new roi_number comes, new video file for that roi is created and frame
                    # counter for that roi number and video writer is initiated.
                    if frame.roi_number not in video_writers:
                        if frame_size is None:
                            frame_size = (img.shape[1], img.shape[0])
                        video_filepath = os.path.join(self.output_folder, f"crop_video_roi_{frame.roi_number}.mp4")
                        video_writers[frame.roi_number] = {
                            'writer': cv2.VideoWriter(video_filepath, fourcc, 25, frame_size),
                            'frame_count': 0,  # Initialize the frame count for each ROI
                            'frame_entries': []
                        }

                    video_writers[frame.roi_number]['writer'].write(img)
                    video_writers[frame.roi_number]['frame_count'] += 1  # Increment frame count

                    entry = entry_skeleton + [frame.roi_number, frame.frame_number, frame.visit_number,
                                              frame.crop_upper_left_corner[0], frame.crop_upper_left_corner[1],
                                              frame.crop_bottom_right_corner[0], frame.crop_bottom_right_corner[1],
                                              frame.name, video_writers[frame.roi_number]['frame_count'],
                                              0, 0, [], [], []]
                    video_writers[frame.roi_number]['frame_entries'].append(entry)

                # Release video writers and print frame counts
                for roi_number, writer_info in video_writers.items():
                    writer_info['writer'].release()
                    print(f"ROI {roi_number} wrote {writer_info['frame_count']} frames.")

                # Update the database
                for key, value in video_writers.items():
                    self.frame_metadata_database.add_multiple_entries(video_writers[key]['frame_entries'])

                # Run object detection on each roi specific video and update database entries
                for key, value in video_writers.items():
                    update_entries = []
                    video_file_path = os.path.join(self.output_folder, f"crop_video_roi_{key}.mp4")
                    detection_metadata = detect_visitors_on_video(video_file_path)

                    for data in detection_metadata:
                        update_entries.append(data + [key])

                    self.frame_metadata_database.update_detection_to_last_column(update_entries)


if __name__ == '__main__':
    cProfile.run("mtc_crop = mtcCrop('videos', 'output')")
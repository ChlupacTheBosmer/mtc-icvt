# Part of python modules
import datetime
import itertools
import multiprocessing
import os

# Import ICVT components
from modules.database import sqlite_data
from modules.video import video_passive
from modules.yolo.yolo_video_od_simple import detect_visitors_on_video


def process_video(video_filepath):
    video_file = video_passive.VideoFilePassive(video_filepath)
    database_path = os.path.join("videos", f"{video_file.recording_identifier}_{video_file.timestamp}_frame_metadata.db")
    frame_metadata_database = sqlite_data.frameDatabase(database_path)
    width, height = video_file.get_frame_shape()
    entry_skeleton = [video_file.recording_identifier, video_file.timestamp, -1, 0, -1, 0, 0, width, height, "", -1]
    database_entries = []
    detection_metadata = detect_visitors_on_video(video_file.filepath, os.path.join('resources', 'yolo', 'best.pt'),(height, width), frames_to_skip=15)
    for data in detection_metadata:
        entry_skeleton[3] = data[0]
        entry = entry_skeleton + data[1:]
        database_entries.append(entry)
    frame_metadata_database.add_multiple_entries(database_entries)


if __name__ == "__main__":
    print("Start Time:", datetime.datetime.now())
    num_processes = multiprocessing.cpu_count()  # Use the number of available CPU cores
    chunk_size = 1
    video_filepaths = [r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_09_29.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_09_59.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_10_29.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_10_44.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_17_14.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220525_09_17.mp4"]  # List of your video filepaths

    chunks = iter(video_filepaths)
    for chunk in iter(lambda: list(itertools.islice(chunks, chunk_size)), []):
       with multiprocessing.Pool(processes=num_processes) as pool:
           pool.map(process_video, chunk)

    print("All chunks processed")
    print("End Time:", datetime.datetime.now())


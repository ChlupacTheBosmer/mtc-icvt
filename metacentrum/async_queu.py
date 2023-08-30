import asyncio
import itertools as it
import os
import random
import time
import imageio
import cv2
from modules.video.video_passive import VideoFilePassive
from modules.crop.crop import icvtFrame
import threading
import queue as qut
from concurrent.futures import ThreadPoolExecutor, as_completed


def generate_frame_indices(total_frames, frames_to_skip):

    # Generate a list of indices of every n-th frame
    frame_indices = list(range(1, total_frames, frames_to_skip))

    # Make sure that the last index doesn't exceed the total_frames
    frame_indices = [idx for idx in frame_indices if idx < total_frames]

    return frame_indices

def crop_frame(rois, frame, frame_metadata, crop_size, offset_range):

    recording_identifier, timestamp, frame_number = frame_metadata

    for i, point in enumerate(rois):

        # Prepare local variables
        x, y = point

        # Add a random offset to the coordinates, but ensure they remain within the image bounds
        frame_height, frame_width,_ = frame.shape

        # Check if any of the dimensions is smaller than crop_size and if so
        # upscale the image to prevent crops smaller than desired crop_size
        if frame_height < crop_size or frame_width < crop_size:
            # Calculate the scaling factor to upscale the image
            scaling_factor = crop_size / min(frame_height, frame_width)

            # Calculate the new dimensions for the upscale frame
            new_width = int(round(frame_width * scaling_factor))
            new_height = int(round(frame_height * scaling_factor))

            # Upscale the frame using cv2.resize with Lanczos up-scaling algorithm
            frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)


        # Get the new frame size
        frame_height, frame_width,_ = frame.shape

        # Calculate the coordinates for the area that will be cropped
        x_offset = random.randint(-offset_range, offset_range)
        y_offset = random.randint(-offset_range, offset_range)
        x1 = max(0, min(((x - crop_size // 2) + x_offset), frame_width - crop_size))
        y1 = max(0, min(((y - crop_size // 2) + y_offset), frame_height - crop_size))
        x2 = max(crop_size, min(((x + crop_size // 2) + x_offset), frame_width))
        y2 = max(crop_size, min(((y + crop_size // 2) + y_offset), frame_height))

        # Crop the image

        crop = frame[y1:y2, x1:x2]


        # Convert to correct color space
        crop_img = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        if crop_img.shape[2] == 3:
            crop_img = cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB)

        cropped_frame = icvtFrame(crop_img, recording_identifier, timestamp, frame_number, i + 1,
                                  (x1, y1), (x2, y2))

        yield cropped_frame


def producer_task(filepath, queue):
    video_object_file = VideoFilePassive(filepath)
    frame_indices = generate_frame_indices(video_object_file.total_frames, 150)

    if video_object_file.video_origin == "MS":
        for frame_list in video_object_file.read_frames_imageio(frame_indices):
            queue.put(frame_list)
            print(f"Producer <{os.path.basename(filepath)}> added <{frame_list[2]}> to queue.")
    else:
        for frame_list in video_object_file.read_frames_decord(frame_indices):
            queue.put(frame_list)
            print(f"Producer <{os.path.basename(filepath)}> added <{frame_list[2]}> to queue.")
    return True

def process_frame(frame_list, rois):
    recording_identifier, timestamp, frame_number, frame, _ = frame_list
    yield from crop_frame(rois, frame, [recording_identifier, timestamp, frame_number], 640, 100)

def consumer_task(name, rois, queue):
    c = (
        "\033[0m",  # End of color
        "\033[36m",  # Cyan
        "\033[91m",  # Red
        "\033[35m",  # Magenta
    )
    print(f"Consumer {name} created.")
    while True:
        frame_list = queue.get()
        if frame_list is None:
            print(f"Consumer {name} finished.")
            break

        recording_identifier, timestamp, frame_number, frame, _ = frame_list
        now = time.perf_counter()
        print(f"Consumer {name} got element <{frame_number}> at {now}")

        cropped_frames = process_frame(frame_list, rois)
        for frame in cropped_frames:
            print(c[2] + f"FUCK YEEES {frame.name}" + c[0])


def main(nprod: int, ncon: int, filepaths: list, rois: list):
    queue = qut.Queue()  # Create a shared queue

    with ThreadPoolExecutor(max_workers=nprod + ncon) as executor:
        producer_futures = []
        for filepath in filepaths[:nprod]:
            future = executor.submit(producer_task, filepath, queue)
            producer_futures.append(future)

        consumer_futures = []
        for n in range(ncon):
            future = executor.submit(consumer_task, n, rois[n % len(rois)], queue)
            consumer_futures.append(future)

        for future in as_completed(producer_futures):
            print(f"<{future}> completed.")

        for _ in range(ncon):
            queue.put(None)


def determine_optimal_thread_count():
    # Calculate optimal thread count based on available system resources
    max_threads = os.cpu_count()  # Use the number of CPU cores as a starting point
    # You can adjust max_threads based on your requirements and testing
    return max_threads

if __name__ == "__main__":
    import argparse
    import multiprocessing
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--nprod", type=int, default=1)
    parser.add_argument("-c", "--ncon", type=int, default=1)
    parser.add_argument("-fp", "--filepaths", type=list, default=[r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_09_29.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_09_59.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_10_29.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_10_44.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_17_14.mp4", r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220525_09_17.mp4"])
    parser.add_argument("-rs", "--rois", type=list, default=[[[300, 300], [320, 400]], [[300, 300], [320, 400]], [[300, 300], [320, 400]], [[300, 300], [320, 400]], [[300, 300], [320, 400]], [[300, 300], [320, 400]]])
    ns = parser.parse_args()
    start = time.perf_counter()
    main(**ns.__dict__)
    elapsed = time.perf_counter() - start
    print(f"Program completed in {elapsed:0.5f} seconds.")





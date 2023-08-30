# import asyncio
# import cv2
#
# async def count():
#     print("One")
#     await asyncio.sleep(1)
#     print("Two")
#
# async def get_cap(frame_no):
#     cap = cv2.VideoCapture(r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_09_29.mp4")
#     cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
#     return cap
#
# async def get_frame(cap):
#     success, frame = cap.read()
#     cap.release()
#     return frame
#
# def getr(frame_no):
#     cap = cv2.VideoCapture(r"D:\Dílna\Kutění\Python\ICCS\icvt\videos\GR2_L2_LavSto2_20220524_09_29.mp4")
#     cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
#     success, frame = cap.read()
#     cap.release()
#     return frame
#
# async def framin(frame_no):
#     import time
#     print("One")
#     cap = await get_cap(frame_no)
#     print("Two")
#     frame = await get_frame(cap)
#     print("Three")
#     cv2.imshow(f"{time.perf_counter()}", frame)
#     cv2.waitKey(1)
#
# async def main():
#    # await asyncio.gather(count(), count(), count())
#     await asyncio.gather(framin(250), framin(3056), framin(9000))
#
# if __name__ == "__main__":
#     import time
#     s = time.perf_counter()
#     asyncio.run(main())
#     elapsed = time.perf_counter() - s
#     print(f"{__file__} executed in {elapsed:0.2f} seconds.")
#
#     s = time.perf_counter()
#     frame = getr(896)
#     cv2.imshow(f"{time.perf_counter()}", frame)
#     cv2.waitKey(1)
#     frame = getr(8745)
#     cv2.imshow(f"{time.perf_counter()}", frame)
#     cv2.waitKey(1)
#     frame = getr(5555)
#     cv2.imshow(f"{time.perf_counter()}", frame)
#     cv2.waitKey(1)
#     elapsed = time.perf_counter() - s
#     print(f"{__file__} executed in {elapsed:0.2f} seconds.")

import asyncio
import random

# ANSI colors
c = (
    "\033[0m",   # End of color
    "\033[36m",  # Cyan
    "\033[91m",  # Red
    "\033[35m",  # Magenta
)

async def makerandom(idx: int, threshold: int = 6) -> int:
    print(c[idx + 1] + f"Initiated makerandom({idx}).")
    i = random.randint(0, 10)
    while i <= threshold:
        print(c[idx + 1] + f"makerandom({idx}) == {i} too low; retrying.")
        await asyncio.sleep(idx + 1)
        i = random.randint(0, 10)
    print(c[idx + 1] + f"---> Finished: makerandom({idx}) == {i}" + c[0])
    return i

async def main():
    res = await asyncio.gather(*(makerandom(i, 10 - i - 1) for i in range(3)))
    return res

if __name__ == "__main__":
    random.seed(444)
    r1, r2, r3 = asyncio.run(main())
    print()
    print(f"r1: {r1}, r2: {r2}, r3: {r3}")
import logging
import cv2
from pathlib import Path
from PIL import Image
from moviepy import VideoFileClip
from video_processing.loader import inspect_video, extract_audio_from_video
logger = logging.getLogger(__name__)


def extract_frame_at_time(video_path: str, output_path: str, t_seconds: float) -> str:

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    clip = VideoFileClip(str(video_path))
    try:
        clip.save_frame(output_path, t=t_seconds)
        logger.info(f'Saved frame at t={t_seconds}s -> {output_path}')
        return output_path
    finally:
        clip.close()


def extract_keyframes(video_path: str, output_dir: str, interval_seconds: float = 5.0) -> list:

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    clip   = VideoFileClip(str(video_path))
    saved  = []
    try:
        total = clip.duration
        t     = 0.0
        while t < total:
            fname = Path(output_dir) / f'frame_{int(t):04d}.png'
            clip.save_frame(str(fname), t=t)
            saved.append(str(fname))
            t += interval_seconds
        logger.info(
            f'Extracted {len(saved)} keyframes from {Path(video_path).name} '
            f'(every {interval_seconds}s)'
        )
    finally:
        clip.close()
    return saved


def extract_keyframes_opencv(video_path: str, output_dir: str, interval_seconds: float = 5.0) -> list:

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    cap   = cv2.VideoCapture(str(video_path))
    fps   = cap.get(cv2.CAP_PROP_FPS)
    step  = int(fps * interval_seconds)
    saved = []
    frame_num = 0
    idx       = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_num % step == 0:
            rgb   = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img   = Image.fromarray(rgb)
            fname = Path(output_dir) / f'frame_{idx:04d}.png'
            img.save(str(fname))
            saved.append(str(fname))
            idx += 1
        frame_num += 1
    cap.release()
    logger.info(f'OpenCV extracted {len(saved)} keyframes')
    return saved



# VIDEO = 'data/raw/video/Inception _ The Dream Sequence _ HBO Max_trailer.mp4'

# # Inspect video properties
# info = inspect_video(VIDEO)
# print(f"Duration: {info['duration_s']}s, FPS: {info['fps']}, ",
#       f"Resolution: {info['resolution']}")

# # Extract a single frame at the 5-second mark
# frame_path = extract_frame_at_time(VIDEO, 'data/processed/frames/thumb.png', t_seconds=5.0)
# print(f'Saved frame: {frame_path}')

# # Extract keyframes every 10 seconds
# frames = extract_keyframes(VIDEO, 'data/processed/frames/', interval_seconds=10.0)
# print(f'Extracted {len(frames)} keyframes')
# for f in frames:
#     print(f'  {f}')

# # Extract audio track
# audio_path = extract_audio_from_video(VIDEO, 'data/processed/audio/video_audio.mp3')
# print(f'Extracted audio: {audio_path}')

video_folder = Path("../../data/raw/video")

video_files = list(video_folder.glob("*.mp4"))

if not video_files:
    raise ValueError("No video files found in data/raw/video")

for video_path in video_files:
    print(f"\nProcessing: {video_path.name}")
    info = inspect_video(str(video_path))
    print(f"Duration: {info['duration_s']}s, FPS: {info['fps']}, "
          f"Resolution: {info['resolution']}")

    frame_path = extract_frame_at_time(
        str(video_path),
        f"../../data/processed/frames/{video_path.stem}_thumb.png",
        t_seconds=5.0
    )
    print(f"Saved frame: {frame_path}")

    frames = extract_keyframes(
        str(video_path),
        f"../../data/processed/frames/{video_path.stem}/",
        interval_seconds=10.0
    )
    print(f"Extracted {len(frames)} keyframes")

    audio_path = extract_audio_from_video(
        str(video_path),
        f"../../data/processed/audio/{video_path.stem}.mp3"
    )
    print(f"Extracted audio: {audio_path}")

    print(f"{video_path.name} passed.")

print("\nAll video processing tests passed.")
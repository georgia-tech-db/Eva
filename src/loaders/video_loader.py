from src.loaders.abstract_loader import AbstractVideoLoader
import cv2

from src.models import VideoMetaInfo, FrameInfo, ColorSpace, Frame, FrameBatch
from src.utils import framediff_utils


class SimpleVideoLoader(AbstractVideoLoader):
    def __init__(self, video_metadata: VideoMetaInfo, *args, **kwargs):
        super().__init__(video_metadata, *args, **kwargs)

    def load(self):
        video = cv2.VideoCapture(self.video_metadata.file)
        video_start = self.offset if self.offset else 0
        video.set(cv2.CAP_PROP_POS_FRAMES, video_start)

        _, frame = video.read()
        frame_ind = video_start - 1

        info = None
        if frame is not None:
            (height, width, channels) = frame.shape
            info = FrameInfo(height, width, channels, ColorSpace.BGR)

        prev_frame = None
        frames = []
        while frame is not None:
            frame_ind += 1
            eva_frame = Frame(frame_ind, frame, info)
            if self.skip_frames > 0 and frame_ind % self.skip_frames != 0:
                _, frame = video.read()
                continue

            # Skip similar frames if threshold is a positive value
            if self.threshold > 0:
                if prev_frame is not None:
                    """
                    If compare_foreground set to true, calculate distance 
                    metric on only the foreground pixels 
                    else on the entire image.
                    """
                    if self.compare_foreground is True:
                        frame_diff = framediff_utils.compare_foreground_mask(
                            frame, prev_frame, self.distance_metric)
                    else: 
                        frame_diff = framediff_utils.frame_difference(
                            frame, prev_frame, self.distance_metric)
                    if frame_diff < self.threshold:
                        _, frame = video.read()
                        continue
                prev_frame = frame

            frames.append(eva_frame)
            if self.limit and frame_ind >= self.limit:
                return FrameBatch(frames, info)

            if len(frames) % self.batch_size == 0:
                yield FrameBatch(frames, info)
                frames = []

            _, frame = video.read()

        if frames:
            return FrameBatch(frames, info)

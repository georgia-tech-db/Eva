from src.models.catalog.properties import VideoFormat


class VideoMetaInfo:
    """
    Data model used for storing video related information
    # TODO: This is database metadata. Need to discuss what goes in here

    Arguments:
        file (str): path where the video is stored
        fps (int): Frames per second in the video
        c_format (VideoFormat): Video File Format

    """

    def __init__(self, file: str, fps: int, c_format: VideoFormat):
        self._fps = fps
        self._file = file
        self._c_format = c_format

    @property
    def file(self) -> str:
        return self._file

    @property
    def fps(self) -> int:
        return self._fps

    @property
    def c_format(self) -> VideoFormat:
        return self._c_format

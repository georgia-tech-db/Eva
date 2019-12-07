from src.models.catalog.properties import ColorSpace


class FrameInfo:
    """
    Data model contains information about the frame

    Arguments:
        height (int)(default: -1): Height of the image : left as -1
        when the height of the frame is not required

        width (int)(default: -1):  Width of the image : left as -1 when the
        height of the frame is not required

        channels (int)(default: 3): Number of input channels in the video

        color_space (ColorSpace)(default: ColorSpace.RGB): color space of
        the frame (RGB, HSV, BGR, GRAY)

    """

    def __init__(self, height=-1, width=-1, channels=3,
                 color_space=ColorSpace.RGB):
        self._color_space = color_space
        self._width = width
        self._height = height
        self._channels = channels

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def color_space(self):
        return self._color_space

    @property
    def channels(self):
        return self._channels

    def __eq__(self, other):
        return self.color_space == other.color_space and \
            self.width == other.width and \
            self.height == other.height and \
            self.channels == other.channels

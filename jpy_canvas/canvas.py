import ipywidgets
import traitlets

import numpy as np
import image_attendant as imat

from ._version import __version__


@ipywidgets.register
class Canvas(ipywidgets.DOMWidget):
    """HTML5 canvas-based image widget
    """
    # Widget information
    _view_name = traitlets.Unicode('CanvasView').tag(sync=True)
    _view_module = traitlets.Unicode('jupyter-canvas').tag(sync=True)
    _view_module_version = traitlets.Unicode(__version__).tag(sync=True)

    _model_name = traitlets.Unicode('CanvasModel').tag(sync=True)
    _model_module = traitlets.Unicode('jupyter-canvas').tag(sync=True)
    _model_module_version = traitlets.Unicode(__version__).tag(sync=True)

    # Private information
    _data_compressed = traitlets.Bytes(help='Compressed image data').tag(sync=True)
    _type = traitlets.Unicode(help='Encoding format, e.g. PNG or JPEG').tag(sync=True)
    # _width = CUnicode(help='Width of the image in pixels').tag(sync=True)
    # _height = CUnicode(help='Height of the image in pixels').tag(sync=True)
    # _event = traitlets.Dict().tag(sync=True)

    # Public information
    # https://developer.mozilla.org/en/docs/Web/CSS/image-rendering
    # pixelated = traitlets.Bool(False, help='Image rendering quality').tag(sync=True)

    def __init__(self, data=None, url=None, format='webp', quality=70):
        """Instantiate a new Canvas Image Widget object.

        Display images using HTML5 Canvas via Jupyter Notebook widget system.
        Image data must be a Numpy array (or equivalent) with a shape
        similar to one of the following:
            (rows, columns)    - Greyscale
            (rows, columns, 1) - Greyscale
            (rows, columns, 3) - RGB
            (rows, columns, 4) - RGBA

        If data type is neither of np.uint8 or np.int16, it will be cast to uint8 by
        scaling min(data) -> 0 and max(data) -> 255.

        If you supply a URL that points to an image then that image will be fetched
        and stored locally as a uint8 byte array.
        """
        super().__init__()

        self._url = ''
        self._data = None
        self._format = None

        self.format = format
        self.quality = quality

        if url:
            self.url = url
        elif data is not None:
            self.data = data

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format = value
        self._type = 'image/{}'.format(self._format)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
        self._data = None

        with self.hold_sync:
            # self._width = 0
            # self._height = 0
            self._data_compressed, self._format = imat.download(self._url)

        # note: this method does not yet capture the image width and height.
        # hopefully I'll be able to determine that at frontend and propagate
        # back here...?

    @property
    def data(self):
        """Image data as Numpy array
        """
        if self._data is None and self._data_compressed is not None:
            self._data = imat.decompress(self._data_compressed)

        return self._data

    @data.setter
    def data(self, value):
        self._data = value

        self._data_compressed = imat.compress(self._data, self._format, quality=self.quality)

    @property
    def shape(self):
        return self.data.shape

    @property
    def height(self):
        return self.data.shape[0]

    @property
    def width(self):
        return self.data.shape[1]

#------------------------------------------------

if __name__ == '__main__':
    pass

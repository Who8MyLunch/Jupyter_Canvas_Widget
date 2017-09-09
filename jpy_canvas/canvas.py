import ipywidgets
import traitlets

import numpy as np
import image_attendant as imat

from ._version import __version__


@ipywidgets.register
class Canvas(ipywidgets.DOMWidget):
    """An example widget
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
    _format = traitlets.Unicode().tag(sync=True)
    _width = CUnicode(help="Width of the image in pixels.").tag(sync=True)
    _height = CUnicode(help="Width of the image in pixels.").tag(sync=True)
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

        If data type is neither of np.uint8 or np.int16, it will be cast to uint8 by scaling
        min(data) -> 0 and max(data) -> 255.

        If you supply a URL that points to an image then that image will be fetched and stored
        locally as a uint8 byte array.
        """
        super().__init__()

        self._url = ''
        self._data = None
        self._format = format
        self.quality = quality

        if url:
            self.url = url
        elif data is not None:
            self.data = data

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value
        self._data_compressed, self._format = imat.download(self._url)

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

        with self.hold_sync:
            self._height = self.height
            self._width = self.width
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

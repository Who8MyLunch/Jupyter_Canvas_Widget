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
    # _width = traitlets.CUnicode(help='Image display width in CSS pixels').tag(sync=True)
    # _height = traitlets.CUnicode(help='Image display height in CSS pixels').tag(sync=True)
    # _event = traitlets.Dict().tag(sync=True)

    # Public information
    # https://developer.mozilla.org/en/docs/Web/CSS/image-rendering
    # pixelated = traitlets.Bool(False, help='Image rendering quality').tag(sync=True)

    def __init__(self, data=None, url=None, format='webp', quality=70):
        """Instantiate a new Canvas Image Widget object.

        Image data must be compatible with a Numpy array with a shape similar to the following:
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
        """Mime-type format, eg. png, jpg, webp
        """
        return self._format

    @format.setter
    def format(self, value):
        valid_values = ['png', 'jpg', 'webp']
        if value.lower() not in valid_values:
            raise ValueError('Invalid image format: {}'.format(value))

        self._format = value
        self._type = 'image/{}'.format(self._format)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

        if self._url:
            self._data = None

            compressed, fmt = imat.download(self._url)

            with self.hold_sync():
                self.format = fmt
                self._data_compressed = compressed

    @property
    def data(self):
        """Image data as Numpy array
        """
        if self._data is None and self._data_compressed:
            # For when widget is instantiated indirectly via image URL
            self._data = imat.decompress(self._data_compressed)

        return self._data

    @data.setter
    def data(self, value):
        self._data = np.asarray(value)

        if self._data is None:
            compressed = b''
            height = 0
            width = 0
        else:
            compressed = imat.compress(self._data, self._format, quality=self.quality)
            height = self._data.shape[0]
            width = self._data.shape[1]

        with self.hold_sync():
            self._data_compressed = compressed
            self.height = height
            self.width = width

    @property
    def width(self):
        """Image display width in CSS pixels
        """
        value = self.layout.width
        if value:
            s = ''.join([v for v in value if v.isnumeric()])
            return int(s)
        else:
            return None

    @width.setter
    def width(self, value):
        if value:
            self.layout.width = '{:.0f}px'.format(value)
        else:
            self.layout.width = ''

    @property
    def height(self):
        """Image display height in CSS pixels
        """
        value = self.layout.height
        if value:
            s = ''.join([v for v in value if v.isnumeric()])
            return int(s)
        else:
            return None

    @height.setter
    def height(self, value):
        if value:
            self.layout.height = '{:.0f}px'.format(value)
        else:
            self.layout.height = ''

#------------------------------------------------

if __name__ == '__main__':
    pass

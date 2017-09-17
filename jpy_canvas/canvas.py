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
    _event = traitlets.Dict(help='Canvas-generated event information').tag(sync=True)
    _events_active = traitlets.Bool(False, help='Indicate if canvas events are actively captured').tag(sync=True)

    # Public information
    # https://developer.mozilla.org/en/docs/Web/CSS/image-rendering
    pixelated = traitlets.Bool(False, help='Image rendering quality').tag(sync=True)

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
        else:
            self.data = data
        # elif data is not None:
        #     self.data = data

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatchers = {}  # ipywidgets.widget.CallbackDispatcher()

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
            compressed, fmt = imat.download(self._url)
            self._data = None

            with self.hold_sync():
                self.format = fmt
                self._data_compressed = compressed
                self.height = 0
                self.width = 0

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
        # if value is None:
        #     # Reset to a small transparent rectangle
        #     value = np.zeros((50, 100, 4), dtype=np.uint8)
        # self._data = np.asarray(value)
        # compressed = imat.compress(self._data, self._format, quality=self.quality)
        height = self._data.shape[0]
        width = self._data.shape[1]

        with self.hold_sync():
            self._update_data(value)
            self.height = height
            self.width = width

    def _update_data(self, value):
        """Update data only, leave shape unchanged
        """
        if value is None:
            # Reset to a small transparent rectangle
            value = np.zeros((50, 100, 4), dtype=np.uint8)

        self._data = np.asarray(value)
        self._data_compressed = imat.compress(self._data, self._format, quality=self.quality)

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
        self._update_pixelated()

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
        self._update_pixelated()

    def _update_pixelated(self):
        """Try to be clever about when to set CSS image rendering to use nearest-neighbor or not
        """
        if self.data is not None:
            cH, cW = self.height, self.width
            dH, dW = self.data.shape[:2]

            with self.hold_sync():
                self.pixelated = False
                if cW:
                    if cW > dW:
                        self.pixelated = True
                elif cH:
                    if cH > dH:
                        self.pixelated = True

    #--------------------------------------------
    # Register Python event handlers
    def register(self, callback, event_type='', remove=False):
        """(un)Register a Python event=-handler functions.
        Default is to register for all event types.  May be called repeatedly to set multiple
        callback functions. Supplied callback function(s) must accept two arguments: widget
        instance and event dict.

        Non-exhaustive list of event types:
            - mousemove
            - mouseup
            - mousedown
            - click
            - contextmenu
            - dblclick
            - wheel

        Set keyword remove=True to unregister an existing callback function
        """
        if event_type not in self._event_dispatchers:
            self._event_dispatchers[event_type] = ipywidgets.widget.CallbackDispatcher()

        # Register with specified dispatcher
        self._event_dispatchers[event_type].register_callback(callback, remove=remove)

        # Enable/disable mouse event handling at front end.
        self._events_active =  self._num_handlers() > 0

    def unregister_all(self):
        """Unregister all known event handlers
        """
        for kind, dispatcher in self._event_dispatchers.items():
            for cb in dispatcher.callbacks:
                self.register(cb, kind, remove=True)

    def register_move(self, callback):
        """Convenience function to register Python event handler for 'mousemove' event
        """
        self.register(callback, 'mousemove')

    def register_click(self, callback):
        """Convenience function to register Python event handler for 'click' event
        """
        self.register(callback, 'click')        # this captures left-clicks
        self.register(callback, 'contextmenu')  # this captures right-clicks

    def _num_handlers(self):
        """Number of registered canvas event handlers
        """
        numbers = [len(dispatcher.callbacks) for dispatcher in self._event_dispatchers.values()]
        return sum(numbers)

    #--------------------------------------------
    # Respond to front-end events by calling user's registered handler functions
    @traitlets.observe('_event')
    def _handle_event(self, change):
        """Respond to front-end backbone events
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        if change['name'] == '_event':
            # new stuff is a dict of event information from front end
            ev = change['new']
        else:
            # raise error or not?
            return

        # Call any registered event-specific handler functions
        if ev['type'] in self._event_dispatchers:
            self._event_dispatchers[ev['type']](self, ev)

        # Call any general event handler function
        if '' in self._event_dispatchers:
            self._event_dispatchers[''](self, ev)

#------------------------------------------------

if __name__ == '__main__':
    pass

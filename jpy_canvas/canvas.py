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
    _width = traitlets.CInt(help='Image display width (CSS pixels)').tag(sync=True)
    _AR = traitlets.Float(help='Image aspect ratio').tag(sync=True)
    _mime_type = traitlets.Unicode(help='Encoding format, e.g. PNG or JPEG').tag(sync=True)
    _event = traitlets.Dict(help='Canvas-generated event information').tag(sync=True)
    _events_active = traitlets.Bool(False, help='Indicate if canvas events are actively captured').tag(sync=True)

    allow_pixelated = traitlets.Bool(True, help='Allow pixelated rendering when zoomed in').tag(sync=True)

    def __init__(self, data=None, url=None, format='png', quality=70):
        """Instantiate a new Canvas Image Widget

        Image data must be compatible with a Numpy array with a shape similar to the following:
            (rows, columns)    - Greyscale
            (rows, columns, 1) - Greyscale
            (rows, columns, 3) - RGB
            (rows, columns, 4) - RGBA

        If data type is not np.uint8 it will be cast to uint8 by scaling
        min(data) -> 0 and max(data) -> 255.

        If you supply instead a URL to an image then it'll be fetched and displayed directly.
        When/if the user asks for it, the compressed image will be uncmpressed at the backend
        and made available as a numpy array via the .data attribute.

        The `quality` keyword is only used for 'webp' and 'jpg' image formats.
        """
        super().__init__()

        self._url = ''
        self._data = None
        self._format = ''

        self.format = format
        self.quality = quality

        if url:
            self.url = url
        else:
            self.data = data

        # Manage user-defined Python callback functions for frontend events
        self._event_dispatchers = {}

    @property
    def format(self):
        """Mime-type format, eg. png, jpg, webp
        """
        return self._format

    @format.setter
    def format(self, value):
        value = value.lower()
        valid_values = ['png', 'jpg', 'webp']
        if value not in valid_values:
            raise ValueError('Invalid image format: {}'.format(value))

        self._format = value
        self._mime_type = 'image/{}'.format(self._format)

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):

        self._url = value
        try:
            compressed, fmt = imat.download(self._url)
        except IOError:
            raise

        self._data = None
        self.format = fmt
        self._data_compressed = compressed

    @property
    def data(self):
        """Image data as Numpy array
        """
        if self._data is None and self._data_compressed:
            # This is for when widget is instantiated indirectly via image URL.
            # Only decompress the data at backend if user asks for it, like right now.
            self._data = imat.decompress(self._data_compressed)

        return self._data

    @data.setter
    def data(self, value):
        if value is None:
            # Reset to a small transparent rectangle
            self._data = None
            value = np.zeros((10, 15, 4), dtype=np.uint8)
        else:
            self._data = value

        with self.hold_sync():
            self.width = 0 #  self._data.shape[1]
            self.AR = 0 #  self._data.shape[0] / self._data.shape[1]
            self._data_compressed = imat.compress(value, self._format, quality=self.quality)

    @property
    def width(self):
        """Image display width in CSS pixels
        """
        return self._width

    @width.setter
    def width(self, value):
        if not value:
            value = self.data.shape[1]

        self._width = value

    @property
    def height(self):
        """Image display height in CSS pixels
        """
        return round(self._AR*self._width)

    @height.setter
    def height(self, value):
        self._width = value / self._AR

    @property
    def AR(self):
        """Image aspect ratio height / width
        """
        return self._AR

    @AR.setter
    def AR(self, value):
        if not value:
            value = self._data.shape[0] / self._data.shape[1]

        self._AR = value

    # def _update_pixelated(self):
    #     """Try to be clever about when to set CSS image rendering to use nearest-neighbor or not
    #     I think this functionality should be moved to the front end??
    #     """
    #     if self.data is not None:
    #         cH, cW = self.height, self.width
    #         dH, dW = self.data.shape[:2]
    #         with self.hold_sync():
    #             self.pixelated = False
    #             if cW:
    #                 if cW > dW:
    #                     self.pixelated = True
    #             elif cH:
    #                 if cH > dH:
    #                     self.pixelated = True

    #--------------------------------------------
    # Register Python event handlers
    def register(self, callback, event_type='', remove=False):
        """(un)Register a Python callback function for frontend canvas-generated events

        Default is to register for all event types.  May be called repeatedly to set multiple
        callback functions. Supplied callback function(s) must accept two arguments: widget
        instance and event dict.

        Non-exhaustive list of canvas event types:
            - mousemove
            - mouseup
            - mousedown
            - click
            - contextmenu
            - dblclick
            - wheel

        Set keyword remove=True to unregister an existing callback function,, or you can call
        unregister_all() to remove all at once.
        """
        if event_type not in self._event_dispatchers:
            self._event_dispatchers[event_type] = ipywidgets.widget.CallbackDispatcher()

        # Register with specified dispatcher
        self._event_dispatchers[event_type].register_callback(callback, remove=remove)

        # Enable/disable canvas event handling at frontend
        self._events_active =  self._num_handlers() > 0

    def _num_handlers(self):
        """Number of registered canvas event handlers
        """
        numbers = [len(dispatcher.callbacks) for dispatcher in self._event_dispatchers.values()]
        return sum(numbers)

    def unregister_all(self):
        """Unregister all previously-registered Python event handlers
        """
        for kind, dispatcher in self._event_dispatchers.items():
            for cb in dispatcher.callbacks:
                self.register(cb, kind, remove=True)

    def register_move(self, callback):
        """Convenience function to register Python event handler for 'mousemove' event
        """
        self.register(callback, 'mousemove')

    def register_click(self, callback):
        """Convenience function to register Python event handler for left- and right-button 'click' events
        """
        self.register(callback, 'click')        # this captures left-clicks
        self.register(callback, 'contextmenu')  # this captures right-clicks

    def register_wheel(self, callback):
        """Convenience function to register Python event handler for mouse `wheel` events
        """
        self.register(callback, 'wheel')

    #--------------------------------------------
    # Respond to front-end events by calling user's registered handler functions
    @traitlets.observe('_event')
    def _handle_event(self, change):
        """Respond to frontend canvas events by calling user's registered callback functions.
        https://traitlets.readthedocs.io/en/stable/api.html#callbacks-when-trait-attributes-change
        """
        if change['name'] == '_event':
            # new stuff is a dict of event information from the frontend
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

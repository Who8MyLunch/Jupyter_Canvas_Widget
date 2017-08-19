
from __future__ import division, print_function, unicode_literals, absolute_import

import os
import base64
import uuid

import numpy as np

import IPython
from ipywidgets import widgets
import traitlets

from . import image


def inject():
    """
    Inject JavaScript component into browser front end.
    """
    fname = 'widget_canvas.js'
    path_module = os.path.abspath(os.path.dirname(__file__))

    f = os.path.join(path_module, fname)
    js = IPython.display.Javascript(filename=f)  # data=None, url=None, filename=None, lib=None

    print('inject!')
    IPython.display.display(js)

# Inject JavaScript when module is first loaded.
inject()


class CanvasImage(widgets.DOMWidget):
    """
    Display images using HTML5 Canvas with IPython Notebook widget system.
    """
    # https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Low%20Level.html

    # _model_name:   Name of Backbone model registered in the front-end to create and sync with.
    # _model_module: A requirejs module name in which to find _model_name.
    # _view_name:    Default view registered in the front-end to use to represent the widget.
    # _view_module:  A requirejs module in which to find _view_name.

    _view_name = traitlets.Unicode('CanvasImageView').tag(sync=True)
    # _view_module  I don't need this field since I directly handle injecting JS into notebook

    # Encoded image data and metadata
    _data_url = traitlets.Bytes(help='Image as data URL').tag(sync=True)
    # _format = traitlets.Unicode(help='Image encoding format', sync=True)

    # HTML/DOM/CSS screen display width and height
    height = traitlets.CInt(help='image display height').tag(sync=True)
    width = traitlets.CInt(help='image display width').tag(sync=True)

    # Canvas width and height, slaved to image data width and height.
    _width_canvas = traitlets.CInt(help='data width').tag(sync=True)
    _height_canvas = traitlets.CInt(help='data height').tag(sync=True)

    # Image rendering quality. https://developer.mozilla.org/en/docs/Web/CSS/image-rendering
    pixelated = traitlets.Bool(False, help='Render via nearest neighbor sampling').tag(sync=True)

    # Mouse event information.
    _mouse_active = traitlets.Bool(False, help='Indicate if mouse events are active').tag(sync=True)
    _mouse_event = traitlets.Dict(help='Front-end mouse event information').tag(sync=True)

    # _uuid = traitlets.Unicode(uuid.uuid1().hex, help='widget unique ID string'.tag(sync=True)
    # _something = traitlets.Bool(True.tag(sync=True)


    def __init__(self, data=None, url=None, format='webp', quality=70,
                 force_js=False, **kwargs):
        """
        Instantiate a new Canvas Image Widget object.

        Display images using HTML5 Canvas with IPython Notebook widget system. Keyword `value`
        contains the input image data.  It must be a Numpy array (or equivalent) with a shape
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
        super(CanvasImage, self).__init__(**kwargs)

        if force_js:
            inject()

        # Internal Python handler for JS mouse events synced through _mouse_event traitlet
        # https://developer.mozilla.org/en-US/docs/Web/Reference/Events
        # https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent
        self.on_trait_change(self._handle_mouse, str('_mouse_event'))  # JS --> Python

        # Allow user to attach Python callback functions to operate in response to mouse events.
        self._mouse_event_dispatchers = {}  # Python (this module) --> user's Python function(s)
        for kind in ['move', 'up', 'down', 'click', 'wheel']:
            # Independent dispatcher for each 'kind' of event.
            self._mouse_event_dispatchers[kind] = widgets.widget.CallbackDispatcher()

        # Store init data in traitlet(s)
        self._format = format
        self.quality = quality

        if url:
            # Fetch image from URL and decompress into local numpy array
            data_comp, format_orig = image.download(url)
            data = image.decompress(data_comp)

        # Set image data
        self.data = data

    # def setup_static(self):
    #     self.static_image = IPython.display.Image(url=self._encoded_url, embed=True)
    # def close(self):
    #     print('close!!')
    #     super().close()
    # def something(self):
    #     """Testing and debugging."""
    #     self._something = not self._something

    @property
    def data(self):
        """
        Image data stored as a numpy array.
        """
        return self._data

    @data.setter
    def data(self, data):
        with self.hold_sync():
            # Pause syncing of state changes until the context manager is released
            if issubclass(type(data), np.ndarray):
                # Process new image data
                HxW = data.shape[:2]

                # Setup data as uint8
                self._data = image.setup_data(data)

                # Compress input image data and encode via Base64
                self._data_comp = image.encode(self._data, fmt=self._format)
                data_url = image.data_url(self._data_comp, self._format)
            else:
                # Clobber image data
                self._data = None
                self._data_comp = None
                HxW = 0, 0
                data_url = ''

            # Update traitlets
            self._data_url = data_url.encode()
            self.height, self.width = HxW
            self._height_canvas, self._width_canvas = HxW

    @property
    def format(self):
        """
        Image compression/encoding format, e.g. 'jpg', 'png', 'webp', etc.
        This format will be used the next time an image is compressed.
        """
        return self._format

    @format.setter
    def format(self, value):
        valid_formats = ['png', 'jpg', 'jpeg', 'webp']
        if value.lower() not in valid_formats:
            raise ValueError('Invalid encoding format: {}'.format(value))
        self._format = value.lower()

    # def inject_static_empty(self):
    #     """
    #     Inject place holder image to allow future placement of static image prior to closing widgt.
    #     """
    #     # template = '<img class="{}" style="display: none">'
    #     template = '<img class="{}">'
    #     c = 'static_image_' + self._uuid
    #     html = template.format(c)
    #     IPython.display.display_html(html, raw=True)


    def _ipython_display_(self):
        """
        Display image to Notebook using IPython's rich-display infrastructure.
        """
        super(CanvasImage, self)._ipython_display_()

        # self.inject_static_empty()



    #####################################################
    # Respond to mouse events by calling registered Python event handlers
    def _scale_xy_screen_to_data(self, event):
        """
        Event XY values are generated in screen coordinates.  This function convert the values
        to data XY coordinates.
        """
        event['canvasY'] = round(event['canvasY'] * self._data.shape[0] / self.height)
        event['canvasX'] = round(event['canvasX'] * self._data.shape[1] / self.width)

        return event

    def _handle_mouse(self, name_trait, event):  # info_old, info_new):
        """
        Respond to JavaScript mouse events by calling registered Python function event handlers
        https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent
        """
        # Event types in JavaScript: 'mousemove', 'mouseup', 'mousedown', 'click', 'wheel'
        # Event types in Python:          'move',      'up',      'down', 'click', 'wheel'
        # kind_js_to_py = {'mousemove': 'move',
        #                  'mouseup': 'up',
        #                  'mousedown': 'down',
        #                  'click': 'click',
        #                  'wheel': 'wheel'}

        # Preprocess event data
        # event['type'] = kind_js_to_py[event['type']]  # update event types
        event = self._scale_xy_screen_to_data(event)

        # Handle the event
        try:
            kind = event['type']
            self._mouse_event_dispatchers[kind](self, event)
        except KeyError:
            raise ValueError('Really unexpected event type: {}'.format(kind))

    #######################################################
    # Register Python functions as mouse event handlers
    #
    #   callback : function to be called with two arguments: widget instance and event information.
    #   remove : bool (optional), set to true to unregister the callback function.
    #
    #   https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent
    #   https://developer.mozilla.org/en-US/docs/Web/Events/wheel
    def _num_handlers(self):
        """
        Number of registered mouse event handlers.
        """
        numbers = [len(d.callbacks) for d in self._mouse_event_dispatchers.values()]
        return sum(numbers)

    def on_mouse(self, callback, kinds=None, remove=False):
        """
        Register a callback function for one or more kinds of mouse events.
        Valid mouse event kinds: 'move', 'up', 'down', 'click', 'wheel'

        Default kinds=None will register the callback with all mouse event types.
        Setting kind to a string or a list of strings will register the callback with
        just the specified kinds.

        Set keyword remove=True in order to unregister an existing callback function.
        Arguments to the supplied callback function are the widget instance and event information.
        """
        # Default to all defined event dispatchers
        if not kinds:
            # Default all mouse event kinds: 'move', 'up', 'down', 'click', 'wheel'
            kinds = self._mouse_event_dispatchers.keys()

        if isinstance(kinds, str):
            kinds = [kinds]

        for k in kinds:
            if k not in self._mouse_event_dispatchers:
                raise ValueError('Invalid callback type: {}'.format(k))

            # Register/un-register user-defined callback function
            self._mouse_event_dispatchers[k].register_callback(callback, remove=remove)

        # Enable/disable mouse event handling at front end.
        self._mouse_active =  self._num_handlers() > 0

    def on_mouse_move(self, callback):
        self.on_mouse(callback, 'move')

    def on_mouse_up(self, callback):
        self.on_mouse(callback, 'up')

    def on_mouse_down(self, callback):
        self.on_mouse(callback, 'down')

    def on_mouse_click(self, callback,):
        self.on_mouse(callback, 'click')

    def on_mouse_wheel(self, callback):
        self.on_mouse(callback, 'wheel')

    def unregister(self):
        """
        Unregister all mouse event handler functions.
        """
        callbacks = []
        for dispatcher in self._mouse_event_dispatchers.values():
            callbacks += dispatcher.callbacks

        for cb in callbacks:
            self.on_mouse(cb, remove=True)

        # Enable/disable mouse event handling at front end.
        self._mouse_active =  self._num_handlers() > 0

#################################################

if __name__ == '__main__':
    pass

import ipywidgets as widgets
from traitlets import Unicode

@widgets.register
class Canvas(widgets.DOMWidget):
    """An example widget
    """
    _model_name = Unicode('CanvasModel').tag(sync=True)
    _model_module = Unicode('jupyter-canvas').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    _view_name = Unicode('CanvasView').tag(sync=True)
    _view_module = Unicode('jupyter-canvas').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)

    value = Unicode('Hello World!').tag(sync=True)

#------------------------------------------------

if __name__ == '__main__':
    pass

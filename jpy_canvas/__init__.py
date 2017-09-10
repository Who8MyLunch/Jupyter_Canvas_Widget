from ._version import version_info, __version__

from .canvas import Canvas

__all__ = 'Canvas'

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-canvas',
        'require': 'jupyter-canvas/extension'
    }]

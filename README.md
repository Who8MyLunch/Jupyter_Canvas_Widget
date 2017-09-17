# Jupyter Canvas Widget

**This is very much a work in progress!**

There already exists a Jupyter Image Widget ([ipywidgets](https://github.com/jupyter-widgets/ipywidgets)),
so why make another one?  That widget takes care of the tricky work involving transfering compressed
image data from the backend to the frontend.  But it leaves it to the user to handle converting an
array of image data into a sequence of compressed image bytes.  It also doesn't readily support
mouse events via Python callback functions.

And that's where this project comes in.  Jupyter Canvas Widget uses the HTML5 Canvas element
instead of the Image element.  The Canvas element inherently supports mouse events and this widget
passes them along to the Python backend.  This makes it very easy for the user to create
interactive Notebook applications that can respond to mouse motion, click, and wheel events via
Python callback functions.


## Features

- Accept image data from Numpy arrays or URLs
- Support Python callback functions for front-end mouse events
- Support Canvas affine transform operations (work in progress)
- Widget properties `width` and `height` allow for direct manipulation displayed image size,
  independent of source data size
- Leverage Jupyter ipywidgets native support for transfering binary data between backend and
  frontend (no more encode-64)

# Work-in-Progress

Things are falling into place.

Mouse event stuff has potential to really complicate the crap out of this project.

Later I might also want to consider capturing keyboard events when the canvas has focus.


# Example Usage

![image](TBD)


# Test it on Binder

[![Binder](http://mybinder.org/badge.svg)](TBD)


# Mouse Event Handling

A user-defined mouse event handler will receive two items: the widget insance and a `dict`
containing event information.  The information describes the state of the mouse (x,y position,
wheel and buttons) and whether certain keys on the keyboard were also depressed (ctrl, alt, shift).

## Example motion event while pressing LMB

```py
{'timeStamp': 1439155950492,
 'canvasX': 20,
 'canvasY': 216,
 'type': 'mousemove',
 'buttons': 1,
 'shiftKey': False,
 'ctrlKey': False,
 'altKey': False}
```

## Example ctrl-click event

```py
{'timeStamp': 1439156075139,
 'canvasX': 147,
 'canvasY': 37,
 'type': 'click',
 'buttons': 0}
 'shiftKey': False,
 'ctrlKey': True,
 'altKey': False,
```


# Installation

## Prerequisites

If not already enabled, you'll need to enable the ipywidgets notebook extension that installs with
Jupyter.  You can use the command `jupyter nbextension list` to see which (if any) notebook
extensions are currently enabled.  Enable it with following:

```bash
jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

## Standard Install

```bash
pip install Jupyter-Canvas-Widget
jupyter nbextension enable --py --sys-prefix jpy_canvas
```

## Developer Install

This requires npm.

```bash
git clone https://github.com/who8mylunch/Jupyter_Canvas_Widget.git
cd Jupyter_Canvas_Widget

pip install -e .

jupyter nbextension install --py --symlink --sys-prefix jpy_canvas
jupyter nbextension enable --py            --sys-prefix jpy_canvas
```

# Making Changes to JavaScript Code

Jupyter widget development uses [npm]([npm](https://docs.npmjs.com/getting-started/what-is-npm)
(Node Package Manager) for handling all the scary JavaScript details. The source code for this
project lives in the folder `js` and the npm package is defined by the file `js/package.json`.  The
actual JavaScript source code for the video widget is contained entirely in the file `js/lib
/jupyter-canvas.js`.  This is the only JavaScript file you should need edit when working on front-
end parts of this project.

After making changes to this JavaScript code it must be prepared and packaged into the `static`
folder on the Python side of the project.  Use the following command from within the `js` folder:

```bash
npm install
```

See the links below for more helpful information:
- https://docs.npmjs.com/cli/install
- http://stackoverflow.com/questions/19578796/what-is-the-save-option-for-npm-install


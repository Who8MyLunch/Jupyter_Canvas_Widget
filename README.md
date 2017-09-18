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

- Accept image data from either Numpy arrays or URLs.  User does not have to think about compression
  methods and details
- Widget properties `width` and `height` allow for direct manipulation displayed image size while
  maintaining original aspect ratio
- Support Python callback functions for canvas-generated mouse events
- Leverage Jupyter ipywidgets native support for efficiently transfering binary data from backend to
  frontend, e.g. [7.0 change log](https://github.com/jupyter-widgets/ipywidgets/blob/master/docs/source/changelog.md#70),
  [#1643](https://github.com/jupyter-widgets/ipywidgets/pull/1643),
  [#1595](https://github.com/jupyter-widgets/ipywidgets/pull/1595), and
  [#1194](https://github.com/jupyter-widgets/ipywidgets/pull/1194)


## Future Plans

- Support for image change deltas


# Work-in-Progress

- Consider capturing keyboard events when the canvas has focus
- Update readme contents
- Verify static HTML embed functionality
- Include URL example
- Consider using ordered namespace objects for storing widget event information
    - This requires ensuring all emitted events contain identical fields, else too much potential
      for stale information.
- Consider setting up poor man's video player example.  Video frames from where?  I'll take a
  sequence of photos with my phone!  Perhaps different view angles of a nice flower.
- Research how to maintain CSS width/height sizes, even when embedded in another container. Might
  be a simple style setting?


Ok, playing with various examples has revealed potential issues:
- Setting data to null is not trivial
- A canvas widget embedded inside a ipywidgets.Box widget overrides CSS display sizes.
- I tried using the static HTML embed feature but couldn't get it to work.  Might have been my fault.


I need two methods for accepting new image data:
- current method using data property.  no options, makes cetain assumptions.
- explicit function like set_image_data(), allowing for complete control.  The above property
  approach should call this function internally.


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


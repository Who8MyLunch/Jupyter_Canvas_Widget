# Jupyter_Canvas_Widget

**This is very much a work in progress!**


The plan is to leverage Javascript support for binary data instead of encode-64.  No more data
URL goofy stuff.

This will ultimately allow for sending image differences from backend to frontend, and operating as
a self-contained video player.  But that's all for later.

In the near-term I simply want a robust tool for displaying images from numpy data arrays.  This
will require the following functionality:
- Accept data from user at backend
- Compress the data
- Store data in binary form in an Attribute that syncs to the front end via Widget's internal
  framework.  Traitlets.Bytes().

- At the frontend I'll need to create the following objects for internal use: Canvas, 2D Context,
- Handle binary data at frontend using Typed Array buffers and views:
  https://developer.mozilla.org/en-US/docs/Web/JavaScript/Typed_arrays
  ImageData?, ImageBitmap??
- Which to use: ImageData or ImageBitmap??  I think ImageBitmap, look here: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/createImageBitmap

- Transfer bytes to a Blob.  Then instantiate an ImageBitmap using 2d context.  Then move/copy image
  data into canvas.  Finally set width and height.


- Width and height require special consideration.  Overall displayed image size is defined by CSS.
  This is independent of actual numbers of pixels.  Canvas itself has a width and height, measured in
  pixels. The image data has its own size of course.

- Size stuff gets complicated once I start allowing for zooming.  Is that something to handle via CSS?
  Via Canvas size?

- Canvas also supports arbitrary affine transforms applied to image.  This cold be useful to handle
  zooming or rotations.  Once I go this far I would need to separate the window size from the
  data size.  I don't really want to go down that route just yet, but one in the future I might
  want that option.  I should simply focus on implementing basic features, and just be aware about
  not painting myself into a corner in the early stages.


# To Do

So far so good!

Next up is to add support for zoom scale factor, including options for rendering (pixelated, etc)



# Installation

## Prerequisites

If not already enabled, you'll need to enable the ipywidgets notebook extension that installs with Jupyter.  You can use the command `jupyter nbextension list` to see which (if any) notebook extensions are currently enabled.  Enable it with following:

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

Jupyter widget development uses [npm]([npm](https://docs.npmjs.com/getting-started/what-is-npm) (Node Package Manager) for handling all the scary JavaScript details. The source code for this project lives in the folder `js` and the npm package is defined by the file `js/package.json`.  The actual JavaScript source code for the video widget is contained entirely in the file `js/lib/jupyter-canvas.js`.  This is the only JavaScript file you should need edit when working on front-end parts of this project.

After making changes to this JavaScript code it must be prepared and packaged into the `static` folder on the Python side of the project.  Do this by typing the following command from within the `js` folder:

```bash
npm install
```

See the links below for more helpful information:
- https://docs.npmjs.com/cli/install
- http://stackoverflow.com/questions/19578796/what-is-the-save-option-for-npm-install


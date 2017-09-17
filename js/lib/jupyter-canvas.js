var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

var version = require('../package.json').version;



// https://remysharp.com/2010/07/21/throttling-function-calls
// See updated version in above article's comments
function throttle(fn, threshhold, scope) {
  // threshhold || (threshhold = 250);
    var last, deferTimer;

    return function () {
        var context = scope || this;

        var now = +new Date, args = arguments
        if (last && now < last + threshhold) {
          // hold on to it
          clearTimeout(deferTimer);
          deferTimer = setTimeout(function () {
            last = now
            fn.apply(context, args);
          }, threshhold + last - now);
        } else {
          last = now
          fn.apply(context, args);
        };
    };
};


function valid_size(value) {
    if (isNaN(value)) return false;
    if (value == '')  return false;

    return true;
};

//-----------------------------------------------
//-----------------------------------------------

// The Model manages widget's state information
var CanvasModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name:           'CanvasModel',
        _model_module:         'jupyter-canvas',
        _model_module_version:  version,

        _view_name:            'CanvasView',
        _view_module:          'jupyter-canvas',
        _view_module_version:   version,

        _data_compressed:       new Uint8Array(0),
        _type:                 'image/webp',
        _event:                 {},
        _events_active:         false,
        pixelated:              false
    })
});

//-----------------------------------------------

// The View renders the widget model
var CanvasView = widgets.DOMWidgetView.extend({
    render: function() {
        // This project's view is a single <canvas/> element.
        this.canvas = document.createElement('canvas');
        this.setElement(this.canvas);

        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext
        var kind = '2d'  // 'webgl'   !!!!!
        this.ctx = this.canvas.getContext(kind);

        // .listenTo() is better than .on()
        // https://coderwall.com/p/fpxt4w/using-backbone-s-new-listento
        this.listenTo(this.model, 'change:_data_compressed', this.update_data);
        this.listenTo(this.model, 'change:pixelated', this.update_pixelated);

        //-------------------------------------------------
        // Canvas element event handlers
        // https://developer.mozilla.org/en-US/docs/Web/Reference/Events
        // https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
        // https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent
        this.canvas.addEventListener('mouseup',     this.handle_mouse_event.bind(this));
        this.canvas.addEventListener('mousedown',   this.handle_mouse_event.bind(this));
        this.canvas.addEventListener('wheel',       this.handle_mouse_event.bind(this));
        this.canvas.addEventListener('click',       this.handle_mouse_event.bind(this));
        this.canvas.addEventListener('contextmenu', this.handle_mouse_event.bind(this));
        this.canvas.addEventListener('dblclick',    this.handle_mouse_event.bind(this));
        this.canvas.addEventListener('mousemove',   this.handle_mouse_event.bind(this));

        // Define throttled event handlers for mouse motion
        // var dt = 50;  // miliseconds
        // var throttled_mouse_motion = throttle(this.handle_event, dt, this);
        // this.canvas.addEventListener('mousemove', throttled_mouse_motion);

        //-------------------------------------------------
        // Prevent mouse from doing default stuff
        this.canvas.onmousedown = function(ev) {
            ev.preventDefault();
        }
        this.canvas.onwheel = function(ev) {
            ev.preventDefault();
        }
        this.canvas.oncontextmenu = function(ev) {
            ev.preventDefault();
        }

        // Done
        this.update();
        this.update_data();
        this.update_pixelated();
    },

    // update_css_size: function() {
    //     // Update CSS display width and height.  No need to redraw canvas.
    //     if (valid_size(this.model.get('_width'))) {
    //         this.canvas.style.width = this.model.get('_width') + 'px';
    //     } else {
    //         this.canvas.style.width = null;
    //     };
    //     if (valid_size(this.model.get('_height'))) {
    //         this.canvas.style.height = this.model.get('_height') + 'px';
    //     } else {
    //         this.canvas.style.height = null;
    //     };
    // },

    update_pixelated: function() {
        // Image rendering quality via CSS style
        // https://developer.mozilla.org/en/docs/Web/CSS/image-rendering
        // Possible values: auto, crisp-edges, pixelated
        if (this.model.get('pixelated')) {
            this.canvas.style.imageRendering = 'pixelated'
        } else {
            this.canvas.style.imageRendering = 'auto'
        }
    },

    update_data: function() {
        // https://developer.mozilla.org/en-US/docs/Web/API/Blob
        var options = {'type': this.model.get('_type')};
        var blob = new Blob([this.model.get('_data_compressed')], options);

        var promise = createImageBitmap(blob);
        promise.then(this.draw.bind(this));
    },

    draw: function(image) {
        // Draw image to the canvas
        this.canvas.width = image.width;     // size changes must be done prior to drawImage function!
        this.canvas.height = image.height;

        this.ctx.drawImage(image, 0, 0);
    },

    handle_mouse_event: function(ev) {
        // General mouse-event handler
        if (this.model.get('_events_active')) {

            var pev = {'type': ev.type};

            var fields = ['shiftKey', 'altKey', 'ctrlKey', 'timeStamp', 'buttons', 'button']
            // movementX, movementY

            for (let f of fields) {
                pev[f] = ev[f]
            }

            // Canvas-local XY coordinates
            // https://developer.mozilla.org/en-US/docs/Web/API/Element.getBoundingClientRect
            var rect = this.canvas.getBoundingClientRect();

            // Relative coordinates
            var X = (ev.clientX - rect.left) / (rect.right  - rect.left);
            var Y = (ev.clientY - rect.top)  / (rect.bottom - rect.top);

            // Data pixel coordinates
            pev.canvasX = Math.floor(X*this.canvas.width);
            pev.canvasY = Math.floor(Y*this.canvas.height);

            // Additional fields for `wheel` event
            // https://developer.mozilla.org/en-US/docs/Web/Reference/Events/wheel
            if (ev.type == 'wheel') {
                fields = ['deltaMode', 'deltaX', 'deltaY', 'deltaZ']
                for (let f of fields) {
                    pev[f] = ev[f]
                }
            }

            // Done
            this.model.set('_event', pev);
            this.touch();
        }
    }

});

module.exports = {
    CanvasModel: CanvasModel,
    CanvasView: CanvasView
}

var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

var version = require('../package.json').version;

function valid_size(value) {
    if (isNaN(value)) return false;
    if (value == '')  return false;

    return true;
};

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
        _type:                 '',
        // _width:                '',
        // _height:                '',
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
        // this.listenTo(this.model, 'change:_width', this.update_css_size);
        // this.listenTo(this.model, 'change:_height', this.update_css_size);

        // Prevent page from scrolling with mouse wheel events over canvas
        this.canvas.onwheel = function(ev) {
            ev.preventDefault();
        };

        // Prevent context menu popup from right-click on canvas
        this.canvas.oncontextmenu = function(ev) {
            ev.preventDefault();
        };

        this.update();
        this.update_data();
        // this.update_css_size();
    },

    update_data: function() {
        // https://developer.mozilla.org/en-US/docs/Web/API/Blob
        var options = {'type': this.model.get('_type')};
        var blob = new Blob([this.model.get('_data_compressed')], options);

        var promise = createImageBitmap(blob);
        promise.then(this.draw.bind(this));
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

    draw: function(image) {
        // Draw image to the canvas
        this.canvas.width = image.width;
        this.canvas.height = image.height;

        this.ctx.drawImage(image, 0, 0);
    }
});

module.exports = {
    CanvasModel: CanvasModel,
    CanvasView: CanvasView
};

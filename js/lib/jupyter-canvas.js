var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');

var version = require('../package.json').version;

// Custom Model. Custom widgets models must at least provide default values
// for model attributes when different from the base class.
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
var CanvasModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name:           'CanvasModel',
        _model_module:         'jupyter-canvas',
        _model_module_version:  version,

        _view_name:            'CanvasView',
        _view_module:          'jupyter-canvas',
        _view_module_version:   version,
    })
});

//-----------------------------------------------

// Custom View. Renders the widget model.
var CanvasView = widgets.DOMWidgetView.extend({
    render: function() {
        // This project's view is a single <canvas/> element.
        this.canvas = document.createElement('canvas');
        this.setElement(this.canvas);

        // https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext
        var kind = '2d'  // 'webgl'   !!!!!
        this.ctx = this.canvas.getContext(kind);

        // .listenTo() is better than .on()
        // http://backbonejs.org/#Events-listenTo
        // https://coderwall.com/p/fpxt4w/using-backbone-s-new-listento
        this.listenTo(this.model, 'change:_data_compressed', this.update_data);

        // Prevent page from scrolling with mouse wheel events over canvas
        this.canvas.onwheel = function(event) {
            event.preventDefault();
        };

        // Prevent context menu popup from right-click on canvas
        this.canvas.oncontextmenu = function(event) {
            event.preventDefault();
        };

        this.updat();   // need this?
        this.update_data();
    },


    update_data: function() {
        // Update image data
        var options;

        // https://developer.mozilla.org/en-US/docs/Web/API/Blob
        options = {type: `image/${this.model.get('_format')}`};
        var blob = new Blob([this.model.get('_compressed_data')], options);

        // Specifies an image scaling algorithm. One of pixelated, low (default), medium, or high
        options = {resizeQuality: 'high'};
        var image = createImageBitmap(blob, options);

        // Draw the image
        this.ctx.drawImage(image, 0, 0);

        // Set CSS width and height
        this.el.setAttribute('width', image.width);
        this.el.setAttribute('height', image.height);
    }
});


module.exports = {
    CanvasModel: CanvasModel,
    CanvasView: CanvasView
};

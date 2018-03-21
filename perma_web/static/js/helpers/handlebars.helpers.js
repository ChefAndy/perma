var Handlebars = require('handlebars');

Handlebars.registerHelper ('truncatechars', function (str, len) {
    if (str.length > len) {
        var new_str = str.substr (0, len+1);

        while (new_str.length) {
            var ch = new_str.substr ( -1 );
            new_str = new_str.substr ( 0, -1 );
            if (ch == ' ') break;
        }

        if ( new_str == '' ) new_str = str.substr ( 0, len );

        return new Handlebars.SafeString ( new_str +'...' );
    }
    return str;
});

/*
Using handlebar's compile method to generate templates on the fly
*/

var templateCache = {};
export function renderTemplate(templateId, args) {
  var args = args || {};
  var $this = $(templateId);
  if (!templateCache[templateId]) {
    templateCache[templateId] = Handlebars.compile($this.html());
  }
  return templateCache[templateId](args);
}

/* simple wrapper around Handlebars.compile() to cache the compiled templates */
export function compileTemplate(templateId) {
  var $this = $(templateId);
  if ($this.length) {
    var template = Handlebars.compile($this.html());
    templateCache[templateId] = template;
    return template;
  }
}

var hbs = require('hbs');
//loads in a library of helpers and adds them to hbs
var helpers = require('./helpers.js');
hbs = helpers.addHelpers(hbs);

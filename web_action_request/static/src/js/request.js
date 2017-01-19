odoo.define('web_action_request.request', function (require) {

var WebClient = require('web.WebClient');
var web_client = require('web.web_client');

    WebClient.include({
        declare_bus_channel: function() {
            this._super();
            var channel = 'action.request_' + this.session.uid;
            this.bus_on(channel, function(action) {
                web_client.action_manager.do_action(action);
            });
            this.add_bus_channel(channel);
        },
    });
});

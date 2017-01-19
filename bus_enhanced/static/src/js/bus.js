odoo.define('bus_enhanced.bus', function (require) {

var session = require('web.session');
var Widget = require('web.Widget');
var WebClient = require('web.WebClient');
var base_bus = require('bus.bus');

var bus_enhanced = {};

bus_enhanced.ERROR_DELAY = 10000;

console.log('bus enhanced start');

WebClient.include({
        init: function(parent, client_options){
            this._super(parent, client_options);
            this.known_bus_channels = [];
            this.known_bus_events = [];
        },
        show_application: function() {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self.start_polling();
            });
            // this._super();
            // this.start_polling();
        },
        on_logout: function() {
            var self = this;
            base_bus.bus.off('notification', this, this.bus_notification);
            _(this.known_bus_channels).each(function (channel) {
                base_bus.bus.delete_channel(channel);
            });
            console.log(_(this.known_bus_events));
            console.log(this.known_bus_events);
            _(this.known_bus_events).each(function(e) {
                console.log(e);
                if (typeof e !== "undefined") {
                    self.bus_off(e[0], e[1]);
                }
            });
            this._super();
        },
        start_polling: function() {
            this.declare_bus_channel();
            base_bus.bus.on('notification', this, this.bus_notification);
            base_bus.bus.start_polling();
        },
        bus_notification: function(notifications) {
            var self = this;
            _.each(notifications, function (notification) { 
                var channel = notification[0];
                if (self.known_bus_channels.indexOf(channel) != -1) {
                    var message = notification[1];
                    base_bus.bus.trigger(channel, message);
                }
            });
        },
        bus_on: function(eventname, eventfunction) {
            // console.log(eventname, eventfunction)
            base_bus.bus.on(eventname, this, eventfunction);
            this.known_bus_events.push([eventname, eventfunction]);
        },
        bus_off: function(eventname, eventfunction) {
            base_bus.bus.on(eventname, this, eventfunction);
            var index = _.indexOf(this.known_bus_events, (eventname, eventfunction));
            this.known_bus_events.splice(index, 1);
        },
        /**
            must be overload
            var WebClient = require('web.WebClient');
            WebClient.include({
                declare_bus_channel: function() {
                    this._super();
                    this.add_bus_channel('enhanced_bus');
                },
            });
        **/
        declare_bus_channel: function() {
        },
        add_bus_channel: function(channel) {
            if (this.known_bus_channels.indexOf(channel) == -1) {
                base_bus.bus.add_channel(channel);
                this.known_bus_channels.push(channel);
            }
        },
    });


});

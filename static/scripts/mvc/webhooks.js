define([],function(){var a=Backbone.Model.extend({defaults:{activate:!0}}),b=Backbone.Collection.extend({model:a}),c=Backbone.View.extend({el:"#webhook-view",initialize:function(b){var c=this;this.model=new a,this.model.urlRoot=b.urlRoot,this.model.fetch({success:function(){c.render()}})},render:function(){var a=this.model.toJSON();return"masthead"==a.type&&a.activate&&$(document).ready(function(){Galaxy.page.masthead.collection.add({id:a.name,icon:"undefined"!=typeof a.config.icon?a.config.icon:"",url:"undefined"!=typeof a.config.url?a.config.url:"",tooltip:"undefined"!=typeof a.config.tooltip?a.config.tooltip:""})}),this.$el.html('<div id="'+a.name+'"></div>'),a.styles&&$("<style/>",{type:"text/css"}).text(a.styles).appendTo("head"),a.script&&$("<script/>",{type:"text/javascript"}).text(a.script).appendTo("head"),this}});return{Webhooks:b,WebhookView:c}});
//# sourceMappingURL=../../maps/mvc/webhooks.js.map
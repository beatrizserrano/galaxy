(function(c){c.fn._hover=c.fn.hover;c.fn.hover=function(f,e,d){if(d){this.bind("hoverstart",f)}if(e){this.bind("hoverend",d?d:e)}return !f?this.trigger("hover"):this.bind("hover",d?e:f)};var b=c.event.special.hover={delay:100,speed:100,setup:function(d){d=c.extend({speed:b.speed,delay:b.delay,hovered:0},d||{});c.event.add(this,"mouseenter mouseleave",a,d)},teardown:function(){c.event.remove(this,"mouseenter mouseleave",a)}};function a(d){var f=d.data||d;switch(d.type){case"mouseenter":f.dist2=0;f.event=d;d.type="hoverstart";if(c.event.dispatch.call(this,d)!==false){f.elem=this;c.event.add(this,"mousemove",a,f);f.timer=setTimeout(e,f.delay)}break;case"mousemove":f.dist2+=Math.pow(d.pageX-f.event.pageX,2)+Math.pow(d.pageY-f.event.pageY,2);f.event=d;break;case"mouseleave":clearTimeout(f.timer);if(f.hovered){d.type="hoverend";c.event.dispatch.call(this,d);f.hovered--}else{c.event.remove(f.elem,"mousemove",a)}break;default:if(f.dist2<=Math.pow(f.speed*(f.delay/1000),2)){c.event.remove(f.elem,"mousemove",a);f.event.type="hover";if(c.event.dispatch.call(f.elem,f.event)!==false){f.hovered++}}else{f.timer=setTimeout(e,f.delay)}f.dist2=0;break}function e(){a(f)}}})(jQuery);
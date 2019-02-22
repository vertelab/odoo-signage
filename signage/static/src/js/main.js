$(document).ready(function(){
    var $hide_signage_edit = $("p#hide_signage_edit").data("value");
    console.log($hide_signage_edit);
    if ($hide_signage_edit) {
        $("nav#oe_main_menu_navbar").addClass("hidden");
    }
});

odoo.define('signage', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
//~ var base = require('web_editor.base');
//~ var Model = require('web.Model');
var website = require('website.website');
var contentMenu = require('website.contentMenu');

var _t = core._t;
var qweb = core.qweb;

ajax.loadXML('/signage/static/src/xml/signage.xml', qweb);

contentMenu.TopBar.include({
     
    new_signage: function () {
         console.log("inne");
            website.prompt({
            id: "title",
            window_title: _t("New Signage"),
            input: _t("Signage Title"),
            init: function () {
                var $group = this.$dialog.find("div.form-group");
                $group.removeClass("mb0");
                
                // render xml from static
                //~ # RELOAD PAGE IN BROWSER FOR CHANGES TO MAKE EFFECT:
                //~ # http://localhost:8069/signage/static/src/xml/signage.xml
                var var_signage_popup = qweb.render("signage.popup");
                console.log(var_signage_popup);

                var $add = $('<div/>', {'class': 'form-group mb0'})
                    //~ .append($('<span/>', {'class': 'col-sm-offset-3 col-sm-9 text-left'})
                    //~ .append($('<span/>', {'class': 'col-sm-offset-0 col-sm-12 text-left'})
                    .append($('<span/>', {'class': 'col-sm-offset-4 col-sm-8 text-left'})
                        //~ .append(qweb.render('web_editor.components.switch', {id: 'switch_addTo_menu', label: _t("Add page in menu")}))
                        //~ .append(qweb.render('signage.template_id', {id: 'switch_addTo_menu', label: _t("Add page in menu")}))
                        //~ .append(qweb.render('signage.template_id'))
                        );
                //~ $add.find('input').prop('checked', true);
                //~ $group.after($add);
                $group.after(var_signage_popup);
            }
        }).then(function (val, field, $dialog) {
            if (val) {
     
                //~ var url = '/signage/admin/menu/insert/' + encodeURIComponent(val);
                //~ if ($dialog.find('input[type="checkbox"]').is(':checked')) url +="?add_menu=1";
                //~ document.location = url;
            }
        });
    }
    
})

});



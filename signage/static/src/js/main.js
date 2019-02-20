$(document).ready(function(){
    var $hide_signage_edit = $("p#hide_signage_edit").data("value");
    console.log($hide_signage_edit);
    if ($hide_signage_edit) {
        $("nav#oe_main_menu_navbar").addClass("hidden");
    }
});

/*
 * 
 * 
 */
odoo.define('signage.contentMenu', function (require) {
"use strict";

var core = require('web.core');
var base = require('web_editor.base');
var Model = require('web.Model');
var website = require('website.website');
var contentMenu = require('website.contentMenu');

var _t = core._t;
var qweb = core.qweb;

contentMenu.TopBar.include({
     
    new_signage: function () {
         console.log("inne");
            website.prompt({
            id: "editor_new_signage",
            window_title: _t("New Showcase"),
            input: _t("Showcase Title"),
            init: function () {
                var $group = this.$dialog.find("div.form-group");
                $group.removeClass("mb0");

                var $add = $('<div/>', {'class': 'form-group mb0'})
                            .append($('<span/>', {'class': 'col-sm-offset-3 col-sm-9 text-left'})
                                    .append(qweb.render('web_editor.components.switch', {id: 'switch_addTo_menu', label: _t("Add page in menu")})));
                $add.find('input').prop('checked', true);
                $group.after($add);
            }
        }).then(function (val, field, $dialog) {
            if (val) {
                /*
                 * # FORM ACTION ="/signage/admin/menu/insert" >> POST
                 * */
                var url = '/signage/admin/menu/insert' + encodeURIComponent(val);
                if ($dialog.find('input[type="checkbox"]').is(':checked')) url +="?add_menu=1";
                document.location = url;
            }
        });
    }
    
})

//~ return {
    //~ 'TopBar': TopBarContent,
    //~ 'EditMenuDialog': contentMenu.EditMenuDialog,
//~ };
//~ return TopBarContent;
});


console.log("hejgggg");

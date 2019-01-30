$(document).ready(function(){
    var $hide_signage_edit = $("p#hide_signage_edit").data("value");
    console.log($hide_signage_edit);
    if ($hide_signage_edit) {
        $("nav#oe_main_menu_navbar").addClass("hidden");
    }
});

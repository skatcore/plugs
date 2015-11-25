/*jslint browser: true*/
/*global  $*/
"use strict";

$(document).ready(function () {
    if ($.material) {
        $.material.init();
        $.material.ripples();
        $.material.input();  
    }
});

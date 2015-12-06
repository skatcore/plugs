/*jslint browser: true*/
/*global  $*/
"use strict";

function toggleSwitch(e) {
    $.ajax({
        type: 'GET',
        contentType: 'application/json',
        url: '/setSwitch',
        data: {
        	'switchid': $(e.target).attr('switchid'),
        	'active': $(e.target).prop('checked') | 0
        }
    }).done(
        function(data) {
        	if (data != "1") {
		        $.snackbar({
		            content: 'Server returned an error: ' + data,
		            style: 'snackbar alert-danger',
		            timeout: 5000
		        });
        	}
        }
    );
}

var lastSwitchState = '';

function updateSwitches() {
    $.ajax({
        type: 'GET',
        dataType: 'json',
        contentType: 'application/json',
        url: '/getSwitches'
    }).done(
        function(data) {
            if (lastSwitchState != JSON.stringify(data)) {
            	$('#switchHolder').html('');
            	$.each(data, function(k, v) {
            		$('#switchHolder').append(
            			$('<div>').addClass('col-md-3').html(
            				$('<div>').addClass('panel panel-default panel-heading').html(
            					$('<div>').addClass('row').html(
            						$('<div>').addClass('col-md-8').html(
            							$('<h1>').addClass('panel-title').html(v.name)
            						)
            					).append(
            						$('<div>').addClass('col-md-4').html(
            							$('<div>').addClass('form-group togglebutton pull-right label-static').html(
            								$('<label>').attr('for', 'btn-' + k).html(
            									$('<input>', {
            										'type': 'checkbox',
            										'value': '',
            										'id': 'btn-' + k,
            										'switchid': k,
            										'class': 'form-control'
            									}).after("<span class='toggle'></span>")
            								)
            							)
            						)
            					)
            				)
            			)
            		);

            		if (v.active == 1) {
            			$('#btn-' + k).attr('checked', '1');
            		}
            		$('#btn-' + k).on('click', toggleSwitch);
            	});

				setTimeout(function() {
					$('.togglebutton > label > input[type=checkbox]').filter(':notmdproc').after("<span class='toggle'></span>");
				}, 100);
            }
            lastSwitchState = JSON.stringify(data);
        }
    );
    setTimeout(updateSwitches, 2000);
}

$(document).ready(function () {
	$.material.init();
	updateSwitches();

	$('#btn-add').on('click', function (e) {
	    $.ajax({
	        type: 'GET',
	        contentType: 'application/json',
	        url: '/addSwitch',
	        data: {
	        	'name': $('#inp-name').val(),
	        	'switchid': $('#inp-id').val()
	        }
	    });
		$('#inp-name').val('');
		$('#inp-id').val('');
		e.preventDefault();
	});
});



(function($){
	$.fn.uxmessage = function(kind, text) {
	  if (text.length > 80) {
	    text = text.slice(0,100) + '\n...'
	  }
	  
	  var div_opener = '<div class="log_item log_notice ui-corner-all" style="display:none">'
  	if (kind == 'notice') {
  		$('#log_content').prepend('<div class="log_item log_notice ui-corner-all" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showNoticeToast', text);
    	}
  	} else if (kind == 'success') {
  		$('#log_content').prepend('<div class="log_item log_success ui-corner-all" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showSuccessToast', text);		
      }
  	} else if (kind == 'warning') {
  		$('#log_content').prepend('<div class="log_item log_warning ui-corner-all" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showWarningToast', text);		
    	}
  	} else if (kind == 'error') {
  		$('#log_content').prepend('<div class="log_item log_error ui-corner-all" style="display:none">' + text + '</div>');
  		$('#log_content').children('div').first().show('blind');
  		if ($("#log_content").is(':hidden')) {
    		$().toastmessage('showErrorToast', text);		
    	}
  	}

  	while ($('#log_content').children('div').length > 200) {
  	  $('#log_content').children('div').last().remove();
  	}

	};
})(jQuery); 


connect_btn_state = false;
connect_btn_in_hover = false;
function connect_btn_set_state(is_connected) {
  if (is_connected) {
    connect_btn_state = true
    if (!connect_btn_in_hover) {
      $("#connect_btn").html("Connected");
    }
    $("#connect_btn").removeClass("btn-danger");
    $("#connect_btn").removeClass("btn-warning");
    $("#connect_btn").addClass("btn-success");      
  } else {
		connect_btn_state = false
    if (!connect_btn_in_hover) {
      $("#connect_btn").html("Disconnected");
    }		
    $("#connect_btn").removeClass("btn-danger");
	  $("#connect_btn").removeClass("btn-success");
	  $("#connect_btn").addClass("btn-warning");     
  }
}


function send_gcode_line(gcode, success_msg, error_msg) {
	$.get('/gcode/'+ gcode, function(data) {
		if (data != "") {
			$().uxmessage('success', success_msg);
		} else {
			$().uxmessage('error', error_msg);
		}
	});
}


var queue_num_index = 1;
function save_and_add_to_job_queue(name, gcode) {  
  if ((typeof(name) == 'undefined') || ($.trim(name) == '')) {
    var date = new Date();
    name = date.toDateString() +' - '+ queue_num_index
  }
  //// store gcode - on success add to queue
	$.post("/queue/save", { 'gcode_name':name, 'gcode_program':gcode }, function(data) {
		if (data == "1") {
		  queue_num_index += 1;
      add_to_job_queue(name);
    } else if (data == "file_exists") {
      // try again with numeral appendix
      $().uxmessage('notice', "File already exists. Appending numeral.");
      save_and_add_to_job_queue(name+' - '+ queue_num_index, gcode);
		} else {
			$().uxmessage('error', "Failed to store G-code.");
		}
  });
}

function add_to_job_queue(name) {
  //// delete excessive queue items
  var num_non_starred = 0;
  $.each($('#gcode_queue li'), function(index, li_item) {
    if ($(li_item).find('a span.icon-star-empty').length > 0) {
      num_non_starred++;
      if (num_non_starred > 7) {
        remove_queue_item(li_item);
      }          
    }
  });
  //// add list item to page
  var star_class = 'icon-star-empty';
  if (name.slice(-8) == '.starred') {
    name = name.slice(0,-8);
    star_class = 'icon-star';
  }
	$('#gcode_queue').prepend('<li><a href="#"><span>'+ name +'</span><span class="starwidget '+ star_class +' pull-right" title=" star to keep in queue"></span></a></li>')
	$('span.starwidget').tooltip({delay:{ show: 1500, hide: 100}})  
  //// action for loading gcode
	$('#gcode_queue li:first a').click(function(){
	  var name = $(this).children('span:first').text();
	  if ($(this).find('span.icon-star').length > 0) {
	    name = name + '.starred'
	  }
    $.get("/queue/get/" + name, function(gdata) {
      if (name.slice(-8) == '.starred') {
        name = name.slice(0,-8);
      }      
      load_into_gcode_widget(gdata, name);
    }).error(function() {
      $().uxmessage('error', "File not found: " + name);
    });     
	});  	
  //// action for star
  $('#gcode_queue li:first a span.starwidget').click(function() {
    if ($(this).hasClass('icon-star')) {
      //// unstar
      $(this).removeClass('icon-star');
      $(this).addClass('icon-star-empty');
      $.get("/queue/unstar/" + name, function(data) {
        // ui already cahnged
        if (data != "1") {
          // on failure revert ui
          $(this).removeClass('icon-star-empty');
          $(this).addClass('icon-star');        
        }      
      }).error(function() {
        // on failure revert ui
        $(this).removeClass('icon-star-empty');
        $(this).addClass('icon-star');  
      });       
    } else {
      //// star
      $(this).removeClass('icon-star-empty');
      $(this).addClass('icon-star');
      $.get("/queue/star/" + name, function(data) {
        // ui already cahnged
        if (data != "1") {
          // on failure revert ui
          $(this).removeClass('icon-star');
          $(this).addClass('icon-star-empty');         
        }
      }).error(function() {
        // on failure revert ui
        $(this).removeClass('icon-star');
        $(this).addClass('icon-star-empty');  
      });        
    }
  });
}


function remove_queue_item(li_item) {
  // request a delete
  name = $(li_item).find('a span:first').text();
  $.get("/queue/rm/" + name, function(data) {
    if (data == "1") {
      $(li_item).remove()
    } else {
      $().uxmessage('error', "Failed to delete queue item: " + name);
    }
  });  
}

function add_to_library_queue(gcode, name) {
  if ((typeof(name) == 'undefined') || ($.trim(name) == '')) {
    var date = new Date();
    name = date.toDateString() +' - '+ queue_num_index
  }
	$('#gcode_library').prepend('<li><a href="#"><span>'+ name +'</span><i class="icon-star pull-right"></i><div style="display:none">'+ gcode +'</div></a></li>')
	
	$('#gcode_library li a').click(function(){
	  load_into_gcode_widget($(this).next().text(), $(this).text())
	});

	$('#gcode_library li a i').click(function(){
	  $().uxmessage('success', "star ...");
	});
}


function load_into_gcode_widget(gcode, name) {
	$('#gcode_name').val(name);
	$('#gcode_program').val(gcode);
	// make sure preview refreshes
	$('#gcode_program').trigger('blur');
}



$(document).ready(function(){
  
  $('#log_toggle').toggle(function() {
    $("#log_content").fadeIn('slow');
  	$("#log_toggle").html("hide log");
  }, function() {
    $("#log_content").fadeOut('slow');
  	$("#log_toggle").html("show log");
  });
  //$('#log_toggle').trigger('click');  // show log, for debugging


  //////// serial connect button ////////
  // get serial state
  var connectiontimer = setInterval(function() {
    $.ajax({
        url: '/serial/2',
        success: function( data ) {
        	if (data != "") {
        	  connect_btn_set_state(true);
        	} else {
        	  connect_btn_set_state(false);
        	}
        },
        error: function(request, status, error) {
          // lost connection to server
      		connect_btn_set_state(false); 
        }
    });
  }, 3000);
  connect_btn_width = $("#connect_btn").innerWidth();
  $("#connect_btn").width(connect_btn_width);
  $("#connect_btn").click(function(e){	
  	if (connect_btn_state == true) {
  		$.get('/serial/0', function(data) {
  			if (data != "") {
  				connect_btn_set_state(false);   
  			} else {
  			  // was already disconnected
  			  connect_btn_set_state(false);
  			}
  			$("#connect_btn").html("Disconnected");
  		});
  	}	else {
  	  $("#connect_btn").html('Connecting...');
  		$.get('/serial/1', function(data) {
  			if (data != "") {
  			  connect_btn_set_state(true);
  			  $("#connect_btn").html("Connected");		  
  			} else {
  			  // failed to connect
  			  connect_btn_set_state(false);
		  	  $("#connect_btn").removeClass("btn-warning");
      	  $("#connect_btn").addClass("btn-danger");  
  			}		
  		});
  	}	
  	e.preventDefault();		
  });	
  $("#connect_btn").hover(
    function () {
      connect_btn_in_hover = true;
      if (connect_btn_state) {
        $(this).html("Disconnect");
      } else {
        $(this).html("Connect");
      }
      $(this).width(connect_btn_width);
    }, 
    function () {
      connect_btn_in_hover = false;
      if (connect_btn_state) {
        $(this).html("Connected");
      } else {
        $(this).html("Disconnected");
      }
      $(this).width(connect_btn_width);      
    }
  );
  //\\\\\\ serial connect button \\\\\\\\
  
  

  $("#cancel_btn").click(function(e){
  	var gcode = '!\n'  // ! is enter stop state char
  	$().uxmessage('notice', gcode.replace(/\n/g, '<br>'));
  	send_gcode_line(gcode, "Stopping ...", "Serial not connected.");	
	  var delayedresume = setTimeout(function() {
    	var gcode = '~\nG0X0Y0F20000\n'  // ~ is resume char
    	$().uxmessage('notice', gcode.replace(/\n/g, '<br>'));
    	send_gcode_line(gcode, "Resetting ...", "Serial not connected.");
	  }, 1000);
  	e.preventDefault();		
  });
  
  $("#find_home").click(function(e){
  	var gcode = '~G30\n'  // ~ is the cancel stop state char
  	$().uxmessage('notice', gcode);	
  	send_gcode_line(gcode, "Homing cycle ...", "Serial not connected.");
  	e.preventDefault();		
  });

  $("#go_to_origin").click(function(e){
  	var gcode = 'G0X0Y0F20000\n'
  	$().uxmessage('notice', gcode);	
  	send_gcode_line(gcode, "Going to origin ...", "Serial not connected.");
  	e.preventDefault();		
  });
  
  $("#set_custom_offset").click(function(e){
  	var gcode = 'G10L20P1\nG55\n'
  	$().uxmessage('notice', gcode);	
  	send_gcode_line(gcode, "Setting custom offset ...", "Serial not connected.");
  	e.preventDefault();		
  });
  
  $("#use_table_offset").click(function(e){
  	var gcode = 'G54\n'
  	$().uxmessage('notice', gcode);
  	send_gcode_line(gcode, "Using table offset ...", "Serial not connected.");
  	e.preventDefault();		
  });
  
  
});  // ready

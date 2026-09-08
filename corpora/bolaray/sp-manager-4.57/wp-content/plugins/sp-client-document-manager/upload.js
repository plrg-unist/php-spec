if(!(window.console && console.log)) {
  console = {
    log: function(){},
    debug: function(){},
    info: function(){},
    warn: function(){},
    error: function(){}
  };
}
	
function cdm_update_projects_dropdown(){
	
	
	
	jQuery.post(sp_vars.ajax_url, {action: "cdm_update_projects_dropdown"}, function(msg){
				
				console.log(msg);
				console.log('replacing selects');
				jQuery(".pid_select").empty();
				jQuery(".pid_select").html(msg);
				
		});
	
}
	
jQuery( document ).ready(function($) {
	
			console.log(jQuery.cookie("pid"));
		
	
	
	
	
	
	
	
	if(sp_vars.sp_cu_user_projects_required == 1 && (jQuery.cookie("pid") == 0 || jQuery.cookie("pid") == null)){
			
			$('.sp_cdm_add_file').hide();
		}
	
	

	
	
	$( document ).on( "click", ".cdm-add-file-button", function() {
			$('#file_upload').trigger('click'); 
			return false;
		});

		$( document ).on( "click", ".sp-cdm-search-button", function() {
			cdm_ajax_search();
			return false;
		});
		
		
		$('#search_files').keypress(function (e) {
		  if (e.which == 13) {
			cdm_ajax_search();
			return false;    //<---- Add this line
		  }
		});
		
		



	
		$( document ).on( "click", ".sp_cdm_open_modal", function() {
		
		var modal_name = $(this).attr('data-modal');
		
		if(modal_name == 'folder'){
		$("#sub_category_name").val('');	
		}
		var inst = $('[data-remodal-id='+modal_name+']').remodal();
		inst.open();
					
		
		return false;
	});
	
	// edit a folder
	$( document ).on( "click", ".sp-cdm-save-category", function() {
			
			var id = jQuery(this).attr('data-id');
					
			if(jQuery("#edit_project_name_" + id).val() == ""){
			alert("Please enter a project name");
	
			}else{
			
			
				jQuery.post(sp_vars.ajax_url, {action: "cdm_save_category", name: jQuery("#edit_project_name_" + id).val(), id: id}, function(response){
										cdm_ajax_search();
		
					jQuery("#edit_category").dialog("close");
					cdm_update_projects_dropdown();
					alert(response);	
				})
			
			}
			
			return false;
			
		});
		
		
		// Delete a folder
		$( document ).on( "click", ".sp-cdm-delete-category", function() {
			var id = jQuery(this).attr('data-id');
			
			jQuery( "#delete_category_" + id ).dialog({

			resizable: false,

			height:240,

			width:440,

			modal: true,

			buttons: {

				"Delete all items": function() {

							jQuery.post(sp_vars.ajax_url, {action: "cdm_remove_category", id: id}, function(response){
								jQuery.cookie("pid", 0, { expires: 7 , path:"/" }); 
								cdm_ajax_search();
							})

					 

					jQuery( this ).dialog( "close" );	

						

				},

				Cancel: function() {

					jQuery( this ).dialog( "close" );

				}

			}

		});

			
		return false;	
			
		});
		
		
});
				


	
	function cdm_download_file(id){
		jQuery.get(sp_vars.ajax_url, {action: "cdm_download_file", fid:id}, function(response){
			
		});
		return false;
	}
	function cdm_download_project(id,nonce){
		
			window.location.href = sp_vars.ajax_url +"?action=cdm_download_project&nonce=" + nonce + "&id="+ id;
		
			
				return false;
	}

	function cdmOpenModal(name){
				jQuery(".cdm-modal").remodal({ hashTracking: false});	
			  var inst = jQuery.remodal.lookup[jQuery("[data-remodal-id=" + name + "]").data("remodal")];
				inst.open();	
				
	}
			function cdmCloseModal(name){
				jQuery(".cdm-modal").remodal({ hashTracking: false});	
			  var inst = jQuery.remodal.lookup[jQuery("[data-remodal-id=" + name + "]").data("remodal")];
			
				inst.close();	
				
			}
			
			function cdmRefreshFile(file){
				
					jQuery(".view-file-content").empty();
				
				jQuery.get(sp_vars.ajax_url, {action: "cdm_view_file", id: file}, function(response){
						jQuery(".view-file-content").html(response);
				})		
				
			}
			function cdmViewFile(file){
				
				jQuery(".view-file-content").empty();
				
				jQuery.get(sp_vars.ajax_url, {action: "cdm_view_file", id: file}, function(response){
						jQuery(".view-file-content").html(response);
						 jQuery(".cdm-modal").remodal({ hashTracking: false});	
						 var inst = jQuery.remodal.lookup[jQuery("[data-remodal-id=file]").data("remodal")];
						 inst.open();
				})
			 
						 		
		
		}
		
		
jQuery(document).on('closed', ".cdm-modal", function (e) {

jQuery.cookie("viewfile_tab", 0, { expires: 7 , path:"/" }); 	
 
});

		function sp_cu_add_project(){
		
			
				jQuery.post(sp_vars.ajax_url, {action: "cdm_save_category", name: jQuery("#sub_category_name").val(), uid: jQuery("#sub_category_uid").val(),parent: jQuery(".cdm_premium_pid_field").val()}, function(response){
						 cdmCloseModal("folder");
						 cdm_ajax_search();
										cdm_update_projects_dropdown();
		
				})				
		
			
		
		}




function cdm_refresh_file_view(fid){
	jQuery(".view-file-content").empty();
	
	 jQuery.get(sp_vars.ajax_url, {action: "cdm_view_file", id: fid}, function(response){
						jQuery(".view-file-content").html(response);
	})	
	 
	
}

function cdm_check_file_perms(pid){
			
		
		jQuery.post(sp_vars.ajax_url, {action: "cdm_file_permissions", pid:pid}, function(msg){
					
					if(msg == 1){
						
					if(sp_vars.sp_cu_user_projects_required == 1 && (jQuery.cookie("pid") == 0 || jQuery.cookie("pid") == null)){
					jQuery('.hide_add_file_permission').hide();	
					}else{
						jQuery('.hide_add_file_permission').show();	
					}
						
					
					}else{
					jQuery('.hide_add_file_permission').hide();		
					}	
		});
				
	
}

function cdm_check_folder_perms(pid){
			
			
		jQuery.post(sp_vars.ajax_url, {action: "cdm_file_permissions", pid:pid}, function(msg){
					
					if(msg == 1){
					jQuery('.hide_add_folder_permission').show();	
					}else{
					jQuery('.hide_add_folder_permission').hide();		
					}	
		});
		



jQuery.event.trigger({
	type: "cdm_check_folder_perms",
	pid: pid
});		
	
}


function sp_cu_reload_all_projects(context_folder_pid){
	

		
		jQuery.post(sp_vars.ajax_url, {action: "cdm_project_dropdown", pid:ontext_folder_pid}, function(msg){
					
					jQuery('.pid_select').html(msg);		
		});
		


		
	
}

function sp_cu_confirm_delete(div,h,file_id){

		
if(jQuery(window).width()*0.9< 768){
	var width = jQuery(window).width()*0.9;	
	}else{
		var width = 320;
	}

	var NewDialog = jQuery('<div id="sp_cu_confirm_delete"> ' + div + '</div>');

	

	jQuery(  NewDialog ).dialog({

			width:width,

			height:'auto',

			modal: true,

			buttons: {

				"Yes": function() {

				
					jQuery.post(sp_vars.ajax_url, {action: "cdm_delete_file", file_id:file_id}, function(response){
						
				cdmCloseModal('file');
				jQuery( NewDialog ).remove();
				 cdm_ajax_search();
				});
				

				

				},

				Cancel: function() {

					jQuery( NewDialog ).remove();

				}

			}

		});

	

}







function sp_cu_confirm(div,h,url){

	
if(jQuery(window).width()*0.9< 768){
	var width = jQuery(window).width()*0.9;	
	}else{
		var width = 320;
	}
	jQuery(  div ).dialog({

			width:width,

			height:'auto',

			modal: true,

			buttons: {

				"Yes": function() {

					window.location = url;

				},

				Cancel: function() {

					jQuery( this ).dialog( "close" );

				}

			}

		});

	

}



function sp_cu_dialog(div,w,h){

	
	
	
	if(jQuery(window).width()*0.9< 768){
	var width = jQuery(window).width()*0.9;	
	}else{
		var width = w;
	}
	var dialogBox = jQuery(div);
     var usableDialog = dialogBox[0];
      //jQuery("div.ui-dialog").remove();
            
	
	
	jQuery(usableDialog).dialog({

			height:'auto',

			width:width

	});

}

/*
jQuery(document).ready(function() {
//  jQuery("#cdm_upload_table tr:first").css("display", "none");
jQuery("#cdm_og").attr("checked","checked");
   
setInterval(function(){cdmPremiumReValidate();},1000);

});
*/

function cdm_disable_uploads(){
	
	jQuery(".sp_cdm_add_file").hide();
	jQuery(".sp_cdm_add_folder").hide();
	
}

function cdm_enable_uploads(){
	
	jQuery(".sp_cdm_add_file").hide();
	jQuery(".sp_cdm_add_folder").hide();
	
}
jQuery(document).ready(function($) {

	
	
	jQuery( document ).on( "click", ".cdm_refresh_file_view", function() {
		cdm_refresh_file_view(jQuery(this).attr('data-id'));
		
		return false;
	});
	
	

jQuery( ".cdm_button" ).button();


jQuery.ajaxSetup({ cache: false });



//add another file input when one is selected

var max = 20;

var replaceMe = function(){

	var obj = jQuery(this);

	if(jQuery("#cdm_upload_fields input[type='file']").length > max)

	{

		alert('fail');

		obj.val("");

		return false;

	}

	
	
	
	
	jQuery(obj).css({'position':'absolute','left':'-9999px','display':'none'}).parent().prepend('<input class="sp-cdm-file-input" type="file" name="'+obj.attr('name')+'"/>')
	
	var text = obj.val();
	var text = text.substring(text.lastIndexOf("\\") + 1, text.length);
	
	jQuery('#upload_list').append('<div class="sp_upload_div" data-id="'+ text+'"><span class="sp_upload_name">'+ text+'</span><span class="dashicons dashicons-trash cdm-community-remove-queue"></span><div>');

	jQuery("#cdm_upload_fields input[type='file']").change(replaceMe);

	jQuery("#cdm_upload_fields .cdm-community-remove-queue").click(function(){

		jQuery(this).parent().remove();

		jQuery(obj).remove();

		return false;

		

		

	});

}
function bytesToSize(bytes) {
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
   if (bytes == 0) return '0 Byte';
   var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
   return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}
var filesToUpload = [];	
	
jQuery.fn.fileUploader = function (filesToUpload) {
    this.closest(".files").change(function (evt) {

        for (var i = 0; i < evt.target.files.length; i++) {
            filesToUpload.push(evt.target.files[i]);
        };
        var output = [];

        for (var i = 0, f; f = evt.target.files[i]; i++) {
            var removeLink = "<a class=\"removeFile\" href=\"#\" data-fileid=\"" + i + "\" id=\"cdm-file-id-" + i + "\"><span class=\"dashicons dashicons-trash cdm-community-remove-queue\"></span></a>";

            output.push("<div class=\"sp_upload_div\"><strong>", escape(f.name), "</strong> - ",
                bytesToSize(f.size), ". &nbsp; &nbsp; ", removeLink, "</div>");
			
        }
		console.log( filesToUpload);
       jQuery(this).children(".fileList")
            .append(output.join(""));
    });
};



jQuery(document).on("click",".removeFile", function(e){
    e.preventDefault();
    var fileName = jQuery(this).parent().children("strong").text();
     // loop through the files array and check if the name of that file matches FileName
    // and get the index of the match
    for(i = 0; i < filesToUpload.length; ++ i){
        if(filesToUpload[i].name == fileName){
            //console.log("match at: " + i);
            // remove the one element at the index where we get a match
            filesToUpload.splice(i, 1);
        }	
	}
    //console.log(filesToUpload);
    // remove the <li> element of the removed file from the page DOM
    jQuery(this).parent().remove();
});


    $("#cdmfiles").fileUploader(filesToUpload);
  

 

	    $('body').on('click', '#dlg-upload', function() {
        $this = $(this);
       
		$('.remodal').prepend('<div class="sp-loading-now" style="position:absolute;height:100%;width:100%;background-color: rgba(0, 0, 0, 0.3); z-index:1000000000000000000000;top:0px;left:0px;padding:10%;"><img src="' +sp_vars.plugin_url+ 'images/loading-black.gif"></div>');
		var  file_obj = $(".sp-cdm-file-input").prop('files');
		console.log(filesToUpload);
        form_data = new FormData();
        
		for(i=0; i<filesToUpload.length; i++) {
            form_data.append('file[]', filesToUpload[i]);
			
			
        }
		form_data.append('action', 'sp_file_upload_callback');
		var final ={};
		var error = {};
		var post = $("#upload_form").serializeArray();
			console.log(post);
				$.each(post, function( index, value ) {
					
					form_data.append(value.name,value.value);	
					final[value.name] = value.value;
});
		
			
		final['action'] = 'display_sp_client_upload_process';	
		final['post'] = post;
			console.log(final);
        $.ajax({
            url: sp_vars.ajax_url,
            type: 'POST',
            contentType: false,
            processData: false,
            data: form_data,
            success: function (response) {
               
             	var obj = $.parseJSON(response);
				if(obj.error != null){
					
				alert(obj.error);	
				}
				if(obj.current_upload.length>0){
				
				jQuery.post(sp_vars.ajax_url, final, function(response) {
			
				$(".sp-loading-now").remove();
				
			
					 document.upload_form.reset();
					jQuery('.fileList').empty();
			
					
					for (var i = filesToUpload.length - 1; i >= 0; i--) {

  filesToUpload.splice(i, 1);
 
}
					 sp_cu_dialog("#sp_cu_thankyou",400,200);
					cdmCloseModal('upload');
					cdm_ajax_search();
		});
				
				}else{
					$(".sp-loading-now").remove();
					document.upload_form.reset();
					jQuery('.fileList').empty();
			
					
					for (var i = filesToUpload.length - 1; i >= 0; i--) {

  filesToUpload.splice(i, 1);
 
}
					
					cdmCloseModal('upload');
					cdm_ajax_search();
				}
				
				
				
            }
			
        });
		
		
		
		return false;
    });
	
	
	
	
	
	
	

jQuery("#cdm_upload_fields input[type='file']").change(function(){

	for(var i = 0 ; i < this.files.length ; i++){
      var fileName = this.files[i].name;
      $('.filenames').append('<div class="name">' + fileName + '</div>');
    }
	
	
});















        jQuery('a.su_ajax').click(function() {

            var url = this.href;

            // show a spinner or something via css

            var dialog = jQuery('<div style="display:none" class="loading"></div>').appendTo('body');

            // open the dialog

            dialog.dialog({

                // add a close listener to prevent adding multiple divs to the document

                close: function(event, ui) {

                    // remove div with all data and events

                    dialog.remove();

                },

                modal: true,

				title: jQuery(this).attr('title'),

				height:'auto',

				width:700

            });

            // load remote content

            dialog.load(

                url, 

                {}, // omit this param object to issue a GET request instead a POST request, otherwise you may provide post parameters within the object

                function (responseText, textStatus, XMLHttpRequest) {

                    // remove the loading class

                    dialog.removeClass('loading');

                }

            );

            //prevent the browser to follow the link

            return false;

        });



});





//var btn = jQuery.fn.button.noConflict() // reverts $.fn.button to jqueryui btn
//jQuery.fn.btn = btn // assigns bootstrap button functionality to $.fn.btn

function cdm_community_load_ajax(form,callback,data){
	jQuery(data).html('<i class="fa fa-cog fa-spin fa-lg"></i> Loading...');
	
	
	if(sp_vars.recaptcha_enable == 1){
		
		    grecaptcha.ready(function() {
            grecaptcha.execute(sp_vars.recaptcha_site_key, {action: callback}).then(function(token) {
                jQuery(form).prepend('<input type="hidden" name="token" value="' + token + '">');
                jQuery(form).prepend('<input type="hidden" name="action" value="'+callback+'">');
             //   jQuery(form).unbind('submit').submit();
            });;
        });
		
	}
	jQuery.ajax({
			   type: "POST",
			   url: sp_vars.ajax_url,
			   data: jQuery(form).serialize(),
			   cache: false,			
			   success: function(msg){
				
				if(msg == 'refresh'){
				location.reload();
				}else{
				jQuery(data).html(msg);
				}
				  		 
			   }

			 });		
	
}

jQuery(document).ready(function ($) {



$( document ).on( "click", ".reset-password", function(event) {

	 event.preventDefault();
  jQuery('.reset-password-form').toggle();

	return false;
});

jQuery('.logoff-user').on('click',function(event){
		 event.preventDefault();
		jQuery.removeCookie('pid', { path: '/' }); 
		jQuery.removeCookie('cdm_group_id', { path: '/' }); 
		jQuery.removeCookie('cdm_client_id', { path: '/' }); 
	 cdm_dashboard_load_ajax_function({"action":'cdm_community_logout'},'cdm_community_logout','');
	return false;
});
});





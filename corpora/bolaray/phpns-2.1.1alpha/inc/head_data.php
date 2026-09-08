<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

//This is the 'default' javascript that should be included with every theme/page

$head_data['wysiwyg'] = '
<link rel="alternate" type="application/rss+xml" title="phpns rss feed" href="etc.php?do=rss"/>
<script language="javascript" type="text/javascript" src="inc/wysiwyg/tiny_mce_gzip.js"></script>
<script language="javascript" type="text/javascript">
	tinyMCE_GZ.init({
		theme : "advanced",
		mode : "exact",
		elements : "main, full",
		apply_source_formatting : true,
		content_css : "example_advanced.css",
		extended_valid_elements : "a[href|target|name]",
		plugins : "table",
		theme_advanced_toolbar_location : "top",
		theme_advanced_buttons1 : "forecolor,backcolor,separator,bold,italic,underline,separator,link,unlink,separator,bullist,numlist,separator,indent,outdent,separator,justifyleft,justifycenter,justifyright,separator,hr,separator,tablecontrols,separator,charmap,formatselect",
		theme_advanced_buttons2 : "",
		theme_advanced_buttons3 : "",
		//theme_advanced_buttons2_add : "forecolor,backcolor,seperator",
		//theme_advanced_buttons3_add_before : "tablecontrols,separator",
		//invalid_elements : "a",
		 theme_advanced_path_location : "bottom",
    theme_advanced_resizing : true,
    theme_advanced_resize_horizontal : false,
		theme_advanced_styles : "Header 1=header1;Header 2=header2;Header 3=header3;Table Row=tableRow1", // Theme specific setting CSS classes
		//execcommand_callback : "myCustomExecCommandHandler",
		fix_list_elements : true,
		debug : false
	});
</script>
<script language="javascript" type="text/javascript">
	tinyMCE.init({
		theme : "advanced",
		mode : "exact",
		elements : "main",
		apply_source_formatting : true,
		content_css : "example_advanced.css",
		extended_valid_elements : "a[href|target|name]",
		plugins : "table",
		theme_advanced_toolbar_location : "top",
		theme_advanced_buttons1 : "forecolor,backcolor,separator,bold,italic,underline,separator,link,unlink,separator,bullist,numlist,separator,indent,outdent,separator,justifyleft,justifycenter,justifyright,separator,hr,separator,tablecontrols,separator,charmap,formatselect",
		theme_advanced_buttons2 : "",
		theme_advanced_buttons3 : "",
		//theme_advanced_buttons1_add_before : "forecolor,backcolor,separator",
		//theme_advanced_buttons3_add_before : "tablecontrols,separator",
		//invalid_elements : "a",
		 theme_advanced_path_location : "bottom",
		 fix_list_elements : true,
    theme_advanced_resizing : true,
    theme_advanced_resize_horizontal : false,
		//execcommand_callback : "myCustomExecCommandHandler",
		debug : false
	});
</script>
';

$head_data['other_js'] = '
<script language="javascript" type="text/javascript">
	function togglewysiwyg(id) {
		var elm = document.getElementById(id);
		if (tinyMCE.getInstanceById(id) == null)
			tinyMCE.execCommand(\'mceAddControl\', false, id);
		else
			tinyMCE.execCommand(\'mceRemoveControl\', false, id);
	}
		
	function expandwysiwyg(id) {
		var expelm = document.getElementById(id);
		var expstyle = expelm.style.height;
		document.getElementById(id).style.height = "500px";
		togglewysiwyg(id);
		togglewysiwyg(id);
	}
		
	function validate_required(field,alerttxt) {
		with (field) {
			if (value==null||value=="") {
				alert(alerttxt);
				return false
			} else {
				return true
			}
		}
	}
	
	function validate_form(thisform) {
		with (thisform) {
			if (validate_required(title,"You must enter a title to continue.")==false) {
				return false
			}
		}
	}
	
	function Checkall(form) { 
		for (var i = 1; i < form.elements.length; i++) {    
			eval("form.elements[" + i + "].checked = form.elements[0].checked");  
		} 
	}

	function new_window(url) {
		var newwindow;
		newwindow=window.open(url,\'name\',\'height=500,width=400,left=100,top=100,resizable=yes,scrollbars=yes,status=yes\');
		if (window.focus) {
			newwindow.focus()
		}
	}
	
	function expand() {
	for (var i=0; i<expand.arguments.length; i++) {
		var element = document.getElementById(expand.arguments[i]);
		element.style.display = (element.style.display == "none") ? "block" : "none";

	}
}

 // Set desired tab- defaults to four space softtab
        var tab = "    ";
        
        function checkTab(evt) {
            var t = evt.target;
            var ss = t.selectionStart;
            var se = t.selectionEnd;

            // Tab key - insert tab expansion
            if (evt.keyCode == 9) {
                evt.preventDefault();
                
                // Special case of multi line selection
                if (ss != se && t.value.slice(ss,se).indexOf("\n") != -1) {
                    // In case selection was not of entire lines (e.g. selection begins in the middle of a line)
                    // we ought to tab at the beginning as well as at the start of every following line.
                    var pre = t.value.slice(0,ss);
                    var sel = t.value.slice(ss,se).replace(/\n/g,"\n"+tab);
                    var post = t.value.slice(se,t.value.length);
                    t.value = pre.concat(tab).concat(sel).concat(post);
                    
                    t.selectionStart = ss + tab.length;
                    t.selectionEnd = se + tab.length;
                }
                
                // "Normal" case (no selection or selection on one line only)
                else {
                    t.value = t.value.slice(0,ss).concat(tab).concat(t.value.slice(ss,t.value.length));
                    if (ss == se) {
                        t.selectionStart = t.selectionEnd = ss + tab.length;
                    }
                    else {
                        t.selectionStart = ss + tab.length;
                        t.selectionEnd = se + tab.length;
                    }
                }
            }
            
            // Backspace key - delete preceding tab expansion, if exists
            else if (evt.keyCode==8 && t.value.slice(ss - 4,ss) == tab) {
                evt.preventDefault();
                
                t.value = t.value.slice(0,ss - 4).concat(t.value.slice(ss,t.value.length));
                t.selectionStart = t.selectionEnd = ss - tab.length;
            }
            
            // Delete key - delete following tab expansion, if exists
            else if (evt.keyCode==46 && t.value.slice(se,se + 4) == tab) {
                evt.preventDefault();
                
                t.value = t.value.slice(0,ss).concat(t.value.slice(ss + 4,t.value.length));
                t.selectionStart = t.selectionEnd = ss;
            }
            
            // Left/right arrow keys - move across the tab in one go
            else if (evt.keyCode == 37 && t.value.slice(ss - 4,ss) == tab) {
                evt.preventDefault();
                t.selectionStart = t.selectionEnd = ss - 4;
            }
            else if (evt.keyCode == 39 && t.value.slice(ss,ss + 4) == tab) {
                evt.preventDefault();
                t.selectionStart = t.selectionEnd = ss + 4;
            }
            
        }
</script>
<script language="javascript" type="text/javascript" src="inc/js/highlight.js"></script>
';

//end head declarations

<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

include("inc/page_desc.php"); //include the page descriptions

//connect to database.themes, and find selected theme
$themeres = general_query("SELECT * FROM ".$databaseinfo['prefix']."themes WHERE theme_selected='1' LIMIT 1");

//Set variables for paths
$admin = "admin.tpl.php";
$login = "login.tpl.php";
//help.php doesn't have a template.

//read the theme data, and get the contents of the selected theme
while ($trow = mysql_fetch_assoc($themeres)) {
    //change file tread upon page type in global vars
    if ($globalvars['pagetype'] == "admin") {
        $file = file_get_contents($trow['theme_dir'].$admin);
    } elseif ($globalvars['pagetype'] == "login") {
        $file = file_get_contents($trow['theme_dir'].$login);
    }

    //modification of theme here (var replacement, img fix, ect ect)
    $uri = $_SERVER['PHP_SELF'];
    $rep_replace = 'themes/'.$trow['base_dir'].'/';
    $uri = preg_replace($rep_patt, $rep_replace, $uri);
    $file = str_replace('{prepath}', 'http://'.$_SERVER['SERVER_NAME'].$uri, $file);  //fix problem.

    if ($globalvars['pagetype'] == "admin") {  //if page is "admin" replace admin vars
        //admin configuration variables replaced with the system generated content
        $phpns_logo = '<a href="index.php"><img src="images/logo.png" alt="phpns logo" border="0" /></a>';
        $current_page_name = $globalvars['page_name'];

        //generate wysiwyg setting, and act accordingly (to disable/enable)
        $wysiwyg = load_config('wysiwyg');

        //if the wysiwyg editor is enabled...
        if ($wysiwyg['v1'] == 'yes') {
            $head_include .= $head_data['wysiwyg'];
        }
        //set the rest of the javascript, after wysiwyg
        $head_include .= $head_data['other_js'];

        //declare the variable for the current page image, 3 variations. automatic, custom, or none.
        if (empty($globalvars['page_image'])) { //automatic
            $page_image = '<img src="images/'. $globalvars['page_name'] . '.png" alt="'. $globalvars['page_name'] .'" alt="'.$globalvars['page_name'].' icon" title="'.$globalvars['page_name'].' icon" class="icon" />';
        } elseif ($globalvars['page_image']) { //custom
            $page_image = '<img src="images/'. $globalvars['page_image'] . '.png" alt="'. $globalvars['page_name'] .'" title="'.$globalvars['page_name'].' icon" class="icon" />';
        } elseif ($globalvars['page_image'] == "none") {
            $page_image = '';
        }

        //now, we'll actually replace the variables in the theme
        $file = str_replace('{version}', $globalvars['version'], $file);
        $file = str_replace('{username}', $_SESSION['username'], $file);
        $file = str_replace('{head_data}', $head_include, $file);
        $file = str_replace('{page_image}', $page_image, $file);
        $file = str_replace('{content}', $content, $file);
        $file = str_replace('{page_desc}', $page_desc[$globalvars['page_name']], $file);
        $file = str_replace('{current_page_name}', $current_page_name, $file);

        //load the global message
        $global_message = load_config('global_message');

        //if the global message isn't null, we'll display it.
        if ($global_message['v3'] != null) {
            $important_notice .= '<div class="global_message"><div class="global_message_link"><a href="preferences.php?do=globalmessage">[Change Message]</a></div>'.decode_data($global_message['v3']).'</div>';
        }

        //we're going to do a quick check to see if the 'install' directory is installed and
        //the SQL file from a previous backup is removed. We don't limit the user, but just nag them. =D
        //ADD TO GLOBAL MESSAGE
        if (file_exists('install')) {
            $important_notice .= '<div class="warning"><strong>Important!</strong> The /install/ directory is still present. Please delete this as soon as possible to avoid potiental security issues.</div>';
        }
        if (file_exists($databaseinfo['dbname'].'.sql')) {
            if ($globalvars['page_name'] == "index") {
                @unlink($databaseinfo['dbname'].'.sql');
            }
            $important_notice .= '<div class="warning">Phpns tried to delete the database backup file you created (/'.$databaseinfo['dbname'].'.sql), but could not. Please delete it.</div>';
        }

        //finally, insert all our notices into global_message.
        $file = str_replace('{global_message}', $important_notice, $file); //replace login message

    } elseif ($globalvars['pagetype'] == "login") {

        //grab the global message
        $global_message = load_config('global_message');

        //replace the theme variables
        $file = str_replace('{content}', $error_message.$content, $file);
        $file = str_replace('{logo}', $error_message.'<a href="index.php"><img src="images/logo.png" id="logo" class="logo" /></a>', $file);
        $file = str_replace('{version}', $globalvars['version'], $file);
        $file = str_replace('{current_page_name}', $current_page_name, $file);

    } //end modification of theme

    echo $file;  //output theme, decoded, and vars replaced. Basically the last step in the whole system.

} //end while statement. we're done.

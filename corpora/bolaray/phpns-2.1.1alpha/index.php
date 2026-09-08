<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

$globalvars['page_name'] = 'index';
include("inc/header.php");

if ($_GET['do'] == null) { //if no action, we display index as usual
    $num['article'] = content_num("articles", 1, 0);
    $num['users'] = content_num("users", 1, 0);
    $num['categories'] = content_num("categories", 1, 0);
    $num['pendarticle'] = content_num("articles", 1, 1);
    $num['logins'] = content_num("userlogin", 1, 0);
    $num['unapproved'] = content_num("articles", 1, 2);

    $load_recent = load_items('articles', 0, 4, '', '');  //load recent items (SQL)

    while($recent_row = mysql_fetch_array($load_recent)) {
        $recent_row_gen = $recent_row_gen.
        '<li><a href="article.php?id='.$recent_row['id'].'&do=edit">'.$recent_row['article_title'].'</a></li>';
    }

    $content = "			
			<h3>Information</h3>
			<div id=\"columnright\">
				<h4>Recent articles</h4>
				<ul>
					".$recent_row_gen."
				</ul>
			</div>
			<h4>Statistics</h4>
			<ul id=\"stats\">
				<li>There are currently <a href=\"manage.php\">" . $num['article'] . " articles posted</a>  with <a href=\"preferences.php?do=categories\">" . $num['categories'] . " categories</a></li>
				<li>There are currently <a href=\"user.php\">" . $num['users'] . " active users</a></li>
				<li>There are currently <a href=\"manage.php?v=unactive\">" . $num['pendarticle'] . " drafts</a> and <a href=\"manage.php?v=unapproved\">" . $num['unapproved'] . " unapproved articles</a></li>
				<li>There are currently <a href=\"user.php?do=loginrec\">" . $num['logins'] . " login records</a></li>
			</ul>
		";
} elseif ($_GET['do'] == "permissiondenied") { //display permission denied error
    $globalvars['page_name'] = 'permission denied';
    $globalvars['page_image'] = 'lock';

    $content = '<h3>Why am I getting this?</h3>
		<p>When your rank was created, the author denied any members associated with this rank to view this feature/page. If you think you should have access, contact your admin. If this has just barely been changed for you, you will need to logout and log back in.</p> ';
}

include("inc/themecontrol.php");  //include theme script

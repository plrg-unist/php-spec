<?php

//error_reporting( E_ALL | E_STRICT ); //DEBUGGING, uncommment to activate

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

/*
    README
    This file is used to generate a customized title for each of your articles. To get this working, place this file inside the folder where PHPNS resides (next to shownews.php, index.php, article.php... etc etc). That's all the installation, now we can use this file by going inside any PHP/HTML file on your server, and locating the following:

    <title>{your title here}</title>

    Now, simply replace this with:

    <title><?php include("/path/to/showtitle.php"); ?> {your site title here}</title>

    It's that easy. This file (showtitle.php) will automatically place an html character in place after the actual title, like &raquo; or &bull;. The default is &raquo; which looks the best. =)
*/

//define some variables, immediately protect against injection
//this the seperator, ie: Your News Title SEPERATOR Site title (space between Title and SEPERATOR is included in the script, you don't need to supply this.)

$default_seperator = '&raquo;';
$id = $_GET['a'];

//before continuing, protect from injection
if (!is_numeric($id) && $id && $id != 'do=rss') {
    $inject_error = '
			<h1>security breach</h1>
			<hr />
			<strong>'.$id.'</strong>
			<p>Phpns has detected that you (or the link you used to get here) attempted to breach our database with a method called "injection". This is usually because the id variable contains a non-numeric character. If you think this message is a mistake, contact the system administrator.</p>

			<div><h5>Copyright 2007-08 Alec Henriksen | GPL License</h5></div>
		';
    die($inject_error);
}

//include database information
@require("inc/config.php");
//connect.
$mysql['connection'] = mysql_connect($databaseinfo['host'], $databaseinfo['user'], $databaseinfo['password'])
or die($error['connection']);
//select mysql database
$mysql['db'] = mysql_select_db($databaseinfo['dbname'], $mysql['connection'])
or die($error['database']);

//define show_news functions, and check if functions are already defined.
if (!function_exists('clean_data')) {
    function clean_data($data)
    {
        if (is_array($data)) {
            foreach ($data as $key => $value) {
                if(ini_get('magic_quotes_gpc')) {
                    $data[$key] = stripslashes($value);
                }
                $data[$key] = htmlspecialchars($value);
            }
        } else {
            if(ini_get('magic_quotes_gpc')) {
                $data = stripslashes($data);
            }
            $data = htmlspecialchars($data, ENT_QUOTES);
        }
        return $data;
    }
}
if (!function_exists('get_title')) {
    function get_title($id, $mr=false)
    {
        if (is_array($data)) {
            foreach ($data as $key => $value) {
                $data[$key] = htmlspecialchars_decode($value);
            }
        } else {
            $data = htmlspecialchars_decode($data);
        }
        return $data;
    }
}

// END FUNCTION DEFINITIONS //

if ($mod_rewrite) {
    $column = 'article_title';
    $id = str_replace('-', ' ', $id);
} else {
    $column = 'id';
}
$title_sql = "
			SELECT * FROM ".$databaseinfo['prefix']."articles
			WHERE
			active='1' AND approved='1' AND ".$column."='".$id."'
			LIMIT 1
			";

$title_res = mysql_query($title_sql) or die(mysql_error());

while ($row = mysql_fetch_assoc($title_res)) {  //start fetch loop
    if ($time >= $row['start_date'] || $time <= $row['end_date']  || $row['start_date'] == null || $row['end_date'] == null) {
        echo $row['article_title'].' '.$default_seperator;
    }
}

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

$globalvars['version'] = "2.1.1alpha2";  // define phpns version. :)

//we're going to set some quick vars, although important.
$globalvars['full_page'] = $_SERVER['PHP_SELF'].'?'.$_SERVER['QUERY_STRING']; //define full path + GET
$globalvars['path_to'] = dirname($_SERVER['PHP_SELF']);
$globalvars['path_to_uri'] = $_SERVER['SERVER_NAME'].$globalvars['path_to'];

session_start(); //start session management

include("inc/config.php");   // include database information

//redirect to install dir if not installed
if ($globalvars['installed'] == "no") {
    header("Location: install/index.php");
}

//connect to mysql database for all files
$mysql['connection'] = @mysql_connect($databaseinfo['host'], $databaseinfo['user'], $databaseinfo['password'])
or die($error['connection']);

//select mysql database
$mysql['db'] = @mysql_select_db($databaseinfo['dbname'], $mysql['connection'])
or die($error['database']);

include("inc/errors.php");   // include error profiles
include("inc/function.php"); // include function header

if (!$globalvars['pagetype']) {
    $globalvars['pagetype'] = "admin"; //set admin pagetype if no pagetype detected. :)
}

if ($globalvars['pagetype'] == "admin" || $globalvars['pagetype'] == "about") {
    include("inc/auth.php"); //include auth info if pagetype is admin (not login page)
}

if (!$globalvars['page_name']) { //display error if there is no content.
    $globalvars['page_name'] = 'error';
    $page_desc['error'] = "You have reached this page in error! Phpns couldn't find any page with the information supplied. If you think this is a bug in the phpns software, we would appreciate you filing the bug at <a href=\"http://launchpad.net/phpns\">the phpns launchpad website</a>!
			<div class=\"warning\">
				<strong>Before reporting this bug, keep in mind, this is alpha software, and some preference pages may not work yet. If this is the case, we already know, and there is no need to report the bug.</strong>
			</div>";
}


$sys_time_format = load_config('sys_time_format');
//define ip address and other vars
$globalvars['ip'] = $_SERVER['REMOTE_ADDR'];
$globalvars['time'] = time();
$globalvars['time_format'] = $sys_time_format['v1'];

include("inc/head_data.php"); //include head_data
include("inc/global_files.php");  //global files array

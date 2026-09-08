<?php


// database connection variables
//
$site = 'localhost';
$user = '';
$pass = '';


// Blog install directory.  You probably only need to modify $wb_dir.
$wb_dir 				= '/www/wheatblog';
$wb_inc_dir   	= "$wb_dir/includes";
$wb_lang_dir  	= "$wb_dir/language";
$wb_admin_dir 	= "$wb_dir/admin";
$wb_class_dir 	= "$wb_dir/classes";


// SQLite users: This is a file on your filesystem (wheatblog.db).
// Everyone else: This is the name of a database.
//
$database					= 'wheatblog';
$tblPosts					= 'wbtbl_posts';
$tblUsers 					= 'wbtbl_users';
$tblComments				= 'wbtbl_comments';
$tblCategories		= 'wbtbl_categories';
$tblLinks     			= 'wbtbl_links';


// Choose a database backend (Uncomment the appropriate line)  MySQL is
// enabled by default
//
// include('includes/backend_sqlite.php');
// include('includes/backend_pgsql.php');
include('includes/backend_mysql.php');

// Chose a language file for the interface (Uncomment the appropriate line)
//
$ui_language = 'english.php';

// Wheatblog prefs
//
// posts on front page
$front_page_max = 10;


// blog directory url
//
$wb_url = 'http://www.example.org/wheatblog';


// blog admin directory url
//
$wb_admin_url = "$wb_url/admin";


// blog index page name
//
$blog_index_page_name = 'index.php';


// email address for notification of new comments
//
$notify_on_new_comment = 'user@example.com';


// Should only registered users be able to comment?
//
$registered_comments = false;


// name of your blog
//
$blog_title = 'MyBlog';

$blog_subtitle = 'A Blog that is Mine';


// Name of RSS file to write.  This file MUST be writable by the server.
// Uncomment this for a simple filename
$wb_rss = 'rss.xml';

// OR uncomment this to allow wB to create the file based on your blog's name
//
// $wb_rss = $name_of_blog.'_rss.xml';

// Language support for RSS.
// See http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes for
// further details.
//
$wb_rss_lang = 'en_us';

// Use sessions to log in?
//
$use_sessions = 1;

// Session directory.  In most cases, you leave this blank.  However, for
// websites that have multiple hosts like sourceforge.net, you want to
// specify a directory that's shared by all hosts.
//
$session_dir = '';
// $session_dir = '/home/groups/w/wh/wheatblog/sessions';    // for sf.net


// Archive interval ['monthly' | 'daily'].
//
$archive_type = 'daily';


// Wheatblog Stylesheet (Uncoment one.  "universal" is enabled by default)

$wb_style = "universal";
// $wb_style = "dividedsky";
// $wb_style = "cleanslate";
// $wb_style = "default";
// $wb_style = "stoiclook";
// $wb_style = "bigtime";

require_once('includes/functions.php');


// Enable use of settings_personalized.php.  This is for the developers or
// heavy users of the CVS version only.  You'll still need to set $wb_dir in
// settings.php
/*
if ( file_exists("$wb_dir/settings_personalized.php") ) {
    require("$wb_dir/settings_personalized.php");
} else {
  echo("<div style=\"width : 40%; padding : 10px;border: 1px solid #000;background : #EEF; margin : auto;\"
  <h2 style=\"font: bold 14px Tahoma, Verdana, Helvetica, sans-serif;\">wheatblog error:</h2>
  <hr />
  <p style=\"font: 14px Tahoma, Verdana, Helvetica, sans-serif;\"> The required file
  'settings_personalized.php' was not found in the location set by the \$wb_dir variable ($wb_dir).
   \$wb_dir is not set correctly.<br /><br />  Change its setting in the settings.php file and reload/refresh
    this page.</p></div>");
  exit(0);
}
*/
require_once("$wb_inc_dir/sessions.php");
require_once("$wb_lang_dir/$ui_language");

Start_Session();
$db       = $_SESSION['db'];
$self     = $_SERVER['PHP_SELF'];
$template = basename(dirname($self)) == 'admin' ? 4 : 3;

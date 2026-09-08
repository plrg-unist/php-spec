<?php

//
// File:    admin/add_post_002.php
// License: GNU GPL
// Purpose: Receives the data from edit_post.php and updates entry with it
//					very similar to add_post.php, except for the SQL statement.
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}



$page_title = 'Post Successfully Edited';
include_once("$wb_inc_dir/header.php");


// Parse variables passed from the form in add_post.php
//
$the_id    = $_POST['the_id'];
$The_id   = $db->quote($the_id);
$the_day   = $_POST['the_day'];
$The_day  = $db->quote($the_day);
$the_body  = $_POST['the_body'];
$The_body = $db->quote($the_body);
$the_month = $_POST['the_month'];
$The_month= $db->quote($the_month);
$the_date  = $_POST['the_date'];
$The_date = $db->quote($the_date);
$the_year  = $_POST['the_year'];
$The_year = $db->quote($the_year);
$the_cat   = $_POST['the_category'];
$The_cat  = $db->quote($the_cat);
$the_show  = $_POST['the_showpref'];
$The_show = $db->quote($the_show);
$the_lock  = $_POST['the_locked'];
$The_lock = $db->quote($the_lock);
$the_title = $_POST['the_title'];
$The_title= $db->quote($the_title);

// Fixes quoting hell when viewing the post body.
//
$show_body = stripslashes($_POST['the_body']);


// insert post into the database
//
$db->query("update wbtbl_posts set day=$The_day, month=$The_month,
		date=$The_date, year=$The_year, category=$The_cat, title=$The_title, 
		body = $The_body, locked=$The_lock, showpref=$The_show where id=$The_id");


// Post body
//
echo '<div class="subcontent">'."\n";
echo '<div class="post-heading">'."\n"; # heading is important, needs to be seperate
echo '<h3 class="post-title">'.$the_title.'</h3>'."\n";
echo '<h4 class="post-date">'.$the_day.', '.$the_month.'.'.$the_date.'.'.$the_year.'</h4>'."\n";
echo '</div>'."\n";  # closes div.post-heading
echo '<div class="post-body">'.$show_body.'</div>'."\n\n";

// Post category

echo '<div class="post-menu">'."\n".'<ul class="postnav">'."\n"; #links are now unordered list

# only difference from  "universal" post display is the ommission of comments and the addition of the show preference.

if ($the_show == 1) {
    echo '<li>This post is currently <strong>visible</strong>. </li>'."\n";
} else {
    echo '<li>This post is currently <strong>hidden</strong> .</li>'."\n";
}


echo '</ul>'."\n".'</div>'."\n";  # closes list and div.post-menu
echo '</div>'."\n\n"; # closes div.indent



include("$wb_inc_dir/rss.php");
include("$wb_inc_dir/footer.php");

<?php

//
// File:    list_category.php
// License: GNU GPL
// Purpose: Lists all categories as clickable links which will retreive posts
//    that fit under that category
//
require_once('./settings.php');
$page_title = '';
include_once("$wb_inc_dir/header.php");


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// select recent posts in the database
$result = DB_query("select * 
        from wbtbl_categories
        order by category", $db);


// open output div
echo "\n\n<div class=\"indent\">\n" . "<span class=\"cnt-subhead\">\n";

// loop through results and list each category
//
while($row = DB_fetch_array($result)) {
    $the_category      = $row['id'];
    $the_category_name = $row['category'];

    echo "<a href=\"view_by_category.php?the_category=$the_category\">" .
        "$the_category_name</a><br />\n";
}

// Close the output div
echo("</span>\n</div>\n\n");

echo "<br />\n<div class='description'>powered by <a " .
    "href='http://wheatblog.sourceforge.net' title='blogware for the rest " .
    "of us'>wheatblog</a></div>";


include_once("$wb_inc_dir/footer.php");

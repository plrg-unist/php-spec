<?php

//
// File:    view_by_archive.php
// License: GNU GPL
//
require_once('./settings.php');
$page_title = ':: archive view';
include_once("$wb_inc_dir/header.php");

$the_month = $_GET['the_month'];
$the_year  = $_GET['the_year'];
$The_month = $db->quote($the_month);
$The_year  = $db->quote($the_year);


// select recent posts in the database
$db->query("select * from wbtbl_posts
        where year=$The_year and month=$The_month
        order by year DESC, month DESC, date DESC, id DESC");

// output the current entries

echo("
		<div class=\"indent2\">
		<span class='cnt-subhead'>Filter: View by Archive</span><br>
		[archived entires for : $the_month.$the_year] 
		[<a href=\"$blog_index_page_name\"]>remove</a>]
		</div>
	");


$db2 = new DatabaseClass();

while($row = $db->fetchArray()) {
    $the_id       = $row['id'];
    $the_day      = $row['day'];
    $the_month    = $row['month'];
    $the_date     = $row['date'];
    $the_year     = $row['year'];
    $The_category = $db->quote($row['category']);

    // parse out the category id into its string value
    $db2->query("select * from wbtbl_categories where id=$The_category");

    while($row2 = $db2->fetchArray()) {
        $the_category_name = $row2['category'];
    }

    $the_showpref = $row['showpref'];
    $the_title    = $row['title'];
    $the_body     = $row['body'];
    $comments     = $row['comments'];

    // post
    echo("
			<div class=\"indent\">
			<span class=\"cnt-subhead\">$the_day, $the_month.$the_date.$the_year :: $the_title</span><br>
			$the_body<br>
			[<a href=\"view_by_category.php?the_category=$the_category\">$the_category_name</a>] 
			[<a href=\"view_by_permalink.php?the_id=$the_id\">comments ($comments)</a>]
			</div>
		");
}


include_once("$wb_inc_dir/footer.php");

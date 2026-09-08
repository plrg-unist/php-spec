<?php

//
// File:    admin/update_archive.php
// License: GNU GPL
// Purpose:
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$page_title = 'Update Archive';
include_once("$wb_inc_dir/header.php");


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// select recent posts in the database
$result = DB_query("select * 
        from wbtbl_posts
        where showpref = '1'   
        order by year DESC, month DESC, date DESC, id DESC", $db);

// output the current entries

if ($archive_type="monthly") {
    while($row = DB_fetch_array($result)) {
        $the_month = $row["month"];
        $the_year = $row["year"];

        $archive_start_year = 2000;
        $archive_end_year = date('Y');

        for($i=$archive_start_year; $i < $archive_end_year+1; $i++) {
            echo("<div class='wheatblog_indent'>year: $i");
            for($ii=1; $ii < 13; $ii++) {
                echo("[<a href=\"./view_by_archive.php?the_year=$i&the_month=$ii\" title=\"all posts from $ii $i\">$ii</a>]<br />");
            }
            echo("</div>");
        }
    }
} elseif ($archive_type="daily") {
    while($row = DB_fetch_array($result)) {
        $the_month = $row["month"];
        $the_year = $row["year"];

        echo("[<a href=\"./view_by_archive.php?the_year=$the_year&the_month=$the_month\" title=\"all posts from $the_month $the_year\">$the_month</a>]<br />");

    }
}

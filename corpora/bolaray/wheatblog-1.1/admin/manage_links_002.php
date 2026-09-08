<?php

//
// File:    admin/manage_links_002.php
// License: GNU GPL
// Purpose: Save edits submitted via manage_links.php
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}

$page_title = 'Links Successfully Updated';
include_once("$wb_inc_dir/header.php");


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

$the_id            = DB_Quote($_POST['the_id']);
$the_link_name     = DB_Quote($_POST['the_link_name']);
$the_link_location = DB_Quote($_POST['the_link_location']);

$result = DB_query("update wbtbl_links set link_name=$link_name, " .
    "link_location=$link_location where id=$id", $db);

insert_form_heading('Update Link');
insert_navigation();

// echo feedback to the user
echo '<div class="subcontent">' .
    "Link updated: $link_name($link_location)[id=$id]" .
    "</div>\n";


include_once("$wb_inc_dir/footer.php");

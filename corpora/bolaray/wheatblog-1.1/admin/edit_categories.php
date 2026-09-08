<?php

//
// File:    admin/edit_categories.php
// License: GNU GPL
// Purpose: Save edits submitted via manage_categories.php
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

$id       = DB_quote($_REQUEST['the_id']);
$category = DB_quote($_REQUEST['the_category']);

DB_query("update wbtbl_categories set category=$category where id=$id", $db);


Header("Location: $wb_admin_url/manage_categories.php");

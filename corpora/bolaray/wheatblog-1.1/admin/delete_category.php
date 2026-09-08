<?php

//
// File:    admin/delete_category.php
// License: GNU GPL
// Purpose: Deletes a category.  Called from manage_categories.php
//
require('../settings.php');

// This script should not be executed by non-root users.
//
if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);
$category = DB_Quote($_POST['the_category']);

DB_query("delete from wbtbl_categories where category=$category", $db);


Header("Location: $wb_admin_url/manage_categories.php");

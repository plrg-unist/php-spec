<?php

//
// File:    admin/add_category.php
// License: GNU GPL
// Purpose: Add categories submitted via manage_categories.php
//
require_once('../settings.php');

// This script should not be executed by non-root users.
//
if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db  = DB_connect($site, $user, $pass);
DB_select_db($database, $db);
$cat = DB_quote($_POST['the_category']);

DB_query("insert into wbtbl_categories (id, category) values (null, $cat)", $db);


Header("Location: $wb_admin_url/manage_categories.php");

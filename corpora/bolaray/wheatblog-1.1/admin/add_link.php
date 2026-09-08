<?php

//
// File:    admin/add_link.php
// License: GNU GPL
// Purpose: Save edits submitted via manage_links.php
//
require('../settings.php');

// This script should not be executed by non-root users.
//
if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

$link_name     = DB_Quote($_POST['the_link_name']);
$link_location = DB_Quote($_POST['the_link_location']);

// FIXME - Really, this is the job of the DB_Quote function, which returns
// FALSE if the string is not successfully quoted.  Until DB_Quote() does
// the checking, keep this check around.
//
if (! $link_name) {
    HariKari('The link_name variable is false.');
}

DB_query("insert into wbtbl_links (id, link_name, link_location)    
		values (null, $link_name, $link_location)", $db);


Header("Location: $wb_admin_url/manage_links.php");

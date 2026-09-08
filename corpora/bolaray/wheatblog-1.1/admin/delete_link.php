<?php

//
// File:    admin/delete_link.php
// License: GNU GPL
// Purpose: deletes links received from manage_links.php
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

$the_id = DB_Quote($_REQUEST['the_id']);

DB_query("delete from wbtbl_links where id=$the_id", $db);


Header("Location: $wb_admin_url/manage_links.php");

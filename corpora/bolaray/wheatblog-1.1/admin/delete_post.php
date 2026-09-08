<?php

//
// File:    admin/delete_post.php
// License: GNU GPL
// Purpose: Performs the post deletion from the database.
//
require('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);
$id = DB_Quote($_REQUEST['id']);

$result = DB_query("delete from wbtbl_posts where id = $id", $db);

// Attempt to redirect back to referring page.  If we don't know what
// that is, go back to sane default: manage_posts.php.
//
if (isset($_SERVER['HTTP_REFERER'])) {
    header('Location: ' . $_SERVER['HTTP_REFERER']);
} else {
    header("Location: $wb_admin_url/manage_posts.php");
}

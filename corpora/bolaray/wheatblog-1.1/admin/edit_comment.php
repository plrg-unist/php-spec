<?php

//
// File:    admin/edit_comment.php
// License: GNU GPL
// Purpose: Receives data from edit_post.php and updates entry with it.  What
// 	edit_post_002.php does for posts, edit_comment.php does for comments.
//
require('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

$id   = DB_Quote($_REQUEST['comment_id']);
$body = DB_Quote($_REQUEST['comment_body']);


DB_query("update wbtbl_comments set comment_body=$body where id=$id", $db);


// Attempt to redirect back to referring page.  If we don't know what that
// is, go back to sane default: manage_posts.php.
//
if (isset($_SERVER['HTTP_REFERER'])) {
    Header('Location: ' . $_SERVER['HTTP_REFERER']);
} else {
    Header("Location: $wb_admin_url/manage_posts.php");
}

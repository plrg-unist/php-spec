<?php

//
// File:    admin/delete_comment.php
// License: GNU GPL
// Purpose:
//
require('../settings.php');

// This script should not be executed by non-root users.
//
if (! isAdmin()) {
    HariKari('You are not the admin.');
}

$page_title = 'Comment Successfully Deleted';
include_once("$wb_inc_dir/header.php");


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// translate incoming vars
$id     = DB_Quote($_REQUEST['id']);
$postid = DB_Quote($_REQUEST['post_id']);


DB_query("delete from wbtbl_comments where id=$id", $db);

// confirmation
echo '<div class="subcontent" id="comment">'."\n".
     '<span class="dirs">Comment successfully Deleted.  ' .
        'Please wait five seconds to be redirected to the ' .
        '<a href="./' . $blog_index_page_name .
        '">Admin Page</a>.</span>' . "\n".
     '<span class="dirs">Return to <a href="edit_post.php?id=' .
        $postid.'">the post</a></span>' . "\n" .
     '</div>' . "\n";

// decrement the $comments field in the posts db ($tblPosts)
$res = DB_query("select comments from wbtbl_posts where id=$postid", $db);

while($row = DB_fetch_array($res)) {
    $comments = $row['comments'];
}

$comments--;

DB_query("update wbtbl_posts set comments='$comments' where id=$postid", $db);


include_once("$wb_inc_dir/footer.php");

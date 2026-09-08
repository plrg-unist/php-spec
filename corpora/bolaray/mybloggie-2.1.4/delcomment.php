<?php


// Blog Script - File Name : delcomment.php
// Copyright (C) myBloggie Sean
// http://www.mywebland.com , http://mybloggie.mywebland.com

// You are requested to retain this copyright notice in order to use
// this software.


//This program is free software; you can redistribute it and/or
//modify it under the terms of the GNU General Public License
//as published by the Free Software Foundation; either version 2
//of the License, or (at your option) any later version.

//This program is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.

//You should have received a copy of the GNU General Public License
//along with this program; if not, write to the Free Software
//Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

if (!defined('IN_MYBLOGGIE')) {
    die("You are not allowed to access this page directly !");
}

if (!isset($_SESSION['username']) && !isset($_SESSION['passwd'])) {
    header("Location: ./login.php");
}

if (isset($_GET['comment_id'])) {
    $comment_id = intval($_GET['comment_id']);
}
if (isset($_GET['post_id'])) {
    $post_id = intval($_GET['post_id']);
} else {
    $post_id = "";
}
if (isset($_POST['confirm'])) {
    $confirm = $_POST['confirm'];
}

if (!isset($confirm)  && isset($post_id) && isset($comment_id)) {
    message($lang['Confirm'], " <form action=\"".$_SERVER['PHP_SELF']."?mode=delcom\" method=\"post\"><br />". $lang['Msg_Del_error3']."<br />
                           <input type=\"hidden\" name=\"post_id\" value=\"".$post_id."\" />
                           <input type=\"hidden\" name=\"comment_id\" value=\"".$comment_id."\" />
                           <input type=\"submit\" name=\"confirm\" value=\"yes\" />&nbsp;&nbsp;<input type=\"submit\" name=\"confirm\" value=\"no\" /></form>");
} elseif ($confirm=="yes") {
    if (isset($_POST['comment_id'])) {
        $comment_id = intval($_POST['comment_id']);
    }
    if (isset($_POST['post_id'])) {
        $post_id = intval($_POST['post_id']);
    }
    // Data Base Connection  //
    $sql = "DELETE FROM ".COMMENT_TBL." WHERE comment_id=$comment_id";
    if(!($result = $db->sql_query($sql))) {
        $sql_error = $db->sql_error();         //214
        error($lang['Error'], 'SQL Query Error : '.$sql_error['message'].' !');
    }
    $confirm ="";
    message($lang['Del'], $lang['Msg_Del']."<br /><br />Click <a href=\"".self_url()."/admin.php?mode=all_com\">>Here<</a> if redirect failed ");
    metaredirect(self_url()."/admin.php?mode=all_com", 1);
} elseif ($confirm=="no") {
    metaredirect(self_url()."/admin.php?mode=all_com", 0);
} else {
    message($lang['Error'], 'Abnormal Operation ! Request Aborted.');
    metaredirect(self_url()."/admin.php", 0);
}

<?php


// Blog Script - File Name : del.php
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
// Added security
if (!isset($_SESSION['username']) && !isset($_SESSION['passwd'])) {
    echo "<meta http-equiv=\"Refresh\" content=\"2;url=".self_url()."/login.php\" />";
} else {
    $username = $_SESSION['username'];
    $sql =  "SELECT id, user, level FROM ".USER_TBL." WHERE user='$username'" ;
    $result = $db->sql_query($sql);
    $userid = $db->sql_fetchrow($result);
    $_SESSION['user_id'] =   $userid['id'];
    $accesslevel =   $userid['level'];
}

$user_id= $userid['id'];
if (isset($_GET['post_id'])) {
    $post_id = $_GET['post_id'];
}
if (isset($_POST['confirm'])) {
    $confirm = $_POST['confirm'];
} else {
    unset($confirm);
}
if (isset($_POST['post_id'])) {
    $post_id = $_POST['post_id'];
}

$sql = "SELECT post_id FROM ".POST_TBL." WHERE post_id='$post_id'";
$result = $db->sql_query($sql);
if($db->sql_numrows($result) < 1) {
    message($lang['Error'], $lang['Msg_Del_error2']."<br /><br />Click <a href=\"".self_url()."/admin.php?mode=addcat\">>Here<</a> if redirect failed ");
    metaredirect(self_url()."/admin.php?mode=viewlist", 1);
} else {

    if (!isset($confirm) && isset($post_id)) {
        message($lang['Confirm'], " <form action=\"".$_SERVER['PHP_SELF']."?mode=del\" method=\"post\"><br />". $lang['Msg_Del_error3']."<br />
   <input type=\"hidden\" name=\"post_id\" value=\"".$post_id."\" />
   <input type=\"submit\" name=\"confirm\" value=\"yes\" />&nbsp;&nbsp;<input type=\"submit\" name=\"confirm\" value=\"no\" /></form>");
    } elseif ($confirm=="yes") {

        if ($level==1) {
            $sql = "DELETE FROM ".POST_TBL." WHERE post_id='$post_id'";
            $result = $db->sql_query($sql);
            $confirm ="";
            message($lang['Del'], $lang['Msg_Del']);
            echo "<meta http-equiv=\"Refresh\" content=\"3;url=./admin.php?mode=viewlist\" />";
        } elseif ($level==2) {
            $sql = "SELECT * FROM ".POST_TBL." WHERE post_id='$post_id' and  user_id='$user_id'";
            $result = $db->sql_query($sql);
            if($db->sql_numrows($result)== 1) {
                $sql = "DELETE FROM ".POST_TBL." WHERE post_id='$post_id' and user_id='$user_id'";
                $result = $db->sql_query($sql);
                $confirm ="";
                message($lang['Del'], $lang['Msg_Del']."<br /><br />Click <a href=\"".self_url()."/admin.php?mode=viewlist\">>Here<</a> if redirect failed ");
                metaredirect(self_url()."/admin.php?mode=viewlist", 1);
            } else {
                message($lang['Error'], $lang['Msg_Del_error1']);
            }
        }
    } elseif ($confirm=="no") {
        metaredirect(self_url()."/admin.php?mode=viewlist", 1);
    } else {
        message($lang['Error'], $lang['Msg_Del_error2']);
    }
}

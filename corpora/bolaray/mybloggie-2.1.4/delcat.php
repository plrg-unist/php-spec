<?php

// Blog Script - File Name : delcat.php
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
    header("Location: ./login.php");
} else {
    $username = $_SESSION['username'];
    $sql =  "SELECT id, user, level FROM ".USER_TBL." WHERE user='$username'" ;
    $result = $db->sql_query($sql);
    $userid = $db->sql_fetchrow($result);
    $_SESSION['user_id'] =   $userid['id'];
    $accesslevel =   $userid['level'];
}

if ($accesslevel==1) {

    if (isset($_GET['cat_id'])) {
        $cat_id = $_GET['cat_id'];
    }
    if (isset($_POST['confirm'])) {
        $confirm = $_POST['confirm'];
    } else {
        unset($confirm);
    }
    if (isset($_POST['cat_id'])) {
        $cat_id = $_POST['cat_id'];
    }

    $sql = "SELECT cat_id FROM ".CAT_TBL." WHERE cat_id='$cat_id'";
    $result = $db->sql_query($sql);
    if($db->sql_numrows($result) < 1) {
        message($lang['Error'], $lang['Msg_invalid_cat']."<br /><br />Click <a href=\"".self_url()."/admin.php?mode=addcat\">>Here<</a> if redirect failed ");
        metaredirect(self_url()."/admin.php?mode=addcat", 1);
    } else {
        if (!isset($confirm) && isset($cat_id)) {
            message($lang['Confirm'], " <form action=\"".$_SERVER['PHP_SELF']."?mode=delcat\" method=\"post\"><br />". $lang['Msg_Del_error3']."<br />
                           <input type=\"hidden\" name=\"cat_id\" value=\"".$cat_id."\" />
                           <input type=\"submit\" name=\"confirm\" value=\"yes\" />&nbsp;&nbsp;<input type=\"submit\" name=\"confirm\" value=\"no\" /></form>");
        } elseif ($confirm=="yes") {

            $sql = "DELETE FROM ".CAT_TBL." WHERE cat_id=$cat_id";
            $result = $db->sql_query($sql);
            if (isset($confirm)) {
                unset($confirm);
            }
            message($lang['Del'], $lang['Msg_Del']."<br /><br />Click <a href=\"".self_url()."/admin.php?mode=addcat\">>Here<</a> if redirect failed ");
            echo "<meta http-equiv=\"Refresh\" content=\"1;url=./admin.php?mode=addcat\" />";
        } elseif ($confirm=="no") {
            metaredirect(self_url()."/admin.php?mode=addcat", 1);
        }
    }
} else {
    metaredirect(self_url()."/oops.php", 1);
    //echo "<meta http-equiv=\"Refresh\" content=\"1;url=".self_url()."/oops.php\" />";
}

<?php

// Blog Script - File Name : edituser.php
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
$errormsg = "";
$pass ="";
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

    $template->set_filenames(array(
            'userform' => 'admin/userform.tpl'));

    if (isset($_GET["id"])) {
        $id = $_GET["id"] ;
    }
    if (isset($_GET["pass"])) {
        $pass = $_GET["pass"] ;
    }

    $sql = "SELECT * FROM ".USER_TBL." WHERE id='$id'";
    $result = $db->sql_query($sql);
    if($db->sql_numrows($result)== 1) {
        $edit = $db->sql_fetchrow($result);

        $template->assign_vars(array(
             'FORMHEADER'       => "ADD USER",
             'L_LEVEL'          => $lang['Level'],
             'FORMHEADER'       => "EDIT USER",
             'ACTIONFILENAME'   =>  $_SERVER['PHP_SELF']."?mode=edituser&pass=yes&amp;id=".$id,
             'USER'             =>  $edit['user'],
        ));

        if ($pass=="yes") {
            $template->assign_block_vars('pass', array(
               'L_PASSWORD'       => $lang['Password'],
               'L_REENTER_PASS'   => $lang['Reenter_password'],
             ));
        }
    }

    if (isset($_POST["submit"])) {
        if (isset($_POST['user'])) {
            $user = htmlspecialchars($_POST['user']);
        }
        if (isset($_POST['level'])) {
            $level = intval($_POST['level']);
        }
        $user = trim($user);
        $level = trim($level);

        if ($pass=="yes") {
            $password = $_POST['password'];
            $repassword = $_POST['repassword'];
            if ($repassword!=$password) {
                $error_flag = true;
                $errormsg =$lang['Msg_pwd_notmatch']."<br />";
            } else {
                $error_flag = false;
            }
            if ($password == "" || $repassword == "") {
                $error_flag = true;
                $errormsg = $errormsg." ".$lang['Msg_2x_pwd']."<br />" ;
            }
        } else {
            $error_flag = false;
        }

        if (!isset($user) or $user=="") {
            $error_flag = true;
            $errormsg =$errormsg." ".$lang['Msg_req_name']."<br />" ;
        } else {
            $error_flag = false;
        }
        if ($error_flag) {
            error($lang['Msg_reg_err'], "$errormsg");
        }

        $sql = "SELECT user, id FROM ".USER_TBL." WHERE user='$user'";
        $result = $db->sql_query($sql);
        $userdata = $db->sql_fetchrow($result);
        if($db->sql_numrows($result)>= 1 && $userdata['id']!==$id) {
            error($lang['Error'], $lang['Msg_user_available']);
        }

        if ($pass=="yes") {
            $password = md5(trim($password));
            $sql = "UPDATE ".USER_TBL." SET user='$user', password='$password', level='$level' where id='$id'";
            $result = $db->sql_query($sql);

            if ($user == $username) {
                unset($_SESSION['username']);
                unset($_SESSION['passwd']);
            }
        } else {
            $sql = "UPDATE ".USER_TBL." SET user='$user', level='$level' where id='$id'";
            $result = $db->sql_query($sql);
        }
        message($lang['Msg_edit_user'], $lang['Msg_posted']);
        metaredirect(self_url()."/admin.php?mode=edituserlist", 1);


    } else {

        $template->pparse('userform');
    }
} else {
    message($lang['Error'], 'Abnormal Operation ! Request Aborted.');
    metaredirect(self_url()."/admin.php", 0);
}

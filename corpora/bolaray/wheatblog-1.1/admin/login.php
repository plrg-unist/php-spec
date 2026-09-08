<?php

//
// File:    admin/login.php
// License: GNU GPL
// Purpose: Login script.
//
require_once('../settings.php');

// Check to see if the user wants to log out.
//
if (isset($_REQUEST['action']) && $_REQUEST['action'] == 'logout') {
    Kill_Session();
}


// Right now, ring 0 is the admin and ring 1 is everyone else.  Maybe we can
// think of functionality that would require difference class of non-admin
// users?
//
session_register('login');
session_register('flags');
session_register('www');
session_register('email');


// Innocent until proven guilty
//
$valid_user = 1;

// Handle the POST variables.  I wish PHP were Perl...
//
$login     = (isset($_POST['login'])) ? $_POST['login'] : '';
$password  = (isset($_POST['password'])) ? $_POST['password'] : '';

// Get the user info from tblUsers
//
$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);
$sql = "select * from wbtbl_users where login = '$login'";
$result = DB_query($sql, $db);

$num_rows = DB_num_rows($result);

if ($num_rows > 1) {
    die("More than one login by name row['login'] found in login.php");
}


if ($num_rows == 1) {

    $row = DB_fetch_array($result);


    // Authenticate
    //
    if ($login     != $row['login']) {
        $valid_user = 0;
    }
    if ($password  != $row['password']) {
        $valid_user = 0;
    }
} else {
    $valid_user = 0;
}


if ($valid_user == 1) {
    // Coming from a form placed in header.php
    //
    $_SESSION['login'] = $_POST['login'];
    $_SESSION['flags'] = $row['flags'];
    $_SESSION['www'] = $row['www'];
    $_SESSION['email'] = $row['email'];
    Header("Location: $wb_url/index.php");
    exit(0);
} else {
    Kill_Session();
}

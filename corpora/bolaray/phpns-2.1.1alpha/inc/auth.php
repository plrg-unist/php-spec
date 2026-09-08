<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/
if ($_COOKIE['cookie_auth'] && !$_SESSION['auth']) { //if we detect a cookie, we have to verify that it is valid.
    $globalvars['cookie_auth'] = clean_data($_COOKIE['cookie_auth']); //clean the data

    //check and see if there is an entry with that cookie auth code
    $cookie_check = general_query('SELECT * FROM '.$databaseinfo['prefix'].'cookielog WHERE cookie_id="'.$globalvars['cookie_auth'].'"');

    if (mysql_num_rows($cookie_check) > 0) {

        //we need an mysql_fetch_array too... so we can't use the previous one (without annoying while clauses)
        $cookie_check = general_query('SELECT * FROM '.$databaseinfo['prefix'].'cookielog WHERE cookie_id="'.$globalvars['cookie_auth'].'"', true);
        $user_fetch = general_query('SELECT * FROM '.$databaseinfo['prefix'].'users WHERE id="'.$cookie_check['user_id'].'"', true);
        $user_rank_data = general_query('SELECT * FROM '.$databaseinfo['prefix'].'ranks WHERE id="'.$user_fetch['rank_id'].'"', true);

        $_SESSION['auth'] = 'yes';
        $_SESSION['username'] = $user_fetch['user_name'];
        $_SESSION['userID'] = $user_fetch['id'];
        $_SESSION['permissions'] = $user_rank_data['permissions'];
        $_SESSION['path'] = $globalvars['path_to'];
    }
}

if (@$_SESSION['auth'] != "yes") {
    header("Location: login.php");
    die();
}

if (@$_SESSION['path'] != $globalvars['path_to']) {
    header("Location: login.php");
    die();
}

$globalvars['rank'] = $_SESSION['permissions']; //set new array

/* Rank authority

    ranks are recordered in a session variable, somewhat like this:
    1,1,1,1,1,1,1,1,1,1,1,1

    WHICH TRANLATES TO

    createranks,manageranks,loginrecords,preferences,loggingin,
    createarticles,approve,editarticles,deletearticles,createusers,
    editusers,deleteusers

    So, we can use the following vars to identify each permission #:

    create ranks = $data['permissions'][0];
    manage ranks = $data['permissions'][2];
    view login records = $data['permissions'][4];
    edit preferences = $data['permissions'][6];
    logging in = $data['permissions'][8];
    *create articles = $data['permissions'][10];
    *approve articles = $data['permissions'][12];
    edit articles = $data['permissions'][14];
    delete articles = $data['permissions'][16];
    create users = $data['permissions'][18];
    edit users = $data['permissions'][20];
    delete users = $data['permissions'][22];


    ====================
    TEMPLATE FOR DISALLOWING/ALLOWING
    ====================

        //quick permission check (redir to error) reference above this
        if ($globalvars['rank'][#] == 0) {
            header("Location: index.php?do=permissiondenied");
            die(); //if header doesn't work, kill the script.
        }
*/

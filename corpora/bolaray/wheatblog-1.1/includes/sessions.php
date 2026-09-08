<?php

include_once("$wb_class_dir/classDatabase.php");


function Start_Session()
{
    global $session_dir;

    if ($session_dir != '') {
        session_save_path($session_dir);
    }

    if (! isset($_SESSION)) {
        session_start();
        // Supposedly a fix for IE6
        header('Cache-control: private');
        My_Cache();

        if (! isset($_SESSION['db']) || gettype($_SESSION['db']->db) != 'resource') {
            touchDatabaseSession();
        }

    }
}



function touchDatabaseSession()
{
    $_SESSION['db'] = new DatabaseClass();
}







function Start_Admin_Session()
{
    global $wb_url, $session_dir;

    if ($session_dir != '') {
        session_save_path($session_dir);
    }

    session_start();

    // Supposedly a fix for IE6
    header('Cache-control: private');

    if (! isAdmin()) {
        Header("Location: $wb_url");
    }
}



// Note: Session has to already be started before you can kill it.
//
function Kill_Session()
{
    global $wb_url;

    session_unset();
    session_destroy();
    Header("Location: $wb_url/index.php?login=0");
    exit(0);
}




function My_Cache()
{
    header("Expires: Mon, 26 Jul 1984 05:00:00 GMT");
    header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
    header("Cache-Control: no-store, no-cache, must-revalidate");
    header("Cache-Control: post-check=0, pre-check=0", false);
    header("Pragma: no-cache");
}



function isAdmin()
{
    if (! isLoggedIn()) {
        return false;
    }

    global $bitmask;

    $arg = func_get_args();

    if (func_num_args() != 1) {
        $flags = $_SESSION['flags'];
    } else {
        $flags = $arg[0];
    }


    if ($flags & $bitmask['admin']) {
        return true;
    } else {
        return false;
    }
}



function isLoggedIn()
{
    if (! isset($_SESSION['login'])) {
        return false;
    } else {
        return true;
    }
}



function isRegistered()
{
    if (! isLoggedIn()) {
        return false;
    }

    global $bitmask;

    $arg = func_get_args();

    if (func_num_args() != 1) {
        $flags = $_SESSION['flags'];
    } else {
        $flags = $arg[0];
    }

    if ($flags & $bitmask['registered']) {
        return true;
    } else {
        return false;
    }
}


function isCookies()
{
    if (! isLoggedIn()) {
        return false;
    }

    global $bitmask;

    $arg = func_get_args();

    if (func_num_args() != 1) {
        $flags = $_SESSION['flags'];
    } else {
        $flags = $arg[0];
    }

    if ($flags & $bitmask['cookies']) {
        return true;
    } else {
        return false;
    }
}



// Bitmask Fields
//
$bitmask = array(
    'admin'      => 0x1,      // 2^0  =  1    // 1: Admin       0: Non admin
    'cookies'    => 0x2,      // 2^1  =  2    // 1: Cookies     0: No Cookies
    'registered' => 0x4,      // 2^2  =  4    // 1: Registered  0: Unregistered
    'unused'     => 0x8,      // 2^3  =  8
    'unused'     => 0x10,     // 2^4  = 16
    'unused'     => 0x20,     // 2^5  = 32
    'unused'     => 0x40,     // 2^6  = 64
    'unused'     => 0x80,     // 2^7  = 128
    'unused'     => 0x100,    // 2^8  = 256
    'unused'     => 0x200,    // 2^9  = 512
    'unused'     => 0x400,    // 2^10 = 1024
    'unused'     => 0x800,    // 2^11 = 2308
    'unused'     => 0x1000,   // 2^12 = 4096
    'unused'     => 0x2000,   // 2^13 = 8192
    'unused'     => 0x4000,   // 2^14 = 16384
    'unused'     => 0x8000    // 2^15 = 32768
);

<?php

if (isset($_POST['GLOBALS']) || isset($_FILES['GLOBALS']) || isset($_GET['GLOBALS']) || isset($_COOKIE['GLOBALS'])  || isset($_REQUEST['GLOBALS'])) {
    die("Possibility of hacking attempt !");
}

if (isset($_SESSION) && !is_array($_SESSION)) {
    die("Possibility of hacking attempt !");
}

if(!get_magic_quotes_gpc()) {
    if(is_array($_GET)) {
        while(list($k, $v) = each($_GET)) {
            if(is_array($_GET[$k])) {
                while(list($k2, $v2) = each($_GET[$k])) {
                    $_GET[$k][$k2] = addslashes($v2);
                    $_GET[$k][$k2] = htmlspecialchars($v2);
                }
                @reset($_GET[$k]);
            } else {
                $_GET[$k] = addslashes($v);
                $_GET[$k] = htmlspecialchars($v);
            }
        }
        @reset($_GET);
    }

    if(is_array($_POST)) {
        while(list($k, $v) = each($_POST)) {
            if(is_array($_POST[$k])) {
                while(list($k2, $v2) = each($_POST[$k])) {
                    $_POST[$k][$k2] = addslashes($v2);
                }
                @reset($_POST[$k]);
            } else {
                $_POST[$k] = addslashes($v);
            }
        }
        @reset($_POST);
    }

    if(is_array($_COOKIE)) {
        while(list($k, $v) = each($_COOKIE)) {
            if(is_array($_COOKIE[$k])) {
                while(list($k2, $v2) = each($_COOKIE[$k])) {
                    $_COOKIE[$k][$k2] = addslashes($v2);
                }
                @reset($_COOKIE[$k]);
            } else {
                $_COOKIE[$k] = addslashes($v);
            }
        }
        @reset($_COOKIE);
    }
}

<?php
/*********************************************
* ------------                               *
* | Auth.php |                               *
* ------------                               *
* PHPNews - 1.3.0 Release                    *
* Open Source Project started by Pierce Ward *
*                                            *
* Software Distributed at:                   *
* http://newsphp.sourceforge.net             *
* ========================================== *
* (c) 2003, 2005 Pierce Ward (Big P)         *
* All rights reserved.                       *
* ========================================== *
* This program has been written under the    *
* terms of the GNU General Public Licence as *
* published by the Free Software Foundation. *
*                                            *
* The GNU GPL can be found in gpl.txt        *
*********************************************/

session_start();
$dbQueries = 0;

include_once('settings.php');

/* Change error reporting for connection to DB */
error_reporting(E_NOTICE);

/* Don't edit - Connects to DB */
$dbcon = mysql_connect($db_server, $db_user, $db_passwd);
checkCon($dbcon);

$dbcon = mysql_select_db($db_name);
checkCon($dbcon);

/* Grabs Settings and puts it in an Array */
$dbcon = mysql_query('SELECT variable,value FROM ' . $db_prefix . 'settings');
$dbQueries++;
checkCon($dbcon);

/* Checks if there was an error with connection & prints error  */
function checkCon($con)
{
    if (!$con) {
        echo mysql_error();
        exit();
    }
}

/* Change back error reporting */
error_reporting(E_ALL ^ E_NOTICE);

$Settings = array();
while ($row = mysql_fetch_array($dbcon)) {
    $Settings[$row[0]] = $row[1];
}

$auth = false;
$in_user = '';
$in_password = '';

if((isset($_POST['user']) && isset($_POST['password'])) || (isset($_SESSION['user']) && isset($_SESSION['password']))) {
    if(isset($_SESSION['user']) && isset($_SESSION['password'])) {
        $in_user = $_SESSION['user'];
        $in_password = $_SESSION['password'];
    } elseif(isset($_POST['user']) && isset($_POST['password'])) {
        if (!get_magic_quotes_gpc()) {
            $in_user = addslashes($_POST['user']);
            $in_password = addslashes($_POST['password']);
        } else {
            $in_user = $_POST['user'];
            $in_password = $_POST['password'];
        }
    }

    $result = mysql_query('SELECT * FROM ' . $db_prefix . 'posters WHERE username = \'' . $in_user . '\' AND password = password(\'' . $in_password . '\')');
    $dbQueries++;

    if(mysql_numrows($result) != 0) {
        $auth = true;
        $_SESSION['user'] = $in_user;
        $_SESSION['password'] = $in_password;
    } else {
        $bad_details = true;
    }

    /* Put all the Users Details in one Array */
    $userDetails = array();
    while($row = mysql_fetch_assoc($result)) {
        $userDetails = $row;
    }
}

$lang = $Settings['language'];

/* Inlcude users specific language */
if (is_Array($userDetails)) {
    if(file_exists('languages/' . $userDetails['language'] . '.admin.lng')) {
        include_once('languages/' . $userDetails['language'] . '.admin.lng');
        setlocale(LC_TIME, $userDetails['language']);
    } else {
        include_once('languages/' . $lang  . '.admin.lng');
        setlocale(LC_TIME, $lang);
    }
}
/* You're about to log in/no user language is specified */
elseif(file_exists('languages/' . $lang . '.admin.lng')) {
    include_once('languages/' . $lang . '.admin.lng');
    setlocale(LC_TIME, $lang);
} else {
    include_once('languages/en_GB.admin.lng');
    setlocale(LC_TIME, $lang);
}

$language = $lng;

/* If user isn't logged in, print the login form */
if(!$auth) {
    echo '<?xml version="1.0" encoding="'.$language['CHARSET'].'"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
      <title>
         PHPNews - ' , $language['CONTENT_LOGIN'] , '
      </title>
      <link href="phpnews_package.css" rel="stylesheet" type="text/css" />
   </head>
   <body>
      <form action="index.php" method="post">';

    /* If username / password is incorrect */
    if($bad_details == true) {
        echo '
         <table class="login" cellspacing="0" cellpadding="0">
            <tr>
               <th colspan="2">
                  ' , $language['CONTENT_ERRORLOGINHEAD'] , '
               </th>
            </tr>
            <tr>
                <td colspan="2">
                   ' , $language['CONTENT_ERRORLOGIN'] , '
                </td>
            </tr>
         </table>
         <br />';
    }

    echo '
         <table class="login" cellspacing="0" cellpadding="0">
            <tr>
               <th colspan="2">
                  ' , $language['CONTENT_LOGIN'] , '
               </th>
            </tr>';
    /* Don't let the user log in if install.php hasn't been removed */
    if(file_exists('install.php')) {
        echo '
                    <tr colspan="2">
                        <td>
                           ' , $language['CONTENT_INSTALLER_REMOVE'] , '
                        </td>
                    </tr>';
    }
    /* Otherwise, print the Login Form */
    else {
        echo '
            <tr>
               <td class="left">
                  <label for="user">' , $language['CONTENT_POSTERUSERNAME'] , ':</label>
               </td>
               <td>
                  <input id="user" name="user" type="text" size="25" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="password">' , $language['CONTENT_POSTERPASSWORD'] , ':</label>
               </td>
               <td>
                  <input id="password" name="password" type="password" size="25" />
               </td>
            </tr>
            <tr>
               <td class="center" colspan="2">
                  <input type="submit" name="submit" value="' , $language['CONTENT_BUTTONSUBMIT'] , '" />
               </td>
            </tr>';
    }
    echo '
         </table>
      </form>
      <p class="copyright">
         Copyright &copy; 2003 - 2005 <a href="http://newsphp.sourceforge.net/">PHPNews</a>
      </p>
   </body>
</html>';
    exit;
}

<?php
/*********************************************
* --------------------                       *
* | SendToFriend.php |                       *
* --------------------                       *
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

include('settings.php');

/* Don't edit - Connects to DB */
$dbcon = mysql_connect($db_server, $db_user, $db_passwd);
mysql_select_db($db_name);

/* Grabs Settings and puts it in an Array */
$result = mysql_query('SELECT variable,value FROM ' . $db_prefix . 'settings');
$dbQueries++;

$Settings = array();
while ($row = mysql_fetch_array($result)) {
    $Settings[$row[0]] = $row[1];
}

$lang = $Settings['language'];

if(!file_exists('languages/' . $lang . '.news.lng')) {
    include_once('languages/en_GB.news.lng');
} else {
    include_once('languages/' . $lang . '.news.lng');
}
$language = $lng;

/* Make sure the Send To Friend function is enabled before doing anything else */
if ($Settings['enablestf'] != 1) {
    die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_DISABLED']);
}

if (!$_POST['mid'] && !$_GET['mid']) {
    die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_GENERALERROR']);
}

if ($_GET['action'] == 'post') {
    post();
}

function post()
{
    global $Settings, $language;

    /* Error message given if a mistake is made */
    $error_goback = '<br /><a href="#" onClick="history.go(-1);">' . $language['CONTENT_SETTINGSCLICKHERE'] . '</a> ' . $language['CONTENT_ERROREMAIL2'];

    $_POST['fromname'] = trim($_POST['fromname']);
    $_POST['fromemail'] = trim($_POST['fromemail']);
    $_POST['toemail'] = trim($_POST['toemail']);
    $_POST['message'] = trim($_POST['message']);

    /* Check required fields were entered */
    if (!$_POST['fromname']) {
        die($language['CONTENT_SENDTOFRIENDFROMNAME'] . ' ' . $error_goback);
    }

    if (!$_POST['fromemail']) {
        die($language['CONTENT_SENDTOFRIENDFROMEMAIL'] . ' ' . $error_goback);
    }

    if (!$_POST['toemail']) {
        die($language['CONTENT_SENDTOFRIENDTOEMAIL'] . ' ' . $error_goback);
    }

    if (!$_POST['message']) {
        die($language['CONTENT_SENDTOFRIENDMSG'] . ' ' . $error_goback);
    }

    /* Check for valid Email Addresses */
    if (!eregi('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', $_POST['toemail'])) {
        die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_ERROREMAIL'] . '' . $error_goback);
    }

    if (!eregi('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', $_POST['fromemail'])) {
        die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_ERROREMAIL'] . '' . $error_goback);
    }

    /* The Message body of the Email */
    $newmsg = "{$_POST['message']}\n\n{$language['CONTENT_SENDTOFRIENDEMAILMSG']}\n{$Settings['siteurl']}?action=fullnews&id={$_POST['mid']}";
    $newmsg = stripslashes($newmsg);

    /* Add good header information to keep the email being turned away from Hotmail. */
    $headers = "MIME-Version: 1.0\r\n";
    $headers .= "From: {$_POST['fromname']} <{$_POST['fromemail']}>\r\n";
    $headers .= "X-Priority: 1\r\n";
    $headers .= "X-MSMail-Priority: High\r\n\r\n";

    mail($_POST['toemail'], $_POST['subject'], $newmsg, $headers) or die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_SENDTOFRIENDERROR']);

    /* Include Thank You Message */
    include('templates/sent_temp.php');

    exit;
}

/* check for mid */
if (!is_numeric($_GET['mid'])) {
    die('hacking attempt');
}

/* Grab the Subject of News Post */
$SQL_query = mysql_query('SELECT subject,maintext FROM ' . $db_prefix . 'news WHERE id = ' . $_GET['mid'] . '');
$title = mysql_fetch_assoc($SQL_query);

/* Give error message */
if ($title['subject'] == '') {
    die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_ERRORREQUIREDVARIABLE']);
}

/* Print out the Send to a Friend Form */
echo '<?xml version="1.0" encoding="' , $language['CHARSET'] , '"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
      <title>
         ' , $language['CONTENT_SENDTOFRIENDTITLE'] , '
      </title>
   </head>
   <body>
      <form action="sendtofriend.php?action=post" method="post">
         <p>
            <input type="hidden" name="mid" value="' , $_GET['mid'] , '" />
            <input type="hidden" name="subject" value="' , stripslashes($title['subject']) , '" />
         </p>';

/* Include Send To Friend Template */
include('templates/sendtofriend_temp.php');

echo '
      </form>
   </body>
</html>';

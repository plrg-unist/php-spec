<?php

error_reporting(E_ALL ^ E_NOTICE);
/*********************************************
* -----------------                          *
* | Headlines.php |                          *
* -----------------                          *
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

/* Get the absolute path */
$path = __FILE__;
$path = str_replace('headlines.php', '', $path);

include($path . 'settings.php');

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

/* Check if headlines are being display by category or by views */
if(isset($_GET['headcat']) && is_Numeric($_GET['headcat'])) {
    $sql = 'SELECT id,posterid,time,subject FROM ' . $db_prefix . 'news WHERE catid=\'' . $_GET['headcat'] . '\' AND trusted = 1 ORDER BY id DESC LIMIT ' . $Settings['numtoshowhead'] . '';
} elseif(isset($_GET['headviews']) && ($_GET['headviews'] == '1')) {
    if(($_GET['headorder'] == 'down') || ($_GET['headorder'] == '')) {
        $sql = 'SELECT id,posterid,time,subject FROM ' . $db_prefix . 'news WHERE trusted = 1 ORDER BY views DESC LIMIT ' . $Settings['numtoshowhead'] . '';
    } elseif($_GET['headorder'] == 'up') {
        $sql = 'SELECT id,posterid,time,subject FROM ' . $db_prefix . 'news WHERE trusted = 1 ORDER BY views ASC LIMIT ' . $Settings['numtoshowhead'] . '';
    }
} else {
    $sql = 'SELECT id,posterid,time,subject FROM ' . $db_prefix . 'news WHERE trusted = 1 ORDER BY id DESC LIMIT ' . $Settings['numtoshowhead'] . '';
}

/* Do the desired Query */
$SQL_query = mysql_query($sql);

while($headlines = mysql_fetch_assoc($SQL_query)) {
    /* Set Variables */
    $time = strftime($Settings['shorttimeformat'], $headlines['time']);
    $subject = stripslashes($headlines['subject']);
    $mid = $headlines['id'];

    /* Find out who made the post (keeps track of usernames) */
    $query = mysql_query('SELECT username,email,avatar FROM ' . $db_prefix . 'posters WHERE id = ' . $headlines['posterid'] . ' OR username = \'' . $headlines['postername'] . '\'');
    $details = mysql_fetch_assoc($query);
    $username = $details['username'];

    if (!$username) {
        $username = $headlines['postername'];
    }

    include($path . 'templates/headlines_temp.php');
}

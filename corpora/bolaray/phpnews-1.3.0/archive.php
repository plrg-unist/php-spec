<?php

error_reporting(E_ALL ^ E_NOTICE);
/*********************************************
* ---------------                            *
* | Archive.php |                            *
* ---------------                            *
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
$path = str_replace('archive.php', '', $path);

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

/* Include The Language File */
$lang = $Settings['language'];

if(!file_exists($path . 'languages/' . $lang . '.news.lng')) {
    include_once($path . 'languages/en_GB.news.lng');
    setlocale(LC_TIME, $lang);
} else {
    include_once($path . 'languages/' . $lang . '.news.lng');
    setlocale(LC_TIME, $lang);
}
$language = $lng;

/*
  Archive Functions
  You can call each function by its name, eg.
  <? byMonth(); ?>
  You can only call either byMonth(); or byCat();
  not both in the same page.
*/

/* Display News in Archive by Month/Year */
function byMonth()
{
    global $Settings, $language, $path, $_SERVER, $db_prefix;

    /* Order the news by Month/Year  */
    if (!$_GET['month'] && !$_GET['year']) {
        $SQL_query = mysql_query('SELECT DISTINCT month,year FROM ' . $db_prefix . 'news ORDER by id DESC');

        while ($arc = mysql_fetch_assoc($SQL_query)) {
            /* Get the total number of posts per month */
            $total = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news WHERE month = \'' . $arc['month'] . '\' AND year = \'' . $arc['year'] . '\'');
            $var = mysql_fetch_assoc($total);

            /* Set up Variables for Template */
            $month = strftime('%B', mktime(0, 0, 0, $arc['month'], 1, 0));
            $year = $arc['year'];
            $numPosts = $var['total'];
            $url = $_SERVER['PHP_SELF'];

            include($path . 'templates/date_temp.php');
        }
    }
    /* Display links to the articles */
    elseif (isset($_GET['month']) && isset($_GET['year'])) {
        $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.subject,n.time,p.username,p.email'
                                 . ' FROM ' . $db_prefix . 'news AS n'
                                 . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                                 . ' WHERE month=\'' . $_GET['month']. '\' AND year=\'' . $_GET['year'] . '\''
                                 . ' AND n.trusted = 1'
                                 . ' ORDER by n.id DESC');

        while ($posts = mysql_fetch_assoc($SQL_query)) {
            /* Set up easy variables */
            $url = $Settings['siteurl'];
            $id = $posts['id'];
            $subject = stripslashes($posts['subject']);
            $username = $posts['username'];
            $time = strftime($Settings['shorttimeformat'], $posts['time']);

            if (!$username) {
                $username = $posts['postername'];
            }

            if ($posts['email'] != '') {
                $username = '<a href="mailto:' . $posts['email'] . '">' . $username . '</a>';
            } else {
                $username = $username;
            }

            include($path . 'templates/link_temp.php');
        }
    }
    /* Otherwise, something went wrong, so print out an error message */
    else {
        echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_ERRORREQUIREDVARIABLE'];
    }
}

/* Display News in Archive ordered by Categories */
function byCat()
{
    global $Settings, $language, $path, $_SERVER, $db_prefix;

    /* Sort News by Categories */
    if (!$_GET['cat']) {
        $SQL_query = mysql_query('SELECT DISTINCT * FROM ' . $db_prefix . 'categories ORDER by id ASC');
        while ($cat = mysql_fetch_assoc($SQL_query)) {
            $url = $_SERVER['PHP_SELF'];
            $catid = $cat['id'];
            $category = $cat['catname'];

            if ($cat['caticon'] != '') {
                $caticon = '<img src="' . $cat['caticon'] . '" border="0" alt="' . $category . '">';
            } else {
                $caticon = '';
            }

            include($path . 'templates/cat_temp.php');
        }
    }
    /* Sort News by month, with News from selected Category only */
    elseif (isset($_GET['cat']) && !isset($_GET['month']) && !isset($_GET['year'])) {
        $SQL_query = mysql_query('SELECT DISTINCT month,year FROM ' . $db_prefix . 'news ORDER by id DESC');

        while ($cat = mysql_fetch_assoc($SQL_query)) {
            /* Get the total number of posts per month */
            $total = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news WHERE catid = \'' . $_GET['cat'] . '\' AND month=\'' . $cat['month'] . '\' AND year=\'' . $cat['year'] . '\'');
            $var = mysql_fetch_assoc($total);

            /* Set up easy Variables */
            $month = strftime('%B', mktime(0, 0, 0, $cat['month'], 1, 0));
            $year = $cat['year'];
            $numPosts = $var['total'];
            $url = $_SERVER['PHP_SELF'];
            $catid = $_GET['cat'];

            include($path . 'templates/catdate_temp.php');
        }
    }
    /* Display the news links from the Category */
    elseif (isset($_GET['cat']) && isset($_GET['month']) && isset($_GET['year'])) {
        $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.subject,n.time,p.username,p.email'
                                 . ' FROM ' . $db_prefix . 'news AS n'
                                 . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                                 . ' WHERE catid=\'' . $_GET['cat'] . '\' AND month=\'' . $_GET['month']. '\' AND year=\'' . $_GET['year'] . '\''
                                 . ' AND n.trusted = 1'
                                 . ' ORDER by n.id DESC');

        while ($posts = mysql_fetch_assoc($SQL_query)) {
            /* Set up easy variables */
            $url = $Settings['siteurl'];
            $id = $posts['id'];
            $subject = stripslashes($posts['subject']);
            $username = $row['username'];
            $time = strftime($Settings['shorttimeformat'], $posts['time']);

            if (!$username) {
                $username = $posts['postername'];
            }

            if ($row['email'] != '') {
                $username = '<a href="mailto:' . $row['email'] . '">' . $username . '</a>';
            } else {
                $username = $username;
            }

            include($path . 'templates/link_temp.php');
        }
    } else {
        /* Otherwise, something went wrong, so print out an error message */
        echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_ERRORREQUIREDVARIABLE'];
    }
}

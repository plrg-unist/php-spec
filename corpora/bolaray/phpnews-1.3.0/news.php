<!-- (c) 2003, 2005 PHPNews - http://newsphp.sourceforge.net/ -->
<?php
error_reporting(E_ALL ^ E_NOTICE);
/*********************************************
* ------------                               *
* | News.php |                               *
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

/* Get the absolute path for including files */
$path = __FILE__;
$path = str_replace('news.php', '', $path);

include_once($path . 'settings.php');

/* Don't edit - Connects to DB */
$dbcon = mysql_connect($db_server, $db_user, $db_passwd);
mysql_select_db($db_name);

/* Grabs Settings and puts it in an Array */
$result = mysql_query('SELECT variable,value FROM ' . $db_prefix . 'settings');

$Settings = array();
while ($row = mysql_fetch_array($result)) {
    $Settings[$row['0']] = $row['1'];
}

$lang = $Settings['language'];

/* Opens language file */
if(!file_exists($path . 'languages/' . $lang . '.news.lng')) {
    include_once($path . 'languages/en_GB.news.lng');
    setlocale(LC_TIME, $lang);
} else {
    include_once($path . 'languages/' . $lang . '.news.lng');
    setlocale(LC_TIME, $lang);
}
$language = $lng;

if(!isset($_GET['action'])) {
    news();
} elseif($_GET['action'] == 'fullnews') {
    fullNews();
} elseif($_GET['action'] == 'post') {
    post();
} elseif($_GET['action'] == 'showcat' && isset($_GET['catid'])) {
    showCat();
}

function news()
{
    global $Settings, $language, $_SERVER, $path, $db_prefix;

    /* Prints JavaScript for Send to Friend Link */
    if ($Settings['enablestf'] == 1) {
        if (isset($_GET['prevnext']) && !is_Numeric($_GET['prevnext'])) {
            die('<b>' . $language['CONTENT_ERROR'] . '</b>: Hacking Attempt');
        }

        ?>
<script type="text/javascript">
<!--
        function sendtof(desktopURL)
        {
          desktop = window.open(desktopURL, "SendToFriend", "toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,width=400,height=275,resizable=no");
        }
// -->
</script>
<?php
    }
    /* Set up Previous/Next links if enabled */
    if ($Settings['enableprevnext'] == 1) {
        /* If we're on the first page set defaults */
        if (!isset($_GET['prevnext']) || $_GET['prevnext'] == 0) {
            $_GET['prevnext'] = 0;
            $nextpage = $_GET['prevnext'] + $Settings['numtoshow'];
            $previouspage = $_GET['prevnext'];

            /* Find total number of News Posts */
            $numPosts = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news');
            $var = mysql_fetch_assoc($numPosts);

            if ($var['total'] > $Settings['numtoshow']) {
                $include = 1;
            }
        }
        /* Otherwise calculate prev/next links */
        elseif (isset($_GET['prevnext']) && is_Numeric($_GET['prevnext'])) {
            $previouspage = $_GET['prevnext'] - $Settings['numtoshow'];

            /* Find total number of News Posts */
            $numPosts = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news');
            $var = mysql_fetch_assoc($numPosts);

            /* If the number of posts is greater, there's enough room for another page */
            if ($var['total'] > ($_GET['prevnext'] + $Settings['numtoshow'])) {
                $nextpage = $_GET['prevnext'] + $Settings['numtoshow'];
            } else {
                $nextpage = 0;
            }

            /* Include Previous/Next Template */
            $include = 1;
        }
    } else {
        $_GET['prevnext'] = 0;
    }

    /* Get information about the News Post */
    $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.time,n.subject,n.titletext,n.maintext,n.catid,n.views,p.username,p.email,p.avatar,c.catname,c.caticon'
                             . ' FROM ' . $db_prefix . 'news AS n'
                             . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                             . ' LEFT JOIN ' . $db_prefix . 'categories AS c ON(n.catid=c.id)'
                             . ' WHERE n.trusted = 1'
                             . ' ORDER by n.id DESC'
                             . ' LIMIT ' . $_GET['prevnext'] . ', ' . $Settings['numtoshow'] . '');

    while($news = mysql_fetch_assoc($SQL_query)) {

        /* Set Variables */
        $time = strftime($Settings['timeformat'], $news['time']);
        $subject = stripslashes($news['subject']);
        $titletext = stripslashes($news['titletext']);
        $maintext = stripslashes($news['maintext']);
        $email = $news['email'];

        /* Find out how many views of this article */
        if($Settings['enablecountviews'] == '1') {
            $views = stripslashes($news['views']);
        }

        /* Print Comments if enabled */
        if ($Settings['enablecomments'] == 1) {
            $query2 = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'comments WHERE mid = ' . $news['id'] . '');
            $var = mysql_fetch_assoc($query2);
            $comments = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $news['id'] . '">' . $language['CONTENT_NEWSCOMMENTS'] . ' (' . $var['total'] . ')</a>';
        }

        /* If Categories are enabled... */
        if ($Settings['enablecats'] == 1) {
            if ($news['catid'] != 0) {
                if ($news['catname'] != '') {
                    $category = '<a href="' . $_SERVER['PHP_SELF'] . '?action=showcat&amp;catid=' . $news['catid'] . '">' . $news['catname'] . '</a>';
                }

                if ($news['caticon'] != '') {
                    $caticon = '<img src="' . $news['caticon'] . '" border="0" alt="' . $news['catname'] . '" />';
                }
            }
        }

        /* Set the News Posters Username */
        $username = $news['username'];

        if (!$username) {
            $username = $news['postername'];
        }

        /* Get the Posters Avatar */
        if ($Settings['enableavatars'] == 1) {
            if($news['avatar'] != '') {
                $avatar = '<img src="' . $news['avatar'] . '" border="0" alt="' . $username . '\'s avatar" />';
            } else {
                $avatar = '';
            }
        }

        /* Display link to show comments & news if enabled */
        if ($maintext != '' && $Settings['showcominnews'] == 1 && $Settings['enablecomments'] == 1) {
            $maintext = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $news['id'] . '">' . $language['CONTENT_NEWSFULLSTORY'] . '</a>';
        } elseif ($maintext != '') {
            $maintext = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;id=' . $news['id'] . '">' . $language['CONTENT_NEWSFULLSTORY'] . '</a>';
        } else {
            $maintext = '';
        }

        if ($Settings['enablestf'] == 1) {
            $sendtofriend = '<a href="javascript:sendtof(\'' . $Settings['phpnewsurl'] . 'sendtofriend.php?mid=' . $news['id'] . '\')">' . $language['CONTENT_NEWSSTFLINK'] . '</a>';
        }

        /* Parse the code / smilies */
        $maintext = parseCode($maintext);
        $titletext = parseCode($titletext);

        include($path . 'templates/news_temp.php');
        echo "\n";

        /* Clear Variables */
        $category = '';
        $caticon = '';
    }

    /* If previous/next links are enabled */
    if ($Settings['enableprevnext'] == 1 && $include == 1) {
        echo '<br />' , "\n";

        /* Show Previous Page link? */
        if($_GET['prevnext'] != null && $_GET['prevnext'] != 0) {
            echo '<span style="margin-right:5px;"><a href="' , $_SERVER['PHP_SELF'] , '?prevnext=' , $previouspage , '">' , $language['CONTENT_PREVIOUS'] , '</a></span>';
            echo "\n";
        }

        /* Show Next Page Link? */
        if($nextpage != 0) {
            echo '<span style="margin-left:5px;"><a href="' , $_SERVER['PHP_SELF'] , '?prevnext=' , $nextpage , '">' , $language['CONTENT_NEXT'] , '</a></span>';
            echo "\n";
        }
    }
}

function fullNews()
{
    global $Settings, $language, $_SERVER, $path, $showcomments, $db_prefix;

    /* Check ID is existent and number */
    if (!$_GET['id'] || !is_Numeric($_GET['id'])) {
        echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_GENERALERROR'];
    } else {
        if($Settings['enablecountviews'] == '1') {
            $countviews = mysql_query("UPDATE " . $db_prefix . "news SET views=views+1 WHERE id='" . $_GET['id'] . "'");
        }

        /* Get information about the News Post */
        $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.time,n.subject,n.titletext,n.maintext,n.catid,n.views,p.username,p.email,p.avatar,c.catname,c.caticon'
                               . ' FROM ' . $db_prefix . 'news AS n'
                               . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                               . ' LEFT JOIN ' . $db_prefix . 'categories AS c ON(n.catid=c.id)'
                               . ' WHERE n.id = ' . $_GET['id'] . ''
                               . ' AND n.trusted = 1');

        /* Does this article exist? */
        if (!mysql_numrows($SQL_query)) {
            echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_NOTEXISTS'];
        } else {
            /* Prints JavaScript for Send to Friend Link */
            if ($Settings['enablestf'] == 1) {
                ?>
<script type="text/javascript">
<!--
        function sendtof(desktopURL)
        {
          desktop = window.open(desktopURL, "SendToFriend", "toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,width=400,height=275,resizable=no");
        }
// -->
</script>
<?php
            }

            /* Put News Post Info into an Array */
            $news = mysql_fetch_assoc($SQL_query);

            /* Set the Variables */
            $time = strftime($Settings['shorttimeformat'], $news['time']);
            $subject = stripslashes($news['subject']);
            $titletext = stripslashes($news['titletext']);
            $maintext = stripslashes($news['maintext']);

            /* Find out how many views of this article */
            if($Settings['enablecountviews'] == '1') {
                $views = stripslashes($news['views']);
            }

            /* Find out who made the post */
            $username = $news['username'];
            $email = $news['email'];

            /* Print Comments if enabled */
            if($Settings['enablecomments'] == 1) {
                $query2 = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'comments WHERE mid = ' . $_GET['id'] . '');
                $var = mysql_fetch_assoc($query2);
                $comments = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $_GET['id'] . '">' . $language['CONTENT_NEWSCOMMENTS'] . ' (' . $var['total'] . ')</a>';
            }

            /* If Categories are enabled... */
            if ($Settings['enablecats'] == 1) {
                if ($news['catid'] != 0) {
                    $category = '<a href="' . $_SERVER['PHP_SELF'] . '?action=showcat&amp;catid=' . $news['catid'] . '">' . $news['catname'] . '</a>';

                    if ($news['caticon'] != '') {
                        $caticon = '<img src="' . $news['caticon'] . '" border="0" alt="' . $news['catname'] . '" />';
                    } else {
                        $caticon = '';
                    }
                }
            }

            if($Settings['enableavatars'] == '1' && $news['avatar'] != '') {
                $avatar = '<img src="' . $news['avatar'] . '" border="0" alt="' . $username . '\'s avatar" />';
            }

            if(!$username) {
                $username = $news['postername'];
            }

            if($Settings['enablestf'] == 1) {
                $sendtofriend = '<a href="javascript:sendtof(\'' . $Settings['phpnewsurl'] . 'sendtofriend.php?mid=' . $_GET['id'] . '\')">' . $language['CONTENT_NEWSSTFLINK'] . '</a>';
            }

            /* Parse the code */
            $maintext = parseCode($maintext);
            $titletext = parseCode($titletext);

            /* Include the Template */
            include($path . 'templates/fullnews_temp.php');

            /* Include the Comments */
            if($_GET['showcomments'] == 1 && $Settings['enablecomments'] == 1) {
                comments();
            }
        }
    }
}

function comments()
{
    global $_SERVER, $Settings, $language, $path, $db_prefix;

    // Order the Comments
    if ($Settings['showoldcomfirst'] != 1) {
        $order = ' DESC';
    }

    // Get the data for all the Comments
    $query = mysql_query('SELECT time,name,message,email,website FROM ' . $db_prefix . 'comments WHERE mid = ' . $_GET['id'] . ' ORDER by id' . $order);

    if($Settings['enablecommentpages'] == 1) {
        $num_rows = mysql_numrows($query);

        // Decide how many pages we should have.
        if ($num_rows > $Settings['commentsperpage']) {
            $tmppages = array();
            $tmpa = 1;
            for ($tmpb = 0; $tmpb < $num_rows; $tmpb += $Settings['commentsperpage']) {
                $tmppages[] = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $_GET['id'] . '&amp;pageid=' . $tmpb . '">' . $tmpa . '</a>';
                $tmpa++;
            }

            /*
            * The following was taken out because it was buggy
            */
            // Show links to all the pages?
            //if (count($tmppages) <= 5)
            $pages = implode(' ', $tmppages);
        // Or skip a few?
        //else
        //$pages = $tmppages[0] . ' ' . $tmppages[1] . ' ... ' . $tmppages[count($tmppages) - 2] . ' ' . $tmppages[count($tmppages) - 1];
        } else {
            $pages = '1';
        }

        // Check if it's the first page
        if(!isset($_GET['pageid']) || !is_Numeric($_GET['pageid']) || $_GET['pageid'] > $num_rows) {
            $_GET['pageid'] = 0;
        }

        $query = mysql_query('SELECT time,name,message,email,website FROM ' . $db_prefix . 'comments WHERE mid = ' . $_GET['id'] . ' ORDER by id' . $order . ' LIMIT ' . $_GET['pageid'] . ', ' . $Settings['commentsperpage']);
    }

    while ($comment = mysql_fetch_assoc($query)) {
        $time = strftime($Settings['shorttimeformat'], $comment['time']);
        $message = stripslashes($comment['message']);

        if ($comment['website'] != '') {
            $link = '[<a href="' . $comment['website'] . '">' . $language['CONTENT_NEWSWEBSITE'] . '</a>]';
        } else {
            $link = '';
        }

        // Censor comment if it is enabled
        if ($Settings['enablecensor'] == 1) {
            $comment['name'] = censor($comment['name']);
            $message = censor($message);
        }

        if ($comment['email'] != '') {
            $name = '<a href="mailto:' . $comment['email'] . '">' . $comment['name'] . '</a>';
        } else {
            $name = $comment['name'];
        }

        // Include Template for Added Comments
        include($path . 'templates/comments_temp.php');
    }

    // Check if User is banned from making Comments
    $isBanned = checkUserIP($_SERVER['REMOTE_ADDR']);

    // If the person is banned, print warning message
    if ($isBanned == 1) {
        echo '<br /><b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_BANNED'];
    } else {
        // Otherwise, print the form and include the template for adding comments
        echo '
<form action="' , $_SERVER['PHP_SELF'] , '?action=post" method="post">
<p style="margin:0px;">
<input type="hidden" name="mid" value="' , $_GET['id'] , '" />
</p>' , "\n";

        include($path . 'templates/comment_temp.php');

        echo '
</form>' , "\n";
    }
}

function showCat()
{
    global $Settings, $language, $_SERVER, $path, $db_prefix;

    if (!is_Numeric($_GET['catid'])) {
        die('<b>' . $language['CONTENT_ERROR'] . '</b>: ' . $language['CONTENT_GENERALERROR']);
    }

    /* Display Category News if it's enabled */
    if ($Settings['enablecats'] != 1) {
        echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_DISABLED'];
    } else {
        /* Prints JavaScript for Send to Friend Link */
        if ($Settings['enablestf'] == 1) {
            ?>
<script type="text/javascript">
<!--
        function sendtof(desktopURL)
        {
          desktop = window.open(desktopURL, "SendToFriend", "toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,width=400,height=275,resizable=no");
        }
// -->
</script>
<?php
        }

        /* Set up Previous/Next links if enabled */
        if ($Settings['enableprevnext'] == 1) {
            /* If we're on the first page set defaults */
            if (!isset($_GET['prevnext']) || $_GET['prevnext'] == 0) {
                $_GET['prevnext'] = 0;
                $nextpage = $_GET['prevnext'] + $Settings['numtoshowcat'];
                $previouspage = $_GET['prevnext'];

                /* Find total number of News Posts */
                $numPosts = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news WHERE catid=' . $_GET['catid'] . '');
                $var = mysql_fetch_assoc($numPosts);

                /* Only Include Previous/Next links if there is another page! */
                if ($var['total'] > $Settings['numtoshowcat']) {
                    $include = 1;
                }
            }
            /* Otherwise calculate prev/next links */
            elseif (isset($_GET['prevnext']) && is_Numeric($_GET['prevnext'])) {
                $previouspage = $_GET['prevnext'] - $Settings['numtoshowcat'];

                /* Find total number of News Posts */
                $numPosts = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news WHERE catid=' . $_GET['catid'] . '');
                $var = mysql_fetch_assoc($numPosts);

                /* If the number of posts is greater, there's enough room for another page */
                if ($var['total'] > ($_GET['prevnext'] + $Settings['numtoshowcat'])) {
                    $nextpage = $_GET['prevnext'] + $Settings['numtoshowcat'];
                } else {
                    $nextpage = 0;
                }

                /* Include Previous/Next Template */
                $include = 1;
            }
        } else {
            $_GET['prevnext'] = 0;
        }

        $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.time,n.subject,n.titletext,n.maintext,n.views,n.catid,p.username,p.email,p.avatar,c.catname,c.caticon'
                                 . ' FROM ' . $db_prefix . 'news AS n'
                                 . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                                 . ' LEFT JOIN ' . $db_prefix . 'categories AS c ON(n.catid=c.id)'
                                 . ' WHERE n.catid = ' . $_GET['catid'] . ''
                                 . ' AND n.trusted = 1'
                                 . ' ORDER by n.id DESC'
                                 . ' LIMIT ' . $_GET['prevnext'] . ', ' . $Settings['numtoshowcat'] . '');

        while($news = mysql_fetch_assoc($SQL_query)) {
            /* Set Variables */
            $time = strftime($Settings['timeformat'], $news['time']);
            $subject = stripslashes($news['subject']);
            $titletext = stripslashes($news['titletext']);
            $maintext = stripslashes($news['maintext']);
            $email = $news['email'];

            /* Find out how many views of this article */
            if($Settings['enablecountviews'] == '1') {
                $views = stripslashes($news['views']);
            }

            /* Find out who made the post (keeps track of usernames) */
            $username = $news['username'];

            /* Print Comments if enabled */
            if ($Settings['enablecomments'] == 1) {
                $query = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'comments WHERE mid = ' . $news['id'] . '');
                $var = mysql_fetch_assoc($query);
                $comments = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $news['id'] . '">' . $language['CONTENT_NEWSCOMMENTS'] . ' (' . $var['total'] . ')</a>';
            }

            $category = '<a href="' . $_SERVER['PHP_SELF'] . '?action=showcat&amp;catid=' . $news['catid'] . '">' . $news['catname'] . '</a>';

            if ($news['caticon'] != '') {
                $caticon = '<img src="' . $news['caticon'] . '" border="0" alt="' . $news['catname'] . '" />';
            } else {
                $caticon = '';
            }

            if (!$username) {
                $username = $news['postername'];
            }

            if ($Settings['enableavatars'] == 1) {
                if($news['avatar'] != '') {
                    $avatar = '<img src="' . $news['avatar'] . '" border="0" alt="' . $username . '\'s avatar" />';
                } else {
                    $avatar = '';
                }
            }

            /* Display link to show comments & news if enabled */
            if ($maintext != '' && $Settings['showcominnews'] == 1 && $Settings['enablecomments'] == 1) {
                $maintext = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $news['id'] . '">' . $language['CONTENT_NEWSFULLSTORY'] . '</a>';
            } elseif ($maintext != '') {
                $maintext = '<a href="' . $_SERVER['PHP_SELF'] . '?action=fullnews&amp;id=' . $news['id'] . '">' . $language['CONTENT_NEWSFULLSTORY'] . '</a>';
            } else {
                $maintext = '';
            }

            if ($Settings['enablestf'] == 1) {
                $sendtofriend = '<a href="javascript:sendtof(\'' . $Settings['phpnewsurl'] . 'sendtofriend.php?mid=' . $news['id'] . '\')">' . $language['CONTENT_NEWSSTFLINK'] . '</a>';
            }

            /* Parse the code */
            $maintext = parseCode($maintext);
            $titletext = parseCode($titletext);

            include($path . 'templates/news_temp.php');
            echo "\n";
        }

        /* If previous/next links are enabled */
        if ($Settings['enableprevnext'] == 1 && $include == 1) {
            echo '<br />' , "\n";
            $catid = $_GET['catid'];

            /* Show Previous Page link? */
            if($_GET['prevnext'] != null && $_GET['prevnext'] != 0) {
                echo '<span style="margin-right:5px;"><a href="' , $_SERVER['PHP_SELF'] , '?action=showcat&amp;catid=' , $catid , '&amp;prevnext=' , $previouspage , '">' , $language['CONTENT_PREVIOUS'] , '</a></span>';
                echo "\n";
            }

            /* Show Next Page Link? */
            if($nextpage != 0) {
                echo '<span style="margin-left:5px;"><a href="' , $_SERVER['PHP_SELF'] , '?action=showcat&amp;catid=' , $catid , '&amp;prevnext=' , $nextpage , '">' , $language['CONTENT_NEXT'] , '</a></span>';
                echo "\n";
            }
        }
    }
}

function post()
{
    global $_SERVER, $language, $Settings, $db_prefix;

    // Check if User is banned from making Comments
    $isBanned = checkUserIP($_SERVER['REMOTE_ADDR']);

    // If the person is banned, print warning message
    if ($isBanned == 1) {
        echo '<br /><b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_BANNED'];
    } else {
        /* Clean up */
        $_POST['name'] = str_replace(array('&', '"', '<', '>', '|'), array('&amp;', '&quot;', '&lt;', '&gt;', '&#124;'), trim($_POST['name']));
        $_POST['message'] = str_replace(array('&', '"', '<', '>', '|'), array('&amp;', '&quot;', '&lt;', '&gt;', '&#124;'), trim($_POST['message']));

        $_POST['email'] = trim($_POST['email']);
        $_POST['email'] = strip_tags($_POST['email']);
        $_POST['email'] = htmlspecialchars($_POST['email']);

        $_POST['website'] = trim($_POST['website']);
        $_POST['website'] = strip_tags($_POST['website']);
        $_POST['website'] = htmlspecialchars($_POST['website']);

        $_POST['message'] = replace($_POST['message'], 1);

        /* Make sure set amount of time has passed since last post by this person */
        $query = mysql_query('SELECT time FROM ' . $db_prefix . 'comments WHERE ip = \'' . $_SERVER['REMOTE_ADDR'] . '\' ORDER by id DESC LIMIT 1');
        $result = mysql_fetch_assoc($query);

        /* Make sure there are no problems with the Post */
        if ($Settings['enablecomments'] != 1) {
            echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_DISABLED'];
        } elseif (!$_POST['mid']) {
            echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_GENERALERROR'];
        } elseif ((time() + ($Settings['timeoffset']*60))-$result['time'] < $Settings['floodprotection']) {
            echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_ERRORWAIT'];
        }
        /* Check if it's a valid email */
        elseif ($_POST['email'] != '' && !eregi('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', $_POST['email'])) {
            echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_ERROREMAIL'];
        } elseif (!$_POST['message']) {
            echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $language['CONTENT_SENDTOFRIENDMSG'];
        }
        /* Everything is okay! */
        else {
            /* Set final defaults */
            if($_POST['website'] == 'http://') {
                $_POST['website'] = '';
            }

            if (!$_POST['name']) {
                $_POST['name'] = 'Guest';
            }

            $time = time() + ($Settings['timeoffset']*60);
            mysql_query('INSERT INTO ' . $db_prefix . 'comments (ip,mid,time,name,message,email,website) VALUES (\'' . $_SERVER['REMOTE_ADDR'] . '\', \'' . $_POST['mid'] . '\', \'' . $time . '\', \'' . mysql_escape_string($_POST['name']) . '\', \'' . mysql_escape_string($_POST['message']) . '\', \'' . $_POST['email'] . '\', \'' . $_POST['website'] . '\')');

            /* Display the comments */
            $_GET['showcomments'] = 1;
            $_GET['id'] = $_POST['mid'];
            fullNews();
        }
    }
}

/* Common actions used when posting/modifying a News Post */
function replace($what, $replace)
{
    global $Settings;

    /* Trim whitespace at Beginning and End of post */
    $what = trim($what);
    $what = shy($what, 50);

    if($replace == 1) {
        $what = str_replace("\r\n", '<br />', $what);
    }

    if ($replace == 2) {
        $what = str_replace('&lt;br /&gt;', "\r\n", $what);
    }


    return $what;
}

/* Inserts the &shy; thingie into certain posts */
function shy($text, $max, $char = "&shy;")
{
    if($max > 0) {
        $words = explode(' ', $text);

        foreach($words as $key => $word) {
            $length = strlen($word);

            if($length > $max) {
                $word = chunk_split($word, floor($length/ceil($length/$max)), $char);
            }

            $words[$key] = $word;
        }

        return implode(' ', $words);
    } else {
        return $text;
    }
}

/* Parses Code */
function parseCode($news)
{
    global $Settings;

    /* Parse the BBCode */
    if($Settings['enablebbcode'] == 1) {
        // Search for this...
        $replacewhat = array(
                             '/\[url\](.+?)\[\/url\]/is',
                             '/\[url=(.+?)\](.+?)\[\/url\]/is',

                             '/\[ftp\](.+?)\[\/ftp\]/is',
                             '/\[ftp=(.+?)\](.+?)\[\/ftp\]/is',

                             '/\[b\](.+?)\[\/b\]/is',
                             '/\[i\](.+?)\[\/i\]/is',
                             '/\[u\](.+?)\[\/u\]/is',
                             '/\[del\](.+?)\[\/del\]/is',

                             '/\[img\](.+?)\[\/img\]/i',
                             '/\[img width=([0-9]+) height=([0-9]+)\s*\](.+?)\[\/img\]/i',
                             '/\[img width=([0-9]+)\s*\](.+?)\[\/img\]/i',
                             '/\[img height=([0-9]+) width=([0-9]+)\s*\](.+?)\[\/img\]/i',
                             '/\[img height=([0-9]+)\s*\](.+?)\[\/img\]/i',

                             '/\[email\](.+?)\[\/email\]/is',
                             '/\[email=(.+?)\](.+?)\[\/email\]/is',
                             '/(\/|=|"mailto:)?([a-z0-9_-][a-z0-9\._-]*@[a-z0-9_-]+(\.[a-z0-9_-]+)+)(\/|<)?/eis',
                             );

        // ...and replace it with this
        $replacewith = array(
                             '<a href="\\1">\\1</a>',
                             '<a href="\\1">\\2</a>',
                             '<a href="\\1">\\1</a>',
                             '<a href="\\1">\\2</a>',

                             '<b>\\1</b>',
                             '<i>\\1</i>',
                             '<u>\\1</u>',
                             '<del>\\1</del>',

                             '<img src="\\1" alt="" />',
                             '<img src="\\3" alt="" width="\\1" height="\\2" />',
                             '<img src="\\2" alt="" width="\\1" />',
                             '<img src="\\3" alt="" width="\\2" height="\\1" />',
                             '<img src="\\2" alt="" height="\\1" />',

                             '<a href="mailto:\\1">\\1</a>',
                             '<a href="mailto:\\1">\\2</a>',
                             "('\\4' == '' && '\\1' == '' ? '<a href=\"mailto:\\2\">\\2</a>' : stripslashes('\\1\\2\\4'))",
                             );

        $news = preg_replace($replacewhat, $replacewith, $news);
    }

    /* Parse the Smilies */
    if($Settings['enablesmilies'] == 1) {
        static $smileyfromcache, $smileytocache;

        /* If the smiley array hasn't been set, do it now */
        if (!is_array($smileyfromcache)) {
            $smiliesfrom = array(':rolleyes:', ':angry:', ':smiley:', ':wink:', ':cheesy:', ':grin:', ':sad:', ':shocked:', ':cool:', ':tongue:', ':huh:', ':embarassed:', ':lipsrsealed:', ':kiss:', ':cry:', ':undecided:', ':laugh:');
            $smiliesto = array('rolleyes', 'angry', 'smiley', 'wink', 'cheesy', 'grin', 'sad', 'shocked', 'cool', 'tongue', 'huh', 'embarassed', 'lipsrsealed', 'kiss', 'cry', 'undecided', 'laugh');

            for ($i = 0; $i < count($smiliesfrom); $i++) {
                $smileyfromcache[] = $smiliesfrom[$i];
                $smileytocache[] = '<img src="' . $Settings['phpnewsurl'] . 'images/smilies/' . $smiliesto[$i] . '.gif" alt="' . $smiliesto[$i] . '" style="border:none;" />';
            }

            /* Now unneeded */
            unset($smiliesfrom);
            unset($smiliesto);
        }

        /* Replace away! */
        $news = str_replace($smileyfromcache, $smileytocache, $news);
    }

    return $news;
}

/* Censors Comments */
function censor($text)
{
    global $Settings;
    static $goodword, $badword;

    /* Checks if good/bad words list has already been done (stored in static variable to increase speed) */
    if (!is_array($goodword)) {
        $badword = array();
        $goodword = array();

        /* Format the censor list */
        $array = explode('|', $Settings['censorlist']);

        /* Put the list of words in Arrays */
        foreach ($array as $i) {
            list($badword[], $goodword[]) = explode('=', $i);
        }
    }

    /* Replace bad words with clean words */
    for($i = 0; $i < count($goodword); $i++) {
        $text = preg_replace('/' . preg_quote($badword[$i], '/') . '/i', $goodword[$i], $text);
    }

    /* Return the censored text */
    return $text;
}

/* Checks Banned IPs */
function checkUserIP($ip)
{
    global $db_prefix;

    /* Search the 'banned' table for occurences of this IP */
    $query = mysql_query('SELECT isbanned FROM ' . $db_prefix . 'banned WHERE ip = \'' . $ip . '\'');
    $request = mysql_fetch_assoc($query);

    /* If the User is banned, return a 1 */
    if ($request['isbanned'] == 1) {
        return 1;
    } else {
        return 0;
    }
}
?>
<!-- (c) 2003, 2005 PHPNews - http://newsphp.sourceforge.net/ -->

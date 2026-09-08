<?php
error_reporting(E_ALL ^ E_NOTICE);
/* Sets up gzipping. Remove this *entire* line to turn it off. */
ob_start('ob_gzhandler');
/*********************************************
* -------------                              *
* | Index.php |                              *
* -------------                              *
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

/* Redirect to users SiteURL */
if ($_GET['action'] == 'redirect') {
    require('settings.php');

    $dbcon = mysql_connect($db_server, $db_user, $db_passwd);
    mysql_select_db($db_name);

    $result = mysql_query('SELECT variable,value FROM ' . $db_prefix . 'settings');

    $Settings = array();
    while ($row = mysql_fetch_array($result)) {
        $Settings[$row[0]] = $row[1];
    }

    header('Location: ' . $Settings['siteurl']);
    exit;
}

$time_start = getMicrotime();
define('PHPNews', 1);

session_start();

require('auth.php');

/* Display link to plain News, if SiteURL hasn't been set */
if($Settings['siteurl'] == '') {
    $link = 'news.php';
} else {
    $link = $Settings['siteurl'];
}

echo '<?xml version="1.0" encoding="' , $language['CHARSET'] , '"?>' , "\n";
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
      <title>
         PHPNews - Admin Center
      </title>
      <link href="phpnews_package.css" rel="stylesheet" type="text/css" />
      <script type="text/javascript">
      <!--
        function help(desktopURL)
        {
            desktop = window.open(desktopURL, "desktop", "toolbar=no,location=no,status=yes,menubar=no,scrollbars=yes,width=400,height=250,resizable=no");
        }

        function insertext(text,area)
        {
            if(area=="title") {
                document.getElementById("titletext").value += text;
            }
            if(area=="main") {
               document.getElementById("maintext").value += text;
            }
        }
      // -->
      </script>
   </head>
   <body>
      <div id="border">
         <div style="background-color:#5F7797; color:#E9F2FC;">
            <h1>
               PHPNews - Admin Center
            </h1>
         </div>
         <div id="navigation">
            <div class="menu">
               <img alt="&gt;" src="bullet.gif" /><strong>
               <?php echo $language['MENU_GENERAL']; ?>:</strong>
               <ul>
                  <li>
                     <a href="javascript:" onclick="window.open('<?php echo $link?>')"><?php echo $language['MENU_CHECK'];?></a>
                     <?php echo $language['MENUITEM_CHECKNEWS'],"\n";?>
                  </li>
<?php
if ($userDetails['access'] == 'admin') {
    ?>
                  <li>
                     <a href="index.php?action=settings"><?php echo $language['MENU_MODIFY'];?></a>
                     <?php echo $language['MENUITEM_MODIFYSETTINGS'],"\n";?>
                  </li>
                  <li>
                     <a href="index.php?action=modtemp"><?php echo $language['MENU_MODIFY'];?></a>
                     <?php echo $language['MENUITEM_MODIFYTEMPLATES'],"\n";?>
                  </li>
<?php
}
?>
               </ul>
            </div>
            <div class="menu">
               <img alt="&gt;" src="bullet.gif" /><strong>
               <?php echo $language['MENU_NEWSARTICLES'];?>:</strong>
               <ul>
                  <li>
                     <a href="index.php?action=post"><?php echo $language['MENU_POST'];?></a>
                     <?php echo $language['MENUITEM_POSTNEWS'],"\n";?>
                  </li>
                  <li>
                     <a href="index.php?action=modify"><?php echo $language['MENU_MODIFY'];?></a>
                     <?php echo $language['MENUITEM_MODIFYNEWS'],"\n";?>
                  </li>
               </ul>
            </div>
<?php
if ($userDetails['access'] == 'admin') {
    ?>
            <div class="menu">
               <img alt="&gt;" src="bullet.gif" /><strong>
               <?php echo $language['MENU_NEWSPOSTERS'];?>:</strong>
               <ul>
                  <li>
                     <a href="index.php?action=newsposter"><?php echo $language['MENU_ADD'];?></a>
                     <?php echo $language['MENUITEM_ADDPOSTER'],"\n";?>
                  </li>
                  <li>
                     <a href="index.php?action=modifynewsposter"><?php echo $language['MENU_MODIFY'];?></a>
                     <?php echo $language['MENUITEM_MODIFYPOSTER'],"\n";?>
                  </li>
               </ul>
            </div>
<?php
}
?>
            <div class="menu">
               <img alt="&gt;" src="bullet.gif" /><strong>
               <?php echo $language['MENU_MODIFYPROFILE'];?>:</strong>
               <ul>
                  <li>
                     <a href="index.php?action=modifynewsposter2&amp;id=<?php echo $userDetails['id']?>">
                     <?php echo $language['MENU_MODIFY'];?></a> <?php echo $language['MENUITEM_MODIFYDETAILS'],"\n";?>
                  </li>
               </ul>
            </div>
            <div class="menu">
               <img alt="&gt;" src="bullet.gif" /><strong>
               <?php echo $language['MENU_MISCELLANEOUS'];?>:</strong>
               <ul>
<?php
if ($userDetails['access'] == 'admin') {
    ?>
                  <li>
                     <a href="index.php?action=advanced"><?php echo $language['MENU_MODIFY'];?></a>
                     <?php echo $language['MENUITEM_ADVSETTINGS'],"\n";?>
                  </li>
<?php
}
?>
                  <li>
                     <a href="index.php?action=logout"><?php echo $language['MENU_LOGOUT'];?></a>
                     <?php echo $language['MENUITEM_LOGOUT'],"\n";?>
                  </li>
               </ul>
            </div>
         </div>
         <div id="content">
<?php
        include_once('admin.php');

/* Place the function names in an Array */
$Array = array(
        'modtemp',
        'modifytemp',
        'modifycomtemp',
        'modifystf',
        'modifyarchive',
        'modifysearch',
        'modifyheadlines',
        'modifytemp2',
        'censorlist',
        'modcensorlist',
        'settings',
        'modsettings',
        'cats',
        'addcat',
        'modifycats',
        'post',
        'post2',
        'newsposter',
        'newsposter2',
        'modify',
        'modifypost',
        'modifypending',
        'modifypost2',
        'modifypost3',
        'modifycomment',
        'updatecomments',
        'banning',
        'addbannedip',
        'modbanned',
        'modifynewsposter',
        'modifynewsposter2',
        'modifynewsposter3',
        'checkVersion',
        'advanced',
        'createRSSFeed',
        'images',
        'uploadimages',
        'imagesdelete',
        'logout');

/* If action doesn't exist, do the main() function */
if (!in_array($_GET['action'], $Array, true)) {
    main();
} else {
    $_GET['action']();
}

/* Used to get the Script Execution time */
function getMicrotime()
{
    list($usec, $sec) = explode(' ', microtime());
    return ((float)$usec + (float)$sec);
}
?>
         </div>
      </div>
      <p class="copyright" style="clear:left; padding-top:20px;">Copyright &copy; 2003 - 2005
          <a href="http://newsphp.sourceforge.net">PHPNews</a> - 1.3.0<br />
          <?php echo $time; ?> [ <?php echo $dbQueries; ?> queries used ]
      </p>
    </body>
</html>

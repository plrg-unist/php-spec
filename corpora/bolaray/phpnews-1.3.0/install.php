<?php
error_reporting(E_ALL ^ E_NOTICE);
/*********************************************
* -------------                              *
* |install.php|                              *
* -------------                              *
* PHPNews - 1.3.0 Release                    *
* Open Source Project started by Pierce Ward *
*                                            *
* Software Distributed at:                   *
* http://newsphp.sourceforge.net             *
* ========================================== *
* (c) 2003, 2004 Pierce Ward (Big P)         *
* All rights reserved.                       *
* ========================================== *
* This program has been written under the    *
* terms of the GNU General Public Licence as *
* published by the Free Software Foundation. *
*                                            *
* The GNU GPL can be found in gpl.txt        *
*********************************************/

/* Sets up gzipping. Remove this *entire* line to turn it off. */
ob_start('ob_gzhandler');

// Json ->
if (stristr($_SERVER['HTTP_USER_AGENT'], 'MSIE')) {
    $iebuttonfix = 'style="border: 1px solid #354463; background-color: #5F7797; color: #FFFFFF; font-size: 11px; padding-bottom: 1px; padding-top: 1px; width: 90px;"';
}

$lang = $_REQUEST['language'];
if($lang == '') {
    $lang = $Settings['language'];
}

if(!file_exists('languages/' . $lang . '.admin.lng')) {
    include_once('languages/en_GB.admin.lng');
} else {
    include_once('languages/' . $lang . '.admin.lng');
}
$language = $lng;

/* Displays error, and kills program */
function fatal_error($error)
{
    global $language, $step;
    ?>
         <table class="installer" cellspacing="0" cellpadding="0">
            <tr>
               <th>
                  PHPNews - <?php echo $language['CONTENT_INSTALLER'];?> -
                  <?php echo $language['CONTENT_INSTALLER_STEP']?> <?php echo $step,"\n"?>
               </th>
            </tr>
            <tr>
               <td class="left">
                   <?php echo $language[$error];?><br />
               </td>
            </tr>
         </table>
      </form>
      <p class="copyright">Copyright &copy; 2003, 2005 <a href="http://newsphp.sourceforge.net/">PHPNews</a></p>
   </body>
</html>
<?php
      exit();
}

// <- Json

$step = $_REQUEST['step'];
if($step == '') {
    $step = 1;
}
echo '<?xml version="1.0" encoding="'.$language['CHARSET'].'"?>' , "\n";
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
      <title>
         PHPNews - <?php echo $language['CONTENT_INSTALLER']?> - <?php echo $language['CONTENT_INSTALLER_STEP']?> <?php echo $step,"\n";?>
      </title>
      <link href="phpnews_package.css" rel="stylesheet" type="text/css" />
   </head>
   <body>
      <form action="install.php" method="post">
<?php
    // =======================================================
    // STEP 1
    // =======================================================
    if($step == 1) {
        ?>
         <table class="installer" cellspacing="0" cellpadding="0">
            <tr>
               <th colspan="2">
                  PHPNews - <?php echo $language['CONTENT_INSTALLER']?> - <?php echo $language['CONTENT_INSTALLER_STEP']?> <?php echo $step,"\n";?>
                  <input type="hidden" name="step" value="2" />
               </th>
            </tr>
            <tr>
               <td class="left" colspan="2">
                  <label for="language"><?php echo $language['CONTENT_INSTALLER_LANGUAGEINFO']?></label>
               </td>
            </tr>
            <tr>
               <td colspan="2" align="center">
                  <select id="language" name="language">
<?php
              /* Look for all .lng files and make em selectable in the settings screen */
              $dir = opendir('languages/');

        $i = 0;
        while (false !== ($file = readdir($dir))) {
            if(substr($file, strlen($file) - 10, 10) == '.admin.lng') {
                include('languages/' . $file);

                if($Settings['language'] == substr($file, 0, strlen($file) - 10)) {
                    ?>
                     <option value="<?php echo substr($file, 0, strlen($file) - 10);?>" selected="selected">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
                } else {
                    ?>
                     <option value="<?php echo substr($file, 0, strlen($file) - 10);?>">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
                }
            }
        }

        closedir($dir);
        ?>
                  </select>
               </td>
            </tr>
            <tr>
               <td class="center" colspan="2">
                  <input type="submit" name="submit" value="<?php echo $language['CONTENT_BUTTONNEXT']?>" <?php echo $iebuttonfix?> />
               </td>
            </tr>
         </table>
      </form>
<?php
    }
    // =======================================================
    // STEP 2
    // =======================================================
    elseif ($step == 2) {
        global $language;

        $requirement = array('PHP_VERSION' => array(),
                             'EXT_XML' => array(),
                 'EXT_EXIF' => array(),
                             'EXT_SESSION' => array());

        // Checks if PHP version is above or equal 4.1.0
        if (intval(str_replace('.', '', phpversion())) >= 410) {
            $requirement['PHP_VERSION']['status'] = true;
            $requirement['PHP_VERSION']['image'] =
            '<img alt="PHP Version is okay" src="right.png" />';
        } elseif (intval(str_replace('.', '', phpversion())) < 410) {
            $requirement['PHP_VERSION']['status'] = false;
            $requirement['PHP_VERSION']['image'] =
            '<img alt="PHP Version is not okay" src="wrong.png" />';
        }
        $requirement['PHP_VERSION']['text'] = phpversion();

        // Checks wether the Sablot XML extension is loaded
        if (extension_loaded('xml')) {
            $requirement['EXT_XML']['status'] = true;
            $requirement['EXT_XML']['text'] = $language['CONTENT_INSTALLER_ACTIVE'];
            $requirement['EXT_XML']['image'] =
            '<img alt="XML Support enabled" src="right.png" />';
        } else {
            $requirement['EXT_XML']['status'] = false;
            $requirement['EXT_XML']['text'] = $language['CONTENT_INSTALLER_INACTIVE'];
            $requirement['EXT_XML']['image'] =
            '<img alt="XML Support disabled" src="wrong.png" />';
        }

        // Checks wether the Sablot XML extension is loaded
        if (extension_loaded('exif')) {
            $requirement['EXT_EXIF']['status'] = true;
            $requirement['EXT_EXIF']['text'] = $language['CONTENT_INSTALLER_ACTIVE'];
            $requirement['EXT_EXIF']['image'] =
            '<img alt="EXIF Support enabled" src="right.png" />';
        } else {
            $requirement['EXT_EXIF']['status'] = false;
            $requirement['EXT_EXIF']['text'] = $language['CONTENT_INSTALLER_INACTIVE'];
            $requirement['EXT_EXIF']['image'] =
            '<img alt="EXIF Support disabled" src="wrong.png" />';
        }

        // Checks wether Session support is loaded
        if (extension_loaded('session')) {
            $requirement['EXT_SESSION']['status'] = true;
            $requirement['EXT_SESSION']['text'] = $language['CONTENT_INSTALLER_ACTIVE'];
            $requirement['EXT_SESSION']['image'] =
            '<img alt="Session Support enabled" src="right.png" />';
        } else {
            $requirement['EXT_SESSION']['status'] = false;
            $requirement['EXT_SESSION']['text'] = $language['CONTENT_INSTALLER_INACTIVE'];
            $requirement['EXT_SESSION']['image'] =
            '<img alt="Session Support disabled" src="wrong.png" />';
        }
        ?>
         <table class="installer" cellspacing="0" cellpadding="0">
            <tr>
               <th colspan="4">
                  PHPNews - <?php echo $language['CONTENT_INSTALLER']?> - <?php echo $language['CONTENT_INSTALLER_STEP']?> <?php echo $step,"\n"?>
                  <input type="hidden" name="step" value="3" />
                  <input type="hidden" name="language" value="<?php echo $lang?>" />
                  <input type="hidden" name="EXT_XML" value="<?php echo $requirement['EXT_XML']['status'];?>" />
                  <input type="hidden" name="EXT_SESSION" value="<?php echo $requirement['EXT_XML']['status'];?>" />
               </th>
            </tr>
            <tr>
               <td>

               </td>
               <td>
                  <?php echo $language['CONTENT_INSTALLER_REQUIRED'],"\n";?>
               </td>
               <td>
                  <?php echo $language['CONTENT_INSTALLER_FOUND'],"\n";?>
               </td>
               <td>
               </td>
            </tr>
            <tr>
               <td class="right">
                  <?php echo $language['CONTENT_INSTALLER_PHP'],"\n";?>
               </td>
               <td>
                  4.1.0
               </td>
               <td>
                  <?php echo $requirement['PHP_VERSION']['text'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['PHP_VERSION']['image'],"\n";?>
               </td>
            </tr>
<?php
            if ($requirement['PHP_VERSION']['status'] == false) :
                ?>
            <tr class="notify">
               <td colspan="4" class="left">
                  <?php echo $language['CONTENT_INSTALLER_PHP_EXP'],"\n";?>
               </td>
            </tr>
<?php
            endif;
        ?>
            <tr>
               <td class="right">
                  <?php echo $language['CONTENT_INSTALLER_XML'],"\n";?>
               </td>
               <td>
                  <?php echo $language['CONTENT_INSTALLER_ACTIVE'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['EXT_XML']['text'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['EXT_XML']['image'],"\n";?>
               </td>
            </tr>
<?php
            if ($requirement['EXT_XML']['status'] == false) :
                ?>
            <tr class="notify">
               <td colspan="4" class="left">
                  <?php echo $language['CONTENT_INSTALLER_XML_EXP'],"\n";?>
               </td>
            </tr>
<?php
            endif;
        ?>


            <tr>
               <td class="right">
                  <?php echo $language['CONTENT_INSTALLER_EXIF'],"\n";?>
               </td>
               <td>
                  <?php echo $language['CONTENT_INSTALLER_ACTIVE'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['EXT_EXIF']['text'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['EXT_EXIF']['image'],"\n";?>
               </td>
            </tr>
<?php
            if ($requirement['EXT_EXIF']['status'] == false) :
                ?>
            <tr class="notify">
               <td colspan="4" class="left">
                  <?php echo $language['CONTENT_INSTALLER_EXIF_EXP'],"\n";?>
               </td>
            </tr>
<?php
            endif;
        ?>


            <tr>
               <td class="right">
                  <?php echo $language['CONTENT_INSTALLER_SESSION'],"\n";?>
               </td>
               <td>
                  <?php echo $language['CONTENT_INSTALLER_ACTIVE'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['EXT_SESSION']['text'],"\n";?>
               </td>
               <td>
                  <?php echo $requirement['EXT_SESSION']['image'],"\n";?>
               </td>
            </tr>
<?php
            if ($requirement['EXT_SESSION']['status'] == false) :
                ?>
            <tr class="notify">
               <td colspan="4" class="left">
                  <?php echo $language['CONTENT_INSTALLER_SESSION_EXP'];?>
               </td>
            </tr>
<?php
            endif;
        if ($requirement['PHP_VERSION']['status'] == true && $requirement['EXT_SESSION']['status'] == true) {
            ?>
            <tr>
               <td class="center" colspan="4">
                  <input type="submit" name="submit" value="<?php echo $language['CONTENT_BUTTONNEXT']?>" <?php echo $iebuttonfix?> />
               </td>
            </tr>
<?php
        }
        ?>
         </table>
      </form>
<?php
    }
    // =======================================================
    // STEP 3
    // =======================================================
    elseif($step == 3) {
        // Grab Directory Name
        $host = getenv('HTTP_HOST');
        $address = $host . $_SERVER['PHP_SELF'];
        $address = str_replace('install.php', '', $address);
        ?>
         <table class="installer" cellspacing="0" cellpadding="0">
            <tr>
               <th colspan="2">
                  PHPNews - <?php echo $language['CONTENT_INSTALLER']?> - <?php echo $language['CONTENT_INSTALLER_STEP']?> <?php echo $step,"\n"?>
                  <input type="hidden" name="step" value="4" />
                  <input type="hidden" name="language" value="<?php echo $lang?>" />
                  <input type="hidden" name="EXT_XML" value="<?php echo $_POST['EXT_XML'];?>" />
                  <input type="hidden" name="EXT_SESSION" value="<?php echo $_POST['EXT_XML'];?>" />
               </th>
            </tr>
            <tr>
               <td class="left" colspan="2">
                  <?php echo $language['CONTENT_INSTALLER_OPTFIELDS'],"\n";?>
                  <hr />
               </td>
            </tr>
            <tr>
               <td class="left" colspan="2">
                  <?php echo $language['CONTENT_INSTALLER_DATABASEINFO'],"\n";?>
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="dbname"><?php echo $language['CONTENT_INSTALLER_DATABASENAME']?></label>
               </td>
               <td>
                  <input type="text" id="dbname" name="dbname" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="dbuser"><?php echo $language['CONTENT_INSTALLER_DATABASEUSER']?></label>
               </td>
               <td>
                  <input type="text" id="dbuser" name="dbuser" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="dbpassword"><?php echo $language['CONTENT_INSTALLER_DATABASEPASS']?></label>
               </td>
               <td>
                  <input type="text" id="dbpassword" name="dbpassword" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="dbserver"><?php echo $language['CONTENT_INSTALLER_DATABASESERVER']?></label>
               </td>
               <td>
                  <input type="text" id="dbserver" name="dbserver" value="localhost" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="dbprefix"><?php echo $language['CONTENT_INSTALLER_DATABASEPREFIX']?></label>
               </td>
               <td>
                  <input type="text" id="dbprefix" name="dbprefix" value="phpnews_" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="createdb"><?php echo $language['CONTENT_INSTALLER_CREATEDATABASE']?>?</label>
               </td>
               <td>
                  <input type="checkbox" id="createdb" name="createdb" value="1" />
               </td>
            </tr>
            <tr>
               <td class="left" colspan="2">
                  <hr />
                  <?php echo $language['CONTENT_INSTALLER_SETTINGSINFO'],"\n";?>
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="sitename"><?php echo $language['CONTENT_SETTINGSSITENAME'],"\n"?>
                  <span style="color:red;">*</span></label>
               </td>
               <td>
                  <input type="text" id="sitename" name="sitename" value="My Site" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="phpnewsurl"><?php echo $language['CONTENT_SETTINGSPHPNEWSURL'],"\n"?>
                  <span style="color:red;">*</span></label>
               </td>
               <td>
                  <input type="text" id="phpnewsurl" name="phpnewsurl" value="http://<?php echo $address?>" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="siteurl"><?php echo $language['CONTENT_SETTINGSNEWSURL'],"\n"?>
                  <span style="color:red;">*</span></label>
               </td>
               <td>
                  <input type="text" id="siteurl" name="siteurl" value="http://<?php echo $host?>" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="lang"><?php echo $language['CONTENT_SETTINGSLANGUAGE']?></label>
               </td>
               <td>
                  <select id="lang" name="lang">
<?php
            /* Look for all .lng files and make em selectable in the settings screen */
            $dir = opendir('languages/');

        $i = 0;
        while (false !== ($file = readdir($dir))) {
            if(substr($file, strlen($file) - 10, 10) == '.admin.lng') {
                include('languages/' . $file);

                if($_POST['language'] == substr($file, 0, strlen($file) - 10)) {
                    ?>
                     <option value="<?php echo substr($file, 0, strlen($file) - 10);?>" selected="selected">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
                } else {
                    ?>
                     <option value="<?php echo substr($file, 0, strlen($file) - 10);?>">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
                }
            }
        }

        closedir($dir);
        ?>
                  </select>
               </td>
            </tr>
            <tr>
               <td class="left" colspan="2">
                  <hr />
                  <?php echo $language['CONTENT_CHOOSE_LOGIN'],"\n";?>
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="user"><?php echo $language['CONTENT_POSTERUSERNAME']?></label>
               </td>
               <td>
                  <input type="text" id="user" name="user" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="pass"><?php echo $language['CONTENT_POSTERPASSWORD']?></label>
               </td>
               <td>
                  <input type="password" id="pass" name="pass" />
               </td>
            </tr>
            <tr>
               <td class="left">
                  <label for="pass2"><?php echo $language['CONTENT_POSTERCONFIRMPASSWORD'];?></label>
               </td>
               <td>
                  <input type="password" id="pass2" name="pass2" />
               </td>
            </tr>
            <tr>
               <td class="center" colspan="2">
                  <input type="submit" name="submit" value="<?php echo $language['CONTENT_BUTTONNEXT']?>" <?php echo $iebuttonfix?> />
               </td>
            </tr>
         </table>
      </form>
      <table class="installer" cellspacing="0" cellpadding="0">
         <tr>
            <th colspan="2">
               PHPNews - <?php echo $language['CONTENT_INSTALLER']?> - Settings.php
            </th>
         </tr>
         <tr>
            <td class="left" colspan="2">
              <?php echo $language['CONTENT_INSTALLER_INFO'],"\n";?>
              <?php echo $language['CONTENT_INSTALLER_NEXTSTEP']?><br />
            </td>
         </tr>
      </table>
<?php
    }
    // =======================================================
    // STEP 4
    // =======================================================
    elseif($step == 4) {
        /* Database settings */
        $dbname = $_REQUEST['dbname'];
        $dbuser = $_REQUEST['dbuser'];
        $dbpass = $_REQUEST['dbpassword'];
        $dbhost = $_REQUEST['dbserver'];
        $dbprefix = $_REQUEST['dbprefix'];
        $createdb = $_REQUEST['createdb'];

        /* Basic PHPNews Settings */
        $sitename = $_REQUEST['sitename'];
        $phpnewsurl = $_REQUEST['phpnewsurl'];
        $siteurl = $_REQUEST['siteurl'];
        $lang = $_REQUEST['lang'];

        /* Log in Details */
        $user = $_REQUEST['user'];
        $pass = $_REQUEST['pass'];
        $pass2 = $_REQUEST['pass2'];

        if($dbname != '' && $dbuser != '' && $dbhost != '' && $dbprefix != '' && $user != '' && ($pass == $pass2)) {
            // Set it all up
            $dbconnection = 'done';
            $dbcreate = 'skipped';
            $banned = '10%';
            $comments = '20%';
            $news = '30%';
            $posters = '40%';
            $categories = '50%';
            $settings = '60%';
            $settingsdata = '70%';
            $postersdata = '95%';
            $filesettings = '100%';

            $connection = @mysql_connect($dbhost, $dbuser, $dbpass);

            if($connection) {
                /* Save Settings Data */
                $settingsfile .= '<?php' . "\n";
                $settingsfile .= '$db_name = "' . $dbname . '";' . "\n";
                $settingsfile .= '$db_user = "' . $dbuser . '";' . "\n";
                $settingsfile .= '$db_passwd = "' . $dbpass . '";' . "\n";
                $settingsfile .= '$db_server = "' . $dbhost . '";' . "\n";
                $settingsfile .= '$db_prefix = "' . $dbprefix . '";' . "\n";
                $settingsfile .= '?>' . "\n";

                /* Create the file settings.php and it's contents */
                @touch('settings.php');
                $file = @fopen('settings.php', 'wt');
                if($file) {
                    fwrite($file, $settingsfile);
                    fclose($file);
                } else {
                    // Exit program is settings file cannot be created
                    fatal_error(CONTENT_INSTALLER_MANUALEDIT);
                }

                /* Does the user want to create a database? */
                if($dbname != '' && $createdb == 1) {
                    /* Get list of all databases */
                    $db_list = mysql_list_dbs();

                    while ($row = mysql_fetch_array($db_list)) {
                        if ($row['Database'] == strtolower($dbname)) {
                            fatal_error('CONTENT_INSTALLER_ERRORCREATEDB');
                        }
                    }
                    /* Create new database */
                    mysql_query('CREATE DATABASE '.$dbname.'');

                    $dbcreate = 'done';
                }

                mysql_select_db($dbname);
                mysql_query('CREATE TABLE '. $dbprefix  .'banned (id int(4) unsigned NOT NULL auto_increment, ip varchar(80) NOT NULL, timesbanned tinyint(3) NOT NULL default \'0\', isbanned tinyint(1) NOT NULL default \'0\', PRIMARY KEY (id)) TYPE=MyISAM');
                mysql_query('CREATE TABLE '. $dbprefix  .'comments (id int(11) unsigned NOT NULL auto_increment, ip varchar(80) NOT NULL, mid int(11) NOT NULL, time bigint(20) NOT NULL, name varchar(40) NOT NULL, message text NOT NULL, email varchar(50), website tinytext, PRIMARY KEY (id)) TYPE=MyISAM') or $comments = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('CREATE TABLE '. $dbprefix  .'news (id int(11) unsigned NOT NULL auto_increment, posterid int(5) NOT NULL, postername varchar(40) NOT NULL, time bigint(20) NOT NULL, month TINYINT(2) UNSIGNED DEFAULT \'0\' NOT NULL, year smallint(4) UNSIGNED DEFAULT \'0\' NOT NULL, subject tinytext NOT NULL, titletext text NOT NULL, maintext text, views int DEFAULT \'0\', break tinyint(1), catid int(3) NOT NULL default \'0\', trusted TINYINT(1) DEFAULT \'1\', PRIMARY KEY (id)) TYPE=MyISAM') or $news = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('CREATE TABLE '. $dbprefix  .'categories (id int(3) unsigned NOT NULL auto_increment, catname varchar(40) NOT NULL, caticon tinytext NOT NULL, PRIMARY KEY (id)) TYPE=MyISAM');
                mysql_query('CREATE TABLE '. $dbprefix  .'posters (id int(5) unsigned NOT NULL auto_increment, username varchar(40) NOT NULL default \'\', password varchar(50) NOT NULL, email varchar(50), avatar tinytext, language VARCHAR(10), access varchar(20) NOT NULL, PRIMARY KEY (id)) TYPE=MyISAM') or $posters = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('CREATE TABLE '. $dbprefix  .'settings (variable char(20) NOT NULL, value text NOT NULL) TYPE=MyISAM') or $settings = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'sitename\', \''. $sitename .'\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'phpnewsurl\', \''. $phpnewsurl .'\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'siteurl\', \''. $siteurl .'\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'language\', \''. $lang .'\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'numtoshow\', \'8\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'numtoshowhead\', \'8\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablestf\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablesmilies\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enableavatars\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix . 'settings VALUES (\'enablevalidation\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablecensor\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enableprevnext\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablecomments\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'showcominnews\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'showoldcomfirst\',\'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablecats\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'numtoshowcat\', \'8\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'floodprotection\',\'15\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'timeoffset\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'timeformat\', \'%B %d, %Y, %I:%M:%S %p\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'shorttimeformat\', \'%d %B, %Y\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'censorlist\', \'\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablebbcode\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablerss\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'manualrss\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablecommentpages\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'commentsperpage\', \'15\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'settings VALUES (\'enablecountviews\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix . 'settings VALUES (\'enableimgupload\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix . 'settings VALUES (\'uploadfiles\', \'5\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix . 'settings VALUES (\'imguploadpath\', \'images/\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                mysql_query('INSERT INTO '. $dbprefix  .'posters VALUES (\'1\', \''. $user .'\', password(\''. $pass .'\'), \'\', \'\', \'\', \'admin\')') or $postersdata = $language['CONTENT_INSTALLER_ERROREXISTS'];

                if ($_POST['EXT_XML'] == 1) {
                    mysql_query('INSERT INTO '. $dbprefix . 'settings VALUES (\'enablecheckversion\', \'1\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                } else {
                    mysql_query('INSERT INTO '. $dbprefix . 'settings VALUES (\'enablecheckversion\', \'0\')') or $settingsdata = $language['CONTENT_INSTALLER_ERROREXISTS'];
                }

                mysql_close($connection);
            } else {
                fatal_error('CONTENT_INSTALLER_ERRORCONNECT');
            }

            // DONE!
            ?>
         <table class="installer" cellspacing="0" cellpadding="0">
            <tr>
               <th colspan="2">
                  <?php echo $language['CONTENT_INSTALLER']?> - <?php echo $language['CONTENT_INSTALLER_STEP']?> <?php echo $step,"\n"?>
                  <input type="hidden" name="step" value="5" />
                  <input type="hidden" name="language" value="<?php echo $lang;?>" />
               </th>
            </tr>
            <tr>
               <td class="left" colspan="2">
                    <?php echo $language['CONTENT_INSTALLER_DATABASECONNECT']?>: <b><?php echo $dbhost;?></b> - <?php echo $dbconnection;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATEDATABASE']?>: <b><?php echo $dbname;?></b> - <?php echo $dbcreate;?><br />
                 <?php
                             if($connection) {
                                 ?>
                    <?php echo $language['CONTENT_INSTALLER_CREATINGTABLE']?>: <b><?php echo $dbprefix;?>banned</b> - <?php echo $banned;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATINGTABLE']?>: <b><?php echo $dbprefix;?>comments</b> - <?php echo $comments;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATINGTABLE']?>: <b><?php echo $dbprefix;?>news</b> - <?php echo $news;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATINGTABLE']?>: <b><?php echo $dbprefix;?>posters</b> - <?php echo $posters;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATINGTABLE']?>: <b><?php echo $dbprefix;?>categories</b> - <?php echo $categories;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATINGTABLE']?>: <b><?php echo $dbprefix;?>settings</b> - <?php echo $settings;?><br />
                    <?php echo $language['CONTENT_INSTALLER_FILLINGTABLE']?>: <b><?php echo $dbprefix;?>settings</b> - <?php echo $settingsdata;?><br />
                    <?php echo $language['CONTENT_INSTALLER_FILLINGTABLE']?>: <b><?php echo $dbprefix;?>posters</b> - <?php echo $postersdata;?><br />
                    <?php echo $language['CONTENT_INSTALLER_CREATINGFILE']?>: <b>settings.php</b> - <?php echo $filesettings;?><br /><br />
                    <?php echo $language['CONTENT_INSTALLER_COMPLETE']?><br />
                 <?php
                             } else {
                                 ?>
                    <?php echo $language['CONTENT_INSTALLER_ABORTED']?><br />
                 <?php
                             }
            ?>
               </td>
            </tr>
         </table>
      </form>
// <?php
       /* If a problem occured with the installer writing to settings.php */
        if((!$file) && ($connection)) {
            ?>
      <table class="installer" cellspacing="0" cellpadding="0">
         <tr>
            <th colspan="2">
               PHPNews - <?php echo $language['CONTENT_INSTALLER']?> - Settings.php
            </th>
         </tr>
         <tr>
            <td class="left" colspan="2">
              <?php echo $language['CONTENT_INSTALLER_MANUALEDIT'],"\n";?>
              <?php echo $language['CONTENT_INSTALLER_NEXTSTEP']?><br />
            </td>
         </tr>
      </table>
<?php
        }
        } else {
            fatal_error('CONTENT_INSTALLER_ERRORFIELDS');
        }
    }
?>
      <p class="copyright">Copyright &copy; 2003, 2005 <a href="http://newsphp.sourceforge.net/">PHPNews</a></p>
   </body>
</html>
<?php
ob_end_flush();
?>

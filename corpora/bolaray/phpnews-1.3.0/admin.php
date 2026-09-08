<?php
/*********************************************
* -------------                              *
* | Admin.php |                              *
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

if (!defined('PHPNews')) {
    fatal_error($language['CONTENT_ERRORDEFINED']);
}

function is_admin()
{
    global $userDetails, $language;

    /* If the user isn't an Administrator, give an error message */
    if($userDetails['access'] != 'admin') {
        fatal_error($language['CONTENT_ERRORACCESSDENIED']);
    }
}

function main()
{
    global $userDetails, $language;
    ?>
            <p>
               <?php echo $language['CONTENT_LOGGEDIN'] , ', ' , $userDetails['username'];?>.
            </p>
<?php
      checkForIE();
}

/*********************
* Template Functions *
*********************/

function modtemp()
{
    is_admin();
    global $language;

    /* Displays links to modify Templates */
    ?>
            <p>
               <?php echo $language['CONTENT_TEMPLATESINFO'];?>:
            </p>
            <h2>
               <?php echo $language['CONTENT_TEMPLATESNEWSHEAD'],"\n";?>
            </h2>
            <p>
               <a href="index.php?action=modifytemp&amp;temp=news">
               <?php echo $language['CONTENT_HELPNEWSTEMPLATE'];?></a><br />
               <a href="index.php?action=modifytemp&amp;temp=fullnews">
               <?php echo $language['CONTENT_TEMPLATESFULLNEWS'];?></a>
            </p>
            <h2>
               <?php echo $language['CONTENT_TEMPLATESCOMSTFHEAD'],"\n";?>
            </h2>
            <p>
               <a href="index.php?action=modifycomtemp">
               <?php echo $language['CONTENT_TEMPLATESCOMMENTS'];?></a><br />
               <a href="index.php?action=modifystf">
               <?php echo $language['CONTENT_TEMPLATESSENDTOFRIEND'];?></a>
            </p>
            <h2>
               <?php echo $language['CONTENT_TEMPLATESARCHEAD'],"\n";?>
            </h2>
            <p>
               <a href="index.php?action=modifyarchive">
               <?php echo $language['CONTENT_TEMPLATESARCHIVES'];?></a>
            </p>
            <h2>
               <?php echo $language['CONTENT_TEMPLATESMISCHEAD'],"\n";?>
            </h2>
            <p>
               <a href="index.php?action=modifyheadlines">
               <?php echo $language['CONTENT_TEMPLATESHEAD'];?></a><br />
               <a href="index.php?action=modifyprevnext">
               <?php echo $language['CONTENT_TEMPLATESPREVNEXT'];?></a>
            </p>
            <div style="height:10px;">
               &nbsp;
            </div>
<?php
}

function modifytemp()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    /* If no template is selected, there's a problem */
    if (!$_GET['temp']) {
        fatal_error($language['CONTENT_ERRORREQUIREDVARIABLE']);
    }

    if ($_GET['temp'] == 'news') {
        $templateFile = 'news_temp.php';
    } elseif ($_GET['temp'] == 'fullnews') {
        $templateFile = 'fullnews_temp.php';
    }

    /* Format the template for editing */
    $fulltemplate = formatTemplate($templateFile);
    ?>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESMODIFYTEMPLATE'];?>
                (<?php echo $templateFile?>):
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESMODIFYINFO'];?>
                <a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=temphelp')">
                <?php echo $language['CONTENT_TEMPLATESCLICKHERE'];?></a>
                <?php echo $language['CONTENT_TEMPLATESFULLLIST'];?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="<?php echo $templateFile?>" />
                   <textarea cols="1" name="template" rows="15" style="width:98%"><?php echo $fulltemplate?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
<?php
}

function modifycomtemp()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    /* Format the templates for editing */
    $commentstemp = formatTemplate('comments_temp.php');
    $commenttemp = formatTemplate('comment_temp.php');
    ?>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESCOMMENTMODIFY'];?>
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESCOMMENTINFO'],"\n";?>
             </p>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESCOMMENTS'];?>:
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESCOMMENTSINFO'],"\n";?>
                <a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=comtemphelp')"><?php echo $language['CONTENT_TEMPLATESCLICKHERE'];?></a>.
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input type="hidden" name="templateFile" value="comments_temp.php" />
                   <textarea cols="1" name="template" rows="15"
                   style="width:98%"><?php echo $commentstemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
             <hr />
             <h2>
                <?php echo $language['CONTENT_TEMPLATESADDCOMMENT'];?>:
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESADDCOMMENTINFO'],"\n";?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input type="hidden" name="templateFile" value="comment_temp.php" />
                   <textarea cols="1" name="template" rows="15"
                   style="width:98%"><?php echo $commenttemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
<?php

}

function modifystf()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    /* Format the template for editing */
    $sendtemp = formatTemplate('sendtofriend_temp.php');
    $senttemp = formatTemplate('sent_temp.php');
    ?>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESSTFMODIFY'];?>:
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESSTFINFO'],"\n";?>
             </p>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESSTFFORM'];?>:
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESSTFFORMINFO'];?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="sendtofriend_temp.php" />
                   <textarea cols="1" name="template" rows="15"
                   style="width:98%"><?php echo $sendtemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
             <hr />
             <h2>
                <?php echo $language['CONTENT_TEMPLATESSTFTHANKYOU'];?>:
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESSTFTHANKYOUINFO'];?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="sent_temp.php" />
                   <textarea cols="1" name="template" rows="15"
                   style="width:98%"><?php echo $senttemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
<?php

}

function modifyarchive()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    /* Format the templates for editing */
    $datetemp = formatTemplate('date_temp.php');
    $cattemp = formatTemplate('cat_temp.php');
    $catdatetemp = formatTemplate('catdate_temp.php');
    $newslinktemp = formatTemplate('link_temp.php');
    ?>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESARCTOP'];?>:
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESARCINFO'];?>:
             </p>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESARCLIST'],"\n";?>
             </p>
             <h2>
                date_temp.php
             </h2>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="date_temp.php" />
                   <textarea cols="1" name="template" rows="4" style="width:98%"><?php echo $datetemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
             <hr>
             <h2>
                cat_temp.php
             </h2>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="cat_temp.php" />
                   <textarea cols="1" name="template" rows="4"
                   style="width:98%"><?php echo $cattemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
             <hr>
             <h2>
                catdate_temp.php
             </h2>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="catdate_temp.php" />
                   <textarea cols="1" name="template" rows="4"
                   style="width:98%"><?php echo $catdatetemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
             <hr>
             <h2>
                link_temp.php
             </h2>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input name="templateFile" type="hidden" value="link_temp.php" />
                   <textarea cols="1" name="template" rows="4"
                   style="width:98%"><?php echo $newslinktemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
<?php
}

function modifyheadlines()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    $headtemp = formatTemplate('headlines_temp.php');
    ?>
             <h2>
                <?php echo $language['CONTENT_TEMPLATESMODIFYTEMPLATE']?> (headlines_temp.php):
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESHEADINFO'],"\n";?>
                <a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=headlineshelp')">
                <?php echo $language['CONTENT_TEMPLATESCLICKHERE'];?></a> <?php echo $language['CONTENT_TEMPLATESFULLLIST'],"\n";?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input type="hidden" name="templateFile" value="headlines_temp.php" />
                   <textarea cols="1" name="template" rows="12"
                   style="width:98%"><?php echo $headtemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
<?php

}

function modifyprevnext()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    $prevnexttemp = formatTemplate('prevnext_temp.php');
    $prevnextcattemp = formatTemplate('prevnextcat_temp.php');
    ?>
             <h2>
               <?php echo $language['CONTENT_TEMPLATESMODIFYTEMPLATE']?> (prevnext_temp.php):
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESPREVNEXTINFO'],"\n";?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input type="hidden" name="templateFile" value="prevnext_temp.php" />
                   <textarea cols="1" name="template" rows="12"
                   style="width:98%"><?php echo $prevnexttemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
             <hr />
             <h2>
                <?php echo $language['CONTENT_TEMPLATESMODIFYTEMPLATE']?> (prevnextcat_temp.php):
             </h2>
             <p class="subtext">
                <?php echo $language['CONTENT_TEMPLATESPREVNEXTCATINFO'],"\n";?>
             </p>
             <form action="index.php?action=modifytemp2" method="post">
                <p>
                   <input type="hidden" name="templateFile" value="prevnextcat_temp.php" />
                   <textarea cols="1" name="template" rows="12"
                   style="width:98%"><?php echo $prevnextcattemp?></textarea>
                </p>
                <p class="center">
                   <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE'];?>" <?php echo $iebuttonfix?> />
                </p>
             </form>
<?php

}

function modifytemp2()
{
    is_admin();
    global $language;

    /* Make sure template file is chosen */
    if (!$_POST['templateFile']) {
        fatal_error($language['CONTENT_ERRORREQUIREDVARIABLE']);
    }

    $_POST['template'] = stripslashes($_POST['template']);
    $_POST['template'] = str_replace("\r", '', $_POST['template']);
    $_POST['template'] = trim($_POST['template']);

    /* Put the code back into the template file */
    $temp = "<?php\nprint<<<EOT\n{$_POST['template']}\nEOT;\n?>";

    /* Open/Write/Close the file */
    $fh = fopen('templates/' . $_POST['templateFile'], 'w');
    fputs($fh, $temp);
    fclose($fh);

    echo "            {$language['CONTENT_UPDATETEMPLATESUCCESS']}<br />\n";
    echo "            <a href=\"index.php?action=modtemp\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/*********************
* Settings Functions *
*********************/

function settings()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    /* Tick the checkboxes */
    if ($Settings['enablecats'] == 1) {
        $enablecats = 'checked="checked"';
    }
    if ($Settings['enablestf'] == 1) {
        $enablestf = 'checked="checked"';
    }
    if ($Settings['enablesmilies'] == 1) {
        $enablesmilies = 'checked="checked"';
    }
    if ($Settings['enableavatars'] == 1) {
        $enableavatars = 'checked="checked"';
    }
    if ($Settings['enablevalidation'] == 1) {
        $enablevalidation = 'checked="checked"';
    }
    if ($Settings['enablecensor'] == 1) {
        $enablecensor = 'checked="checked"';
    }
    if ($Settings['enableprevnext'] == 1) {
        $enableprevnext = 'checked="checked"';
    }
    if ($Settings['enablecomments'] == 1) {
        $enablecomments = 'checked="checked"';
    }
    if ($Settings['showcominnews'] == 1) {
        $showcominnews = 'checked="checked"';
    }
    if ($Settings['showoldcomfirst'] == 1) {
        $showoldcomfirst = 'checked="checked"';
    }
    if ($Settings['enablebbcode'] == 1) {
        $enablebbcode = 'checked="checked"';
    }
    if ($Settings['enablerss'] == 1) {
        $enablerss = 'checked="checked"';
    }
    if ($Settings['manualrss'] == 1) {
        $manualrss = 'checked="checked"';
    }
    if ($Settings['enableimgupload'] == 1) {
        $enableimgupload = 'checked="checked"';
    }
    if ($Settings['enablecommentpages'] == 1) {
        $enablecommentpages = 'checked="checked"';
    }
    if ($Settings['enablecheckversion'] == 1) {
        $enablecheckversion = 'checked="checked"';
    }
    if ($Settings['enablecountviews'] == 1) {
        $enablecountviews = 'checked="checked"';
    }
    ?>
             <p>
                <?php echo $language['CONTENT_SETTINGSINFO'],"\n";?>
                <a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=settingshelp')">
                <?php echo $language['CONTENT_SETTINGSCLICKHERE'];?></a>.
             </p>
             <form action="index.php?action=modsettings" method="post">
             <hr />
             <table>
                <tr>
                   <td>
                      <label for="sitename"><?php echo $language['CONTENT_SETTINGSSITENAME'];?></label>
                   </td>
                   <td>
                      <input id="sitename" name="sitename" type="text"
                      value="<?php echo $Settings['sitename']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="phpnewsurl"><?php echo $language['CONTENT_SETTINGSPHPNEWSURL'];?></label>
                   </td>
                   <td>
                      <input id="phpnewsurl" name="phpnewsurl" type="text"
                      value="<?php echo $Settings['phpnewsurl']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="siteurl"><?php echo $language['CONTENT_SETTINGSNEWSURL'];?></label>
                   </td>
                   <td>
                      <input id="siteurl" name="siteurl" type="text"
                      value="<?php echo $Settings['siteurl']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="language"><?php echo $language['CONTENT_SETTINGSLANGUAGE'];?></label>
                   </td>
                   <td>
                      <select id="language" name="language">
<?php
        /* Look for all .lng files and make em selectable in the settings screen */
        $dir = opendir('languages/');

    $i = 0;
    while (false !== ($file = readdir($dir))) {
        if(substr($file, 5) == '.admin.lng') {
            include('languages/' . $file);

            if($Settings['language'] == substr($file, 0, 5)) {
                ?>
                         <option value="<?php echo substr($file, 0, 5);?>" selected="selected">
                            <?php echo $lng['LANGUAGE'],"\n";?>
                         </option>
<?php
            } else {
                ?>
                         <option value="<?php echo substr($file, 0, 5);?>">
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
                   <td colspan="2">
                      <hr />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="numtoshow"><?php echo $language['CONTENT_SETTINGSPOSTSTOSHOW'];?></label>
                   </td>
                   <td>
                      <input id="numtoshow" name="numtoshow" type="text"
                      value="<?php echo $Settings['numtoshow']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="numtoshowhead"><?php echo $language['CONTENT_SETTINGSHEADTOSHOW'];?></label>
                   </td>
                   <td>
                      <input id="numtoshowhead" name="numtoshowhead" type="text"
                      value="<?php echo $Settings['numtoshowhead']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablestf"><?php echo $language['CONTENT_SETTINGSENABLESENDTOFRIEND'];?></label>
                   </td>
                   <td>
                      <input id="enablestf" name="enablestf"
                      type="checkbox" value="1" <?php echo $enablestf?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablesmilies"><?php echo $language['CONTENT_SETTINGSENABLESMILIES'];?></label>
                   </td>
                   <td>
                      <input id="enablesmilies" name="enablesmilies"
                      type="checkbox"value="1" <?php echo $enablesmilies?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enableavatars"><?php echo $language['CONTENT_SETTINGSENABLEAVATARS'];?></label>
                   </td>
                   <td>
                      <input id="enableavatars" name="enableavatars"
                      type="checkbox" value="1" <?php echo $enableavatars?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablevalidation"><?php echo $language['CONTENT_SETTINGSENABLEVALIDATION'];?></label>
                   </td>
                   <td>
                      <input id="enablevalidation" name="enablevalidation"
                      type="checkbox" value="1" <?php echo $enablevalidation?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablecensor"><?php echo $language['CONTENT_SETTINGSENABLECENSOR'];?></label>
                   </td>
                   <td>
                      <input id="enablecensor" name="enablecensor"
                      type="checkbox" value="1" <?php echo $enablecensor?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enableprevnext"><?php echo $language['CONTENT_SETTINGSENABLEPREVNEXT'];?></label>
                   </td>
                   <td>
                      <input id="enableprevnext" name="enableprevnext"
                      type="checkbox" value="1" <?php echo $enableprevnext?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablebbcode"><?php echo $language['CONTENT_SETTINGSENABLEBBCODE'];?></label>
                   </td>
                   <td>
                      <input id="enablebbcode" name="enablebbcode"
                      type="checkbox" value="1" <?php echo $enablebbcode?> />
                   </td>
                </tr>
<?php
    // You can't check your version unless the XML extension is found
        if((extension_loaded('xml'))) {
            ?>
                <tr>
                   <td>
                      <label for="enablecheckversion"><?php echo $language['CONTENT_SETTINGSENABLECVERSION'];?></label>
                   </td>
                   <td>
                      <input id="enablecheckversion" name="enablecheckversion"
                      type="checkbox" value="1" <?php echo $enablecheckversion?> />
                   </td>
                </tr>
<?php
        }
    ?>
                <tr>
                   <td>
                      <label for="enablecountviews"><?php echo $language['CONTENT_SETTINGSENABLECOUNTVIEWS'];?></label>
                   </td>
                   <td>
                      <input id="enablecountviews" name="enablecountviews"
                      type="checkbox" value="1" <?php echo $enablecountviews?> />
                   </td>
                </tr>
                <tr>
                   <td colspan="2">
                      <hr />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablecomments"><?php echo $language['CONTENT_SETTINGSENABLECOMMENTS'];?></label>
                   </td>
                   <td>
                      <input id="enablecomments" name="enablecomments"
                      type="checkbox" value="1" <?php echo $enablecomments?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="showcominnews"><?php echo $language['CONTENT_SETTINGSSHOWCOMINNEWS'];?></label>
                   </td>
                   <td>
                      <input id="showcominnews" name="showcominnews"
                      type="checkbox" value="1" <?php echo $showcominnews?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="showoldcomfirst"><?php echo $language['CONTENT_SETTINGSSHOWOLDCOM'];?></label>
                   </td>
                   <td>
                      <input id="showoldcomfirst" name="showoldcomfirst"
                      type="checkbox" value="1" <?php echo $showoldcomfirst?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="floodprotection"><?php echo $language['CONTENT_SETTINGSFLOODPROTECTION'];?></label>
                   </td>
                   <td>
                      <input id="floodprotection" name="floodprotection"
                      type="text" value="<?php echo $Settings['floodprotection']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablecommentpages"><?php echo $language['CONTENT_SETTINGSENABLECOMPAGES'];?></label>
                   </td>
                   <td>
                      <input id="enablecommentpages" name="enablecommentpages"
                      type="checkbox" value="1" <?php echo $enablecommentpages?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="commentsperpage"><?php echo $language['CONTENT_SETTINGSPERPAGE'];?></label>
                   </td>
                   <td>
                      <input id="commentsperpage" name="commentsperpage"
                      type="text" value="<?php echo $Settings['commentsperpage']?>" />
                   </td>
                </tr>
                <tr>
                   <td colspan="2">
                      <hr />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablecats"><?php echo $language['CONTENT_SETTINGSENABLECATS'];?></label>
                   </td>
                   <td>
                      <input id="enablecats" name="enablecats"
                      type="checkbox" value="1" <?php echo $enablecats?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="numtoshowcat"><?php echo $language['CONTENT_SETTINGSCATTOSHOW'];?></label>
                   </td>
                   <td>
                      <input id="numtoshowcat" name="numtoshowcat" type="text"
                      value="<?php echo $Settings['numtoshowcat']?>" />
                   </td>
                </tr>
                <tr>
                   <td colspan="2">
                      <hr />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="enablerss"><?php echo $language['CONTENT_SETTINGSENABLERSS'];?></label>
                   </td>
                   <td>
                      <input id="enablerss" name="enablerss"
                      type="checkbox" value="1" <?php echo $enablerss?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="manualrss"><?php echo $language['CONTENT_SETTINGSMANUALRSS'];?></label>
                   </td>
                   <td>
                      <input id="manualrss" name="manualrss" type="checkbox"
                      value="1" <?php echo $manualrss?> />
                   </td>
                </tr>
                <tr>
                   <td colspan="2">
                      <hr />
                   </td>
                </tr>
<?php
        // Make sure the GD library is loaded otherwise the image functions wont work anyways
    //    if((extension_loaded('gd')))
    //    {
    ?>
                <tr>
                   <td>
                      <label for="enableimgupload"><?php echo $language['CONTENT_SETTINGSENABLEIMGUPLOAD'];?></label>
                   </td>
                   <td>
                      <input id="enableimgupload" name="enableimgupload" type="checkbox" value="1" <?php echo $enableimgupload?> />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="imguploadpath"><?php echo $language['CONTENT_SETTINGSIMGUPLOADPATH'];?></label>
                   </td>
                   <td>
                      <input id="imguploadpath" name="imguploadpath" type="text" value="<?php echo $Settings['imguploadpath']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="uploadfiles"><?php echo $language['CONTENT_SETTINGSUPLOADFILES'];?></label>
                   </td>
                   <td>
                      <input id="uploadfiles" name="uploadfiles" type="text" value="<?php echo $Settings['uploadfiles']?>" />
                   </td>
                </tr>
                <tr>
                   <td colspan="2">
                      <hr />
                   </td>
                </tr>
<?php
    //    }
    ?>
                <tr>
                   <td>
                      <label for="timeoffset"><?php echo $language['CONTENT_SETTINGSTIMEADJUSTMENT'];?></label>
                   </td>
                   <td>
                      <input id="timeoffset" name="timeoffset"
                      type="text" value="<?php echo $Settings['timeoffset']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="timeformat"><?php echo $language['CONTENT_SETTINGSTIMEFORMAT'];?></label>
                   </td>
                   <td>
                      <input id="timeformat" name="timeformat"
                      type="text" value="<?php echo $Settings['timeformat']?>" />
                   </td>
                </tr>
                <tr>
                   <td>
                      <label for="shorttimeformat"><?php echo $language['CONTENT_SETTINGSSHORTTIMEFORMAT'];?></label>
                   </td>
                   <td>
                      <input id="shorttimeformat" name="shorttimeformat" type="text"
                      value="<?php echo $Settings['shorttimeformat']?>" />
                   </td>
                </tr>
             </table>
             <hr />
             <p class="center">
                <input type="submit" value="<?php echo $language['CONTENT_BUTTONSAVE']?>" <?php echo $iebuttonfix?> />
             </p>
          </form>
<?php

}

function modsettings()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;

    if(!$_POST['timeformat'] || !$_POST['shorttimeformat']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* Prevent errors, by making sure values are Numbers */
    if (!$_POST['numtoshow'] || !is_Numeric($_POST['numtoshow'])) {
        $_POST['numtoshow'] = 8;
    }

    if (!$_POST['numtoshowcat'] || !is_Numeric($_POST['numtoshowcat'])) {
        $_POST['numtoshowcat'] = 8;
    }

    if (!$_POST['numtoshowhead'] || !is_Numeric($_POST['numtoshowhead'])) {
        $_POST['numtoshowhead'] = 8;
    }

    if ($_POST['floodprotection'] == '' || !is_Numeric($_POST['floodprotection'])) {
        $_POST['floodprotection'] = 15;
    }

    if(!$_POST['timeoffset'] || !is_Numeric($_POST['timeoffset'])) {
        $_POST['timeoffset'] = 0;
    }

    if(!$_POST['uploadfiles'] || !is_Numeric($_POST['uploadfiles'])) {
        $_POST['uploadfiles'] = 0;
    }

    /* Place all the Settings Variables in an Array */
    $Vars = array(
           'sitename',
           'phpnewsurl',
           'siteurl',
           'language',
           'numtoshow',
           'numtoshowhead',
           'enablestf',
           'enablesmilies',
           'enableavatars',
           'enablevalidation',
           'enablecensor',
           'enableprevnext',
           'enablebbcode',
           'enablecomments',
           'showcominnews',
           'showoldcomfirst',
           'enablecommentpages',
           'commentsperpage',
           'enablecats',
           'numtoshowcat',
           'floodprotection',
           'timeoffset',
           'timeformat',
           'shorttimeformat',
           'enablerss',
           'manualrss',
           'pathtorss',
           'enableimgupload',
           'imguploadpath',
           'thumbwidth',
           'thumbheight',
           'imagewidth',
           'imageheight',
           'uploadfiles',
           'enablecheckversion',
           'enablecountviews');

    /* Update each field individually */
    foreach($Vars as $Var) {
        $request = mysql_query('UPDATE ' . $db_prefix . 'settings SET value = \'' . $_POST[$Var] . '\' WHERE variable = \'' . $Var . '\'');
        $dbQueries++;
    }

    echo "            {$language['CONTENT_UPDATESETTINGSSUCCESS']}<br />\n";
    echo "            <a href=\"index.php\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/************************
* Advanced Options list *
************************/

function advanced()
{
    is_admin();
    global $language, $Settings;
    ?>
            <h2>
               <?php echo $language['CONTENT_ADVTITLE'];?>
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_ADVINFO'];?>
            </p>
            <p>
<?php if($Settings['enablecats'] == 1):?>
                     <a href="index.php?action=cats"><?php echo $language['MENU_MANAGE'];?></a>
                     <?php echo $language['MENUITEM_CATEGORIES'];?><br />
<?php endif; ?>

<?php if($Settings['enablecensor'] == 1):?>
                     <a href="index.php?action=censorlist"><?php echo $language['MENU_SET'];?></a>
                     <?php echo $language['MENUITEM_SETCENSOREDWORDS'];?><br />
<?php endif; ?>

                     <a href="index.php?action=banning"><?php echo $language['MENU_MODIFY'];?></a>
                     <?php echo $language['MENUITEM_BANNEDIPADDRESSES'];?><br />

<?php if($Settings['enablerss'] == 1 && $Settings['manualrss'] == 1):?>
                     <a href="index.php?action=createRSSFeed"><?php echo $language['MENU_CREATE'];?></a>
                     <?php echo $language['MENUITEM_CREATERSS'];?><br />
<?php endif; ?>

<?php if($Settings['enableimgupload'] == 1):?>
                     <a href="index.php?action=images"><?php echo $language['MENU_MANAGE'];?></a>
                     <?php echo $language['MENUITEM_IMAGES'];?><br />
<?php endif; ?>

<?php if($Settings['enablecheckversion'] == 1):?>
                     <a href="index.php?action=checkVersion"><?php echo $language['MENU_CHECK'];?></a>
                     <?php echo $language['MENUITEM_CHECKVERSION'];?><br />
<?php endif; ?>
                     <a href="javascript:" onclick="window.open('http://newsphp.sourceforge.net/register.php?name=<?php echo $Settings['sitename']?>&amp;url=<?php echo $Settings['phpnewsurl']?>')"><?php echo $language['MENU_REGISTER'];?></a>
                     <?php echo $language['MENUITEM_REGISTER'];?>
            </p>
<?php
        checkForIE();
}

/************************
* Censor List Functions *
************************/

function censorlist()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;

    $Settings['censorlist'] = str_replace('|', "\r\n", $Settings['censorlist']);
    ?>
            <h2>
               <?php echo $language['CONTENT_CENSORHEAD'],"\n";?>
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_CENSORINFO'],"\n";?>
            </p>
            <form action="index.php?action=modcensorlist" method="post">
               <p>
                  <textarea cols="42" name="censoredwords" rows="9"><?php echo $Settings['censorlist'];?></textarea>
               </p>
               <p class="center">
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
}

function modcensorlist()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;

    $_POST['censoredwords'] = trim($_POST['censoredwords']);
    $_POST['censoredwords'] = str_replace("\r\n", '|', $_POST['censoredwords']);

    mysql_query('UPDATE ' . $db_prefix . 'settings SET value = \'' . $_POST['censoredwords'] . '\' WHERE variable = \'censorlist\'');
    $dbQueries++;

    echo "            {$language['CONTENT_UPDATECENSOR']} <br />\n";
    echo "            <a href=\"index.php\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/*********************
* Category Functions *
*********************/

function cats()
{
    is_admin();
    global $language, $dbQueries, $db_prefix, $iebuttonfix;
    ?>
            <h2>
               <?php echo $language['CONTENT_CATSADD'],"\n"?>
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_CATINFO'],"\n";?>
               <a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=categoryhelp')">
               <?php echo $language['CONTENT_SETTINGSCLICKHERE'];?></a>.
            </p>
            <form action="index.php?action=addcat" method="post">
               <table class="tablecenter" summary="">
                  <tr>
                     <td>
                        <label for="catname"><?php echo $language['CONTENT_CATNAME'];?></label>
                     </td>
                     <td>
                        <input id="catname" name="catname" type="text" size="16" />
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <label for="caticon"><?php echo $language['CONTENT_CATICON'];?></label>
                     </td>
                     <td>
                        <input id="caticon" name="caticon" type="text" size="16" />
                     </td>
                  </tr>
               </table>
               <p class="center">
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONADDCAT'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
            <hr />
            <h2>
               <?php echo $language['CONTENT_CATMODIFY'],"\n";?>
            </h2>
            <form action="index.php?action=modifycats" method="post">
<?php
      $query = mysql_query('SELECT * FROM ' . $db_prefix . 'categories ORDER BY id');
    $dbQueries++;
    $i = 0;

    while($catinfo = mysql_fetch_assoc($query)) {
        ?>
               <table class="tablecenter" style="border-top:#000000 solid 1px;" summary="">
                  <tr>
                     <td>
                        <label for="id[<?php echo $i?>]"><?php echo $language['CONTENT_CATID'];?></label>
                     </td>
                     <td>
                       <b><?php echo $catinfo['id'];?></b>
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <label for="catname[<?php echo $i?>]"><?php echo $language['CONTENT_CATNAME'];?></label>
                     </td>
                     <td>
                       <input id="catname[<?php echo $i?>]" name="catname[<?php echo $i?>]" type="text" size="16" value="<?php echo $catinfo['catname'];?>" />
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <label for="caticon[<?php echo $i?>]"><?php echo $language['CONTENT_CATICON'];?></label>
                     </td>
                     <td>
                        <input id="caticon[<?php echo $i?>]" name="caticon[<?php echo $i?>]" type="text" size="16" value="<?php echo $catinfo['caticon'];?>" />
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <label for="delete[<?php echo $i?>]"><?php echo $language['CONTENT_CATREMOVE'];?></label>
                     </td>
                     <td>
                        <input type="checkbox" id="delete[<?php echo $i?>]" name="delete[<?php echo $i?>]" value="1" />
                        <input type="hidden" name="id[<?php echo $i?>]" value="<?php echo $catinfo['id'];?>" />
                     </td>
                  </tr>
               </table>
<?php
            $i++;
    }
    ?>
               <p class="center">
                 <input type="hidden" name="numcats" value="<?php echo $i?>" />
                 <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                 <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
}

function addcat()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;

    $_POST['catname'] = trim($_POST['catname']);
    $_POST['caticon'] = trim($_POST['caticon']);

    if (!$_POST['catname']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* Check if Category Name already exists */
    $result = mysql_query('SELECT catname FROM ' . $db_prefix . 'categories WHERE catname = \'' . $_POST['catname'] . '\'');
    $dbQueries++;

    if (mysql_numrows($result) != 0) {
        fatal_error($language['CONTENT_CATEXISTS']);
    }

    mysql_query('INSERT INTO ' . $db_prefix . 'categories (catname,caticon) VALUES (\'' . $_POST['catname'] . '\', \'' . $_POST['caticon'] . '\')');
    $dbQueries++;

    echo "            {$language['CONTENT_ADDEDCATSUCCESS']}<br />\n";
    echo "            <a href=\"index.php?action=cats\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

function modifycats()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;

    /* Assign arrays variables */
    $catname = $_POST['catname'];
    $caticon = $_POST['caticon'];
    $delete = $_POST['delete'];
    $id = $_POST['id'];

    $i = 0;

    /* Update/Delete the Categories */
    while ($i < $_POST['numcats']) {
        //        eval("\$name = \$catname[$i];");
        $name = $catname[$i];
        //        eval("\$icon = \$caticon[$i];");
        $icon = $caticon[$i];
        //        eval("\$del = \$delete[$i];");
        $del = $delete[$i];
        //        eval("\$cid = \$id[$i];");
        $cid = $id[$i];

        if ($del == 1) {
            $qs = 'DELETE FROM ' . $db_prefix . 'categories WHERE id = ' . $cid . '';
        } else {
            $qs = 'UPDATE ' . $db_prefix . 'categories SET catname = \'' . $name . '\', caticon = \'' . $icon . '\' WHERE id = ' . $cid . '';
        }

        mysql_query($qs);
        $dbQueries++;
        $i++;
    }

    echo "            {$language['CONTENT_UPDATECATS']}<br />\n";
    echo "            <a href=\"index.php?action=cats\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/**********************
* Post News Functions *
**********************/

function post()
{
    global $Settings, $language, $dbQueries, $db_prefix, $iebuttonfix;

    // Check if replace linebreaks checkbox is ticked
    // Makes sure the Post screen is the same when coming back from Preview
    if (!isset($_POST['break'])) {
        $replace = 'checked="checked"';
    } elseif ($_POST['break'] == 1) {
        $_POST['titletext'] = str_replace('<br />', "\r\n", $_POST['titletext']);
        $_POST['maintext'] = str_replace('<br />', "\r\n", $_POST['maintext']);
        $replace = 'checked="checked"';
    } else {
        $replace = '';
    }

    // Don't let the evil double quotes win! >:D
    $_POST['subject'] = htmlentities($_POST['subject'], ENT_COMPAT);
    ?>
            <script type="text/javascript">
                function toggleImageUpload()
                {
                    if(document.getElementById('imageupload').style.display != 'block')
                    {
                        document.getElementById('imageupload').style.display = 'block';
                    }
                    else
                    {
                        document.getElementById('imageupload').style.display = 'none';
                    }
                }
            </script>
            <h2>
               <?php echo $language['CONTENT_NEWSADD'];?>:
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_NEWSADDINFO'],"\n";?><a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=posthelp')"><?php echo $language['CONTENT_NEWSCLICKHERE'];?></a>.<br />
<?php if($Settings['enableimgupload'] == 1):?>
               <?php echo $language['CONTENT_NEWSUPLOADEDIMAGES'],"\n";?><a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=uploadedimages')"><?php echo $language['CONTENT_NEWSCLICKHERE'];?></a>.<br />
               <?php echo $language['CONTENT_NEWSADDIMAGE'],"\n";?><a href="javascript:toggleImageUpload()"><?php echo $language['CONTENT_NEWSCLICKHERE'];?></a>.<br />
<?php endif; ?>
            </p>
            <form enctype="multipart/form-data" action="index.php?action=post2" id="postmodify" method="post">
<?php if($Settings['enableimgupload'] == 1):?>
               <p id="imageupload">
                  <?php echo $language['CONTENT_NEWSIMAGEUPLOAD'];?><br />
                  <label for="image1"><?php echo $language['CONTENT_IMAGE'];?> 1</label>&nbsp;[<a href="javascript:insertext('[image1]','title')" title="<?php echo $language['CONTENT_NEWSTITLE']?>"><?php echo substr($language['CONTENT_NEWSTITLE'], 0, 1);?></a>][<a href="javascript:insertext('[image1]','main')" title="<?php echo $language['CONTENT_NEWSBODY']?>"><?php echo substr($language['CONTENT_NEWSBODY'], 0, 1);?></a>]&nbsp;<input id="image1" name="image1" type="file" size="28" /><br />
                  <label for="image2"><?php echo $language['CONTENT_IMAGE'];?> 2</label>&nbsp;[<a href="javascript:insertext('[image2]','title')" title="<?php echo $language['CONTENT_NEWSTITLE']?>"><?php echo substr($language['CONTENT_NEWSTITLE'], 0, 1);?></a>][<a href="javascript:insertext('[image2]','main')" title="<?php echo $language['CONTENT_NEWSBODY']?>"><?php echo substr($language['CONTENT_NEWSBODY'], 0, 1);?></a>]&nbsp;<input id="image2" name="image2" type="file" size="28" /><br />
                  <label for="image3"><?php echo $language['CONTENT_IMAGE'];?> 3</label>&nbsp;[<a href="javascript:insertext('[image3]','title')" title="<?php echo $language['CONTENT_NEWSTITLE']?>"><?php echo substr($language['CONTENT_NEWSTITLE'], 0, 1);?></a>][<a href="javascript:insertext('[image3]','main')" title="<?php echo $language['CONTENT_NEWSBODY']?>"><?php echo substr($language['CONTENT_NEWSBODY'], 0, 1);?></a>]&nbsp;<input id="image3" name="image3" type="file" size="28" />
               </p>
<?php endif; ?>
               <p>
                  <label for="subject"><?php echo $language['CONTENT_NEWSSUBJECT'];?>:</label><br />
                  <input id="subject" name="subject" size="45" type="text" value="<?php echo stripslashes($_POST['subject'])?>" />
               </p>
               <p>
                  <label for="titletext"><?php echo $language['CONTENT_NEWSTITLE'];?>:</label><br />
<?php
if ($Settings['enablebbcode'] == 1) {
    ?>
                  <a href="javascript:insertext('[b][/b]','title')" class="bbcodebutton" title="[b][/b]"><b>B</b></a>
                  <a href="javascript:insertext('[i][/i]','title')" class="bbcodebutton" title="[i][/i]"><i>I</i></a>
                  <a href="javascript:insertext('[u][/u]','title')" class="bbcodebutton" title="[u][/u]"><u>U</u></a>
                  <a href="javascript:insertext('[del][/del]','title')" class="bbcodebutton" title="[del][/del]"><del>deleted</del></a>
                  <a href="javascript:insertext('[url][/url]','title')" class="bbcodebutton" title="[url][/url]">http://</a>
                  <a href="javascript:insertext('[ftp][/ftp]','title')" class="bbcodebutton" title="[ftp][/ftp]">ftp://</a>
                  <a href="javascript:insertext('[img][/img]','title')" class="bbcodebutton" title="[img][/img]">img</a>
                  <a href="javascript:insertext('[email][/email]','title')" class="bbcodebutton" title="[email][/email]">@</a>
                  <br />
<?php
}

    if ($Settings['enablesmilies'] == 1) {
        ?>
                  <a href="javascript:insertext(':smiley:','title')"><img src="./images/smilies/smiley.gif" alt="Smiley" /></a>
                  <a href="javascript:insertext(':wink:','title')"><img src="./images/smilies/wink.gif" alt="Wink" /></a>
                  <a href="javascript:insertext(':cheesy:','title')"><img src="./images/smilies/cheesy.gif" alt="Cheesy" /></a>
                  <a href="javascript:insertext(':grin:','title')"><img src="./images/smilies/grin.gif" alt="Grin" /></a>
                  <a href="javascript:insertext(':angry:','title')"><img src="./images/smilies/angry.gif" alt="Angry" /></a>
                  <a href="javascript:insertext(':sad:','title')"><img src="./images/smilies/sad.gif" alt="Sad" /></a>
                  <a href="javascript:insertext(':shocked:','title')"><img src="./images/smilies/shocked.gif" alt="Shocked" /></a>
                  <a href="javascript:insertext(':cool:','title')"><img src="./images/smilies/cool.gif" alt="Cool" /></a>
                  <a href="javascript:insertext(':huh:','title')"><img src="./images/smilies/huh.gif" alt="Huh" /></a>
                  <a href="javascript:insertext(':rolleyes:','title')"><img src="./images/smilies/rolleyes.gif" alt="Roll Eyes" /></a>
                  <a href="javascript:insertext(':tongue:','title')"><img src="./images/smilies/tongue.gif" alt="Tongue" /></a>
                  <a href="javascript:insertext(':embarassed:','title')"><img src="./images/smilies/embarassed.gif" alt="embarrassed" /></a>
                  <a href="javascript:insertext(':lipsrsealed:','title')"><img src="./images/smilies/lipsrsealed.gif" alt="lips sealed" /></a>
                  <a href="javascript:insertext(':undecided:','title')"><img src="./images/smilies/undecided.gif" alt="undecided" /></a>
                  <a href="javascript:insertext(':kiss:','title')"><img src="./images/smilies/kiss.gif" alt="kiss" /></a>
                  <a href="javascript:insertext(':cry:','title')"><img src="./images/smilies/cry.gif" alt="cry" /></a><br />
<?php
    }
    ?>
                  <textarea cols="45" id="titletext" name="titletext"
                  rows="5"><?php echo stripslashes($_POST['titletext'])?></textarea>
               </p>
               <p>
                  <label for="maintext"><?php echo $language['CONTENT_NEWSBODY'];?>:</label><br />
<?php
if ($Settings['enablebbcode'] == 1) {
    ?>
                  <a href="javascript:insertext('[b][/b]','main')" class="bbcodebutton" title="[b][/b]"><b>B</b></a>
                  <a href="javascript:insertext('[i][/i]','main')" class="bbcodebutton" title="[i][/i]"><i>I</i></a>
                  <a href="javascript:insertext('[u][/u]','main')" class="bbcodebutton" title="[u][/u]"><u>U</u></a>
                  <a href="javascript:insertext('[del][/del]','main')" class="bbcodebutton" title="[del][/del]"><del>deleted</del></a>
                  <a href="javascript:insertext('[url][/url]','main')" class="bbcodebutton" title="[url][/url]">http://</a>
                  <a href="javascript:insertext('[ftp][/ftp]','main')" class="bbcodebutton" title="[ftp][/ftp]">ftp://</a>
                  <a href="javascript:insertext('[img][/img]','main')" class="bbcodebutton" title="[img][/img]">img</a>
                  <a href="javascript:insertext('[email][/email]','main')" class="bbcodebutton" title="[email][/email]">@</a>
                  <br />
<?php
}

    if ($Settings['enablesmilies'] == 1) {
        ?>
                  <a href="javascript:insertext(':smiley:','main')"><img src="./images/smilies/smiley.gif" alt="Smiley" /></a>
                  <a href="javascript:insertext(':wink:','main')"><img src="./images/smilies/wink.gif" alt="Wink" /></a>
                  <a href="javascript:insertext(':cheesy:','main')"><img src="./images/smilies/cheesy.gif" alt="Cheesy" /></a>
                  <a href="javascript:insertext(':grin:','main')"><img src="./images/smilies/grin.gif" alt="Grin" /></a>
                  <a href="javascript:insertext(':angry:','main')"><img src="./images/smilies/angry.gif" alt="Angry" /></a>
                  <a href="javascript:insertext(':sad:','main')"><img src="./images/smilies/sad.gif" alt="Sad" /></a>
                  <a href="javascript:insertext(':shocked:','main')"><img src="./images/smilies/shocked.gif" alt="Shocked" /></a>
                  <a href="javascript:insertext(':cool:','main')"><img src="./images/smilies/cool.gif" alt="Cool" /></a>
                  <a href="javascript:insertext(':huh:','main')"><img src="./images/smilies/huh.gif" alt="Huh" /></a>
                  <a href="javascript:insertext(':rolleyes:','main')"><img src="./images/smilies/rolleyes.gif" alt="Roll Eyes" /></a>
                  <a href="javascript:insertext(':tongue:','main')"><img src="./images/smilies/tongue.gif" alt="Tongue" /></a>
                  <a href="javascript:insertext(':embarassed:','main')"><img src="./images/smilies/embarassed.gif" alt="embarrassed" /></a>
                  <a href="javascript:insertext(':lipsrsealed:','main')"><img src="./images/smilies/lipsrsealed.gif" alt="lips sealed" /></a>
                  <a href="javascript:insertext(':undecided:','main')"><img src="./images/smilies/undecided.gif" alt="undecided" /></a>
                  <a href="javascript:insertext(':kiss:','main')"><img src="./images/smilies/kiss.gif" alt="kiss" /></a>
                  <a href="javascript:insertext(':cry:','main')"><img src="./images/smilies/cry.gif" alt="cry" /></a><br />
<?php
    }
    ?>
                  <textarea cols="45" id="maintext" name="maintext"
                  rows="8"><?php echo stripslashes($_POST['maintext'])?></textarea>
               </p>
<?php
if($Settings['enablecats'] == 1) {
    ?>
               <p>
                  <label for="catid"><?php echo $language['CONTENT_NEWSCAT'];?>:</label><br />
                  <select id="catid" name="catid">
                     <option value="0">
                     </option>
<?php
      $query = mysql_query('SELECT * FROM ' . $db_prefix . 'categories ORDER BY id');
    $dbQueries++;

    while($catinfo = mysql_fetch_assoc($query)) {
        if($_POST['catid'] == $catinfo['id']) {
            $selected = 'selected="selected"';
        } else {
            $selected = '';
        }
        ?>
                     <option value="<?php echo $catinfo['id']?>" <?php echo $selected?>>
                        <?php echo $catinfo['catname'],"\n";?>
                     </option>
<?php
    }
    ?>
                  </select>
               </p>
<?php
}
    ?>
               <p>
                  <input <?php echo $replace?> name="break" type="checkbox" value="1" />
                  <?php echo $language['CONTENT_NEWSREPLACE'],"\n";?>
               </p>
               <p class="center">
                  <input name="post" type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input name="preview" type="submit" value="<?php echo $language['CONTENT_BUTTONPREVIEW']?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
}

function post2()
{
    global $userDetails, $Settings, $language, $dbQueries, $db_prefix;

    /* Get the time of the post, and calculate curent time set in Settings */
    $time = time() + ($Settings['timeoffset']*60);
    $today = getdate();
    $month = $today['mon'];
    $year = $today['year'];

    $_POST['subject'] = trim($_POST['subject']);
    $_POST['subject'] = stripslashes($_POST['subject']);
    $_POST['subject'] = htmlspecialchars($_POST['subject'], ENT_COMPAT, $language['CHARSET']);

    /* Make sure required fields are entered */
    if(!$_POST['subject'] || !$_POST['titletext']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* Call Replace function to do the common changes */
    $_POST['titletext'] = replace($_POST['titletext'], $_POST['break']);
    $_POST['maintext'] = replace($_POST['maintext'], $_POST['break']);

    /* If no category ID is passed, set it as 0 */
    if(!$_POST['catid']) {
        $_POST['catid'] = 0;
    }

    // Image Files - Json
    if($Settings['enableimgupload'] == 1) {
        for($i = 1; $i <= 3; $i++) {
            if(!empty($_FILES['image' . $i]['name'])) {
                // Check if we really got an image file
                if (is_int(exif_imagetype($_FILES['image' . $i]['tmp_name']))) {
                    $uploadfile = $Settings['imguploadpath'] . $_FILES['image' . $i]['name'];

                    if(move_uploaded_file($_FILES['image' . $i]['tmp_name'], $uploadfile)) {
                        // Check whether to insert image as BBCode or xHTML
                        if ($Settings['enablebbcode'] == 1) {
                            $_POST['titletext'] = str_replace('[image' . $i . ']', '[img]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '[/img]', $_POST['titletext']);
                            $_POST['maintext'] = str_replace('[image' . $i . ']', '[img]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '[/img]', $_POST['maintext']);
                        } else {
                            $_POST['titletext'] = str_replace('[image' . $i . ']', '<img src="' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '" alt="" style="border:none;" />', $_POST['titletext']);
                            $_POST['maintext'] = str_replace('[image' . $i . ']', '<img src="' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '" alt="" style="border:none;" />', $_POST['maintext']);
                        }
                    }
                } else {
                    fatal_error($language['CONTENT_ERRORNOIMAGE']);
                }
            } else {
                // Remove the [image] tag if the image upload failed
                $_POST['titletext'] = str_replace('[image' . $i . ']', 'wtf', $_POST['titletext']);
                $_POST['maintext'] = str_replace('[image' . $i . ']', 'hmm', $_POST['maintext']);
            }
        }
    }

    /* What submit button was pressed? */
    if($_POST['post']) {
        /* Is this user Trusted? */
        if ($userDetails['access'] == 'newsposter') {
            $trusted = 0;
        } else {
            $trusted = 1;
        }

        mysql_query('INSERT INTO ' . $db_prefix . 'news (posterid,postername,time,month,year,subject,titletext,maintext,break,catid,trusted) VALUES (\'' . $userDetails['id'] . '\', \'' . $userDetails['username'] . '\', \'' . $time . '\', \'' . $month . '\', \'' . $year . '\', \'' . mysql_escape_string($_POST['subject']) . '\', \'' . mysql_escape_string($_POST['titletext']) . '\', \'' . mysql_escape_string($_POST['maintext']) . '\', \'' . $_POST['break'] . '\', \'' . $_POST['catid'] . '\', ' . $trusted . ')');
        $dbQueries++;

        if($Settings['enablerss'] == 1 && $Settings['manualrss'] == 0) {
            createRSSFeed();
        }

        echo "            {$language['CONTENT_ADDEDNEWSSUCCESS']}<br />\n";
        echo "            <a href=\"index.php\">{$language['CONTENT_BACK']}</a>\n";
    } elseif($_POST['preview']) {
        ?>
            <form action="index.php?action=post2" id="postmodify" method="post">
               <p style="display:none;">
                  <input id="subject" name="subject" size="45" type="text"
                  value="<?php echo $_POST['subject']?>" />
                  <textarea cols="45" id="titletext" name="titletext"
                  rows="5"><?php echo str_replace('<br />', "\r\n", $_POST['titletext'])?></textarea>
                  <textarea cols="45" id="maintext" name="maintext"
                  rows="8"><?php echo str_replace('<br />', "\r\n", $_POST['maintext'])?></textarea>
                  <input id="catid" name="catid" type="text"
                  value="<?php echo $_POST['catid']?>" />
                  <input id="break" name="break" type="text"
                  value="<?php echo $_POST['break']?>" />
               </p>
<?php
            /* Asign post variables to variables used in template */
            $subject = $_POST['subject'];
        $time = strftime($Settings['timeformat'], $time);
        $titletext = trim($_POST['titletext']);

        /* Find out who made the post (keeps track of usernames) */
        $query = mysql_query('SELECT username,email,avatar FROM ' . $db_prefix . 'posters WHERE id = ' . $userDetails['id'] . ' OR username = \'' . $userDetails['username'] . '\'');
        $dbQueries++;

        $row = mysql_fetch_assoc($query);
        $username = $row['username'];

        /* Display link to show comments & news if enabled */
        if ($_POST['maintext'] != '') {
            $maintext = trim($_POST['maintext']);
        } else {
            $maintext = '';
        }

        /* If Categories are enabled... */
        if ($Settings['enablecats'] == 1) {
            $cat_query = mysql_query('SELECT * FROM ' . $db_prefix . 'categories WHERE id = ' . $_POST['catid'] . '');
            $dbQueries++;

            $cat = mysql_fetch_assoc($cat_query);

            if ($_POST['catid'] != 0) {
                if ($cat['catname'] != '') {
                    $category = '<a href="' . $_SERVER['PHP_SELF'] . '?action=showcat&amp;catid=' . $cat['id'] . '">' . $cat['catname'] . '</a>';
                }

                if ($cat['caticon'] != '') {
                    $caticon = '<img src="' . $cat['caticon'] . '" style="border:none;" alt="' . $cat['catname'] . '" />';
                }
            }
        }

        if ($row['email'] != '') {
            $username = '<a href="mailto:' . $row['email'] . '">' . $username . '</a>';
        } else {
            $username = $username;
        }

        /* Parse the code */
        $maintext = parseCode($maintext);
        $titletext = parseCode($titletext);

        include('templates/fullnews_temp.php');
        echo "\n";
        ?>
              <p class="center">
                 <input name="post" type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT']?>"
                 <?php echo $iebuttonfix?> />
                 <input onclick="document.forms['postmodify'].action = 'index.php?action=post'; document.forms['postmodify'].submit();"
                 type="button" value="<?php echo $language['MENU_MODIFY']?>" <?php echo $iebuttonfix?> />
              </p>
           </form>
<?php
    }
    checkForIE();
}

/****************************
* Add News Poster Functions *
****************************/

function newsposter()
{
    is_admin();
    global $Settings, $language, $iebuttonfix;
    ?>
            <h2>
               <?php echo $language['CONTENT_POSTERADD'];?>:
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_POSTERADDINFO'],"\n";?>
               <a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=posterhelp')">
               <?php echo $language['CONTENT_POSTERCLICKHERE'];?></a>.
            </p>
            <form action="index.php?action=newsposter2" method="post">
               <p>
                  <label for="username"><?php echo $language['CONTENT_POSTERUSERNAME'];?>:</label><br />
                  <input id="username" name="username" type="text" />
               </p>
               <p>
                  <label for="password"><?php echo $language['CONTENT_POSTERPASSWORD'];?>:</label><br />
                  <input id="password" name="password" type="password" />
               </p>
               <p>
                  <label for="password2"><?php echo $language['CONTENT_POSTERRETYPEPASSWORD'];?>:</label><br />
                  <input id="password2" name="password2" type="password" />
               </p>
               <p>
                  <label for="email"><?php echo $language['CONTENT_POSTEREMAIL'];?>:</label><br />
                  <input id="email" name="email" type="text" />
               </p>
<?php
if ($Settings['enableavatars'] == 1) {
    ?>
               <p>
                  <label for="avatar"><?php echo $language['CONTENT_POSTERAVATAR'];?>:</label><br />
                  <input id="avatar" name="avatar" type="text" />
               </p>
<?php
}
    ?>
               <p>
                  <label for="language"><?php echo $language['CONTENT_SETTINGSLANGUAGE'];?>:</label><br />
                  <select id="language" name="language">
<?php
        /* Look for all .lng files and make em selectable in the settings screen */
        $dir = opendir('languages/');

    $i = 0;
    while (false !== ($file = readdir($dir))) {
        if(substr($file, 5) == '.admin.lng') {
            include('languages/' . $file);

            if($Settings['language'] == substr($file, 0, 5)) {
                ?>
                     <option value="<?php echo substr($file, 0, 5);?>" selected="selected">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
            } else {
                ?>
                     <option value="<?php echo substr($file, 0, 5);?>">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
            }
        }
    }

    closedir($dir);
    ?>
                  </select>
               </p>
               <p>
                  <label for="access"><?php echo $language['CONTENT_POSTERUSERACCESS'];?>:</label><br />
                  <select id="access" name="access">
                     <option value="newsposter">
                        <?php echo $language['CONTENT_NEWSPOSTER'],"\n"?>
                     </option>
                     <option value="trusted">
                        <?php echo $language['CONTENT_TRUSTED'],"\n"?>
                     </option>
                     <option value="moderator">
                        <?php echo $language['CONTENT_MODERATOR'],"\n"?>
                     </option>
                     <option value="admin">
                        <?php echo $language['CONTENT_ADMIN'],"\n"?>
                     </option>
                  </select>
               </p>
               <p class="center">
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
}

function newsposter2()
{
    is_admin();
    global $language, $dbQueries, $db_prefix, $Settings;

    /* Trim the fat so to speak */
    $_POST['username'] = trim($_POST['username']);
    $_POST['username'] = htmlspecialchars($_POST['username']);
    $_POST['password'] = trim($_POST['password']);
    $_POST['password2'] = trim($_POST['password2']);
    $_POST['email'] = trim($_POST['email']);
    $_POST['email'] = strip_tags($_POST['email']);

    /* If email address is entered, check it is valid */
    if ($_POST['email'] != '' && $Settings['enablevalidation'] == 1) {
        if (!eregi('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', $_POST['email'])) {
            fatal_error($language['CONTENT_ERROREMAIL']);
        }
    }

    /* Check all required fields were entered correctly */
    if($_POST['password'] != $_POST['password2']) {
        fatal_error($language['CONTENT_ERRORPASSWORD']);
    }
    if(!$_POST['username'] || !$_POST['password'] || !$_POST['password2']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* Check if Username already exists */
    $result = mysql_query('SELECT username FROM ' . $db_prefix . 'posters WHERE username = \'' . $_POST['username'] . '\'');
    $dbQueries++;

    if (mysql_numrows($result) != 0) {
        fatal_error($language['CONTENT_ERRORUSERNAME']);
    }

    /* Add the News Poster */
    mysql_query('INSERT INTO ' . $db_prefix . 'posters (username,password,email,avatar,language,access) VALUES (\'' . $_POST['username'] . '\', password(\'' . $_POST['password'] . '\'), \'' . $_POST['email'] . '\', \'' . $_POST['avatar'] . '\', \'' . $_POST['language'] . '\', \'' . $_POST['access'] . '\')');
    $dbQueries++;

    echo "            {$language['CONTENT_ADDEDNEWUSER']} {$_POST['username']}{$language['CONTENT_ADDEDNEWUSERSUCCESS']}<br />\n";
    echo "            <a href=\"index.php\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/************************
* Modify News Functions *
************************/

function modify()
{
    global $language, $dbQueries, $db_prefix, $userDetails;
    ?>
            <p>
               <?php echo $language['CONTENT_NEWSMODIFYINFO'],"\n";?>
               <a href="index.php?action=banning">
               <?php echo $language['CONTENT_POSTERCLICKHERE'];?></a>.
            </p>
            <table class="tablecenter">
               <tr>
                  <th>
                     <?php echo $language['CONTENT_NEWSMODIFYMONTHYEAR'],"\n";?>
                  </th>
                  <th>
                     <?php echo $language['CONTENT_NEWSMODIFYPOSTS'],"\n";?>
                  </th>
               </tr>
               <tr>
<?php
      $SQL_query = mysql_query('SELECT DISTINCT month,year FROM ' . $db_prefix . 'news ORDER by id DESC');
    $dbQueries++;

    while ($posts = mysql_fetch_assoc($SQL_query)) {
        /* Get the total number of posts per month */
        $total = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news WHERE month = \'' . $posts['month'] . '\' AND year = \'' . $posts['year'] . '\'');
        $dbQueries++;

        $var = mysql_fetch_assoc($total);
        $month = strftime('%B', mktime(0, 0, 0, $posts['month'], 1, 0));

        $mon .= "                     <a href=\"index.php?action=modifypost&amp;month={$posts['month']}&amp;year={$posts['year']}\">$month {$posts['year']}</a><br />\n";
        $post .= "                     {$var['total']}<br />\n";
    }
    ?>
                  <td>
<?php echo $mon;?>
                  </td>
                  <td>
<?php echo $post;?>
                  </td>
               </tr>
            </table>
<?php
      if ($userDetails['access'] == 'admin' || $userDetails['access'] == 'moderator') {
          /* Find number of pending articles */
          $query = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'news where trusted = 0');
          $dbQueries++;

          $pend = mysql_fetch_assoc($query);
          ?>
            <br /><br />
            <table class="tablecenter">
               <tr>
                  <th>
                     <?php echo $language['CONTENT_NEWSPENDHEAD'],"\n";?>
                  </th>
               </tr>
               <tr>
                  <td>
                     <a href="index.php?action=modifypending"><?php echo $language['CONTENT_NEWSPENDINFO']," ",$pend['total'];?></a>
                  </td>
               </tr>
            </table>
<?php
      }

      checkForIE();
}

function modifypost()
{
    global $Settings, $userDetails, $language, $dbQueries, $db_prefix;
    ?>
            <p>
               <?php echo $language['CONTENT_NEWSMODIFYPOSTINFO'],"\n";?>
            </p>
<?php
      /* If you're not an Administrator or a Moderator, show only the Posts you've made for modifying */
      if ($userDetails['access'] == 'admin' || $userDetails['access'] == 'moderator') {
          $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.subject,n.time,p.username'
                                   . ' FROM ' . $db_prefix . 'news AS n'
                                   . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                                   . ' WHERE month=\'' . $_GET['month']. '\' AND year=\'' . $_GET['year'] . '\''
                                   . ' AND n.trusted = 1'
                                   . ' ORDER by n.id DESC');
          $dbQueries++;
      } else {
          $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.subject,n.time,p.username'
                                   . ' FROM ' . $db_prefix . 'news AS n'
                                   . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                                   . ' WHERE month=\'' . $_GET['month']. '\' AND year=\'' . $_GET['year'] . '\''
                                   . ' AND postername = \'' . $userDetails['username'] . '\''
                                   . ' ORDER by n.id DESC');
          $dbQueries++;
      }

      /* Print out the News Posts */
      while ($posts = mysql_fetch_assoc($SQL_query)) {
          $time = strftime($Settings['shorttimeformat'], $posts['time']);
          $posts['subject'] = stripslashes($posts['subject']);

          /* Get the posters name */
          if (!$posts['username']) {
              $posts['username'] = $posts['postername'];
          } else {
              $posts['username'] = $posts['username'];
          }

          /* Shorten Subject to fit */
          if (strlen($posts['subject']) >= 18) {
              $posts['subject'] = substr($posts['subject'], 0, 18);
              $posts['subject'] = $posts['subject'] . '...';
          }

          echo "            <a href=\"index.php?action=modifypost2&amp;id={$posts['id']}\">{$posts['subject']}</a> {$language['CONTENT_NEWSMODIFYPOSTBY']} <strong>{$posts['username']}</strong>\n";
          echo "            {$language['CONTENT_NEWSMODIFYPOSTON']} $time<br />\n";

          $i++;
      }


      /* If you've made no posts, you've nothing to modify =P */
      if (!$i) {
          echo "            {$language['CONTENT_INFONONEWSMADE']}\n";
      }

      if ($i < 22) {
          checkForIE();
      }
}

function modifypending()
{
    global $Settings, $userDetails, $language, $dbQueries, $db_prefix;
    ?>
            <p>
               <?php echo $language['CONTENT_NEWSMODIFYPOSTINFO'],"\n";?>
            </p>
<?php
      $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.subject,n.time,p.username'
                               . ' FROM ' . $db_prefix . 'news AS n'
                               . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                               . ' WHERE n.trusted = 0'
                               . ' ORDER by n.id DESC');
    $dbQueries++;

    /* Print out the News Posts */
    while ($posts = mysql_fetch_assoc($SQL_query)) {
        $time = strftime($Settings['shorttimeformat'], $posts['time']);
        $posts['subject'] = stripslashes($posts['subject']);

        /* Get the posters name */
        if (!$posts['username']) {
            $posts['username'] = $posts['postername'];
        } else {
            $posts['username'] = $posts['username'];
        }

        /* Shorten Subject to fit */
        if (strlen($posts['subject']) >= 18) {
            $posts['subject'] = substr($posts['subject'], 0, 18);
            $posts['subject'] = $posts['subject'] . '...';
        }

        echo "            <a href=\"index.php?action=modifypost2&amp;id={$posts['id']}\">{$posts['subject']}</a> {$language['CONTENT_NEWSMODIFYPOSTBY']} <strong>{$posts['username']}</strong>\n";
        echo "            {$language['CONTENT_NEWSMODIFYPOSTON']} $time<br />\n";

        $i++;
    }

    /* Print a message if there are no pending news articles */
    if (!$i) {
        echo "            {$language['CONTENT_INFONOPOSTSPEND']}\n";
    }

    if ($i < 22) {
        checkForIE();
    }
}

function modifypost2()
{
    global $userDetails, $Settings, $language, $dbQueries, $db_prefix, $iebuttonfix;

    /* Do a query only, if we have no $_POST data */
    if (!isset($_POST['modify'])) {
        $SQL_query = mysql_query('SELECT subject,titletext,maintext,postername,break,catid,trusted FROM ' . $db_prefix . 'news WHERE id = \'' . $_GET['id'] . '\'');
        $dbQueries++;

        $_POST = mysql_fetch_assoc($SQL_query);
    }

    /* This prevents 'News Posters' from editing posts they didn't make */
    if ($userDetails['username'] != $_POST['postername'] && $userDetails['access'] != 'admin' && $userDetails['access'] != 'moderator') {
        fatal_error($language['CONTENT_ERROREDITNEWS']);
    }

    /* Check if replace linebreaks checkbox is ticked */
    if ($_POST['break'] == 1) {
        $replace = 'checked="checked"';
        $_POST['titletext'] = str_replace('<br />', "\r\n", $_POST['titletext']);
        $_POST['maintext'] = str_replace('<br />', "\r\n", $_POST['maintext']);
    }

    /* Remove special characters */
    $chars = array('&lt;','&gt;');
    $charsto = array('<','>');

    $_POST['titletext'] = str_replace($chars, $charsto, $_POST['titletext']);
    $_POST['maintext'] = str_replace($chars, $charsto, $_POST['maintext']);

    $_POST['titletext'] = un_htmlentities($_POST['titletext']);
    $_POST['titletext'] = stripslashes($_POST['titletext']);
    $_POST['maintext'] = un_htmlentities($_POST['maintext']);
    $_POST['maintext'] = stripslashes($_POST['maintext'])
    ?>
            <script type="text/javascript">
                function toggleImageUpload()
                {
                    if(document.getElementById('imageupload').style.display != 'block')
                    {
                        document.getElementById('imageupload').style.display = 'block';
                    }
                    else
                    {
                        document.getElementById('imageupload').style.display = 'none';
                    }
                }
            </script>
            <h2>
               <?php echo $language['CONTENT_NEWSMODIFYNEWS'];?>:
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_NEWSADDINFO'],"\n";?><a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=posthelp')"><?php echo $language['CONTENT_NEWSCLICKHERE'];?></a>.<br />
<?php if($Settings['enableimgupload'] == 1):?>
               <?php echo $language['CONTENT_NEWSUPLOADEDIMAGES'],"\n";?><a href="javascript:help('<?php echo $Settings['phpnewsurl']?>help.php?action=uploadedimages')"><?php echo $language['CONTENT_NEWSCLICKHERE'];?></a>.<br />
               <?php echo $language['CONTENT_NEWSADDIMAGE'],"\n";?><a href="javascript:toggleImageUpload()"><?php echo $language['CONTENT_NEWSCLICKHERE'];?></a>.<br />
<?php endif; ?>
            </p>
            <form enctype="multipart/form-data" action="index.php?action=modifypost3" id="postmodify" method="post">
<?php if($Settings['enableimgupload'] == 1):?>
               <p id="imageupload">
                  <?php echo $language['CONTENT_NEWSIMAGEUPLOAD'];?><br />
                  <label for="image1"><?php echo $language['CONTENT_IMAGE'];?> 1</label>&nbsp;[<a href="javascript:insertext('[image1]','title')" title="<?php echo $language['CONTENT_NEWSTITLE']?>"><?php echo substr($language['CONTENT_NEWSTITLE'], 0, 1);?></a>][<a href="javascript:insertext('[image1]','main')" title="<?php echo $language['CONTENT_NEWSBODY']?>"><?php echo substr($language['CONTENT_NEWSBODY'], 0, 1);?></a>]&nbsp;<input id="image1" name="image1" type="file" size="28" /><br />
                  <label for="image2"><?php echo $language['CONTENT_IMAGE'];?> 2</label>&nbsp;[<a href="javascript:insertext('[image2]','title')" title="<?php echo $language['CONTENT_NEWSTITLE']?>"><?php echo substr($language['CONTENT_NEWSTITLE'], 0, 1);?></a>][<a href="javascript:insertext('[image2]','main')" title="<?php echo $language['CONTENT_NEWSBODY']?>"><?php echo substr($language['CONTENT_NEWSBODY'], 0, 1);?></a>]&nbsp;<input id="image2" name="image2" type="file" size="28" /><br />
                  <label for="image3"><?php echo $language['CONTENT_IMAGE'];?> 3</label>&nbsp;[<a href="javascript:insertext('[image3]','title')" title="<?php echo $language['CONTENT_NEWSTITLE']?>"><?php echo substr($language['CONTENT_NEWSTITLE'], 0, 1);?></a>][<a href="javascript:insertext('[image3]','main')" title="<?php echo $language['CONTENT_NEWSBODY']?>"><?php echo substr($language['CONTENT_NEWSBODY'], 0, 1);?></a>]&nbsp;<input id="image3" name="image3" type="file" size="28" />
               </p>
<?php endif; ?>
               <p>
                  <input id="id" name="id" type="hidden" value="<?php echo $_GET['id']?>" />
                  <label for="subject"><?php echo $language['CONTENT_NEWSSUBJECT'];?>:</label><br />
                  <input id="subject" name="subject" type="text" size="45" value="<?php echo stripslashes($_POST['subject']);?>" />
               </p>
               <p>
                  <label for="titletext"><?php echo $language['CONTENT_NEWSTITLE'];?>:</label><br />
<?php
if($Settings['enablebbcode'] == 1) {
    ?>
                  <a href="javascript:insertext('[b][/b]','title')" class="bbcodebutton" title="[b][/b]"><b>B</b></a>
                  <a href="javascript:insertext('[i][/i]','title')" class="bbcodebutton" title="[i][/i]"><i>I</i></a>
                  <a href="javascript:insertext('[u][/u]','title')" class="bbcodebutton" title="[u][/u]"><u>U</u></a>
                  <a href="javascript:insertext('[del][/del]','title')" class="bbcodebutton" title="[del][/del]"><del>deleted</del></a>
                  <a href="javascript:insertext('[url][/url]','title')" class="bbcodebutton" title="[url][/url]">http://</a>
                  <a href="javascript:insertext('[ftp][/ftp]','title')" class="bbcodebutton" title="[ftp][/ftp]">ftp://</a>
                  <a href="javascript:insertext('[img][/img]','title')" class="bbcodebutton" title="[img][/img]">img</a>
                  <a href="javascript:insertext('[email][/email]','title')" class="bbcodebutton" title="[email][/email]">@</a>
                  <br />
<?php
}

    if ($Settings['enablesmilies'] == 1) {
        ?>
                  <a href="javascript:insertext(':smiley:','title')"><img src="./images/smilies/smiley.gif" alt="Smiley" /></a>
                  <a href="javascript:insertext(':wink:','title')"><img src="./images/smilies/wink.gif" alt="Wink" /></a>
                  <a href="javascript:insertext(':cheesy:','title')"><img src="./images/smilies/cheesy.gif" alt="Cheesy" /></a>
                  <a href="javascript:insertext(':grin:','title')"><img src="./images/smilies/grin.gif" alt="Grin" /></a>
                  <a href="javascript:insertext(':angry:','title')"><img src="./images/smilies/angry.gif" alt="Angry" /></a>
                  <a href="javascript:insertext(':sad:','title')"><img src="./images/smilies/sad.gif" alt="Sad" /></a>
                  <a href="javascript:insertext(':shocked:','title')"><img src="./images/smilies/shocked.gif" alt="Shocked" /></a>
                  <a href="javascript:insertext(':cool:','title')"><img src="./images/smilies/cool.gif" alt="Cool" /></a>
                  <a href="javascript:insertext(':huh:','title')"><img src="./images/smilies/huh.gif" alt="Huh" /></a>
                  <a href="javascript:insertext(':rolleyes:','title')"><img src="./images/smilies/rolleyes.gif" alt="Roll Eyes" /></a>
                  <a href="javascript:insertext(':tongue:','title')"><img src="./images/smilies/tongue.gif" alt="Tongue" /></a>
                  <a href="javascript:insertext(':embarassed:','title')"><img src="./images/smilies/embarassed.gif" alt="embarrassed" /></a>
                  <a href="javascript:insertext(':lipsrsealed:','title')"><img src="./images/smilies/lipsrsealed.gif" alt="lips sealed" /></a>
                  <a href="javascript:insertext(':undecided:','title')"><img src="./images/smilies/undecided.gif" alt="undecided" /></a>
                  <a href="javascript:insertext(':kiss:','title')"><img src="./images/smilies/kiss.gif" alt="kiss" /></a>
                  <a href="javascript:insertext(':cry:','title')"><img src="./images/smilies/cry.gif" alt="cry" /></a><br />
<?php
    }
    ?>
                  <textarea cols="45" id="titletext" name="titletext"
                  rows="5"><?php echo stripslashes($_POST['titletext']);?></textarea>
               </p>
               <p>
                  <label for="maintext"><?php echo $language['CONTENT_NEWSBODY'];?>:</label><br />
<?php
if ($Settings['enablebbcode'] == 1) {
    ?>
                  <a href="javascript:insertext('[b][/b]','main')" class="bbcodebutton" title="[b][/b]"><b>B</b></a>
                  <a href="javascript:insertext('[i][/i]','main')" class="bbcodebutton" title="[i][/i]"><i>I</i></a>
                  <a href="javascript:insertext('[u][/u]','main')" class="bbcodebutton" title="[u][/u]"><u>U</u></a>
                  <a href="javascript:insertext('[del][/del]','main')" class="bbcodebutton" title="[del][/del]"><del>deleted</del></a>
                  <a href="javascript:insertext('[url][/url]','main')" class="bbcodebutton" title="[url][/url]">http://</a>
                  <a href="javascript:insertext('[ftp][/ftp]','main')" class="bbcodebutton" title="[ftp][/ftp]">ftp://</a>
                  <a href="javascript:insertext('[img][/img]','main')" class="bbcodebutton" title="[img][/img]">img</a>
                  <a href="javascript:insertext('[email][/email]','main')" class="bbcodebutton" title="[email][/email]">@</a>
                  <br />
<?php
}

    if ($Settings['enablesmilies'] == 1) {
        ?>
                  <a href="javascript:insertext(':smiley:','main')"><img src="./images/smilies/smiley.gif" alt="Smiley" /></a>
                  <a href="javascript:insertext(':wink:','main')"><img src="./images/smilies/wink.gif" alt="Wink" /></a>
                  <a href="javascript:insertext(':cheesy:','main')"><img src="./images/smilies/cheesy.gif" alt="Cheesy" /></a>
                  <a href="javascript:insertext(':grin:','main')"><img src="./images/smilies/grin.gif" alt="Grin" /></a>
                  <a href="javascript:insertext(':angry:','main')"><img src="./images/smilies/angry.gif" alt="Angry" /></a>
                  <a href="javascript:insertext(':sad:','main')"><img src="./images/smilies/sad.gif" alt="Sad" /></a>
                  <a href="javascript:insertext(':shocked:','main')"><img src="./images/smilies/shocked.gif" alt="Shocked" /></a>
                  <a href="javascript:insertext(':cool:','main')"><img src="./images/smilies/cool.gif" alt="Cool" /></a>
                  <a href="javascript:insertext(':huh:','main')"><img src="./images/smilies/huh.gif" alt="Huh" /></a>
                  <a href="javascript:insertext(':rolleyes:','main')"><img src="./images/smilies/rolleyes.gif" alt="Roll Eyes" /></a>
                  <a href="javascript:insertext(':tongue:','main')"><img src="./images/smilies/tongue.gif" alt="Tongue" /></a>
                  <a href="javascript:insertext(':embarassed:','main')"><img src="./images/smilies/embarassed.gif" alt="embarrassed" /></a>
                  <a href="javascript:insertext(':lipsrsealed:','main')"><img src="./images/smilies/lipsrsealed.gif" alt="lips sealed" /></a>
                  <a href="javascript:insertext(':undecided:','main')"><img src="./images/smilies/undecided.gif" alt="undecided" /></a>
                  <a href="javascript:insertext(':kiss:','main')"><img src="./images/smilies/kiss.gif" alt="kiss" /></a>
                  <a href="javascript:insertext(':cry:','main')"><img src="./images/smilies/cry.gif" alt="cry" /></a><br />
<?php
    }
    ?>
                  <textarea cols="45" id="maintext" name="maintext"
                  rows="8"><?php echo stripslashes($_POST['maintext']);?></textarea>
               </p>
<?php
    /* Displays pull down menu of the Categories, if they're enabled */
    if($Settings['enablecats'] == 1) {
        ?>
               <p>
                  <label for="catid"><?php echo $language['CONTENT_NEWSCAT'];?>:</label><br />
                  <select id="catid" name="catid">
                     <option value="0">
                     </option>
<?php
          $query = mysql_query('SELECT * FROM ' . $db_prefix . 'categories ORDER by id');
        $dbQueries++;
        $i = 0;

        while($catinfo = mysql_fetch_assoc($query)) {
            if($_POST['catid'] == $catinfo['id']) {
                $selected = 'selected="selected"';
            }
            ?>
                     <option value="<?php echo $catinfo['id']?>" <?php echo $selected?>>
                        <?php echo $catinfo['catname'],"\n";?>
                     </option>
<?php
                $selected = empty($selected);
        }
        ?>
                  </select>
               </p>
<?php
    }
    ?>
               <p>
<?php
      if ($_POST['trusted'] == 0 && $userDetails['access'] == 'admin' || $userDetails['access'] == 'moderator') {
          ?>
                  <input type="checkbox" name="trusted" value="1" /> <?php echo $language['CONTENT_ALLOWARTICLE'];?><br />
<?php
      }
    ?>
                  <input type="checkbox" name="delete" value="1" /> <?php echo $language['CONTENT_NEWSDELETE'];?><br />
                  <input <?php echo $replace?> type="checkbox" name="break" value="1" /> <?php echo $language['CONTENT_NEWSREPLACE'],"\n";?>
               </p>
               <p class="center">
                  <input name="post" type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input name="preview" type="submit" value="<?php echo $language['CONTENT_BUTTONPREVIEW']?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
            <hr />
            <h2>
               <?php echo $language['CONTENT_NEWSMODIFYCOMMENTS'];?>:
            </h2>
            <form action="index.php?action=updatecomments" method="post">
               <table class="tablecenter">
                  <tr>
                     <th>
                        <?php echo $language['CONTENT_NEWSMODIFYCOMMENTSPOSTER'],"\n";?>
                     </th>
                     <th>
                        <?php echo $language['CONTENT_NEWSMODIFYCOMMENTSDATE'],"\n";?>
                     </th>
                     <th>
                        <?php echo $language['CONTENT_NEWSMODIFYCOMMENTSDELETE'],"\n";?>
                     </th>
                  </tr>
<?php
      $i = 0;
    $SQL_query = mysql_query('SELECT id,name,time FROM ' . $db_prefix . 'comments WHERE mid = \'' . $_GET['id'] . '\' ORDER by id DESC');
    $dbQueries++;

    /* Put all the comments together at the end for modifying */
    while ($comment = mysql_fetch_assoc($SQL_query)) {
        $time = strftime($Settings['shorttimeformat'], $comment['time']);
        ?>
                  <tr>
                     <td>
                        <a href="index.php?action=modifycomment&amp;id=<?php echo $comment['id'];?>">
                        <?php echo $comment['name'];?></a>
                     </td>
                     <td>
                        <a href="index.php?action=modifycomment&amp;id=<?php echo $comment['id'];?>">
                        <?php echo $time;?></a>
                     </td>
                     <td class="center">
                        <input type="checkbox" name="delete[<?php echo $i;?>]" value="1" />
                        <input name="ids[<?php echo $i;?>]" type="hidden"
                        style="display:none;" value="<?php echo $comment['id'];?>" />
                     </td>
                  </tr>
<?php
            $i++;
    }
    ?>
               </table>
               <p class="center">
                  <input type="hidden" name="numcomments" value="<?php echo $i?>" />
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php

}

function modifypost3()
{
    global $Settings, $userDetails, $language, $dbQueries, $db_prefix;

    $SQL_query = mysql_query('SELECT postername FROM ' . $db_prefix . 'news WHERE id = ' . $_POST['id'] . '');
    $dbQueries++;

    $posts = mysql_fetch_assoc($SQL_query);

    /* This prevents 'News Posters' from editing posts they didn't make */
    if ($userDetails['username'] != $posts['postername'] && $userDetails['access'] != 'admin' && $userDetails['access'] != 'moderator') {
        fatal_error($language['CONTENT_ERROREDITNEWS']);
    }

    $_POST['subject'] = trim($_POST['subject']);
    $_POST['subject'] = htmlspecialchars($_POST['subject']);

    /* Calls replace() function to edit the information */
    $_POST['titletext'] = replace($_POST['titletext'], $_POST['break']);
    $_POST['maintext'] = replace($_POST['maintext'], $_POST['break']);

    /* Make sure the post isn't left empty */
    if (!$_POST['subject'] || !$_POST['titletext']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* If no category ID is passed, set it as 0 */
    if (!$_POST['catid']) {
        $_POST['catid'] = 0;
    }

    //echo $_FILE['image1'];

    // Image Files - Json
    if($Settings['enableimgupload'] == 1) {
        for($i = 1; $i <= 3; $i++) {
            if(!empty($_FILES['image' . $i]['name'])) {
                // Check if we really got an image file
                if (is_int(exif_imagetype($_FILES['image' . $i]['tmp_name']))) {
                    $uploadfile = $Settings['imguploadpath'] . $_FILES['image' . $i]['name'];

                    if(move_uploaded_file($_FILES['image' . $i]['tmp_name'], $uploadfile)) {
                        // Check whether to insert image as BBCode or xHTML
                        if ($Settings['enablebbcode'] == 1) {
                            $_POST['titletext'] = str_replace('[image' . $i . ']', '[img]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '[/img]', $_POST['titletext']);
                            $_POST['maintext'] = str_replace('[image' . $i . ']', '[img]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '[/img]', $_POST['maintext']);
                        } else {
                            $_POST['titletext'] = str_replace('[image' . $i . ']', '<img src="' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '" alt="" style="border:none;" />', $_POST['titletext']);
                            $_POST['maintext'] = str_replace('[image' . $i . ']', '<img src="' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $_FILES['image' . $i]['name'] . '" alt="" style="border:none;" />', $_POST['maintext']);
                        }
                    }
                } else {
                    fatal_error($language['CONTENT_ERRORNOIMAGE']);
                }
            } else {
                // Remove the [image] tag if the image upload failed
                $_POST['titletext'] = str_replace('[image' . $i . ']', 'wtf', $_POST['titletext']);
                $_POST['maintext'] = str_replace('[image' . $i . ']', 'hmm', $_POST['maintext']);
            }
        }
    }

    /* What submit button was pressed? */
    if($_POST['post']) {
        /* Is this post Trusted? */
        if ($userDetails['access'] == 'newsposter') {
            $trusted = 0;
        } elseif ($_POST['trusted'] == 1) {
            $trusted = 1;
        }

        /* If post is being deleted, delete all the comments about it also */
        if($_POST['delete'] == 1) {
            $qs = 'DELETE FROM ' . $db_prefix . 'news WHERE id = ' . $_POST['id'] . '';

            $query = mysql_query('SELECT count(*) as total FROM ' . $db_prefix . 'comments WHERE mid = ' . $_POST['id'] . '');
            $dbQueries++;
            $var = mysql_fetch_assoc($query);

            if ($var['total'] > 0) {
                mysql_query('DELETE FROM ' . $db_prefix . 'comments WHERE mid = ' . $_POST['id'] . '');
                $dbQueries++;
            }

            echo "            {$language['CONTENT_INFOPOSTDELETESUCCESS']}<br />\n";
        }
        /* Update the trusted field for this Article */
        elseif (isset($trusted)) {
            $qs = 'UPDATE ' . $db_prefix . 'news SET subject=\'' . mysql_escape_string($_POST['subject']) . '\', titletext=\'' . mysql_escape_string($_POST['titletext']) . '\', maintext=\'' . mysql_escape_string($_POST['maintext']) . '\', break=\'' . $_POST['break'] . '\', catid=' . $_POST['catid'] . ', trusted=' . $trusted . ' WHERE id = ' . $_POST['id'] . '';
            echo "            {$language['CONTENT_INFOPOSTUPDATESUCCESS']}<br />\n";
        }
        /* Just update the Article as normal */
        else {
            $qs = 'UPDATE ' . $db_prefix . 'news SET subject=\'' . mysql_escape_string($_POST['subject']) . '\', titletext=\'' . mysql_escape_string($_POST['titletext']) . '\', maintext=\'' . mysql_escape_string($_POST['maintext']) . '\', break=\'' . $_POST['break'] . '\', catid=' . $_POST['catid'] . ' WHERE id = ' . $_POST['id'] . '';
            echo "            {$language['CONTENT_INFOPOSTUPDATESUCCESS']}<br />\n";
        }

        mysql_query($qs);
        $dbQueries++;

        echo "            <a href=\"index.php?action=modify\">{$language['CONTENT_BACK']}</a>\n";

        if ($Settings['enablerss'] == 1 && $Settings['manualrss'] == 0) {
            createRSSFeed();
        }
    } elseif($_POST['preview']) {
        ?>
            <form action="index.php?action=modifypost3" id="postmodify" method="post">
               <p style="display:none;">
                  <input id="id" name="id" type="hidden" value="<?php echo $_POST['id']?>" />
                  <input id="subject" name="subject" size="45" type="text"
                  value="<?php echo $_POST['subject']?>" />
                  <textarea cols="45" id="titletext" name="titletext"
                  rows="5"><?php echo str_replace('<br />', "\r\n", $_POST['titletext'])?></textarea>
                  <textarea cols="45" id="maintext" name="maintext"
                  rows="8"><?php echo str_replace('<br />', "\r\n", $_POST['maintext'])?></textarea>
                  <input id="catid" name="catid" type="text"
                  value="<?php echo $_POST['catid']?>" />
                  <input id="break" name="break" type="text"
                  value="<?php echo $_POST['break']?>" />
                  <input id="modify" name="modify" type="hidden" />
               </p>
<?php
            /* Asign post variables to variables used in template */
            $subject = $_POST['subject'];
        $time = strftime($Settings['timeformat'], $time);
        $titletext = trim($_POST['titletext']);

        /* Find out who made the post (keeps track of usernames) */
        $query = mysql_query('SELECT username,email,avatar FROM ' . $db_prefix . 'posters WHERE id = ' . $userDetails['id'] . ' OR username = \'' . $userDetails['username'] . '\'');
        $dbQueries++;

        $row = mysql_fetch_assoc($query);
        $username = $row['username'];

        /* Display link to show comments & news if enabled */
        if ($_POST['maintext'] != '') {
            $maintext = trim($_POST['maintext']);
        } else {
            $maintext = '';
        }

        /* If Categories are enabled... */
        if ($Settings['enablecats'] == 1) {
            $cat_query = mysql_query('SELECT * FROM ' . $db_prefix . 'categories WHERE id = ' . $_POST['catid'] . '');
            $dbQueries++;

            $cat = mysql_fetch_assoc($cat_query);

            if ($_POST['catid'] != 0) {
                if ($cat['catname'] != '') {
                    $category = '<a href="' . $_SERVER['PHP_SELF'] . '?action=showcat&amp;catid=' . $cat['id'] . '">' . $cat['catname'] . '</a>';
                }

                if ($cat['caticon'] != '') {
                    $caticon = '<img src="' . $cat['caticon'] . '" style="border:none;" alt="' . $cat['catname'] . '" />';
                }
            }
        }

        if ($row['email'] != '') {
            $username = '<a href="mailto:' . $row['email'] . '">' . $username . '</a>';
        } else {
            $username = $username;
        }

        /* Parse the code */
        $maintext = parseCode($maintext);
        $titletext = parseCode($titletext);

        include('templates/fullnews_temp.php');
        echo "\n";
        ?>
              <p class="center">
                 <input name="post" type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT']?>"
                 <?php echo $iebuttonfix?> />
                 <input onclick="document.forms['postmodify'].action = 'index.php?action=modifypost2&id=<?php echo $_POST['id'];?>'; document.forms['postmodify'].submit();"
                 type="button" value="<?php echo $language['MENU_MODIFY']?>" <?php echo $iebuttonfix?> />
              </p>
           </form>
<?php
    }
    checkForIE();
}

/******************************
* Comment Modifying Functions *
******************************/

function modifycomment()
{
    global $language, $dbQueries, $userDetails, $db_prefix, $iebuttonfix;

    $SQL_query = mysql_query('SELECT ip,name,message,email,website FROM ' . $db_prefix . 'comments WHERE id = ' . $_GET['id'] . '');
    $dbQueries++;

    /* Make sure a correct ID was passed */
    if (!$SQL_query) {
        fatal_error($language['CONTENT_ERRORREQUIREDVARIABLE']);
    }

    /* Find out name of Poster who created the News Post */
    $SQL_query2 = mysql_query('SELECT postername FROM ' . $db_prefix . 'news WHERE id = ' . $_GET['id'] . '');
    $dbQueries++;

    /* Place information in arrays */
    $comment = mysql_fetch_assoc($SQL_query);
    $user = mysql_fetch_assoc($SQL_query2);

    /* This prevents 'News Posters' from editing comments on posts they didn't make */
    if ($userDetails['username'] != $user['postername'] && $userDetails['access'] != 'admin' && $userDetails['access'] != 'moderator') {
        fatal_error($language['CONTENT_ERRORACCESSDENIED']);
    }

    /* Find out the Users Host */
    $host = gethostbyaddr($comment['ip']);
    ?>
            <h2>
               <?php echo $language['CONTENT_NEWSMODIFYCOMMENT'];?>:
            </h2>
            <form action="index.php?action=updatecomments" method="post">
               <p>
                  <input id="id" name="id" type="hidden" value="<?php echo $_GET['id']?>" />
                  <label for="name"><?php echo $language['CONTENT_NEWSMODIFYCOMMENTNAME'];?>:</label><br />
                  <input id="name" name="name" size="40" value="<?php echo $comment['name']?>" />
               </p>
               <p>
                  <label for="email"><?php echo $language['CONTENT_NEWSMODIFYCOMMENTEMAIL'];?>:</label><br />
                  <input id="email" name="email" size="40" value="<?php echo $comment['email']?>" />
               </p>
               <p>
                  <label for="website"><?php echo $language['CONTENT_NEWSMODIFYCOMMENTWEBSITE'];?>:</label><br />
                  <input id="website" name="website" size="40" value="<?php echo $comment['website']?>" />
               </p>
               <p>
                  <label for="message"><?php echo $language['CONTENT_NEWSMODIFYCOMMENTMESSAGE'];?>:</label><br />
                  <textarea cols="32" id="message" name="message"
                  rows="5"><?php echo $comment['message']?></textarea>
               </p>
               <table summary="">
                  <tr>
                     <td>
                        <?php echo $language['CONTENT_IPADDRESS']?>:
                     </td>
                     <td>
                        <a href="javascript:" onclick="window.open('http://ws.arin.net/cgi-bin/whois.pl?queryinput=<?php echo $comment['ip']?>')">
                        <?php echo $comment['ip']?></a>
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <?php echo $language['CONTENT_HOST']?>:
                     </td>
                     <td>
                        <?php echo $host,"\n";?>
                     </td>
                  </tr>
                  <tr>
                     <td colspan="2">
                        <a href="index.php?action=banning&amp;ip=<?php echo $comment['ip']?>"><?php echo $language['CONTENT_BANIPADDRESS']?></a>
                     </td>
                  </tr>
               </table>
               <p class="center">
                  <input type="hidden" name="numcomments" value="1" />
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
}

function updatecomments()
{
    global $ids, $delete, $language, $dbQueries, $db_prefix;

    /* Make sure a post ID is passed */
    if (isset($_POST['id'])) {
        if (!$_POST['id']) {
            fatal_error($language['CONTENT_ERRORREQUIREDVARIABLE']);
        }
    }
    /* Prevent HTML/Scripts */
    $_POST['name'] = htmlspecialchars($_POST['name']);
    $_POST['email'] = strip_tags($_POST['email']);
    $_POST['website'] = strip_tags($_POST['website']);
    $_POST['message'] = htmlspecialchars($_POST['message']);

    /* Assign arrays variables */
    $ids = $_POST['ids'];
    $delete = $_POST['delete'];

    $i = 0;

    /* Update/Delete the Comments */
    while ($i < $_POST['numcomments']) {
        //        eval("\$mid = \$ids[$i];");
        $mid = $ids[$i];
        //        eval("\$del = \$delete[$i];");
        $del = $delete[$i];

        if ($del == 1) {
            $qs = 'DELETE FROM ' . $db_prefix . 'comments WHERE id = ' . $mid . '';
        } else {
            $qs = 'UPDATE ' . $db_prefix . 'comments SET name=\'' . $_POST['name'] . '\', email=\'' . $_POST['email'] . '\', website=\'' . $_POST['website'] . '\', message=\'' . $_POST['message'] . '\' WHERE id = ' . $_POST['id'] . '';
        }

        mysql_query($qs);
        $dbQueries++;
        $i++;
    }

    echo "            {$language['CONTENT_INFOCOMMENTSUPDATESUCCESS']}<br />\n";
    echo "            <a href=\"index.php?action=modify\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/***********************
* IP Banning Functions *
***********************/

function banning()
{
    is_admin();
    global $language, $dbQueries, $db_prefix, $iebuttonfix;
    ?>
            <h2>
               <?php echo $language['CONTENT_BANNINGTITLE']?>:
            </h2>
            <p>
               <?php echo $language['CONTENT_BANNEDINFO'],"\n";?>
            </p>
            <form action="index.php?action=addbannedip" method="post">
               <p class="center">
                  <label for="subject"><?php echo $language['CONTENT_IPADDRESS']?>:</label>
                  <input id="ip" name="ip" value="<?php echo $_GET['ip'];?>" size="15" type="text" />
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONBANIP']?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
            <hr />
            <h2>
               <?php echo $language['CONTENT_BANNEDTITLE']?>:
            </h2>
            <form action="index.php?action=modbanned" method="post">
<?php
      $query = mysql_query('SELECT * FROM ' . $db_prefix . 'banned WHERE isbanned = 1 ORDER by id');
    $dbQueries++;
    $i = 0;

    while($banned = mysql_fetch_assoc($query)) {
        ?>
               <table class="tablecenter" style="border-top:#000000 solid 1px;" summary="">
                  <tr>
                     <td>
                        <label for="ip[<?php echo $i?>]"><?php echo $language['CONTENT_IPADDRESS']?></label>
                     </td>
                     <td>
                       <a href="javascript:" onclick="window.open('http://www.nic.com/cgi-bin/whois.cgi?query=<?php echo $banned['ip'];?>')"><?php echo $banned['ip'];?></a>
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <label for="timesbanned[<?php echo $i?>]"><?php echo $language['CONTENT_BANNEDTIMESBANNED']?></label>
                     </td>
                     <td>
                       <strong><?php echo $banned['timesbanned'];?></strong>
                     </td>
                  </tr>
                  <tr>
                     <td>
                        <label for="unblock[<?php echo $i?>]"><?php echo $language['CONTENT_BANNEDUNBLOCK']?></label>
                     </td>
                     <td>
                        <input type="checkbox" name="unblock[<?php echo $i?>]" value="1" />
                        <input type="hidden" name="id[<?php echo $i?>]" value="<?php echo $banned['id'];?>" />
                     </td>
                  </tr>
               </table>
<?php
            $i++;
    }
    ?>
               <p class="center">
                 <input type="hidden" name="numips" value="<?php echo $i?>" />
                 <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                 <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
      if (!$i && stristr($_SERVER['HTTP_USER_AGENT'], 'MSIE')) {
          ?>
            <div style="height:100px;">
               &nbsp;
            </div>
<?php
      }
}

function addbannedip()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;

    $_POST['ip'] = trim($_POST['ip']);

    if (!$_POST['ip']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* Check if IP has already been added */
    $result = mysql_query('SELECT ip,timesbanned,isbanned FROM ' . $db_prefix . 'banned WHERE ip = \'' . $_POST['ip'] . '\'');
    $dbQueries++;

    if (mysql_numrows($result) != 0) {
        $ipinfo = mysql_fetch_assoc($result);

        if ($ipinfo['isbanned'] != 1) {
            $ipinfo['timesbanned']++;

            $bo = mysql_query('UPDATE ' . $db_prefix . 'banned SET timesbanned=\'' . $ipinfo['timesbanned'] . '\', isbanned=1 WHERE ip = \'' . $ipinfo['ip'] . '\'');
            $dbQueries++;
        } else {
            fatal_error($language['CONTENT_IPEXISTS']);
        }
    } else {
        mysql_query('INSERT INTO ' . $db_prefix . 'banned (ip,timesbanned,isbanned) VALUES (\'' . $_POST['ip'] . '\',1,1)');
        $dbQueries++;
    }

    echo "            {$language['CONTENT_ADDEDIPSUCCESS']}<br />\n";
    echo "            <a href=\"index.php?action=banning\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

function modbanned()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;

    /* Assign arrays variables */
    $unblock = $_POST['unblock'];
    $id = $_POST['id'];
    $i = 0;

    /* Update/Delete the Categories */
    while ($i < $_POST['numips']) {
        //        eval("\$remove = \$unblock[$i];");
        $remove = $unblock[$i];
        //        eval("\$bid = \$id[$i];");
        $bid = $id[$i];

        if ($remove == 1) {
            mysql_query('UPDATE ' . $db_prefix . 'banned SET isbanned=0 WHERE id = ' . $bid . '');
            $dbQueries++;
        }
        $i++;
    }

    echo "            {$language['CONTENT_INFOBANNEDUPDATESUCCESS']}<br />\n";
    echo "            <a href=\"index.php?action=banning\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/********************************
* Modify News Posters Functions *
********************************/

function modifynewsposter()
{
    is_admin();
    global $language, $dbQueries, $db_prefix;
    ?>
            <p>
               <?php echo $language['CONTENT_POSTERMODIFYINFO'],"\n";?>
            </p>
            <table class="tablecenter">
               <tr>
                  <th>
                     <?php echo $language['CONTENT_POSTERMODIFYPOSTER'],"\n";?>
                  </th>
                  <th>
                     <?php echo $language['CONTENT_POSTERMODIFYACCESS'],"\n";?>
                  </th>
               </tr>
               <tr>
<?php
      $SQL_query = mysql_query('SELECT username,id,access FROM ' . $db_prefix . 'posters ORDER by id ASC');
    $dbQueries++;

    while ($posts = mysql_fetch_assoc($SQL_query)) {
        /* Define Access */
        if ($posts['access'] == 'admin') {
            $posts['access'] = $language['CONTENT_ADMIN'];
        } elseif ($posts['access'] == 'moderator') {
            $posts['access'] = $language['CONTENT_MODERATOR'];
        } elseif ($posts['access'] == 'trusted') {
            $posts['access'] = $language['CONTENT_TRUSTED'];
        } else {
            $posts['access'] = $language['CONTENT_NEWSPOSTER'];
        }

        $poster .= "                     <a href=\"index.php?action=modifynewsposter2&amp;id={$posts['id']}\">{$posts['username']}</a><br />\n";
        $access .= "                     {$posts['access']}<br />\n";
    }
    ?>
                  <td>
<?php echo $poster;?>
                  </td>
                  <td>
<?php echo $access;?>
                  </td>
               </tr>
            </table>
<?php
      checkForIE();
}

function modifynewsposter2()
{
    global $userDetails, $Settings, $language, $dbQueries, $db_prefix, $iebuttonfix;

    /* If you're an Administrator, you can modify everyones profile, otherwise only yourself */
    if ($_GET['id'] != $userDetails['id'] && $userDetails['access'] != 'admin') {
        fatal_error($language['CONTENT_ERROREDITUSER']);
    }

    if (!$_GET['id']) {
        fatal_error($language['CONTENT_ERRORREQUREDVARIABLE']);
    }

    $SQL_query = mysql_query('SELECT id,username,email,avatar,language,access FROM ' . $db_prefix . 'posters WHERE id = ' . $_GET['id'] . '');
    $dbQueries++;

    $users = mysql_fetch_assoc($SQL_query);

    /* Ticket Users Access */
    if ($users['access'] == 'admin') {
        $admin = 'selected="selected"';
    } elseif ($users['access'] == 'moderator') {
        $moderator = 'selected="selected"';
    } elseif ($users['access'] == 'trusted') {
        $trusted = 'selected="selected"';
    } elseif ($users['access'] == 'newsposter') {
        $newsposter = 'selected="selected"';
    }
    ?>
            <h2>
               <?php echo $language['CONTENT_POSTERMODIFYPROFILE'];?>:
            </h2>
            <form action="index.php?action=modifynewsposter3" method="post">
               <p>
                  <input id="id" name="id" type="hidden" value="<?php echo $_GET['id']?>" />
                  <label for="newusername"><?php echo $language['CONTENT_POSTERUSERNAME'];?>:</label><br />
                  <input id="newusername" name="newusername" type="text" value="<?php echo $users['username']?>" />
                  <input name="username" type="hidden" value="<?php echo $users['username']?>" />
               </p>
               <p>
                  <label for="password"><?php echo $language['CONTENT_POSTERCHANGEPASSWORD'];?>:</label><br />
                  <input id="password" name="password" type="password" />
               </p>
               <p>
                  <label for="password2"><?php echo $language['CONTENT_POSTERCONFIRMPASSWORD'];?>:</label><br />
                  <input id="password2" name="password2" type="password" />
               </p>
               <p>
                  <label for="email"><?php echo $language['CONTENT_POSTEREMAIL'];?>:</label><br />
                  <input id="email" name="email" type="text" value="<?php echo $users['email']?>" />
               </p>
<?php
if ($Settings['enableavatars'] == 1) {
    ?>
               <p>
                  <label for="avatar"><?php echo $language['CONTENT_POSTERAVATAR'];?>:</label><br />
                  <input id="avatar" name="avatar" type="text" value="<?php echo $users['avatar']?>" />
               </p>
<?php
}
    ?>
               <p>
                  <label for="language"><?php echo $language['CONTENT_SETTINGSLANGUAGE'];?>:</label><br />
                  <select id="language" name="language">
<?php
        /* Look for all .lng files and make em selectable in the settings screen */
        $dir = opendir('languages/');

    $i = 0;
    while (false !== ($file = readdir($dir))) {
        if(substr($file, 5) == '.admin.lng') {
            include('languages/' . $file);

            if($users['language'] == substr($file, 0, 5)) {
                ?>
                     <option value="<?php echo substr($file, 0, 5);?>" selected="selected">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
            } else {
                ?>
                     <option value="<?php echo substr($file, 0, 5);?>">
                        <?php echo $lng['LANGUAGE'],"\n";?>
                     </option>
<?php
            }
        }
    }

    closedir($dir);
    ?>
                  </select>
               </p>
<?php
    /* If this is the first Admin, you can't delete 'em */
    if ($userDetails['access'] == 'admin' && $users['id'] == 1) {
        ?>
               <p>
                  <label for="access"><?php echo $language['CONTENT_POSTERUSERACCESS'];?>:</label><br />
                  <b><?php echo $language['CONTENT_ADMIN'],"\n";?></b>
                  <input name="access" type="hidden" value="<?php echo $users['access']?>" />
               </p>
<?php
    }
    /* If they're a normal Admin, their access can be changed and they can be removed */
    elseif ($userDetails['access'] == 'admin') {
        ?>
               <p>
                  <label for="access"><?php echo $language['CONTENT_POSTERUSERACCESS'];?>:</label><br />
                  <select id="access" name="access">
                     <option value="newsposter" <?php echo $newsposter?>>
                        <?php echo $language['CONTENT_NEWSPOSTER'],"\n";?>
                     </option>
                     <option value="trusted" <?php echo $trusted?>>
                        <?php echo $language['CONTENT_TRUSTED'],"\n";?>
                     </option>
                     <option value="moderator" <?php echo $moderator?>>
                        <?php echo $language['CONTENT_MODERATOR'],"\n";?>
                     </option>
                     <option value="admin" <?php echo $admin?>>
                        <?php echo $language['CONTENT_ADMIN'],"\n";?>
                     </option>
                  </select>
               </p>
               <p>
                  <input type="checkbox" name="delete" value="1" />
                  <?php echo $language['CONTENT_POSTERREMOVE'],"\n";?>
               </p>
<?php
    }
    ?>
               <p class="center">
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONSUBMIT'];?>" <?php echo $iebuttonfix?> />
                  <input type="reset" value="<?php echo $language['CONTENT_BUTTONRESET'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
<?php
}

function modifynewsposter3()
{
    global $userDetails, $language, $dbQueries, $db_prefix, $Settings;

    if ($_POST['id'] != $userDetails['id'] && $userDetails['access'] != 'admin') {
        fatal_error($language['CONTENT_ERROREDITUSER']);
    }

    /* Trim the fat so to speak */
    $_POST['newusername'] = trim($_POST['newusername']);
    $_POST['newusername'] = htmlspecialchars($_POST['newusername']);
    $_POST['email'] = trim($_POST['email']);
    $_POST['email'] = strip_tags($_POST['email']);
    $_POST['avatar'] = trim($_POST['avatar']);
    $_POST['avatar'] = strip_tags($_POST['avatar']);
    $_POST['password'] = trim($_POST['password']);
    $_POST['password2'] = trim($_POST['password2']);

    /* Check email is valid, if it is entered */
    if ($_POST['email'] != '' && $Settings['enablevalidation'] == 1) {
        if (!eregi('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,3})$', $_POST['email'])) {
            fatal_error($language['CONTENT_ERROREMAIL']);
        }
    }

    /* Check required fields were entered correctly */
    if(!$_POST['newusername']) {
        fatal_error($language['CONTENT_ERRORREQUIREDFIELD']);
    }

    /* Make sure passwords are the same */
    if($_POST['password'] != $_POST['password2']) {
        fatal_error($language['CONTENT_ERRORPASSWORD']);
    }

    /* If username is changed, check it isn't already in use */
    if ($_POST['newusername'] != $_POST['username']) {
        $result = mysql_query('SELECT username FROM ' . $db_prefix . 'posters WHERE username = \'' . $_POST['newusername'] . '\'');
        $dbQueries++;

        if (mysql_numrows($result) != 0) {
            fatal_error($language['CONTENT_ERRORUSERNAME']);
        }

        mysql_query('UPDATE ' . $db_prefix . 'news SET postername = \'' . $_POST['newusername'] . '\' WHERE postername = \'' . $_POST['username'] . '\'');
        $dbQueries++;
    }

    if ($_POST['delete'] == 1) {
        $qs = 'DELETE FROM ' . $db_prefix . 'posters WHERE id = ' . $_POST['id'] . '';
        echo "            {$language['CONTENT_INFOPOSTERDELETESUCCESS']}<br />\n";
    } elseif ($_POST['password']) {
        $qs = 'UPDATE ' . $db_prefix . 'posters SET username=\'' . $_POST['newusername'] . '\', password=password(\'' . $_POST['password'] . '\'), email=\'' . $_POST['email'] . '\', avatar=\'' . $_POST['avatar'] . '\', language=\'' . $_POST['language'] . '\', access=\'' . $_POST['access'] . '\' WHERE id = ' . $_POST['id'] . '';
        echo "            {$language['CONTENT_INFOPOSTERUPDATESUCCESS']}<br />\n";

        $load = 1;
    } elseif ($userDetails['access'] == 'admin') {
        $qs = 'UPDATE ' . $db_prefix . 'posters SET username=\'' . $_POST['newusername'] . '\', email=\'' . $_POST['email'] . '\', avatar=\'' . $_POST['avatar'] . '\', language=\'' . $_POST['language'] . '\', access=\'' . $_POST['access'] . '\' WHERE id = ' . $_POST['id'] . '';
        echo "            {$language['CONTENT_INFOPOSTERUPDATESUCCESS']}<br />\n";

        $load = 2;
    } else {
        $qs = 'UPDATE ' . $db_prefix . 'posters SET username=\'' . $_POST['newusername'] . '\', email=\'' . $_POST['email'] . '\', avatar=\'' . $_POST['avatar'] . '\', language=\'' . $_POST['language'] . '\' WHERE id = ' . $_POST['id'] . '';
        echo "            {$language['CONTENT_INFOPOSTERUPDATESUCCESS']}<br />\n";

        $load = 2;
    }

    /* If you change your username and/or password update $_SESSION so you don't get logged out */
    if ($load == 1 && $_POST['username'] == $userDetails['username']) {
        $_SESSION['user'] = $_POST['newusername'];
        $_SESSION['password'] = $_POST['password'];
    } elseif ($load == 2 && $_POST['username'] == $userDetails['username']) {
        $_SESSION['user'] = $_POST['newusername'];
    }

    mysql_query($qs);
    $dbQueries++;

    echo "            <a href=\"index.php\">{$language['CONTENT_BACK']}</a>\n";

    checkForIE();
}

/*******************
* Version checking *
*******************/

function getVersion($file)
{
    global $language;

    /* Don't present the normal PHP errors to the user. */
    error_reporting(E_NOTICE);

    /* Create the XML parser with ISO-8859-1 encoding */
    $parser = xml_parser_create('iso-8859-1');

    if (!$handler = fopen($file, 'r')) {
        fatal_error($language['CONTENT_ERROROPENXMLFILE']);
    }

    while ($data = fread($handler, 4096)) {
        /* parses the data into array $values */
        if (!xml_parse_into_struct($parser, $data, $values)) {
            fatal_error($language['CONTENT_ERRORPARSEXMLFILE']);
        }
    }

    /* Get the version from the version attribute */
    $version = $values[0]['attributes']['VERSION'];

    fclose($handler);
    return $version;
}

function checkVersion()
{
    is_admin();
    global $language;

    $localVersion = getVersion('phpnews.xml');
    $remoteVersion = getVersion('http://newsphp.sourceforge.net/phpnews.xml');

    /* Tell the user whether they should upgrade or not */
    if ($remoteVersion > $localVersion) {
        ?>
            <p>
               <?php echo $language['CONTENT_NEWVERSIONAVAILABLE'],"\n";?>
            </p>
            <table class="tablecenter" summary="">
               <tr>
                  <th>
                     <?php echo $language['CONTENT_YOURPC'],"\n";?>
                  </th>
                  <th>
                     <?php echo $language['CONTENT_PHPNEWSSERVER'],"\n";?>
                  </th>
                  <th>
                     &nbsp;
                  </th>
               </tr>
               <tr>
                  <td class="center">
                     <?php echo $localVersion;?>
                  </td>
                  <td class="center">
                     <?php echo $remoteVersion;?>
                  </td>
                  <td>
                     <a href="http://newsphp.sourceforge.net/downloads.php">
                     <?php echo $language['CONTENT_BUTTONDOWNLOAD'];?></a>
                  </td>
               </tr>
            </table>
            <p>
<?php
            /* Open the changelog and prints error, if it can't be openend. */
            if (!$handler = fopen('http://newsphp.sourceforge.net/changelog/changelog_'.$remoteVersion.'.txt', 'r')) {
                fatal_error($language['CONTENT_ERROROPENCHANGELOG']);
            }

            /* Read the data stringwise and prints it on the screen. */
            while (!feof($handler)) {
                $buffer = fgets($handler);
                echo nl2br($buffer);
            }
            fclose($handler);
        ?>

            </p>
<?php
    } elseif ($remoteVersion == $localVersion) {
        ?>
            <p>
               <?php echo $language['CONTENT_CURRENTVERSION'],"\n";?><br />
               <a href="index.php?action=advanced"><?php echo $language['CONTENT_BACK'];?></a>
            </p>
<?php
    } elseif ($remoteVersion < $localVersion) {
        ?>
            <p>
               <?php echo $language['CONTENT_BETAVERSION'],"\n";?><br />
               <a href="index.php?action=advanced"><?php echo $language['CONTENT_BACK'];?></a>
            </p>
<?php
    }
    checkForIE();

    /* Switch back to default error reporting */
    error_reporting(E_ALL ^ E_NOTICE);
}

/********************
* RSS Feed Creation *
********************/

function createRSSFeed()
{
    //is_admin();
    global $Settings, $language, $dbQueries, $db_prefix;

    $filename = strtolower(str_replace(' ', '', $Settings['sitename'])) . '.rss';

    if (file_exists($filename)) {
        @unlink($filename);
    }

    $handler = fopen($filename, 'w+');

    // Creates the header for the RSS file
    $rssfile = "<?xml version=\"1.0\" encoding=\"".$language['CHARSET']."\"?>
<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\"
  xmlns=\"http://purl.org/rss/1.0/\">
   <channel rdf:about=\"".$Settings['siteurl']."\">
      <title>".$Settings['sitename']."</title>
      <link>".$Settings['phpnewsurl'] . $filename ."</link>
      <description>
         This RSS feed was generated out of the newsdatabase of
         ".$Settings['sitename']." website.
      </description>
      <items>
         <rdf:Seq>\n";

    /* Get information about the News Post */
    $SQL_query = mysql_query('SELECT n.id,n.posterid,n.postername,n.time,n.subject,n.titletext,n.maintext,p.username,p.email,p.avatar'
                             . ' FROM ' . $db_prefix . 'news AS n'
                             . ' LEFT JOIN ' . $db_prefix . 'posters AS p ON(n.posterid=p.id)'
                             . ' AND n.trusted = 1'
                             . ' ORDER by n.id DESC');
    $dbQueries++;

    while($news = mysql_fetch_assoc($SQL_query)) {
        /* Set Variables */
        $time = strftime($Settings['timeformat'], $news['time']);
        $subject = $news['subject'];
        $titletext = $news['titletext'];
        $username = $news['username'];

        if (!$username) {
            $username = $news['postername'];
        }
        /* Display link to show comments & news if enabled */
        if ($news['maintext'] != '' && $Settings['showcominnews'] == 1 && $Settings['enablecomments'] == 1) {
            $maintext = $Settings['siteurl'] . '?action=fullnews&amp;showcomments=1&amp;id=' . $news['id'] . '';
        } elseif ($news['maintext'] != '') {
            $maintext = $Settings['siteurl'] . '?action=fullnews&amp;id=' . $news['id'] . '';
        } else {
            $maintext = $Settings['siteurl'];
        }

        // Strip tags and BBcode
        $titletext = strip_tags($titletext);
        $titletext = preg_replace('/\[(.+?)\](.+?)\[\/(.+?)\]/is', '\\2', $titletext);

        // Creates table of contents
        $rssfile .= "            <rdf:li resource=\"".$maintext."\" />\n";

        // Creates the <item> construct for every news item
        $items .= "   <item rdf:about=\"".$maintext."\">
      <title>".str_replace('&quot;', '"', $subject) ."</title>
      <link>".$maintext."</link>
      <description>
         ".$titletext."
      </description>
   </item>\n";
    }

    // Closes table of contents
    $rssfile .= "         </rdf:Seq>
      </items>
   </channel>\n";

    // Adds the news items to the string
    $rssfile .= $items;

    // Creates the footer of the RSS file
    $rssfile .= "</rdf:RDF>\n";

    // Puts the string $rssfile in RSS file
    if(!fputs($handler, $rssfile)) {
        fatal_error($language['CONTENT_ERRORWRITETORSSFEED']);
    }

    fclose($handler);

    // Only present this link, if parameter is createRSSFeed
    if ($_GET['action'] == 'createRSSFeed') {
        ?>
            <p>
               <?php echo $language['CONTENT_RSSFEEDCREATED'],"\n";?><br />
               <a href="index.php?action=advanced"><?php echo $language['CONTENT_BACK'];?></a>
            </p>
<?php
    }
    checkForIE();
}

/*************************
* Image Upload Functions *
*************************/

function images()
{
    is_admin();
    global $Settings, $language, $dbQueries, $db_prefix, $iebuttonfix;

    if(is_dir($Settings['imguploadpath'])) {
        /* Look for all .lng files and make em selectable in the settings screen */
        $dir = opendir($Settings['imguploadpath']);

        $i = 0;
        while(false !== ($file = readdir($dir))) {
            if((substr($file, sizeof($file)-5) == '.jpg') || (substr($file, sizeof($file)-5) == '.gif') || (substr($file, sizeof($file)-5) == '.png')) {
                $files .= '<a href="' . $Settings['imguploadpath'] . $file . '" onclick="window.open(this.href,\'_blank\');return false;">' . $file . '</a> [<a href="index.php?action=imagesdelete&image=' . $file . '">' . $language['CONTENT_IMGDELETE'] . '</a>]<br />';
            }
        }

        closedir($dir);
    }
    ?>
            <h2>
               <?php echo $language['CONTENT_IMGUPLOAD'],"\n"?>
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_IMGUPLOADINFO'],"\n";?>
            </p>
            <form enctype="multipart/form-data" action="index.php?action=uploadimages" method="post">
               <table class="tablecenter" summary="">
<?php
        for($i = 1; $i <= $Settings['uploadfiles']; $i++) {
            ?>
                  <tr>
                     <td>
                        <label for="image<?php echo $i?>"><?php echo $language['CONTENT_IMAGE'];?> <?php echo $i?></label>
                     </td>
                     <td>
                        <input id="image<?php echo $i?>" name="image<?php echo $i?>" type="file" size="30" />
                     </td>
                  </tr>
<?php
        }
    ?>
               </table>
               <p class="center">
                  <input type="submit" value="<?php echo $language['CONTENT_BUTTONUPLOADIMAGE'];?>" <?php echo $iebuttonfix?> />
               </p>
            </form>
            <hr />
            <h2>
               <?php echo $language['CONTENT_IMGMANAGE'],"\n"?>
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_IMGMANAGEINFO'],"\n";?>
            </p>
            <?php echo $files?>
<?php
}

function imagesdelete()
{
    global $Settings, $language;

    if($_REQUEST['confirm'] == '1') {
        @unlink($Settings['imguploadpath'] . $_REQUEST['image']);

        ?>
            <h2>
               <?php echo $language['CONTENT_IMGDELETEIMAGE'],"\n"?>
            </h2>
            <p class="subtext">
               <?php echo $_REQUEST['image']?> <?php echo $language['CONTENT_IMGDELETED'],"\n";?><br />
               <br />
               <a href="index.php?action=images"><?php echo $language['CONTENT_BACK']?></a>
            </p>
<?php
                checkForIE();
    } else {
        ?>
            <h2>
               <?php echo $language['CONTENT_IMGDELETEIMAGE'],"\n"?>
            </h2>
            <p class="subtext">
               <?php echo $language['CONTENT_IMGDELETEQUESTION'],"\n";?> <span style="color:red"><?php echo $_REQUEST['image'];?></span>?<br />
               <br />
               <a href="index.php?action=imagesdelete&image=<?php echo $_REQUEST['image']?>&confirm=1"><?php echo $language['CONTENT_YES']?></a> | <a href="index.php?action=images"><?php echo $language['CONTENT_NO']?></a>
            </p>
<?php
                checkForIE();
    }
}

function uploadimages()
{
    is_admin();
    global $Settings, $language;

    for($i = 1; $i <= $Settings['uploadfiles']; $i++) {
        if(isset($_FILES['image' . $i])) {
            $uploadfile = $Settings['imguploadpath'] . $_FILES['image' . $i]['name'];

            if(move_uploaded_file($_FILES['image' . $i]['tmp_name'], $uploadfile)) {
                $uploaded .= $_FILES['image' . $i]['name'] . '<br />';
            }
        }
    }
    ?>
            <p>
               <?php echo $language['CONTENT_IMGUPLOADED'],"\n";?><br />
               <?php echo $uploaded?><br />
               <a href="index.php?action=images"><?php echo $language['CONTENT_BACK'];?></a>
            </p>
<?php
        checkForIE();
}

/******************
* Other Functions *
******************/

/* Formats the template for Modification */
function formatTemplate($template)
{
    $fcontents = file('templates/' . $template);
    $result = count($fcontents);

    /* Remove first 2 and last 2 lines from the templates */
    unset($fcontents[0]);
    unset($fcontents[1]);
    unset($fcontents[($result - 1)]);
    unset($fcontents[($result - 2)]);

    /* Put the code into the $fulltemplate variable */
    while (list($line_num, $line) = each($fcontents)) {
        $fulltemplate .= htmlspecialchars($line);
    }

    $template = $fulltemplate;
    return $template;
}

/* Displays error, and kills program */
function fatal_error($error)
{
    global $language;

    echo '<b>' , $language['CONTENT_ERROR'] , '</b>: ' , $error , '<br /><a href="javascript:history.go(-1)">' , $language['CONTENT_BACK'] , '</a>';

    checkForIE();
    exit;
}

function logout()
{
    global $language;

    /* End the Session */
    session_unset();
    session_destroy();
    ?>
            <p>
               <?php echo $language['CONTENT_LOGOUTINFO'],"\n";?>
            </p>
<?php
      checkForIE();
}

/* Quick Fix for IE browsers */
function checkForIE()
{
    if (stristr($_SERVER['HTTP_USER_AGENT'], 'MSIE')) {
        ?>
            <div style="height:300px;">
               &nbsp;
            </div>
<?php
    }
}

/* Common actions used when posting/modifying a News Post */
function replace($what, $replace)
{
    global $Settings, $language;

    /* Trim whitespace at Beginning and End of post */
    $what = trim($what);
    $what = stripslashes($what);

    if ($Settings['enablebbcode'] == 1) {
        /* Convert HTML Special Chars */
        $what = htmlspecialchars($what, ENT_COMPAT, $language['CHARSET']);
    } else {
        /* If an image was inserted and bbcode is off convert bbcode to HTML for the images */
        $replacewhat = array(
                            '/\[uimg\](.+?)\[\/uimg\]/i',
                            '/\[uimg width=([0-9]+) height=([0-9]+)\s*\](.+?)\[\/uimg\]/i',
                            '/\[uimg width=([0-9]+)\s*\](.+?)\[\/uimg\]/i',
                            '/\[uimg height=([0-9]+) width=([0-9]+)\s*\](.+?)\[\/uimg\]/i',
                            '/\[uimg height=([0-9]+)\s*\](.+?)\[\/uimg\]/i',
                            '/<script.+?<\\/script>/i',
                            );

        $replacewith = array(
                            '<img src="\\1" alt="" />',
                            '<img src="\\3" alt="" width="\\1" height="\\2" />',
                            '<img src="\\2" alt="" width="\\1" />',
                            '<img src="\\3" alt="" width="\\2" height="\\1" />',
                            '<img src="\\2" alt="" height="\\1" />',
                            );

        $what = preg_replace($replacewhat, $replacewith, $what);

        // Convert these entities
        $what = str_replace('&', '&amp;', $what);
    }

    if($replace == 1) {
        $what = str_replace("\r\n", '<br />', $what);
    }

    if ($replace == 2) {
        $what = str_replace('&lt;br /&gt;', "\r\n", $what);
    }

    return $what;
}

/* Parses Code - Used for the Preview */
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
                $smileytocache[] = '<img src="' . $Settings['phpnewsurl'] . 'images/smilies/' . $smiliesto[$i] . '.gif" alt="' . $smiliesto[$i] . '" />';
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


/* Converts entities in the given string back to their character */
function un_htmlentities($string)
{
    /* Get the translation table */
    $ttable = get_html_translation_table(HTML_SPECIALCHARS);

    /* Change the translation table to char <> entity */
    $ttable = array_flip($ttable);

    /* Convert all entities to ther character */
    $decstring = strtr($string, $ttable);

    return $decstring;
}

/* Find out the page creation time */
$time_end = getMicrotime();

$micro = round($time_end - $time_start, 4);
$time = '[ Script Execution time: ' . $micro . ' ]';
?>

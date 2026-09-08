<?php
/*********************************************
* ------------                               *
* | Help.php |                               *
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

include('auth.php');

echo '<?xml version="1.0" encoding="' , $language['CHARSET'] , '"?>' , "\n";
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
      <title>
         <?php echo $language['CONTENT_HELP'],"\n"?>
      </title>
      <link href="phpnews_package.css" rel="stylesheet" type="text/css" />
      <script type="text/javascript">
      <!--
        function inserttext(text,area)
        {
            if(area=="title") {
                opener.document.getElementById('titletext').value += text;
            }

            if(area=="main") {
                opener.document.getElementById('maintext').value += text;
            }
        }
      // -->
      </script>
   </head>
   <body class="jswindow">
      <form action="#">
<?php

/* Determine Help to show */
if ($_GET['action'] == 'temphelp') {
    temphelp();
} elseif ($_GET['action'] == 'headlineshelp') {
    headlineshelp();
} elseif ($_GET['action'] == 'comtemphelp') {
    comtemphelp();
} elseif ($_GET['action'] == 'categoryhelp') {
    categoryhelp();
} elseif ($_GET['action'] == 'posthelp') {
    posthelp();
} elseif ($_GET['action'] == 'posterhelp') {
    posterhelp();
} elseif ($_GET['action'] == 'settingshelp') {
    settingshelp();
} elseif ($_GET['action'] == 'uploadedimages') {
    uploadedimages();
}


function temphelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPNEWSTEMPLATE'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPNEWSTEMPLATEINFO']?>:
            </p>
            <p>
               <?php echo $language['CONTENT_HELPNEWSTEMPLATEHELP'],"\n"?>
            </p>
         </fieldset>
<?php
}

function headlineshelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPHEADLINESTEMPLATE'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPHEADLINESTEMPLATEINFO']?>:
            </p>
            <p>
               <?php echo $language['CONTENT_HELPHEADLINESTEMPLATEHELP'],"\n"?>
            </p>
         </fieldset>
<?php
}

function comtemphelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPCOMMENTSTEMPLATE'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPCOMMENTSTEMPLATEINFO']?>:
            </p>
            <p>
               <?php echo $language['CONTENT_HELPCOMMENTSTEMPLATEHELP'],"\n"?>
            </p>
         </fieldset>
<?php
}

function categoryhelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPCATEGORIES'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPCATEGORIESINFO'],"\n"?>
            </p>
         </fieldset>
<?php
}

function posthelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPPOSTNEWS'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPPOSTNEWSINFO']?>:
            </p>
            <p>
               <?php echo $language['CONTENT_HELPPOSTNEWSHELP'],"\n"?>
            </p>
         </fieldset>
<?php
}

function posterhelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPNEWSPOSTER'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPNEWSPOSTERINFO']?>:
            </p>
            <p>
               <?php echo $language['CONTENT_HELPNEWSPOSTERHELP'],"\n"?>
            </p>
         </fieldset>
<?php
}

function settingshelp()
{
    global $language;
    ?>
         <fieldset>
            <legend>
               <?php echo $language['CONTENT_HELP']?>: <?php echo $language['CONTENT_HELPSETTINGS'],"\n"?>
            </legend>
            <p>
               <?php echo $language['CONTENT_HELPSETTINGSINFO']?>:
            </p>
            <p>
               <?php echo $language['CONTENT_HELPSETTINGSHELP'],"\n"?>
            </p>
         </fieldset>
<?php
}

function uploadedimages()
{
    global $language, $Settings;

    if(is_dir($Settings['imguploadpath'])) {
        $dir = opendir($Settings['imguploadpath']);

        $i = 0;
        while(false !== ($file = readdir($dir))) {
            if((substr($file, sizeof($file)-5) == '.jpg') || (substr($file, sizeof($file)-5) == '.gif') || (substr($file, sizeof($file)-5) == '.png')) {
                if ($Settings['enablebbcode'] == 1) {
                    $files .= '<a href="' . $Settings['imguploadpath'] . $file . '" onclick="window.open(this.href,\'_blank\');return false;">' . $file . '</a> [<a href="javascript:inserttext(\'[img]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $file . '[/img]\',\'title\')" title="' . $language['CONTENT_NEWSTITLE'] . '">'. substr($language['CONTENT_NEWSTITLE'], 0, 1) . '</a>][<a href="javascript:inserttext(\'[img]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $file . '[/img]\',\'main\')" title="' . $language['CONTENT_NEWSBODY'] . '">'. substr($language['CONTENT_NEWSBODY'], 0, 1) . '</a>]<br />';
                } else {
                    $files .= '<a href="' . $Settings['imguploadpath'] . $file . '" onclick="window.open(this.href,\'_blank\');return false;">' . $file . '</a> [<a href="javascript:inserttext(\'[uimg]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $file . '[/uimg]\',\'title\')" title="' . $language['CONTENT_NEWSTITLE'] . '">' . substr($language['CONTENT_NEWSTITLE'], 0, 1). '</a>][<a href="javascript:inserttext(\'[uimg]' . $Settings['phpnewsurl'] . $Settings['imguploadpath'] . $file . '[/uimg]\',\'main\')" title="' . $language['CONTENT_NEWSBODY'] . '">'. substr($language['CONTENT_NEWSBODY'], 0, 1) . '</a>]<br />';
                }
            }
        }

        closedir($dir);
    }
    ?>
    <fieldset>
        <legend>
            <?php echo $language['CONTENT_IMGUPLOADEDIMAGES'],"\n"?>
        </legend>
        <p>
                <?php echo $files?>
        </p>
    </fieldset>

<?php
}
?>
      </form>
   </body>
</html>

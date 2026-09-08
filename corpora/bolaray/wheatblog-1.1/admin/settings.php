<?php

//
// File:    admin/settings.php
// License: GNU GPL
// Purpose: Gets a post from admin/index.php.
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$action = (isset($_REQUEST['action'])) ? $_REQUEST['action'] : '';






//
//   Edit Settings
//
//
if ($action == 'edit') {
    $db = DB_connect($site, $user, $pass);
    DB_select_db($database, $db);

    $var   = DB_quote($_POST['var']);
    $value = DB_quote($_POST['value']);
    $descr = DB_quote($_POST['descr']);

    $sql = "update wbtbl_settings set val=$value, descrip=$descr where var=$var";

    DB_query($sql, $db);

    Header('Location: ' . $_SERVER['PHP_SELF']);
    exit(0);
}







$page_title = ' :: edit settings';
include_once("$wb_inc_dir/header.php");


// $variables is an array of arrays.  Each element is an array named after
// the setting.  The values contained in the individual array are the setting
// value and a short description.  FIXME: This explanation sucks.
//
$varList = array();

$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// Get all the variables
//
$result = DB_query('select * from wbtbl_settings', $db);


while($row = DB_fetch_array($result)) {
    $var     = $row['var'];
    $val     = $row['val'];
    $descrip = $row['descrip'];

    $varList[$var] = array(
        'val' => $val,
        'descrip' => $descrip
    );
}

echo '<table width="70%">';
echo '<tr>';
echo '<td>Variable</td><td>Value</td><td>Description</td><td></td></tr>';

foreach ($varList as $var => $field) {
    Print_Field($var, $field['val'], $field['descrip']);
}




function Print_Field($var, $val, $desc)
{
    echo '<form method="post" action="' . $_SERVER['PHP_SELF'] .  '?action=edit"><tr>';
    echo "<td><input name=\"var\"    type=\"input\" value=\"$var\" /></td>";
    echo "<td><input name=\"value\"  type=\"input\" value=\"$val\" /></td>";
    echo "<td><input name=\"descr\"  type=\"input\" value=\"$desc\" /></td>";
    echo "<td><input type=\"submit\" value=\"edit\" class=\"otherbutton\"/></td>";
    echo '</tr></form>';
}


include_once("$wb_inc_dir/footer.php");

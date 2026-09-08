<?php
//
// File:    admin/manage_users.php
// License: GNU GPL
// Purpose: User management
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}


$action     = (isset($_REQUEST['action'])) ? $_REQUEST['action'] : '';

// Text form data
$usrLogin      = (isset($_POST['login'])) ? $_POST['login'] : '';
$UsrLogin      = $db->quote($usrLogin);
$usrPassword   = (isset($_POST['password'])) ? $_POST['password'] : '';
$UsrPassword   = $db->quote($usrPassword);
$usrFlags      = (isset($_POST['flags'])) ? $_POST['flags'] : '';
$UsrFlags      = $db->quote($usrFlags);
$usrWww        = (isset($_POST['www'])) ? $_POST['www'] : '';
$UsrWww        = $db->quote($usrWww);
$usrEmail      = (isset($_POST['email'])) ? $_POST['email'] : '';
$UsrEmail      = $db->quote($usrEmail);

// Checkboxes
$usrAdmin      = (isset($_POST['admin'])) ? $_POST['admin'] : '';
$usrCookies    = (isset($_POST['cookies'])) ? $_POST['cookies'] : '';
$usrRegistered = (isset($_POST['registered'])) ? $_POST['registered'] : '';

if ($usrFlags == '') {
    $usrFlags = 0;
    if ($usrAdmin      == "on") {
        $usrFlags += 1;
    }
    if ($usrCookies    == "on") {
        $usrFlags += 2;
    }
    if ($usrRegistered == "on") {
        $usrFlags += 4;
    }
    $UsrFlags = $db->quote($usrFlags);
}

////
////  User requested to add a new user
////
if ($action == 'addnew') {
    $db->query("SELECT * FROM wbtbl_users WHERE login=$UsrLogin");

    if ($db->num_rows() > 0) {
        die("There's already a user named $usrLogin.");
    }

    $db->query("INSERT INTO wbtbl_users VALUES ( " .
        "$UsrLogin, $UsrPassword, $UsrFlags, '$UsrWww', $UsrEmail)");

    Header("Location: $wb_admin_url/manage_users.php");
    exit(0);
}



////
////  User requested to delete user
////
if ($action == 'delete') {
    if (! isset($_REQUEST['login'])) {
        die("I don't know who to delete!");
    } else {
        $login = $_REQUEST['login'];
    }

    $db->query("DELETE FROM wbtbl_users WHERE login=$UsrLogin;");

    Header("Location: $wb_admin_url/manage_users.php");
    exit(0);
}



////
////  User requested to edit user
////
if ($action == 'edit') {
    $usrFlags = 0;
    if ($usrAdmin      == 1) {
        $usrFlags += 1;
    }
    if ($usrCookies    == 1) {
        $usrFlags += 2;
    }
    if ($usrRegistered == 1) {
        $usrFlags += 4;
    }

    $UsrFlags = DB_quote($usrFlags);

    $db->query("UPDATE wbtbl_users SET  " .
        "login    = $UsrLogin,     " .
        "password = $UsrPassword,  " .
        "flags    = $UsrFlags,     " .
        "www      = $UsrWww,       " .
        "email    = $UsrEmail      " .
        "WHERE login=$UsrLogin;");


    Header("Location: $wb_admin_url/manage_users.php");
    exit(0);
}




$page_title = 'Managing User Accounts';
include_once("$wb_inc_dir/header.php");

// Print out all the users
//
$db->query("select * from wbtbl_users", $db);

insert_form_heading('Edit Existing Users');

while ($row = $db->fetchArray()) {
    Print_User($row);
}

insert_form_heading('Add New User');

?>
<div class="subcontent-users">
<form id="adduser" method="post" action="./manage_users.php?action=addnew">
<table cellpadding="2" cellspacing="0" border="0">
<tr>
<td class="fieldname" width="20%"><label>login</label></td>
<td width="80%"><input name="login" style="width:8em" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>password</label></td>
<td width="80%"><input name="password" style="width:8em" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>admin</label></td>
<td width="80%"><input class="check" type="checkbox" name="admin" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>cookies</label></td>
<td width="80%"><input class="check" type="checkbox" name="cookies" /></td>
</tr>
<tr><td class="fieldname" width="20%"><label>registered</label></td>
<td width="80%"><input class="check" type="checkbox" name="registered" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>www</label></td>
<td width="80%"><input name="www" style="width:15em" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>email</label></td>
<td width="80%"><input name="email" style="width:12em" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>&nbsp;</label></td>
<td width="80%"><input type="submit" value="submit" /></td>
</tr>
</table>
</form>
</div>
  <?php

include_once("$wb_inc_dir/footer.php");






function Print_User($row)
{
    global $self;

    echo '<div class="subcontent-users">' .
        '<form method="post" class="userlist" action="' . $self . '">' .
        '<table cellpadding="2" cellspacing="0" border="0">';

    Print_Field('login', $row['login'], 8);
    Print_Field('password', $row['password'], 8);

    $flags      = $row['flags'];
    $admin      = (isAdmin($flags)) ? 'checked' : '';
    $cookies    = (isCookies($row['flags'])) ? 'checked' : '';
    $registered = (isRegistered($row['flags'])) ? 'checked' : '';

    Print_Check('admin', $admin);
    Print_Check('cookies', $cookies);
    Print_Check('registered', $registered);

    Print_Field('www', $row['www'], 15);
    Print_Field('email', $row['email'], 12);

    End_User_Table($row['login']);
}
?>
				<tr>
					<td class="fieldname" width="20%">
					</td>
					<td>
						<input type="submit" name="action" value="edit" />
						<input type="submit" name="action" value="delete" />
					</td>
				</tr>
<?php


function Print_check($name, $check)
{
    echo '<tr>'."\n".'<td class="fieldname" width="20%"><label>'.$name.'</label></td>
	      <td width="80%"><input class="check" type="checkbox" name="'.$name.'" '.$check.' value="1" />
		  '."\n".'</td></tr>'."\n";
}
# kludged to assign input size variable, which is deprecated
function Print_field($field, $item, $size)
{
    echo '<tr>'."\n".'<td class="fieldname" width="20%"><label>'.$field.'</label></td><td width="80%">
		  <input name="'.$field.'" value="'.$item.'" style="width:'.$size.'em" />'."\n".'</td></tr>'."\n";
}




function End_User_Table($login)
{


}


?>

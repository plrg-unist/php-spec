<?php
//
// File:    admin/manage_users.php
// License: GNU GPL
// Purpose: Used to register for an account.  Do not use sessions here!
//
// Filtered / safe variables begin with capital letters.
//
require('settings.php');
$page_title = ':: Register Account';
include_once("$wb_inc_dir/header.php");

$action   = (isset($_REQUEST['action'])) ? $_REQUEST['action'] : '';
$login    = (isset($_POST['login'])) ? $_POST['login'] : '';
$Login    = $db->quote($login);
$password = (isset($_POST['password'])) ? $_POST['password'] : '';
$Password = $db->quote($password);
$cookie   = (isset($_POST['cookie'])) ? $_POST['cookie'] : '';
$www      = (isset($_POST['www'])) ? $_POST['www'] : '';
$Www      = $db->quote($www);
$email    = (isset($_POST['email'])) ? $_POST['email'] : '';
$Email    = $db->quote($email);




// If an email is given, filter it.
//
$Email_Regex = '/^[^@s]+@([-a-z0-9]+.)+[a-z]{2,}$/i';

if ($email != '' &&  ! preg_match($Email_Regex, $email)) {
    die('This is not a valid email address');
}




////
////  User requested to add a new user
////
////
if ($action == 'process') {

    if (! $Login  ||  ! $password) {
        die('You must supply a login and password.');
    }

    // Make sure the login is unique.
    //
    $db->query("SELECT * FROM wbtbl_users WHERE login=$Login");
    if ($db->num_rows() > 0) {
        die("There's already a user named $login.");
    }

    $flags = 0;
    $flags += ($cookie == 'on') ? 2 : 0;
    $Flags = $db->quote($flags);

    $db->query("INSERT INTO wbtbl_users
			VALUES ($Login, $Password, $Flags, $Www, $Email)");

    echo "<p>Thanks for registering, $login.</p>";

    if ($registered_comments) {
        echo "<p>An account must be registered before it can comment on " .
        "posts.  The administrator will approve registration shortly.</p>";
    } else {
        echo '<p>You can begin commenting immediately.</p>';
    }

    echo "Please click <a href=\"$wb_url\">here</a> to return to the " .
        "blog.</p>";

    exit(0);
}








insert_form_heading('Register As a New User');


?>
<div class="subcontent-heading" id="reg">
<span>This registration process is necessary to prevent unsolicited 
comments from spammers. If you are a frequent visitor, you may enable <strong>Cookies</strong>
to keep your information active with <strong><?= $name_of_blog ?></strong>. For your privacy, they only store your Username and Password.
</span>
</div>

<div class="subcontent-users">
<form method="post" action="registration.php?action=process">
<table cellpadding="2" cellspacing="0" border="0">
<tr>
<td class="fieldname" width="20%"><label>Login name:</label></td>
<td width="80%"><input name="login" style="width:8em" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>Password:</label></td>
<td width="80%"><input name="password" style="width:8em" /></td>
</tr>
<td class="fieldname" width="20%"><label>Email Address:</label></td>
<td width="80%"><input name="email" style="width:12em" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>Website:</label></td>
<td width="80%"><input name="www" style="width:15em" /></td>
</tr>
<tr>
<tr>
<td class="fieldname" width="20%"><label>Allow cookies:</label></td>
<td width="80%"><input class="check" type="checkbox" name="cookie" /></td>
</tr>
<tr>
<td class="fieldname" width="20%"><label>&nbsp;</label></td>
<td width="80%"><input type="submit" value="Register" /></td>
</tr>
</table>
</form>
</div>


<?php include_once("$wb_inc_dir/footer.php"); ?>

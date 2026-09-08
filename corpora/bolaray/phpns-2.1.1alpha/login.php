<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

$globalvars['pagetype'] = "login";  //set page type
include("inc/header.php"); //include header file

$do = $_GET['do']; //get action

if ($_GET['m'] == "out") {
    $message = '<div class="warning">You are successfully logged out!</div>';
} elseif ($_GET['m'] == "nologin") {
    $message = '<div class="warning">Your username and password are correct, however, your rank is disallowing logging in at this time. Contact your administrator if you think this is a mistake.</div>';
}

if (!$do) {
    $content = '
		<div id="login">
			<form id="login_form" action="?do=p" method="post">
				'.$message.'
				<h2>User login</h2>
				<label for="username">Username</label> <input type="text" name="username" id="username" onLoad="focus()" /><br />
				<label for="password">Password</label> <input type="password" name="password" id="password" /><br />
				<label for="remember">Remember me</label> <input type="checkbox" name="remember" id="remember">
				<div id="login_submit">
					<input type="submit" id="submit" value="Login" />
				</div>
			</form>
			<script type="text/javascript"> 
				document.getElementById(\'username\').focus(); 
			</script> 
		</div>';
} elseif ($do == "p") {
    $loginvar = array("username"=>$_POST['username'],"password"=>sha1($_POST['password']),"remember"=>$_POST['remember']);

    $loginvar = clean_data($loginvar); //clean the data

    //check if database has entry + password
    $lsql = "SELECT * FROM ".$databaseinfo['prefix']."users WHERE user_name='".$loginvar['username']."' AND  password='".$loginvar['password']."'";
    $lres = mysql_query($lsql) or die(mysql_error());
    $lnumcheck = mysql_num_rows($lres);
    if ($lnumcheck == 0) { //if no result was found...
        $content = '<div id="login_error" class="warning">
				<h3>Login failed</h3>
				<p>We could not find a user entry with that username and password. If you have forgotten your password, use the recovery tool. Cookies must be enabled to login to the system!</p>
		</div>
		
				<div id="login">
			<form id="login_form" action="?do=p" method="post">
				<h2>User login</h2>
				<label for="username">Username</label> <input type="text" name="username" id="username" value="' . $loginvar['username'] . '" /><br />
				<label for="password">Password</label> <input type="password" name="password" id="password" class="outline" /><br />

				<label for="remember">Remember me</label> <input type="checkbox" name="remember" id="remember">
				<div id="login_submit">
					<input type="submit" id="submit" value="Login" />
				</div>
			</form>
			<script type="text/javascript"> 
				document.getElementById(\'password\').focus(); 
			</script> 
		</div>';
    } else {
        //insert login record.
        $loginvar['timestamp'] = time();

        //get some vars from db
        $fdata = general_query('SELECT * FROM '.$databaseinfo['prefix'].'users WHERE user_name="'.$loginvar['username'].'"', true);
        //get rank string
        $rdata = general_query('SELECT * FROM '.$databaseinfo['prefix'].'ranks WHERE id='.$fdata['rank_id'].'', true);
        //insert login record
        $res = general_query("INSERT INTO ".$databaseinfo['prefix']."userlogin 
					(username,rank_id,timestamp,ip) 
					VALUES (
					'".$uername."',
					'".$rdata['id']."',
					'".$loginvar['timestamp']."',
					'".$globalvars['ip']."')");

        //define session variables, set cookies
        $_SESSION['username'] = $fdata['user_name'];
        $_SESSION['userID'] = $fdata['id'];
        $_SESSION['permissions'] = $rdata['permissions'];
        $_SESSION['auth'] = "yes";
        $_SESSION['path'] = $globalvars['path_to'];

        //if the user wants to set a cookie, we have to do more stuff. (bleh.)
        if ($loginvar['remember']) {
            //generate randomized string for cookie identification
            //we'll generate it now.
            $cookie_string = md5(uniqid(rand(), true));
            $cookielog_res = general_query('INSERT INTO '.$databaseinfo['prefix'].'cookielog 
					(user_id,rank_id,cookie_id,timestamp,ip)
					VALUES (
					"'.$fdata['id'].'",
					"'.$fdata['rank_id'].'",
					"'.$cookie_string.'",
					"'.$loginvar['timestamp'].'",
					"'.$globalvars['ip'].'"
					)');

            setcookie('cookie_auth', $cookie_string, time()+604800); //set cookie to expire in a week
        }

        //quick permission check (redir to error)
        if ($rdata['permissions'][8] == 0) {
            session_destroy();
            header("Location: login.php?m=nologin");
            die();
        }

        //log the login
        log_this('login', 'User <i>'.$_SESSION['username'].'</i> has <strong>logged in</strong>');

        //go to index
        header("Location: index.php"); //redirect to index
    }

} elseif ($do == "logout") { //if we're logging out...
    log_this('logout', 'User <i>'.$_SESSION['username'].'</i> has <strong>logged out</strong>.');
    session_destroy(); //session is pwned.
    header("Location: login.php?m=out");
}
include("inc/themecontrol.php");

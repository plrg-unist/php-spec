<?php

/* Copyright (c) 2007 Kyle Osborn, Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

//phpns version 1 => version 2 upgrade script, courtasy of our good friend "Kyle Osborn", a
//contributing developer of phpns. Thanks a lot! :D


if(!$_GET[step]) {
    header("location: ?step=1");
}

define("DEBUG", $_GET[debug]);

$step = $_GET['step'];


//   V1 CONNECTION
if(DEBUG) {
    echo $host ."<br />\n". $user ."<br />\n". $password ."<br />\n". $database ."<br /><br />";
}

function v1connect()
{
    $user = $_POST['db_user'];
    $password = $_POST['db_password'];
    $host = $_POST['db_host'];
    $database = $_POST['db_name'];
    $connection = mysql_connect($host, $user, $password) or die("Connection to the phpns version 1 mysql server failed.");
    $db = mysql_select_db($database, $connection) or die(mysql_error());
}






//   V2 CONNECTION
if(DEBUG) {
    echo $databaseinfo['host'] ."<br />\n". $databaseinfo['user'] ."<br />\n". $databaseinfo['password'] ."<br />\n". $databaseinfo['dbname'] ."<br /><br />";
}

function v2connect()
{
    include("../inc/config.php");
    $mysql['connection'] = mysql_connect($databaseinfo['host'], $databaseinfo['user'], $databaseinfo['password']) or die($error['connection']);
    $mysql['db'] = mysql_select_db($databaseinfo['dbname'], $mysql['connection']) or die($error['database']);
}





if($_POST) {


    //From v1 userinfo
    v1connect();
    $user = "SELECT * FROM userinfo";
    $userresult = mysql_query($user);
    $num = mysql_numrows($userresult);
    $i = 0;
    while ($i < $num) {

        $id = mysql_result($userresult, $i, "id");
        $username = mysql_result($userresult, $i, "username");
        $email = mysql_result($userresult, $i, "email");
        $timestamp = mysql_result($userresult, $i, "date");
        $rank = mysql_result($userresult, $i, "rank");
        if(DEBUG) {
            echo $id ."<br />\n". $username ."<br />\n". $email ."<br />\n". $timestamp ."<br />\n". $rank;
        }

        //to v2 users
        v2connect();
        $insert = "INSERT INTO `users` (`user_name`, `email`, `password`, `timestamp`, `rank_id`) VALUES ('$username', 'CHANGEME', '$email', '$timestamp', '$rank');";
        @mysql_query($insert) or die(mysql_error());

        $i++;
    }


    //From v1 news
    v1connect();
    $news = "SELECT * FROM news";
    $newsresult = mysql_query($news);
    $num = mysql_numrows($newsresult);
    $i = 0;
    while ($i < $num) {

        $title = mysql_result($newsresult, $i, "title");
        $subtitle = mysql_result($newsresult, $i, "subtitle");
        $content = mysql_result($newsresult, $i, "content");
        $extcontent = mysql_result($newsresult, $i, "extcontent");
        $author = mysql_result($newsresult, $i, "author");
        $date = mysql_result($newsresult, $i, "date");
        $cat = mysql_result($newsresult, $i, "cat");
        if(DEBUG) {
            echo $id ."<br />\n". $title ."<br />\n". $subtitle ."<br />\n". $content ."<br />\n". $extcontent ."<br />\n". $author ."<br />\n". $date ."<br />\n". $cat;
        }

        //to v2 articles
        v2connect();
        $insert = "INSERT INTO `articles` (`article_title`, `article_subtitle`, `article_author`, `article_cat`, `article_text`, `article_exptext`, `article_imgid`, `allow_comments`, `start_date`, `end_date`, `active`, `approved`, `timestamp`, `ip`) VALUES ('$title', '$subtitle', '$author', '$cat', '$content', '$extcontent', '', '0', '', '', '0', '0', '$date', '127.0.0.1');";
        @mysql_query($insert) or die(mysql_error());

        $i++;
    }
}



if($step == 1) {
    $content = '
			<div class="warning"><strong>YOU NEED TO HAVE PHPNS 2 ALREADY INSTALLED</strong> for this to work.</div>
		<h3>Step 1</h3>
		'.$error_message.'
		<p>To upgrade, you will need the original mysql.php from V1.x of phpNS</p>
		<form action="?step=2" method="post">
				<br />
				<br />
				<br />
				<label for="db_host">Database host</label>
				<input type="text" name="db_host" value="" /> (Usually "localhost")
				</label>
				<br />

				
				<label for="db_user">Database user</label>
				<input type="text" name="db_user" value="" />
				</label>
				<br />
				
				<label for="db_password">Database password</label>
				<input type="password" name="db_password" value="" />
				</label>
				<br />

				
				<label for="db_name">Database name</label>
				<input type="text" name="db_name" value="" />
				<br />

			<br />

			
			<div class="alignr">
				<input type="submit" id="submit" value="Continue" />
			</div>
			<br />

		</form>
		';
} elseif($step == 2) {
    $content = '
	
		<h3>Upgrade has been completed!</h3>
			<br />
		<h2>It is now <strong>STRONGLY</strong> suggest you remove the /install directory!</h2>';
}


include("install.tmp.php");

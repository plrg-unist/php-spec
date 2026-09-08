<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

include("inc/header.php");
$do = $_GET['do'];

if ($do == "backup") { //send backup file to user, header info
    $file = $databaseinfo['dbname'].'.sql'; //the current dump
    header('Content-Type: application/text');
    header('Content-Length: '.$_GET['size'].'');
    header('Content-disposition: attachment; filename='.$databaseinfo['dbname'].'.sql');
    readfile($file);
    log_this('backup', 'User <i>'.$_SESSION['username'].'</i> has <strong>backed up</strong> the system database.');
} elseif ($do == "rss") {
    $mode = 'rss';
    $sef_override = true;
    include('shownews.php');
    $do = 'rss'; //shownews.php resets the $do variable, just resetting it for the rest of the etc.php to avoid error.
}

if ($do == null) {
    echo $do;
    echo "This file is only for special tasks that can't be done on other pages. Go away now. =D";
}

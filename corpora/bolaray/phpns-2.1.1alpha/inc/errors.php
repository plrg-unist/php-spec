<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

$live = "no";

//Arrays are created below for each custom error message.

$error['connection'] = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>database error</title>
</head>
<body>
	<h1>database error</h1>
	<hr />
	<p>Phpns could not contact the database server. This may happen when you have supplied the wrong information in the /inc/config.php file, or the server has been overloaded, and is denying requests from our system.</p>
	<p><a href="../">return to the main directory</a> | <a href="http://phpns.com">phpns.com</a></p>
	<div><h5>Copyright 2007-08 Alec Henriksen | GPL License</h5></div>
</body>
</html>';

$error['database'] = "phpns couldn't select the database specified in the config.php file.";

$error['query'] = "phpns couldn't execute an important query.";

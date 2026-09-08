<?php

/* Copyright (c) 2007 Kyle Osborn, Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>phpns &raquo; install</title>
	<link rel="shortcut icon" href="images/favicon.ico" type="image/x-icon" />
	<link rel="stylesheet" href="../themes/default/styles/main.css" type="text/css" media="screen" />
</head>
<body id="install">
	<noscript>
		<div id="messages">
			Javascript is not enabled on this browser. This will result in decreased accessability, and possibly limited features.
		</div>
	</noscript>
	<div id="head_container">
		<h1><a href="../index.php">phpns</a></h1>
		<div id="tabs"> <!-- navigation start -->
					<ul>
						<li><a href="index.php" title="phpns install index"><span>install index</span></a></li>
						<li><a href="../" title="phpns admin panel"><span>phpns admin panel</span></a></li>

					</ul>
				</div> <!-- navigation end -->
		</div>
		<div id="main_container">
			<div id="main_content">
			<?php echo "$logo"; ?>
			<h2>phpns installation</h2>
			<p>Welcome to the automatic phpns installation. Throughout this installation, we will ask you a few basic questions to get this up and running.</p>
			<?php echo "$content"; ?>
		</div>
		<div class="clear"></div>
	</div>

	<div id="copyright"> <!-- bottom notice/copyright -->
	phpns 2.1.1 is released under the GPL license, by <a href="http://phpns.com">phpns.com</a> | Valid CSS/XHTML (semantic) | <a href="javascript:new_window('help.php#');">Help</a>
	</div>
</body>
</html>

<!--
Template created by Alec Henriksen
Date: Wednesday July 18, 2007
http://phpns.com
standard compliant, semantic
-->

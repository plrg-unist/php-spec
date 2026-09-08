<?php

/* Copyright (c) 2007 Alec Henriksen
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
	<title>phpns &raquo; login</title>
	<link rel="alternate" type="application/rss+xml" title="phpns rss feed" href="etc.php?do=rss"/>
	<link rel="stylesheet" href="{prepath}styles/main.css" type="text/css" media="screen" />
	<script type="text/javascript" src="{prepath}expand.js"></script>
</head>
	<body class="login">
		<noscript>Javascript is disabled on your browser, which will result in reduced features and limited accessability.</noscript>
		<div id="head_container">
			<h1><a href="index.php">phpns</a></h1>
			<div id="tabs"> <!-- navigation start -->
					<ul>
						<li><a href="login.php" title="phpns login page"><span>login</span></a></li>
						<li><a href="help.php" title="phpns documentation/help"><span>phpns documentation</span></a></li>
					</ul>
					<script language="javascript" type="text/javascript">setPage()</script>
				</div> <!-- navigation end -->
		</div>
		<div id="main_container">
			<div id="main_content">
				<h3>{current_page_name}</h3>				
				{content}
			</div>
		</div>
		<div id="copyright"> <!-- bottom notice/copyright -->
	phpns {version} is released under the GPL license, by <a href="http://phpns.com">phpns.com</a> | Valid CSS/XHTML (semantic) | <a href="javascript:new_window('help.php#{current_page_name}');">Help</a>
	</div>
	</body>
	<!-- Done. :) If you need something, contact me at alecwh{at}gmail.com -->
</html>

<!--
Template created by Alec Henriksen
Date: Wednesday July 18, 2007
http://phpns.com
standard compliant, semantic
-->

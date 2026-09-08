<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/


$globalvars['page_name'] = 'about';
include("inc/header.php");

//check some variables on the phpns server, timeout 5 secs...
$version_check = version_check($globalvars['version']);
$phpns_rss = phpns_rss();

if($_GET['version_check']) {
    echo '<link rel="stylesheet" href="./themes/default/styles/main.css" type="text/css" media="screen" />';
    echo $version_check;
    die;
}

$content = '
<h3>Server information</h3>
<div id="columnright">
	<h4>Version check</h4>
	<iframe src="./about.php?version_check=1" scrolling="no" frameborder="0"></iframe>
</div>
	<h4>Latest news</h4>
	'.$phpns_rss.'

<h3>Help and Support</h3>
<p>If you are need standard help with any part of your phpns installation, please consult the <a href="help.php">internal documentation</a> first. If that doesn\'t answer your question, you can do the following (in order of fastest reply):
	<ol>
		<li>Search the <a href="http://phpns.com/documentation">project documentation</a>.</li>
		<li>You can join our <a href="irc://irc.freenode.net:6667/phpns">IRC channel</a> at <strong>irc.freenode.net</strong> (<strong>#phpns</strong>) (Port: 6667)
			<blockquote>The IRC is the best means of getting help, and getting in touch with the administrators.</blockquote>
		</li>
		<li>Try <a href="http://phpns.com/contact.php">contacting us</a> directly.</li>
	</ol>

<h3>Development team</h3>
<p>First, and formost, we would like to thank the community! Not only for using our web application, but for your continued support and donations. Next, our sponsors have contributed so much to the development of phpns, we can\'t thank them enough!</p>
		<blockquote>
		<strong>Primary development</strong>
		<ul>
			<li><a href="http://alecwh.com">Alec Henriksen</a>, lead and primary developer (project owner, copyright holder)</li>
			
		</ul>
		
		<strong>Contributory development</strong>
		<ul>
			<li><a href="http://justarandomblog.com">Kyle Osborn</a>, consultation and misc. scripting</li>
			
		</ul>
		
		
		<strong>Sponsors</strong>
		<ul>
			<li>no sponsors yet. <a href="http://phpns.com/contact">Find out how to become one</a>, and get listed here!</li>
		</ul>
		</blockquote>

<h3>License (gpl)</h3>
<p>   Copyright (C) 2007  Alec Henriksen</p>
<p>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
</p>
<p>
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
</p>
<p>
Please see the GPL at <a href="http://www.gnu.org/copyleft/gpl.html">gnu.org</a> for a complete understanding of what this license means and how to abide by it.
</p>

<h3>Support phpns</h3>
<p>
Although we will never charge for the phpns package, we do ask that you (optionally) help us by...
</p>
	<ol>
		<li><strong>Rating phpns at hotscripts.com</strong>
			<blockquote>
			<form action="http://www.hotscripts.com/rate/66546.html" method="post">                  
				<select name="rating" size="1">
					<optgroup label="Select a rating">
					<option selected="selected" value="5">Excellent!</option>
					<option value="4">Very Good</option>
					<option value="3">Good</option>
					<option value="2">Fair</option>
					<option value="1">Poor</option>
					</optgroup>
				</select><br />
				<input name="submit" value="Rate It!" type="submit">
			</form>
			</blockquote>
		</li>
		<li><strong>Give the software to your friends.</strong></li>
		<li><strong><a href="http://launchpad.net/phpns">report a bug in the software</a></strong></li>
	</ol>

<h3>Miscellaneous</h3>
<p>
This program was created using open-source and free software, on the linux operating system. This web application takes as much advantage of the XHTML/CSS specifications as possible (provided by <a href="http://w3.org">w3C</a>) and is designed to generate compliant and semantic content. The following programs were used in the creation of this project:
</p>
	<div id="columnright">
		<ul>
		<li><a href="http://tango.freedesktop.org/Tango_Icon_Gallery">Tango Desktop Icons</a></li>
		<li><a href="http://tinymce.moxiecode.com/">TinyMCE wysiwyg editor</a></li>
		</ul>
	</div>
	<ul>
		<li><a href="http://www.gnome.org/projects/gedit/">gEdit (Gnome text-editor)</a></li>
		<li><a href="http://inkscape.org/">Inkscape Vector Illistrator</a></li>
		<li><a href="http://www.phpmyadmin.net/home_page/index.php">phpMyAdmin database manager</a></li>
	</ul>
';

include("inc/themecontrol.php");  //include theme script

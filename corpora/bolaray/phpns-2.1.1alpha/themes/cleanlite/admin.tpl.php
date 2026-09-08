<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>phpns &raquo; {current_page_name}</title>
	<link rel="stylesheet" href="{prepath}styles/main.css" type="text/css" media="screen" />
	<link rel="shortcut icon" href="images/favicon.ico" type="image/x-icon" />
	{head_data}
</head>
<body>
	<noscript>
		<div id="messages">
			Javascript is not enabled on this browser. This will result in decreased accessability, and possibly limited features.
		</div>
	</noscript>
	<div id="container">
		<div id="navigation"> <!-- navigation start -->
			<ul>
				<li><a href="index.php" title="phpns index">index</a></li>
				<li><a href="article.php" title="post a new article">new article</a></li>
				<li><a href="manage.php" title="manage current articles">article management</a></li>
				<li><a href="user.php" title="manage user profiles">user management</a></li>
				<li><a href="preferences.php" title="modify phpns preferences">preferences</a></li>
				<li class="slast"><a href="about.php" title="about the phpns project">about</a></a></li>
				<li class="last"><a href="javascript:if(confirm('Are you sure you want to logout?')) top.location='login.php?do=logout'" title="logout as {username}">logout ({username})</a></li>

			</ul>
		</div> <!-- navigation end -->
		<div id="content">
			{global_message}
			{page_image}
			<h2>{current_page_name}</h2>
			<p>{page_desc}</p>
			{content}<br />
		</div>
		<div class="clear"></div>
	</div>
	<div id="copyright"> <!-- bottom notice/copyright -->
	phpns {version} is released under the GPL license, by <a href="http://phpns.com">phpns.com</a> | Valid CSS/XHTML (semantic) | <a href="javascript:new_window('help.php#{current_page_name}');">Help</a>
	</div>
</body>
</html>
	<!-- Template is copyrighted under the GPL. =) -->
	<!-- Alec Henriksen Date: Wednesday July 18, 2007 http://phpns.com -->

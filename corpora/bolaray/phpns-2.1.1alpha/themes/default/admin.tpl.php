<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title>phpns &raquo; {current_page_name}</title>
	<link rel="stylesheet" href="{prepath}styles/main.css" type="text/css" media="screen" />
	<link rel="shortcut icon" href="images/favicon.ico" type="image/x-icon" />
	{head_data}
	</head>
	
	<body class="admin">
		<noscript>
			<div id="messages">
				Javascript is disabled on your browser, which will result in reduced features and limited accessability.
			</div>
		</noscript>
		<div id="head_container">
			<h1><a href="index.php">php<span>ns</span></a></h1>
			<div id="tabs"> <!-- navigation start -->
					<ul>
						<li><a href="index.php" title="phpns index"><span>index</span></a></li>
						<li><a href="article.php" title="post a new article"><span>new article</span></a></li>
						<li><a href="manage.php" title="manage current articles"><span>article management</span></a></li>
						<li><a href="user.php" title="manage user profiles"><span>user management</span></a></li>
						<li><a href="preferences.php" title="modify phpns preferences"><span>preferences</span></a></li>
						<li><a href="about.php" title="about the phpns project"><span>about</span></a></li>
						<li class="slast"><a href="login.php?do=logout" title="logout {username}"><span><strong>logout</strong></span></a></li>
						<!-- <li class="last"><a href="javascript:if(confirm='Are you sure you want to logout?') top.location='login.php?do=logout'" title="logout as {username}">logout ({username})</a></li> -->

					</ul>
					<script language="javascript" type="text/javascript">setPage()</script>
				</div> <!-- navigation end -->
		</div>
		<div id="main_container">
			<div id="main_content">
				{global_message}
				{page_image}
				
				<h2>{current_page_name}</h2>
				<p class="caps">{page_desc}</p>
				
				{content}
			</div>
		</div>
		<div id="copyright"> <!-- bottom notice/copyright -->
	phpns {version} is released under the GPL license, by <a href="http://phpns.com">phpns.com</a> | Valid CSS/XHTML (semantic) | <a href="javascript:new_window('help.php#{current_page_name}');">Help</a>
	</div>
	</body>
	<!-- Template is copyrighted under the GPL. =) -->
	<!-- Done. :) If you need something, contact me at alecwh{at}gmail.com -->
</html>

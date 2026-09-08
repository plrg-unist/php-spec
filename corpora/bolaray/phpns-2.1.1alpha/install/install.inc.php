<?php

/* Copyright (c) 2007 Kyle Osborn, Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

if (INSTALLING == true) {

    $databaseinfo['host'] = $data['db_host'];
    $databaseinfo['user'] = $data['db_user'];
    $databaseinfo['password'] = $data['db_password'];
    $databaseinfo['dbname'] = $data['db_name'];


    include("../inc/errors.php");   // include error profiles



    //connect to mysql database for all files
    $mysql['connection'] = mysql_connect($databaseinfo['host'], $databaseinfo['user'], $databaseinfo['password'])
    or die($error['connection']);

    //select mysql database
    $mysql['db'] = mysql_select_db($databaseinfo['dbname'], $mysql['connection'])
    or die($error['database']);



    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'articles` (
	  `id` int(25) NOT NULL auto_increment,
	  `article_title` varchar(100) NOT NULL,
	  `article_subtitle` varchar(100) NOT NULL,
	  `article_author` varchar(100) NOT NULL,
	  `article_cat` varchar(15) NOT NULL,
	  `article_text` varchar(20000) NOT NULL,
	  `article_exptext` varchar(20000) NOT NULL,
	  `article_imgid` varchar(100) NOT NULL,
	  `allow_comments` varchar(1) NOT NULL,
	  `start_date` varchar(15) NOT NULL,
	  `end_date` varchar(15) NOT NULL,
	  `active` varchar(1) NOT NULL,
	  `approved` varchar(1) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`),
	  KEY `article_title` (`article_title`,`timestamp`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;';
    $res = mysql_query($sql);


    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'banlist` (
	  `id` int(10) NOT NULL auto_increment,
	  `ip` varchar(15) NOT NULL,
	  `banned_by` varchar(20) NOT NULL,
	  `reason` varchar(5000) NOT NULL,
	  `timestamp` varchar(12) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'categories` (
	  `id` int(15) NOT NULL auto_increment,
	  `cat_name` varchar(100) NOT NULL,
	  `cat_parent` varchar(10000) NOT NULL,
	  `cat_author` varchar(100) NOT NULL,
	  `cat_desc` varchar(1000) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=32 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'comments` (
	  `id` int(25) NOT NULL auto_increment,
	  `article_id` varchar(25) NOT NULL,
	  `comment_text` varchar(1000) NOT NULL,
	  `website` varchar(100) NOT NULL,
	  `comment_author` varchar(20) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `approved` varchar(1) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'cookielog` (
	  `id` int(20) NOT NULL auto_increment,
	  `user_id` varchar(15) NOT NULL,
	  `rank_id` varchar(15) NOT NULL,
	  `cookie_id` varchar(32) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`),
	  KEY `user_id` (`user_id`)
	) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;
	';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'gconfig` (
	  `id` int(5) NOT NULL auto_increment,
	  `name` varchar(100) NOT NULL,
	  `v1` varchar(17) NOT NULL,
	  `v2` varchar(10) NOT NULL,
	  `v3` varchar(1000) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=15 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'images` (
	  `id` int(15) NOT NULL auto_increment,
	  `user_id` varchar(15) NOT NULL,
	  `image_filepath` varchar(500) NOT NULL,
	  `alt_description` varchar(100) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`),
	  KEY `user_id` (`user_id`)
	) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'ranks` (
	  `id` int(15) NOT NULL auto_increment,
	  `rank_title` varchar(100) NOT NULL,
	  `rank_desc` varchar(1000) NOT NULL,
	  `rank_author` varchar(100) NOT NULL,
	  `permissions` varchar(100) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=15 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE `'.$data['db_tableprefix'].'syslog` (
	  `id` int(24) NOT NULL auto_increment,
	  `task` varchar(20) NOT NULL,
	  `description` varchar(200) NOT NULL,
	  `user` int(5) NOT NULL,
	  `page` varchar(120) NOT NULL,
	  `timestamp` varchar(12) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=12 ;';
    $res = mysql_query($sql);


    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'templates` (
	  `id` int(15) NOT NULL auto_increment,
	  `template_name` varchar(100) NOT NULL,
	  `template_desc` varchar(1000) NOT NULL,
	  `template_author` varchar(100) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `html_article` varchar(5000) NOT NULL,
	  `html_comment` varchar(5000) NOT NULL,
	  `html_form` varchar(5000) NOT NULL,
	  `html_pagination` varchar(5000) NOT NULL,
	  `template_selected` varchar(1) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'themes` (
	  `id` int(10) NOT NULL auto_increment,
	  `theme_name` varchar(100) NOT NULL,
	  `theme_author` varchar(100) NOT NULL,
	  `theme_dir` varchar(200) NOT NULL,
	  `base_dir` varchar(50) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `theme_selected` varchar(1) NOT NULL,
	  `permissions` varchar(10000) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'userlogin` (
	  `id` int(20) NOT NULL auto_increment,
	  `username` varchar(15) NOT NULL,
	  `rank_id` varchar(15) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`),
	  KEY `user_id` (`username`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=82 ;
	';
    $res = mysql_query($sql);

    $sql = 'CREATE TABLE IF NOT EXISTS `'.$data['db_tableprefix'].'users` (
	  `id` int(15) NOT NULL auto_increment,
	  `user_name` varchar(100) NOT NULL,
	  `full_name` varchar(150) NOT NULL,
	  `email` varchar(100) NOT NULL,
	  `password` varchar(40) NOT NULL,
	  `timestamp` varchar(15) NOT NULL,
	  `ip` varchar(15) NOT NULL,
	  `msn` varchar(100) NOT NULL,
	  `aim` varchar(100) NOT NULL,
	  `yahoo` varchar(100) NOT NULL,
	  `skype` varchar(100) NOT NULL,
	  `display_picture` varchar(150) NOT NULL,
	  `rank_id` varchar(15) NOT NULL,
	  PRIMARY KEY  (`id`)
	) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=8 ;';
    $res = mysql_query($sql);

    $sql = "INSERT INTO `".$data['db_tableprefix']."articles` (`id`, `article_title`, `article_subtitle`, `article_author`, `article_cat`, `article_text`, `article_exptext`, `article_imgid`, `allow_comments`, `start_date`, `end_date`, `active`, `approved`, `timestamp`, `ip`) VALUES (NULL, 'Welcome to phpns!','','".$data['username']."','all','&lt;p&gt;If you see are viewing this message, the phpns installation was a success! This article is filed under &amp;quot;Site Wide News&amp;quot;, which is the default category that is created during installation.&lt;/p&gt;&lt;p&gt;&lt;font color=&quot;#993300&quot;&gt;You are free to modify this message, or delete it all together&lt;/font&gt;. Why should you use phpns?&lt;/p&gt;&lt;ul&gt;&lt;li&gt;&lt;strong&gt;It&#039;s free&lt;/strong&gt;. Phpns is released under the GPL license, which gives you the ability to change it, redistribute it, and use it personally or professionally.&lt;/li&gt;&lt;li&gt;&lt;strong&gt;It&#039;s clean&lt;/strong&gt;. It&#039;s a breath or fresh air, following web standards and semantics. The (open-source) code is neatly organized, logically indented, and well-commented to make changes easier.&lt;/li&gt;&lt;li&gt;I&lt;strong&gt;t&#039;s easy to integrate&lt;/strong&gt;. Only one line of code is necessary on your website, and you have a dynamic, fully functional news system. &lt;/li&gt;&lt;li&gt;&lt;strong&gt;It&#039;s easy to install&lt;/strong&gt;. The guided installation will have you up and running in minutes, asking you just a few questions about your database setup.&lt;/li&gt;&lt;/ul&gt;Some more information is available in the &amp;quot;Full Article&amp;quot; section...','What does &amp;quot;free&amp;quot; mean? &lt;blockquote&gt;To the phpns developers, the word &amp;quot;free&amp;quot; means more than just the cost of the product. The word free means that &lt;strong&gt;you are free&lt;/strong&gt; to modify anything you want about phpns, without any license restrictions.&lt;/blockquote&gt;&lt;p&gt;Why is phpns free in both price and modification?&lt;/p&gt;&lt;blockquote&gt;&lt;p&gt;Because we believe in the open-source message. Closed source applications restrict the user from customizing the way the system works, and prevents the communitiy from contributing to the package. Plus, we love seeing our software being put to good use, and we love modifications.&lt;/p&gt;&lt;/blockquote&gt;&lt;p&gt;Why don&#039;t you require a &amp;quot;Powered by phpns&amp;quot; message at the bottom of each page, like other news systems?&lt;/p&gt;&lt;blockquote&gt;&lt;p&gt;Because we hated that when using other products... and the fact that you had to pay to have it removed. However, if you don&#039;t mind a message like that, it can be enabled in the preferences system. It&#039;s disabled by default.&lt;/p&gt;&lt;/blockquote&gt;&lt;p&gt;What can I do to help the project?&lt;/p&gt;&lt;blockquote&gt;&lt;p&gt;If you would like to be a part of the project, we always appreciate help. What you can do:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;Spread the word. Recommend our system to your friends and co-workers!&lt;/li&gt;&lt;li&gt;Report bugs you&#039;ve encountered at the &lt;a href=&quot;http://launchpad.net/phpns&quot;&gt;phpns launchpad website&lt;/a&gt;. &lt;/li&gt;&lt;li&gt;Submit reviews to software review websites around the internet. As long as they are honest, this is a great way to help us.&lt;/li&gt;&lt;li&gt;Donate. This helps with hosting/domain costs, and you&#039;ll get your name on the website along with a message and URL of your blog/website.&lt;/li&gt;&lt;li&gt;Become a sponsor. If you&#039;re a hosting service, business, or organization, we&#039;re always looking for funding and bandwith.&lt;/li&gt;&lt;li&gt;Develop. Contact us on the website if you think we could use your services.&lt;/li&gt;&lt;/ul&gt;That&#039;s it. Enjoy phpns!&lt;br /&gt;&lt;/blockquote&gt;','imgid','0','','','1','1','".time()."','".$_SERVER['REMOTE_ADDR']."')";
    $res = mysql_query($sql);

    $sql = "INSERT INTO `".$data['db_tableprefix']."gconfig` (`id`, `name`, `v1`, `v2`, `v3`) VALUES 
	(NULL, 'siteonline', '0', '0', '0'),
	(NULL, 'def_rsslimit', '', '', '3'),
	(NULL, 'def_rssorder', 'desc', '', ''),
	(NULL, 'def_items_per_page', '10', '', ''),
	(NULL, 'def_rsstitle', '', '', 'phpns rss feed'),
	(NULL, 'def_rssdesc', '', '', 'An RSS feed from phpns articles.'),
	(NULL, 'def_rssenabled', '1', '', ''),
	(NULL, 'def_limit', '10', '', ''),
	(NULL, 'def_order', 'desc', '', ''),
	(NULL, 'def_offset', '0', '', ''),
	(NULL, 'timestamp_format', '', '', 'l F d, Y  g:i a'),
	(NULL, 'def_comlimit', '', '', '100000'),
	(NULL, 'def_comenabled', '1', '', ''),
	(NULL, 'def_comorder', 'asc', '', ''),
	(NULL, 'global_message', '', '', 'Welcome to the phpns admin panel! Click \'change message\' to modify/delete this message.'),
	(NULL, 'siteonline', '0', '0', '0'),
	(NULL, 'wysiwyg', 'yes', '', ''),
	(NULL, 'sys_time_format', 'l F d, Y  g:i a', '', ''),
	(NULL, 'line', 'yes', '', '');";
    $res = mysql_query($sql);

    $sql = "INSERT INTO `".$data['db_tableprefix']."ranks` (`id`, `rank_title`, `rank_desc`, `rank_author`, `permissions`, `timestamp`) VALUES 
	(1, 'Administrators', 'Any user assigned to this rank will have full access.', '".$data['username']."', '1,1,1,1,1,1,1,1,1,1,1,1', '".time() ."');";
    $res = mysql_query($sql);

    $sql = "INSERT INTO `".$data['db_tableprefix']."themes` (`id`, `theme_name`, `theme_author`, `theme_dir`, `base_dir`, `timestamp`, `theme_selected`, `permissions`) VALUES 
	(NULL, 'default', 'phpns team', 'themes/default/', 'default', '".time() ."', '1', '');";
    $res = mysql_query($sql);

    $sql = "INSERT INTO `".$data['db_tableprefix']."users` (`id`, `user_name`, `full_name`, `email`, `password`, `timestamp`, `ip`, `msn`, `aim`, `yahoo`, `skype`, `display_picture`, `rank_id`) VALUES 
	(NULL, '".$data['username']."', '".$data['username']."', '', '".$data['password'] ."', '".time() ."', '127.0.0.1', '', '', '', '', '', '1');";
    $res = mysql_query($sql);

    $sql = "INSERT INTO `".$data['db_tableprefix']."categories` (`id`, `cat_name`, `cat_parent`, `cat_author`, `cat_desc`, `timestamp`, `ip`) VALUES (NULL, 'Site news', '', '".$data['username']."', 'This is for general news on your website.', '".time()."','".$_SERVER['REMOTE_ADDR']."');";
    $res = mysql_query($sql);

    $sql = 'INSERT INTO `'.$data['db_tableprefix'].'templates` (`id`, `template_name`, `template_desc`, `template_author`, `timestamp`, `html_article`, `html_comment`, `html_form`, `html_pagination`, `template_selected`) VALUES 
(NULL, "Default", "This is the default phpns template.", "Phpns-team", "1194252704", "&lt;div style=&quot;margin-bottom: 30px; min-height: 130px;&quot;&gt;\r\n &lt;h2 style=&quot;margin-bottom: 0pt&quot;&gt;&lt;a href=&quot;{article_href}&quot; style=&quot;text-decoration: none;&quot;&gt;{title}&lt;/a&gt;&lt;/h2&gt;\r\n  &lt;h4 style=&quot;margin: 0 0 0 3em; font-weight: normal;&quot;&gt;&lt;em&gt;Posted by &lt;a href=&quot;#&quot;&gt;{author}&lt;/a&gt;&lt;/em&gt;&lt;/h4&gt;\r\n &lt;div style=&quot;float:right; padding: 0 0 10px 10px&quot;&gt;{reddit} {digg}&lt;/div&gt;\r\n {main_article}\r\n &lt;div&gt;\r\n  {full_story}\r\n\r\n  &lt;div id=&quot;comments&quot; style=&quot;text-align: right;&quot;&gt;\r\n  &lt;strong&gt;&lt;a href=&quot;{article_href}#comments&quot;&gt;{comment_count} comments&lt;/a&gt;&lt;/strong&gt;\r\n  &lt;/div&gt;\r\n &lt;/div&gt;\r\n&lt;/div&gt;", "&lt;div style=&quot;background: #eee; font: caption; margin: 20px 0 0 5%; padding: 5px;&quot;&gt;\r\n &lt;div style=&quot;border: 1px solid #ccc; padding: 3px; background: #ccc; margin-bottom: 5px;&quot;&gt; \r\n  &lt;div style=&quot;text-align: right; float: right&quot;&gt; {timestamp}&lt;/div&gt;  \r\n &lt;strong&gt;Posted by  &lt;a href=&quot;{website}&quot;&gt;{author}&lt;/a&gt;&lt;/strong&gt; as {ip}\r\n &lt;/div&gt;\r\n {comment}\r\n&lt;/div&gt;", "&lt;div style=&quot;font: caption; margin-left: 5%;&quot;&gt;\r\n&lt;form style=&quot;margin-top: 50px;&quot; action=&quot;{action}&quot; method=&quot;post&quot;&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;name&quot; id=&quot;name&quot; /&gt; &lt;label for=&quot;name&quot;&gt;Name (required)&lt;/label&gt;&lt;br /&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;email&quot; id=&quot;email&quot; /&gt; &lt;label for=&quot;email&quot;&gt;Email (not published) (required)&lt;/label&gt;&lt;br /&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;website&quot; id=&quot;website&quot; /&gt; &lt;label for=&quot;website&quot;&gt;Website&lt;/label&gt;&lt;br /&gt;\r\n&lt;textarea name=&quot;comment&quot; style=&quot;width:100%; height: 150px&quot;&gt;&lt;/textarea&gt;&lt;br /&gt;\r\n&lt;input type=&quot;text&quot; name=&quot;captcha&quot; style=&quot;width: 100px&quot; /&gt; &lt;label for=&quot;captcha&quot;&gt;&lt;strong&gt;What is {captcha_question}?&lt;/strong&gt;&lt;/label&gt;&lt;br /&gt;\r\n{hidden_data}\r\n{captcha_answer}\r\n&lt;input type=&quot;submit&quot; value=&quot;Submit comment&quot; id=&quot;submit&quot; /&gt;\r\n&lt;/form&gt;\r\n&lt;/div&gt;","&lt;a style=&quot;padding: 3px; margin: 10px; border: 1px solid #888;&quot; href=&quot;{previous_page}&quot;&gt;Previous Page&lt;/a&gt; {middle_pages} &lt;a  style=&quot;padding: 3px; margin: 10px; border: 1px solid #888;&quot; href=&quot;{next_page}&quot;&gt;Next Page&lt;/a&gt;", "1");';
    $res = mysql_query($sql) or die(mysql_error());

    $sql = "INSERT INTO `".$data['db_tableprefix']."syslog` (`id`, `task`, `description`, `user`, `page`, `timestamp`) VALUES
(NULL, 'INSTALL', 'User &lt;i&gt;".$data['username']."&lt;/i&gt; has installed phpns!', 0, '/phpns/install/', ".time().")";
    $res = mysql_query($sql);

} //end main (installing) if

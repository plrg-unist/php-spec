<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

$page_desc['permission denied'] = "You do not have access to that feature/page of phpns. The rank you are assigned to specifically states that you don't have permission to continue.";

$page_desc['index'] = "Welcome to the phpns admin area, <strong>".$_SESSION['username']."</strong>. To start, you may want to post a <a href=\"article.php\">new article</a>, or choose a different task on the navigation. Below, you'll find a list of your recent articles, and some statistics.";

// $page_desc['new article'] = "Title, Category, and the Main article are the only required fields. If you would like to edit/delete an article, you'll need to head over to the <a href=\"manage.php\">news management</a> section.";

// $page_desc['preview article'] = "Title, Category, and the Main article are the only required fields. If you would like to edit/delete an article, you'll need to head over to the <a href=\"manage.php\">news management</a> section.";

$page_desc['article success'] = "Congratulations, the article has been successfully created. You can <a href=\"article.php\">create another</a> or edit/delete the article at the <a href=\"manage.php\">news management</a> page.";

$page_desc['article management'] = "Using article management, you can edit/delete/categorize/archive different news articles. If you would like to customize the way your articles are displayed, head over to the <a href=\"preferences.php\">preferences section</a>, or you can modify <a href=\"preferences.php?do=categories\">article categories</a>.";

// $page_desc['edit article'] = "You are editing an article that has been previously posted by you or another user. You can delete comments by clicking the appropriate button below. Do you want to return to <a href=\"manage.php\">article management</a>?";

$page_desc['edit success'] = 'The item has been successfully edited. You can return to the <a href="manage.php">news management</a> page, or go to the <a href="index.php">index</a>.';

$page_desc['user success'] = 'The user has been successfully created. Return to the <a href="user.php">user management</a> page, or go to the <a href="index.php">index</a>.';

$page_desc['edit user'] = 'You are editing a user that has been previously created by you or another user. Depending on your rank permissions, you might need to to wait for approval from an administrator. Return to <a href="user.php">user management</a>?';

$page_desc['login records'] = 'You are viewing login records stored by the phpns system. Only successful logins are recorded, so failed login attempts are not shown. Return to <a href="user.php">user management</a>?';

$page_desc['search'] = 'To search for an article, enter your query below. You can narrow your search based on keyword and category.';

$page_desc['user management'] = "User management lets you create, delete, and edit current users and their settings. You can also modify the ranking system for the system.";

$page_desc['new user'] = "Using this tool, you can create a new user which will have access to the phpns administration panel. Fill out the form below.";

$page_desc['rank management'] = "With rank management, you can assign users to specific 'ranks', which limit what the user can do with the system. Simply create your rank, then create/edit a user with the rank reflected at the user options.";

$page_desc['new rank'] = "To create a new rank, please customize what the members will be allowed to do below. Both the rank title and description are required to continue. Make sure to go over this after you are done, although you can change it later.";

$page_desc['edit rank'] = "You are editing a rank that is active on your system. Changes will take effect only when the user relogs in.";

$page_desc['rank success'] = "The rank has been successfully created. You can <a href=\"user.php?do=ranks\">return to rank management</a>, or <a href=\"user.php?do=newrank\">create another rank</a>.";

$page_desc['preferences'] = "Using this tool, you can modify different aspects of the phpns system. You can edit templates, themes, banning options, RSS, and much more.";

$page_desc['display options'] = "Display options lets you define default attributes that your articles will include automatically. Remember, these are just default values. They can be overwritten individually through includes.";

$page_desc['comment options'] = "Comment options allow you to change default settings for users' comments on your news system. Unlike <a href=\"preferences.php?do=display\">display options</a>, these settings are not overrideable.";

$page_desc['rss options'] = "Rss options allow you to change default settings for how your rss page looks, and how it operates.";

$page_desc['templates'] = "Templates are used to customize <em>how</em> the system displays each news item. You can have multiple templates available, but only one can remain the default. The default template is overrideable before an include.";

$page_desc['template success'] = "The template has been successfully created. You can <a href=\"preferences.php?do=templates\">return to template management</a>, or <a href=\"preferences.php?do=templates&action=new\">create another</a>.";

$page_desc['search engine friendly urls'] = "Phpns supports 'Search Engine Friendly URLs', which can be activated to make your URLs look cleaner to you, your visitors, and search engines that might explore your website. You can activate SEF URLs by putting the variable".' $mod_rewrite = TRUE'.".";

$page_desc['ban options'] = "You can easily ban (or disallow) a user from viewing the content in your installation. If you ban a user below (using their IP address), they will not be able to see any articles on the system.";

$page_desc['integration wizard'] = "The integration wizard is a customization walkthrough that will let generate a configured 'code' that you can use for your website.";

$page_desc['system log'] = "The system log records every action taken by any user of the system. You can choose to deactivate the logging feature, but individual logs cannot be deleted.";

$page_desc['system timestamp format'] = "The system timestamp option will allow you to display 'how' the timestamp is dispayed in human-readable format.";

$page_desc['online/offline options'] = "This feature will let you restrict <strong>all</strong> users from accessing the articles on your website. If you want to prevent a single (or group of) user(s) from accessing your website, head over to the <a href=\"preferences.php?do=ban\">ban options</a>.";

$page_desc['wysiwyg editor'] = "A WYSIWYG (what you see is what you get) editor is the editor used for entering data into <textarea>s throughout the system. You can choose between editors below, or just simply turn the feature off.";

$page_desc['database backup'] = "Using database backup, you can easily and safely backup (and restore) your phpns articles. We recommend backing up your database at least once a month, in order to ensure the safety of your data.";

$page_desc['wysiwyg options'] = "A WYSIWYG (What-You-See-Is-What-You-Get) editor is a feature which will enhance the textareas throughout the phpns system. Javascript is required for this feature to work.";

$page_desc['global message'] = "The global message is a simple notice that will appear on every page of phpns. You can use this to inform users of an important announcement, update, or just to say hello.";

$page_desc['themes'] = "Using the theme management tool, you can configure/administer the themes that are located in your /themes/ folder. You can have multiple themes installed, but only one may remain as the 'active' theme.";

$page_desc['categories'] = "Categories act like 'folders' for your articles. They are used to organize your articles into groups which can be controlled as a whole. Sub-categories are allowed. ";

$page_desc['about'] = "Phpns has been in development since the summer of '06, and has become a scalable and powerful system since it's first concept.";

//end page descriptions. You can null out any description you don't want viewed by simply putting a '//' before the array key.

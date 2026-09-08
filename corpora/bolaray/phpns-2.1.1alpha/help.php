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
	<title>phpns : help</title>
	<style type="text/css" media="all">
		h3 {
			background: #333;
			color: white;
			padding: 20px;
			margin: 20px -8px;
		}
		h4 {
			background: #ccc;
			padding: 10px;
			color: #333;
			margin: 10px -8px 10px 20px;
			}
		pre {
			background: #eee;
			margin-left: 5%;
			border: 1px solid #999;
			border-left: 5px solid #999;
			width: 70%;
			padding: 2px;
		}
	</style>
</head>
<body>
	<h1>phpns help</h1>
	<h2>general documentation and manual</h2>
	<p>The phpns documentation aims to help you accomplish certain tasks
	with the phpns software. Click a task below for additional information.</p>
	
	<h4>topics</h4>
	<ul>
		<li><a href="#index">index</a></li>
		<li><a href="#new article">new article</a></li>
		<li><a href="#article management">article management</a></li>
		<li><a href="#user management">user management</a></li>
		<li><a href="#preferences">preferences</a></li>
		<li><a href="#about">about</a></li>
	</ul>
	<h3 id="success">success help</h3>
	<p>You have successfully completed the action you were trying to accomplish. If it doesn't appear to be successful, please let us know at <a href="http://launchpad.net/phpns">our bug tracking system (Launchpad)</a>.
	
	<h3 id="error">error help</h3>
	<p>The action we attempted failed. Usually, the administration interface will give you a reason for the error. If it doesn't make sense, or you think it's a bug, please <a href="http://launchpad.net/phpns">let us know</a>.
	
	<h3 id="including your news">including your news</h3>
		<h4>Phpns includes a wizard to automate this, available at the preferences panel > integration wizard.</h4>
	<p>phpns and it's features are worthless if you can't display your work to the world. You 
	can "include" your news on any php document throughout the server, in all different forms. 
	Phpns includes an integration wizard in the preferences section, however, if you wish to do 
	it by hand, we'll help you here.</p>
	<p>The easiest and quickest way to display your news on your website is to follow these steps:</p>
	<ol>
		<li>Open up the PHP document you wish to have the news 'display' in.</li>
		<li>Paste the following code:
			<pre>
<?php
    echo highlight_string("<?php
	include('path/to/shownews.php');
?>", 1);
?>
</pre>
			You will need to modify the code above to reflect the actual path of the shownews.php file.
		</li>
		<li>Save and exit the document</li>
		<li>Upload it to your server (if necessary)</li>
	</ol>
	<p>This method will give you the default settings, specified in the <a href="preferences.php?do=wizard">preferences of the administration panel</a>. If this is fine for you, then you're done. However, if you want additional customization, continue reading.</p>
	
	<h4>Additional variables</h4>
	<p>Phpns will allow you to specify additional variables, for more advanced generation.</p>
		<ul>
			<li>$limit - The number of items to be listed. Ex: 100</li>
			<li>$template - The ID number of the template to use. Ex: 5</li>
			<li>$category - The ID number of the category you wish to filter. Ex: 1,2,3,4,5</li>
			<li>$mode - RSS feed. Using this variable MUST be used on a blank file. So, if you have rss.php, it must ONLY include the phpns code. No other HTML/CSS. Ex: "rss"
			<li>$offset - The offset starting point. If you specify 1, it will skip 1, and then display 2-$limit. Ex: 4</li>
			<li>$order - The order in which the articles are listed. Ex. "desc" or "asc" for descending and ascending respectively
			<li>$disable_pagination - Will not display pagination links. Ex: TRUE</li>
			<li>$items_per_page - # of articles per page (in pagination). Will be ignored if pagination is disabled. Ex: 5</li>
			<li>$sef_override - Override SEF detection, advanced users only. Force SEF URLs. Ex: TRUE</li>
			<li>$comment_override - This will disable comments on every article, regardless of other settings.</li>
			<li>$static - Using this variable will always display the article list, NEVER a single article. Use this if you have moroe than one phpns includes on a single page.</li>
			<li>$disable_extended_article - Any article will  be displayed WITHOUT the extended article portion.</li>
		</ul>
		We can apply these variables (you can use any of them, none of them, all of them, or some of them):
		<pre>
<?php
    echo highlight_string('<?php
	$limit = 5;
	$category = 1,4,5,6,7;
	$template = 4;
	$offset = 2;
	$mode = \'RSS\';
	include(\'path/to/shownews.php\');
?>', 1);
?>
</pre>
	
	<h3 id="index">index help</h3>
	<p>The phpns index is the main page which you are directed to after logging in. 
	At the top of the page, you'll find multiple links to post a new item, manage 
	current items, manage the phpns users, modify your preferences, and read the 
	phpns about page.</p>
	<p>Displayed below the page description, you'll find an information section, which 
	contains two different sections: statistics, and recent articles. Both are pretty 
	straight forward. You will notice the help hyperlink at the bottom right area of 
	the page, which can be clicked to view certain help topics (the guide you are viewing 
	now!).</p>
	
	<h3 id="new article">new article help</h3>
	<p>posting a new item is fairly straightforward with phpns. Click the 'new article' 
	link in the admin navigation. Once you are at the page, you should see a short 
	description, along with an HTML form. A list of the fields are below:</p>
	<ul>
		<li>article title | <span style="color: red">required</span></li>
		<li>article sub-title | <span style="color: green">optional</span></li>
		<li>article category | <span style="color: red">required</span></li>
		<li>main article | <span style="color: red">required</span></li>
		<li>full story | <span style="color: green">optional</span></li>
		<li>article image | <span style="color: green">optional</span></li>
		<li>start date | <span style="color: green">optional</span></li>
		<li>end date | <span style="color: green">optional</span></li>
		<li>disable comments | <span style="color: green">optional</span></li>
		<li>save as draft | <span style="color: green">optional</span></li>
	</ul>
	
	<h5>article title</h5>
	<p>the title can contain any character, and has a limit of 100 characters. Example: My first post!</p>
	
	<h5>article sub-title</h5>
	<p>the sub-title can contain any character, and has a limit of 100 characters. Example: and why I love this cms...</p>
	
	<h5>article category</h5>
	<p>the article category is very important, and currently you can only have one (1) category per article. We plan to change this in a future release...</p>
	
	<h5>main article</h5>
	<p>the main article is the most important element in article items. Limit of 20,000 characters.</p>
	
	<h5>full story</h5>
	<p>the rest of the article. this is optional! Limit of 20,000 characters.</p>
	
	<h5>article image</h5>
	<p>100px by 100px image representing the article content. optional. Accepts jpg, png, gif, and bmp.</p>
	
	<h5>start date</h5>
	<p>A more obscure feature of phpns. You can specify when a date will become visable on your website. The 
	format must be in the following order: "MM/DD/YYYY". The date is converted to a Unix timestamp, and stored 
	in the database. Leave this field blank if you wish to start the article immediately.</p>
	
	<h5>end date</h5>
	<p>A more obscure feature of phpns. You can specify when a date will stop being visable on your website. The 
	format must be in the following order: "MM/DD/YYYY". The date is converted to a Unix timestamp, and stored 
	in the database. Leave this field blank if you wish to never end the article.</p>
	
	<h5>disable comments</h5>
	<p>Check this box if you wish to disallow comments for this specific article. THIS WILL ONLY affect this 
	article, it will not affect any other item.</p>
	
	<h5>save as draft</h5>
	<p>Check this box if you don't want the article to appear publicly. This is a useful feature if you are 
	working on a long post, or if you want other people to modify the article before it goes live.</p>
	
	
	<h3 id="article management">article management help</h3>
		<p>article management allows you to view the articles you have posted in different ways, orders, and with conditions. By default, articles are listed in a descending date order. That means, the latest article that has been created will be shown at the TOP of the news management table. Although this might suite you, sometimes you may require ordering in a different way, scroll down to sorting options.</p>
		
		<h4>Search</h4>
			<p>Searching is really easy with phpns. At the top of article management, you will see a hyperlink named 'search' (with an expand/collapse option). Expand the search section, and you're presented with 2 fields: your query, and category. Whatever text you enter in the query box (the box with the text 'click here to start your search'), is the text we'll search for in every active article to date. The system will scan the title, subtitle, main article, and full story for that query entered. You also have the option to narrow your search by category. By default, it will search in all categories.</p>
		
		
		<h4>Sorting options</h4>
			<p>The article list can be sorted in various ways, so you can walk through your database articles easily. You have the following sorting options, which you can activate by clicking at the top of each column of the table.</p>
		<h5>Sort by date</h5>
		<p>This will allow you to sort the articles based on the time they were posted. Descending is the default sorting order, however, you may also set this to ascending.</p>
		
		<h5>Sort by title name (alphabetically)</h5>
		<p>This will allow you to sort the articles based on the articles' title. Ascending will order it from 0-9,A-Z. Descending will reverse the order.</p>
		
		<h5>Sort by author</h5>
		<p>This will allow you to sort the articles based on the author of the article. Ascending will sort the articles based on the name of the author, in alphabetical order. Therefore, ascending would present: Alan, Billy, Caty, George, Veronica, Zack. Descending would reverse the order.</p>
		
		<h5>Sort by Active or Activity</h5>
		<p>This will allow you to sort the articles based on their status as active or unactive. This is very useful for weeding out articles that have been dormant for a long time.</p>
		
		<h4>Other uses</h4>
		<h5>View articles by a certain author</h5>
		<p>You can view all the articles posted by a specific user. While viewing articles, you can simply click on the username in the column "Author", and it will load up a selection of articles by that selected author.</p>
		
		<h5>View articles by category</h5>
		<p>You can do the same thing with the author, except clicking on the category next to any article. It will bring up a list of articles posted in that category.</p>
		
		
	<h3 id="user management">user management help</h3>
		<p>User management is a tool which lets you control and see various users on your installation, like creating new users, editing users, deleting users, and viewing different aspects of users.</p>
		<p>By default, the user management page will show a list of options, and a list of users with their information. The table which lists users has the following information:
		<ul>
			<li>username - what the user's username is</li>
			<li>full name - the full name of the user</li>
			<li>date - the date the user was created</li>
			<li>rank - the current rank of the user. You can click on the rank to edit the rank.</li>
			<li>#/articles - displays the current number of articles created by the user. You can click this do display the users.</li>
		</ul>
		<h5>new user</h5>
		<p>Each user must have a <strong>unique username</strong>. A full list of required and optional fields are listed below:</p>
		<ul>
			<li>username [required]</li>
			<li>full name [required]</li>
			<li>password [required]</li>
			<li>confirm password [required]</li>
			<li>email</li>
			<li>msn</li>
			<li>aim</li>
			<li>yahoo</li>
			<li>skype</li>
			<li>rank</li>
		</ul>
		
	<h3 id="preferences">preferences help</h3>
	<p>The preferences area will give you the ability to modify many different aspects of your phpns system. The different tasks you can accomplish are listed below:</p>
	
	<h4>general display options</h4>
	<p>Here, you can set the 'default' values for how your news is displayed to your visitors/viewers. You can set the following:
		<ul>
			<li>Display offset - This is how many articlces are omitted before we start displaying. In other words, this is the number of items that will be 'skipped' by default.</li>
			<li>Date format - This is the default date format which will be used to translate the article timestamp to a human-readable format. It uses the <a href="http://php.net/date">php date();</a> function, you can use that page for reference.</li>
			<li>Display limit - This is how many articles are displayed to the end user.</li>
			<li>Reverse items - You can reverse the order in which the articles appear to the end user. Descending will place the newest articles at the top. Ascending will put the oldest at the top.</li>
		</ul>
	
	<h4>category management</h4>
	<p>Category management will let you create categories and sub-categories in which to file your articles in. You can think of categories like 'folders' in a file system. When you create a new article, you will choose a category in which to place the article into, and later, you can 'filter' the articles (by category) to the end-user.</p>
	
	<h4>template management</h4>
	<p>Templates let you control how your articles are displayed to the end-user. Your template will have 5 fields; a title/name, description, article template, comment template, and comment form. You can set a default template (set at 'Default' during installation) which will appear to the user. You can have multiple templates, and you can use multiple templates at the same time by using extra variables while including your news.</p>
	
	<p>There are multiple variables that you can use in the templates, specified by using {}s. There is a list of them below:</p>
	<h5>Main article variables</h5>
	<ul>
		<li>{title} = article title</li>
		<li>{subtitle} = subtitle</li>
		<li>{date} = timestamp/date</li>
		<li>{image_src} = article image src. (ex: &lt;img src="{image_src}" alt="{title}" /&gt;
		<li>{main_article} = main article</li>
		<li>{full_story} = full story</li>
		<li>{comment_count} = The number of articles this article has</li>
		<li>{author} = author</li>
		<li>{article_href} = the link to the article, but the actual href value</li>
		<li>{reddit} = reddit social networking link</li>
		<li>{digg} = digg social networking link</li>
	</ul>
	<h5>Comment variables</h5>
	<ul>
		<li>{author} = comment author</li>
		<li>{website} = website</li>
		<li>{comment} = comment</li>
		<li>{date} = comment date</li>
		<li>{ip} = comment ip address</li>
	</ul>
	<h5>Comment form variables</h5>
	<p>Please include ALL of the data in the form, or else things won't work.</p>
	<ul>
		<li>{action} = value that goes inside the form</li>
		<li>{hidden_data} = required value somewhere inside the form</li>
		<li>{captcha_question} = In plain text, the question</li>
		<li>{captcha_answer} = The answer encoded and passed through form</li>
	</ul>
	<h5>Pagination variables</h5>
	<ul>
		<li>{previous_page} = previous page number (ex: &lt;a href="{previous_page}"&gt;)</li>
		<li>{middle_pages} = middle pages, includes links already</li>
		<li>{next_page} = next page number</li>
	</ul>
	
	<h4>rss management</h4>
	<p>The rss management lets you set different aspects on the RSS feed phpns generates. You can set the title, description, online status, item limit and order.</p>
	
	<h4>search engine friendly urls</h4>
	<p>SEF URLs are goverened by an apache module known as 'mod_rewrite'. Phpns takes advantage of this module, however, it's still very limited. If you want to activate SEF urls, you will need to copy and paste the .htaccess code (found in preferences > search engine friendly urls) into your website directory. If it's not working, we don't recommend messing with the files or the .htaccess file, as it might break the system.</p>
	<p>If you're having troubles, or you need help, please visit the IRC (irc.freednode.net / #phpns).</p>
	
	<h4>comment options</h4>
	<p>You can set several default options here: If (by default) users can post comments, the order of the comments, and the comment character limit.</p>
	
	<h4>ban options</h4>
	<p>You can ban (IP ban) users who you don't want viewing your articles or posting comments by banning their IP address. In this section, you can provide their IP address, and a reason for the ban. When that user/IP visits your website, they will be presented a message with a reason for their ban.</p>
	
	<h4>integration wizard</h4>
	<p>The integration wizard will let you (easily) generate 'code' for you to copy/paste into your website. It should be good to go, you shouldn't have to modify anything.</p>
	
	<h4>system log</h4>
	<p>The system log will log (almost) every action taken by any user. All the information collected will be stored in this page, so you can view it, and see what users have been doing on your system.</p>
	
	<h4>image uploads and settings</h4>
	<p>This feature is not functional yet, wait until alpha 2.</p>
	
	<h4>database backup</h4>
	<p>This feature will let you backup the data in your database to a file. Just click the backup button, and wait until the file is processed by the server. Once it's done, the server will send you the .sql file that can be downloaded. Once you're done, and navigate to another page on phpns, you will see a notice at the top of the administration panel asking you to delete the file asap. PLEASE DO SO, it's a hazard to leave it untouched. <strong>Phpns will *try* to delete the file every time you visit the index.php page. If it works, you won't see the message anymore.</strong> Upload the file later, to replace the old database and replace it with the downloaded file.</p>
	
	<h4>online/offline options</h4>
	<p>Phpns can turn the whole news system on or off for the end-user. If this is set to offline, the user will not be able to see any article/category/comment in the system.</p>
	
	<h4>theme options</h4>
	<p>Themes let you customize how the phpns is presented to adminstrators. You can have as many themes as you want available, but only one theme (or skin, if you would prefer) can remain active. We will provide additional help on the phpns website.</p>
	
	<h4>wysiwyg editor</h4>
	<p>Phpns uses a WYSIWYG editor to replace all textareas on the system to a customizeable, active and complete editor. Phpns uses the <a href="http://tinymce.moxiecode.com/">TinyMCE wysiwyg editor</a> released under the <a href="inc/wysiwyg/license.txt">Lesser GPL</a> as published by the <a href="http://fsf.org">Free Software Foudation</a>.
	
	<h4>timestamp options</h4>
	<p>The system timestamp format will be used on every timestamp recorderd by phpns on the administration panel. You can see the <a href="http://php.net/date">php date function</a>.</p>
	<p>Note: This does not affect the shownews.php file.</p>
	
	<h4>disable logging in</h4>
	<p>This feature is not implimented yet.</p>
	
	<h4>delete login records</h4>
	<p>Deletes all login records in user management.</p>
	
	<h4>rank management</h4>
	<p>You can manage/create/delete ranks created.</p>
	
	<h4>global message</h4>
	<p>The global message is used to notify fellow administrators of any important messages... or announcements that login to the administration panel. You can leave the global message blank to nullify the message.</p>
	
	<h3 id="about">about help</h3>
	<p>The about page lists many pieces of information that you will find helpful in regards to the phpns project. Please look through the page, and if you feel like it's missing vital information, please tell us!</p>
	<p>The latest articles and version check require you to be connected to the internet, so it can access the phpns website. It's provided purely for your convienence.</p>
</body>
</html>

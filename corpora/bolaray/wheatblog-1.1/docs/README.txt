===============================================================================
Wheatblog (wB) 1.1 -- README.txt (revised 7/30/06)
===============================================================================

Overview
		This file contains information about the wB project as well as 
		installation instructions for setting up wB on your website.  Other 
		support information is available through the project website.

The Development Team
		James Martin, project admin + developer
		wheat@wheatdesign.com  
		http://www.wheatdesign.com/
		
		Peter Jay Salzman, developer
		p@dirac.org
		http://dirac.org/
		
		Joshua Estell, developer & template designer
		hink@hinkybox.com
		http://www.hinkybox.com

The Project Homepage
	http://wheatblog.sourceforge.net

Description
		wB is blogware:  it's a web-based content management system for 
		maintaining online blogs, journals, and news pages.  It allows comments 
		and generates RSS feeds.  wB is database driven.  It provides comment spam 
		protection.  It is powered by PHP and is compatible with you choice of MySQL 
		or SQLite database servers.   

Requirements
		wB requires a PHP-compatible webserver (i.e. Apache, etc.) and either a 
		MySQL or an SQLite database server.  

License
		Wheatblog App is free as in freedom and free as in free beer.  It is 
		released under the GNU Public License (GPL).  You can read about the license 
		at http://www.gnu.org.  A copy is included in with the distribution.  

Features
		* simple installation and use
		* supports MySQL and SQLite
		* pages are dynamically created
		* posts can have titles, but these are not required
		* posts can be assigned to categories and viewed by category
		* posts have permalinks
		* posts can have comments (these can be turned on/off for each post)
		* comment spam protection (via CAPTCHA) helps keep the spambots away
		* posts can be marked to show or to hide
		* all post dates are arbitrary (not based on timestamp)
		* generates RSS 2.0 feeds of your recent posts
		* number of recent posts on your front page can be set in the prefs
		* inclues an assortment of valid XHTML/CSS design templates
		* blogroll/link manager utility included  
		* it's open source, so you can hack it to suit your needs

Brief Version History
		 .01b -- 02/2001 -- Initial release
		 .02b -- 04/2004 -- Complete rewrite
		 .03b -- 04/25/2004 -- RSS improvements + added "by title" archive view
		 .05b -- 03/11/2005 -- Major improvements
		1.0   -- 10/10/2005 -- Major improvements 
		1.1   -- 07/31/2006 -- Minor improvements + added comment spam protection

ChangeLog
	See CHANGELOG.txt for a full version history of changes and known issues

History of the Project
	See HISTORY.txt for background on this project

Installation
		1. Upload everything to a directory in the document root of your 
		webserver.  If the URL of your website is http://example.com and you 
		install wheatblog in a directory called "blog" then the URL to your blog 
		will be http://example.com/blog/  
		
		2. Change permissions on rss.xml to 777 so that your webserver can write 
		to the RSS file (chmod 777 settings.php).  If the rss.xml file does not 
		exist in your blog directory, create it (touch rss.xml) and then set its 
		permissions.  
		
		3. Edit the settings.php file.  Follow the directions in the comments.  The 
		following variables are essential and must be set for the app to work.  
		You can take the defaults on everything else, assuming you use MySQL:
		
				$site			= database connection site (often "localhost")
				$user			= database connection user
				$pass			= database connection password
				$wb_dir	  = file path to your wheatblog install directory
				$wb_url   = URL to your wheatblog install directory
		
		4. Set up your database.  The necessary SQL can be found in the "tools" 
		directory.  Use the appropriate file for your database server 
		(wheatblog-mysql.sql for MySQL or wheatblog-sqlite.sql for SQLite).  
		
			If you are using phpMyAdmin to manage your databases, do the 
			following:
				a. Open wheatblog-mysql.sql in your favorite editor
				b. Delete or comment out the first line and save
				c. Log in to phpMyAdmin, 
				d. Select/create your new database
				e. Click the "SQL" tab, 
				f. Paste the contents of the appropriate SQL file into the 
					 "Run SQL query/queries on database" window
				g. Press the "Go" button.  
		
		5. Load your site in a web browser
		
		6. Log into the admin account using the default user (admin) and the 
		default password (password).  Select "admin page" for the 
		"Administration" menu and "Manage Users" to change your admin username 
		and/or password.  
		
		7. Select "add post" from the "Administration" menu and test it out!

Tweaking the CSS and Other Design Aspects
		wB is CSS driven.  All of the files associated with the templates are in 
		the "css" folder and its subfolders (especially the "elem" subfolder).  
		
		wB makes extensive use of headers and footers.  These control many 
		global aspects of the application. They can be found in the "includes" 
		folder.

Getting Help
		If you encounter problems setting up or using wB or have any questions 
		about it, there are several resources availible:
		
			1. The project website:  
					 http://wheatblog.sf.net
			2. The wheatblog-users mailing list:  
					 http://sourceforge.net/mail/?group_id=22229
			3. The bugs, support request, and feature request tracking system:
					 http://sourceforge.net/tracker/?group_id=22229
			4. The forums:
					 http://sourceforge.net/forum/?group_id=22229
			4. The developers (via email)  

Credits and Thanks
		Thanks to Steven Jarvis for the RSS generation code which is the 
		basis of includes/rss.php.  See the comments in that file for details
		
		Thanks to Daniel Foster at meezerk.com for the GPL captcha code used in 
		captcha.php view_by_permalink.php and add_comment.php.  See the comments in 
		captcha.php for details.  
		
		Thanks to Josh and Pete for all their hard work on this project.
		
		Thanks to everyone who donated money or code to the project or who uses it 
		on a site. 
		
Support the cause
		If you enjoy using wB, consider making a donation to the project:  
		http://sourceforge.net/donate/index.php?group_id=22229

===============================================================================
Wheatblog (wB) 1.1 -- README.txt
===============================================================================

# phpMyAdmin MySQL-Dump
# version 2.3.2m
# http://phpwizard.net/phpMyAdmin/
# http://www.phpmyadmin.net/ (download page)
#
# Host: localhost
# Generation Time: February 22, 2003 at 00:15 AM
# Server version: 4.0.0-alpha-nt
# PHP Version: 4.3.3
# Database : `mysql`
# --------------------------------------------------------

#
# Table structure for table `phpnews_banned`
#

CREATE TABLE phpnews_banned (
  id int(4) unsigned NOT NULL auto_increment,
  ip varchar(80) NOT NULL,
  timesbanned tinyint(3) NOT NULL default '0',
  isbanned tinyint(1) NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

#
# Dumping data for table `phpnews_banned`
#

INSERT INTO phpnews_banned VALUES (1, '123.4.5.6', '1', '1');
# --------------------------------------------------------

#
# Table structure for table `phpnews_comments`
#

CREATE TABLE phpnews_comments (
  id int(11) unsigned auto_increment,
  ip varchar(80) NOT NULL,
  mid int(11) NOT NULL,
  time bigint(20) NOT NULL,
  name varchar(40) NOT NULL,
  message text NOT NULL,
  email varchar(50),
  website tinytext,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

#
# Table structure for table `phpnews_news`
#

CREATE TABLE phpnews_news (
  id int(11) unsigned NOT NULL auto_increment,
  posterid int(5) NOT NULL default '0',
  postername varchar(80) NOT NULL default '',
  time bigint(20) NOT NULL default '0',
  month int(2) NOT NULL default '0',
  year int(4) NOT NULL default '0',
  subject tinytext NOT NULL,
  titletext text NOT NULL,
  maintext text NOT NULL,
  break tinytext NOT NULL,
  catid int(11) NOT NULL default '0',
  trusted tinyint(1) default '1',
  views int(11) NOT NULL default '0',
  PRIMARY KEY  (id),
  KEY trusted (trusted),
  KEY trusted_2 (trusted),
  KEY catid (catid)
) TYPE=MyISAM;

#
# Table structure for table `phpnews_categories`
#

CREATE TABLE phpnews_categories (
  id int(3) unsigned NOT NULL auto_increment,
  catname varchar(40) NOT NULL,
  caticon tinytext NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

#
# Dumping data for table `phpnews_categories`
#

INSERT INTO phpnews_categories VALUES (1, 'General', '');
# --------------------------------------------------------

#
# Table structure for table `phpnews_posters`
#

CREATE TABLE phpnews_posters (
  id int(5) unsigned auto_increment,
  username varchar(40) NOT NULL default '',
  password varchar(50) NOT NULL,
  email varchar(50),
  avatar tinytext,
  language varchar(10),
  access varchar(20) NOT NULL,
  PRIMARY KEY  (id)
) TYPE=MyISAM;

#
# Dumping data for table `phpnews_posters`
# The password here is "admin"

INSERT INTO phpnews_posters VALUES (1, 'admin', '43e9a4ab75570f5b', 'admin@admin.com', '', 'admin');
# --------------------------------------------------------

#
# Table structure for table `phpnews_settings`
#

CREATE TABLE phpnews_settings (
  variable char(20) NOT NULL,
  value text NOT NULL
) TYPE=MyISAM;

#
# Dumping data for table `phpnews_settings`
#

INSERT INTO phpnews_settings VALUES ('sitename', 'My Site');
INSERT INTO phpnews_settings VALUES ('phpnewsurl', 'http://mysite.com/phpnews/');
INSERT INTO phpnews_settings VALUES ('siteurl', 'http://mysite.com/');
INSERT INTO phpnews_settings VALUES ('language', 'en_GB');
INSERT INTO phpnews_settings VALUES ('numtoshow', '8');
INSERT INTO phpnews_settings VALUES ('numtoshowhead', '5');
INSERT INTO phpnews_settings VALUES ('enablestf', '1');
INSERT INTO phpnews_settings VALUES ('enablesmilies', '1');
INSERT INTO phpnews_settings VALUES ('enableavatars', '0');
INSERT INTO phpnews_settings VALUES ('commentsperpage', '5');
INSERT INTO phpnews_settings VALUES ('enablecensor', '0');
INSERT INTO phpnews_settings VALUES ('enableprevnext', '0');
INSERT INTO phpnews_settings VALUES ('enablecomments', '1');
INSERT INTO phpnews_settings VALUES ('enablebbcode', '1');
INSERT INTO phpnews_settings VALUES ('enablerss', '1');
INSERT INTO phpnews_settings VALUES ('manualrss', '1');
INSERT INTO phpnews_settings VALUES ('showcominnews', '0');
INSERT INTO phpnews_settings VALUES ('showoldcomfirst','0');
INSERT INTO phpnews_settings VALUES ('enablecommentpages', '0');
INSERT INTO phpnews_settings VALUES ('commentsperpage', '5');
INSERT INTO phpnews_settings VALUES ('enablecats', '0');
INSERT INTO phpnews_settings VALUES ('numtoshowcat', '0');
INSERT INTO phpnews_settings VALUES ('floodprotection', '15');
INSERT INTO phpnews_settings VALUES ('timeoffset', '0');
INSERT INTO phpnews_settings VALUES ('timeformat', '%B %d, %Y, %I:%M:%S %p');
INSERT INTO phpnews_settings VALUES ('shorttimeformat', '%d %B, %Y');
INSERT INTO phpnews_settings VALUES ('censorlist', '');
INSERT INTO phpnews_settings VALUES ('enableimgupload', '1');
INSERT INTO phpnews_settings VALUES ('imguploadpath', 'images/');
INSERT INTO phpnews_settings VALUES ('uploadfiles', '6');

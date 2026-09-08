CREATE TABLE wbtbl_categories
(
	id                   integer      serial primary key,
	category             varchar(30)  not null default ''
);

INSERT INTO wbtbl_categories (id, category)
	VALUES (null, 'unfiled');


CREATE TABLE wbtbl_comments
(
	id                   serial primary key,
	comment_author_name  varchar(100) not null default '',
	comment_author_email varchar(100) not null default '',
	comment_author_url   varchar(100) not null default '',
	post_id              integer(11)  not null default '0',
	comment_month        integer(2)   not null default '0',
	comment_date         integer(2)   not null default '0',
	comment_year         integer(4)   not null default '0',
	comment_body         varchar      not null,
	timestamp            varchar      not null
);


CREATE TABLE wbtbl_links (
	id                   integer     not null    serial primary key,
	link_name            varchar(30) not null    default     'name',
	link_location        varchar(50) not null    default     'http://'
);

INSERT INTO wbtbl_links (id, link_name, link_location)
   VALUES (null, 'wheatblog app', 'http://wheatblog.sourceforge.net');


CREATE TABLE wbtbl_posts
(
	id                   integer primary key,
	title                varchar(100)          default '',
	day                  varchar(10)           default '',
	month                integer(2)   not null default '0',
	date                 integer(2)   not null default '0',
	year                 integer(4)   not null default '0',
	category             integer(1)   not null default '1',
	showpref             boolean      not null default '1',
	locked               boolean      not null default '0',
	comments             integer(11)  not null default '0',
	body                 varchar      not null,
	timestamp            varchar      not null
);


CREATE TABLE wbtbl_users (
	login                varchar(12)  not null primary key,
	password             varchar(12) not null,
	flags                integer(2)  not null,
	www                  varchar(50),
	email                varchar(30)
);

INSERT INTO wbtbl_users (login, password, flags)
	VALUES ('admin', 'password', 1);



CREATE TABLE wbtbl_settings (
	var                  varchar(20) not null primary key,
	val                  varchar(60),
	descrip              varchar(255)
);

INSERT INTO wbtbl_settings ( var, descrip )
VALUES (
		'wb_dir',
		'The directory that Wheatblog is installed.  Should be a directory pathname on your filesystem without a trailing slash'
);

INSERT INTO wbtbl_settings ( var, descrip )
VALUES (
		'wb_admin_dir',
		'The directory that Wheatblog''s admin directory is installed.  Should be a directory pathname on your filesystem without a trailing slash'
);

INSERT INTO wbtbl_settings ( var, descrip )
VALUES (
		'wb_url',
		'The URL of your blog (eg http://myblog.org) without a trailing slash.'
	);

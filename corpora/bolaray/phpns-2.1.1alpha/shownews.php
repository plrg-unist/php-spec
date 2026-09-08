<?php

//error_reporting( E_ALL | E_STRICT ); //DEBUGGING, uncommment to activate

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/

/* This file will need little to NO modification. All customization can be done
before including the file, using pre-set variables. If you need to make modifications
to this file, it's important to comment your code. This is obviously the most important
file in the system, so understanding it is important. All functions are defined here are
seperate from the main system (for security reasons.)

-- Alec Henriksen (http://phpns.com | http://alecwh.com)
*/

/* Optional variables that can be called before user include:
   * $limit = 1-9999
   * $template = template_id
   * $category (multiple) = ID Number(s) (seperated by commas (cat1, cat2, cat3))
   * $mode (RSS) = RSS, XML, ATOM
   * $offset = 1-9999
   * $sef_override = TRUE/FALSE;
   * $comment_override = TRUE/FALSE;
   * $static = TRUE/FALSE;
*/

//define some variables, immediately protect against injection

$do = htmlentities($_POST['do']);
if (!$do && !strstr($_GET['a'], 'page:')) {
    $id = htmlentities($_GET['a']);
}
$mode = htmlentities($mode);
$offset = htmlentities($offset);

//generate current time, used globally
$time = time();
$ip = $_SERVER['REMOTE_ADDR'];

//before continuing, protect from injection
if ($sef_override == false) {
    if (!is_numeric($id) && $id && $id != 'do=rss') {
        $inject_error = '
			<h1>stop!</h1>
			<hr />
			ID paramater used: <strong>'.$id.'</strong>
			<p>Phpns has detected a possible security breach, or a mal-formed URL. The ID paramater cannot contain a letter in non-SEF mode.</p>
		';
        die($inject_error);
    }
} else {
    $mod_rewrite = true;
    if ($id && substr($id, strlen($id)-1, 1) == '/') {
        $id = substr_replace($id, "", -1);
    }
}

//include database information
@require("inc/config.php");
//connect.
$mysql['connection'] = mysql_connect($databaseinfo['host'], $databaseinfo['user'], $databaseinfo['password'])
or die($error['connection']);
//select mysql database
$mysql['db'] = mysql_select_db($databaseinfo['dbname'], $mysql['connection'])
or die($error['database']);

//define show_news functions, and check if functions are already defined.
if (!function_exists('clean_data')) {
    function clean_data($data)
    {
        if (is_array($data)) {
            foreach ($data as $key => $value) {
                if(ini_get('magic_quotes_gpc')) {
                    $data[$key] = stripslashes($value);
                }
                $data[$key] = htmlspecialchars($value);
            }
        } else {
            if(ini_get('magic_quotes_gpc')) {
                $data = stripslashes($data);
            }
            $data = htmlspecialchars($data, ENT_QUOTES);
        }
        return $data;
    }
}
if (!function_exists('decode_data')) {
    function decode_data($data)
    {
        if (is_array($data)) {
            foreach ($data as $key => $value) {
                $data[$key] = htmlspecialchars_decode($value);
            }
        } else {
            $data = htmlspecialchars_decode($data);
        }
        return $data;
    }
}
if (!function_exists('db_fetch')) {
    function db_fetch($query, $type, $clean=null)
    {
        //echo '<textarea width="100%">'.$query.'</textarea>'; //debugging, this will output every query.
        if ($clean == true) {
            $query = clean_data($query); //clean
        }

        $res = mysql_query($query) or die(mysql_error().'<br /><br />Line '.__LINE__.'<br /><br /> query: '.$query.'');
        //return value or not?
        if ($type == 1) { //if we want a value
            $value = mysql_fetch_array($res) or die('fetch array failed, line: '.__LINE__.', query: '.$query.'<p>'.mysql_error().'');
            return $value;
        } else {
            return $res;
        }
    }
}
if (!function_exists('db_insert')) {
    function db_insert($query)
    {
        //sql construction
        $insert_res = mysql_query($query) or die(mysql_error());
        $affected = mysql_affected_rows();
        return $affected;
    }
}
if (!function_exists('fetch_template')) {
    function fetch_template() //figure out default template, or use a user defined one.
    {
        global $databaseinfo; //for table prefix
        global $template;

        if (!$template) {  //if template is not defined by pre-var include... get default
            $res = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."templates WHERE template_selected='1' LIMIT 1", 1);
            return $res; //return default template (changeable in preferences)
        } else {
            $res = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."templates WHERE id=".$template." LIMIT 1", 1);
            return $res;
        }
    }
}
if (!function_exists('translate_item')) {
    function translate_item($item, $template, $type)
    {
        global $id;
        /*
        HTML_ARTICLE:
            {title} = article title
            {subtitle} = subtitle
            {date} = timestamp/date
            {main_article} = main article
            {full_story} = full story
            {image} = article image
            {author} = author
            {article_href} = the link to the article, but the actual href value
            {reddit} = reddit social networking link
            {digg} = digg social networking link
        HTML_COMMENT
            {author} = comment author
            {website} = website
            {comment} = comment
            {date} = comment date
            {ip} = comment ip address
        HTML_FORM:
            {action} = value that goes inside the <form>
            {hidden_data} = required value somewhere inside the <form>
            {captcha_question} = In plain text, the question
            {captcha_answer} = The answer encoded and passed through <form>

        */
        global $timestamp_format;
        global $mod_rewrite; //globalize mod_rewrite for URL mods
        global $databaseinfo; //for table prefix
        global $disable_extended_article; //globalize disable_extended_article (to determine whether we should allow full stories in str_replace)
        $template = decode_data($template);
        if ($type == "html_article") { //if we are working with the html_article
            //change back from htmlspecialchars to htmlspecialchars_decode, and define some other vars
            $item = decode_data($item);
            $item['timestamp'] = date($timestamp_format['v3'], $item['timestamp']);

            if ($mod_rewrite == true) {
                $item['article_title_mod'] = str_replace(' ', '-', $item['article_title']);
                $url = 'http://'.$_SERVER['SERVER_NAME'].dirname($_SERVER['PHP_SELF']).$item['article_title_mod'];
            } else {
                $url = 'http://'.$_SERVER['SERVER_NAME'].$_SERVER['PHP_SELF'].'?a='.$item['id'];
            }
            $template = str_replace('{title}', $item['article_title'], $template);
            $template = str_replace('{id}', $item['id'], $template);
            $template = str_replace('{subtitle}', $item['article_subtitle'], $template);
            $template = str_replace('{main_article}', $item['article_text'], $template);
            if ($id && $disable_extended_article != true) {
                $template = str_replace('{full_story}', $item['article_exptext'], $template);
            } else {
                $template = str_replace('{full_story}', '', $template);
            }
            $template = str_replace('{image_src}', $item['article_imgid'], $template);
            $template = str_replace('{date}', $item['timestamp'], $template);
            $template = str_replace('{author}', $item['article_author'], $template);

            //construct href for a
            $template = str_replace('{article_href}', $url, $template);

            //reddit, digg, del.icio.us buttons
            $template = str_replace('{reddit}', '
				<script>reddit_url=\''.$url.'\'</script>
				<script>reddit_title=\''.$item['article_title'].'\'</script>
				<script language="javascript" src="http://reddit.com/button.js?t=2"></script>
				', $template);

            //digg_url = \''.$url.'\'; is the real one
            $template = str_replace('{digg}', '
				<script type="text/javascript">
					digg_url = \''.$url.'\';
					digg_bgcolor = \'transparent\';
				</script>
				<script src="http://digg.com/tools/diggthis.js" type="text/javascript"></script> 
				', $template);

            //comment numeric representations
            $comment_num = db_fetch('SELECT COUNT(*) FROM '.$databaseinfo['prefix'].'comments WHERE article_id='.$item['id'].'', 1, false);
            $template = str_replace('{comment_count}', $comment_num[0], $template);
            return $template;
        } elseif ($type == "html_comment") {
            $item['timestamp'] = date($timestamp_format['v3'], $item['timestamp']);
            $item['comment_text'] = nl2br($item['comment_text']);
            $template = str_replace('{author}', $item['comment_author'], $template);
            $template = str_replace('{timestamp}', $item['timestamp'], $template);
            $template = str_replace('{comment}', $item['comment_text'], $template);
            $template = str_replace('{website}', $item['website'], $template);
            $template = str_replace('{ip}', $item['ip'], $template);
            return $template;


        } elseif ($type == "html_form") {
            @require("inc/captcha.php"); //require captcha info
            //if SEF urls, we write a SEF url. ;) IF NOT, regular ?$id
            if ($mod_rewrite == true) {
                $url = 'http://'.$_SERVER['SERVER_NAME'].dirname($_SERVER['PHP_SELF']).''.$id;
            } else {
                $url = '?a='.$id;
            }
            //captcha determination
            $captcha['question'] = array_rand($captcha);
            $captcha['answer'] = base64_encode($captcha[$captcha['question']] + (60-20));
            //start translation for the html comment form
            $template = str_replace('{action}', $url, $template);
            $template = str_replace('{captcha_question}', $captcha['question'], $template);
            $template = str_replace('{captcha_answer}', '<input type="hidden" name="captcha_answer" value="'.$captcha['answer'].'" />', $template);
            $template = str_replace('{hidden_data}', '<input type="hidden" name="id" value="'.$id.'" />', $template);
            return $template;

        } elseif ($type == "html_pagination") { //pagination template

            if ($item['previous']) {
                $template = str_replace('{previous_page}', '?a=page:'.$item['previous'], $template);
            } else {
                $template = str_replace('{previous_page}', '', $template);
            }
            if ($item['next']) {
                $template = str_replace('{next_page}', '?a=page:'.$item['next'], $template);
            } else {
                $template = str_replace('{next_page}', '', $template);
            }
            $template = str_replace('{middle_pages}', $item['middle'], $template);
            return $template;

        } elseif ($type == "rss") { //we translate each item with RSS syntax. <item>s and such.
            $url = 'http://'.$_SERVER['SERVER_NAME'].dirname($_SERVER['PHP_SELF']);
            if (strstr($_SERVER['PHP_SELF'], 'etc.php')) {
                $url = $url.'/article.php?do=edit&amp;id='.$item['id'].'';
                $rss_link = $url;
            } else {
                if ($mod_rewrite) {
                    $item['article_title'] =  str_replace(' ', '-', $item['article_title']);
                    $rss_link = $url.''.$item['article_title'].'';
                } else {
                    $rss_link = $url.'?a='.$item['id'].'';
                }
            }
            $template = '
<item>
	<title>'.$item['article_title'].'</title>
	<author>'.$item['article_article'].'</author>
	<category>'.$item['article_cat'].'</category>
	<pubDate>'.$item['timestamp'].'</pubDate>
	<link>'.$rss_link.'</link>
	<description>'.$item['article_text'].'</description>
</item>';
            return $template; //return template
        }
    }
}
//check to see if the system is online. If yes, we continue, if no, well... no. ;)
$siteonline = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='line'", 1, false);
if ($siteonline['v1'] == 'no') {
    die('<div class="disabled_message">The administrator has disabled the news system.</div>');
}
$banned = db_fetch("SELECT ip, reason FROM ".$databaseinfo['prefix']."banlist", 0);
while ($ip = mysql_fetch_assoc($banned)) {
    if ($ip['ip'] == $_SERVER['REMOTE_ADDR']) {
        die("<strong>You have been banned from viewing this article system.</strong>
					<p>Reason: ".$ip['reason']."</p>
					");
    }
}

//timestamp format fetch
$timestamp_format = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='timestamp_format'", 1, false);

//fetch template. :)
$template = fetch_template();

//before anything else, we're going to detect if there is post data, and if there is, we'll insert the db. If there is no post data, just pass over this.
if ($_POST && $static != true) {
    //IF THERE IS POST DATA, then we're submitting the form. We need to clean data.
    $comment = clean_data($_POST);

    //set the continue to yes.
    $comment_continue = true;

    //validate data (regex for email)
    if (!$comment['name'] || !$comment['email'] || !$comment['comment'] || !preg_match("/^[A-Za-z0-9_-]+@[A-Za-z0-9_-]+\.([A-Za-z0-9_-][A-Za-z0-9_]+)$/", $comment['email'])) {
        $comment_error = 'You need to enter all required fields, and a valid email. Press back to try again.';
        $comment_continue = false;
    }
    if ($comment['captcha'] != base64_decode($comment['captcha_answer'])-(60-20) || !$comment['captcha']) {
        $comment_continue = false;
        $comment_error .= ' The captcha answer was incorrect. Press "back" on your browser to try again.';
    }
    if ($mod_rewrite == true) {
        $title_id = str_replace('-', ' ', $comment['id']);
        $article_id = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."articles WHERE article_title='".$title_id."'", 1);
        $article_id = $article_id['id'];
    } else {
        $article_id = $comment['id'];
    }


    //if comment_id is not numeric, kill with message
    if (!is_numeric($comment['id']) && $mod_rewrite == false) {
        die("non-numeric form id, invalid information.");
    }
    if ($comment_continue == true) {
        $insert = db_insert('INSERT INTO '.$databaseinfo['prefix'].'comments (article_id,comment_text,comment_author,website,timestamp,approved,ip) VALUES ("'.$article_id.'","'.$comment['comment'].'","'.$comment['name'].'","'.$comment['website'].'","'.$time.'","1","'.$ip.'")');
    } else {
        $content .= '<div class="warning">'.$comment_error.'</div>';
    }
}




/*
    ACTUAL CONTENT GENERATION.
    If there is no $do, we're not using RSS or ATOM, and there is no specific $id, we display the list.
*/

if (((!$do || $do == 'rss') && (!$id || $id == 'do=rss')) || $static == true) { //if no defined action, show news as it is meant to be displayed.

    //gather some important variables from db.
    if ($category) {
        $category = "WHERE article_cat IN ($category,'all') &&";
    } else {
        $category = "WHERE";
    }
    if (!$offset) {
        $offset = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_offset'", 1);
        $offset = $offset['v1'];
    } $original_offset = $offset; //to be used later...
    if (!$limit) {
        $limit = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_limit'", 1);
        $limit = $limit['v1'];
    }
    if (!$order) {
        $order = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_order'", 1);
        $order = $order['v3'];
    }
    if (!$items_per_page) {
        $items_per_page = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_items_per_page'", 1);
        $items_per_page = $items_per_page['v1'];
    }

    /* Pagination management:
            phpns works by using QUERY_STRING like this: filename.php?page:1
        So, if no page is defined, we're going to default to 1. */

    //get the current page from the URI.
    $current_page = str_replace('page:', '', $_GET['a']);

    //if the string is empty, we assume page 1.
    if (!is_numeric($current_page) && !$current_page) {
        $current_page = 1;
    }

    if ($current_page == 1) {
        //determine offset
        $offset = ($current_page * $items_per_page - ($items_per_page)) + $offset;
    } else {
        $offset = ($current_page * $items_per_page - ($items_per_page));
    }


    //MODE MODIFICATION
    if ($mode == "rss") {
        $rsslimit = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_rsslimit'", 1);
        $limit['v1'] = $rsslimit['v3'];
        $order = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_rssorder'", 1);
        $order = $order['v3'];
    }

    //form count query, then figure out the total amount of rows in the news generation (including all pages)
    $fetch_news_count = db_fetch("
				SELECT * FROM ".$databaseinfo['prefix']."articles
				".$category."
				active='1' AND approved='1'
				LIMIT ".$original_offset.",".$limit."
				", 0);
    $total_news_count = mysql_num_rows($fetch_news_count);

    //forming actual news query.
    $fetch_news_res = db_fetch("
			SELECT * FROM ".$databaseinfo['prefix']."articles
			".$category."
			active='1' AND approved='1'
			ORDER BY timestamp ".$order."
			LIMIT ".$offset.",".$items_per_page."
			", 0);

    //pagination determinaion continuation =)


    while ($row = mysql_fetch_assoc($fetch_news_res)) {  //start fetch loop

        if ($time >= $row['start_date'] || $time <= $row['end_date']  || $row['start_date'] == null || $row['end_date'] == null) {

            //put into $items if rss mode, else just $content
            if ($mode == 'rss') {
                $returned_data = translate_item($row, $template['html_article'], 'rss'); //translate into template
                $items .= $returned_data;
            } else {

                $returned_data = translate_item($row, $template['html_article'], 'html_article'); //translate into template

                $content .= $returned_data;
            }

        }
    }

    if (!$mode && $disable_pagination != true) {
        $pages = array();

        //find the total number of pages
        $pages['page_num'] = ceil($total_news_count / $items_per_page);

        //generate previous page link
        if ($current_page > 1) {
            $page['previous'] = $current_page - 1;
        }

        //generate next page link
        if ($current_page < $pages['page_num']) {
            $page['next'] = $current_page + 1;
        }

        //generate middle pages
        for($i = 1; $i <= $pages['page_num']; $i++) {
            if ($i == $current_page) {
                $page['middle'] = $page['middle'] . "\n".'<span class="pagination page_link_'.$i.'"><a>'.$i.'</a></span> ';
            } else {
                $page['middle'] =  $page['middle'] . "\n".'<span class="pagination page_link_'.$i.'"><a href="?a=page:'.$i.'">'.$i.'</a></span> ';
            }
        }

        //add pagination links to content
        $content .= translate_item($page, $template['html_pagination'], 'html_pagination');
    }

} elseif ($id && !$mode && $static == false) { //if we're dealing with singles, and the admin wants single articles to be displayed....
    if (!$comment_override) {
        $allow_com = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_comenabled'", 1);
    } else {
        $allow_com = true;
    }
    //if SEF URLs are enabled, we need to change a few things, and make it search for titles instead of id

    if ($mod_rewrite == true) {
        $title_id = str_replace('-', ' ', $id);
        $where_spec = "article_title='".$title_id."'";
    } else {
        $where_spec = "id='".$id."'";
    }

    //forming actual news query.
    $fetch_news_res = db_fetch("
			SELECT * FROM ".$databaseinfo['prefix']."articles
			WHERE
			active='1' AND approved='1' AND ".$where_spec." LIMIT 1
			", 0);
    //we're checking how many results were retrieved. If none, we set an error message and display it.
    if (mysql_num_rows($fetch_news_res) == 0) {

        //set the error message, and display it.
        $error_message = '<div class="error_message">The article/page requested ('.$id.' | '.$title_id.') does not exist.</div>';
        echo $error_message;

    } else { //if there IS an article, we proceed. =)
        while ($row = mysql_fetch_assoc($fetch_news_res)) {  //start fetch loop
            if ($time >= $row['start_date'] || $time <= $row['end_date']  || $row['start_date'] == null || $row['end_date'] == null) { //if we're set for time landings
                $allow_com['article_specific'] = $row['allow_comments'];
                $returned_data = translate_item($row, $template['html_article'], 'html_article'); //translate into template
                $content .= $returned_data;
                //if rss, we have to write it to $items
            }

        }
        //echo var_dump($allow_com); //debug
        //now, we generate comments for this specific article IF they are enabled
        if ($allow_com['v1'] == true) {
            if ($mod_rewrite == true) {
                $title_id = str_replace('-', ' ', $id);
                $article_id = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."articles WHERE article_title='".$title_id."'", 1);
                $fetch_com_res = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."comments WHERE article_id='".$article_id['id']."' AND approved='1'", 0);
            } else {
                $fetch_com_res = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."comments WHERE article_id='".$id."' AND approved='1'", 0);
            }
            //for each row (or comment) generated, we translate the item and assign it to $content
            while ($row = mysql_fetch_assoc($fetch_com_res)) {
                $comment_list .= translate_item($row, $template['html_comment'], 'html_comment');
            }
        }
        //assign $comment_list to $content
        $content .= $comment_list;

        //translate html comment form, then add it to the end of $content, if comments are enabled
        if (($allow_com['v1'] == true && $allow_com['article_specific'] == 1 && $static != true) || $comment_override == true && $static != true) {
            $form_template = translate_item('', $template['html_form'], 'html_form');
        } else {
            $form_template = '<span class="comments_are_disabled">Comments are disabled.</span>';
        }
        //add it to $content ($form_template will be empty if comments are not enabled)
        $content .= '
				'.$form_template;
    } //end of the ELSEIF of mysql_num_rows (there were results...)

} //end main if

// echo var_dump($allow_com); //debugging, keep commented.

if ($mode == 'rss') { //we generate the header information
    header("Content-type: text/xml"); //set header for XML (for RSS)
    //some variable grabbing
    $rss['title'] = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_rsstitle'", 1);
    $rss['desc'] = db_fetch("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='def_rssdesc'", 1);
    $content .= '<rss version="2.0">
	<channel>
		<title>'.$rss['title']['v3'].'</title>
		<link></link>
		<description>'.$rss['desc']['v3'].'</description>
		'.$items.'
	</channel>
</rss>';
}

echo $content; //and... finally post the content

/* WE NEED TO UNDECLARE THE FOLLOWING VARIABLES just in case we have multiple scripts on one page.
   * $limit
   * $template
   * $category
   * $mode
   * $offset
   * $order
   * $disable_pagination
   * $items_per_page
   * $sef_override
   * $comment_override
   * $static
   * $disable_extended_article

   //non-user input
   * $content
   * $comment_list
   * $id
*/
unset($limit);
unset($template);
unset($category);
unset($mode);
unset($offset);
unset($order);
unset($disable_pagination);
unset($items_per_page);
unset($sef_override);
unset($comment_override);
unset($static);
unset($disable_extended_article);

//non-user input unsetting
unset($content);
unset($comment_list);
unset($id);

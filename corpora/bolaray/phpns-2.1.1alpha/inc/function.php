<?php

/* Copyright (c) 2007 Alec Henriksen
 * phpns is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public Licence (GPL) as published by the Free
 * Software Foundation; either version 2 of the Licence, or (at your option) any
 * later version.
 * Please see the GPL at http://www.gnu.org/copyleft/gpl.html for a complete
 * understanding of what this license means and how to abide by it.
*/




/*
SITE WIDE FUNCTIONS
The following functions are used for mice
##############################################
##############################################
*/
function general_query($query, $array=false) //for simple/misc queries
{
    if ($clean == true) {
        $query = clean_data($query); //clean
    }

    $res = mysql_query($query) or die('<p><textarea style="width: 50%; height: 200px;">FAILED QUERY: '.$query.'
			
			'.mysql_error().'</textarea></p>');
    //return value or not?
    if ($array == true) { //if we want a value
        $value = mysql_fetch_array($res);
        return $value;
    } else {
        return $res;
    }
}
function content_num($table, $type, $ext)
{
    global $databaseinfo; //for table prefix
    if ($type == 1) {
        $stat_sql = 'SELECT * FROM '.$databaseinfo['prefix'].''.$table.'';
        if ($ext == 1) {
            $extra = "WHERE active=0";
        } //add selector for unactive stories
        if ($ext == 2) {
            $extra = "WHERE approved=0";
        } //add selector for approved stories
        $stat_res = general_query('SELECT * FROM '.$databaseinfo['prefix'].''.$table.' '.$extra.'');
        $final = mysql_num_rows($stat_res);
    }
    return $final;
}

function load_items($table, $start, $limit, $sort, $v)
{
    global $databaseinfo; //for table prefix
    //determine viewable items
    $vcond = $v;
    if ($v == "unactive") {
        $vcond = "WHERE active=0 ";
    } elseif ($v == "active") {
        $vcond = "WHERE active=1 ";
    } elseif (is_numeric($v)  || $v == 'all') {
        $vcond = 'WHERE article_cat="'.$v.'"';
    } elseif ($v == "unapproved") {
        $vcond = "WHERE approved=0 ";
    } elseif ($v != "") {
        $vcond = "WHERE article_author='".$v."'";
    }
    //determine sorting ASC and DESC, and column to sort. Syntax: $sort = column|(desc,asc);
    if ($sort) {
        $sort = split("/", $sort);
    } else { //else default sorting/column
        $sort[0] = 'timestamp';
        $sort[1] = 'desc';
    }
    $load_res = general_query("SELECT * FROM ".$databaseinfo['prefix']."$table 
		".$vcond."
		ORDER BY ".$sort[0]." ".$sort[1]." 
		LIMIT $start, $limit");

    if (mysql_num_rows($load_res) == 0) {
        $table_rows = '<td colspan="6">No returned results...</td>';
    }
    //return
    return $load_res;
}

function search($search) //search function. $search = array(); ['category'] and ['query']
{
    global $databaseinfo; //for table prefix
    global $page_start;
    global $items_per_page;
    //if all categories or just a certain category
    if ($search['category'] == "all") {
        $category_s = "";
    } else {
        $category_s = "article_cat=".$search['category']." AND (";
        $category_s_e = ')';
    }
    //form the actual query
    $searchres = general_query("
		SELECT * FROM ".$databaseinfo['prefix']."articles
		WHERE $category_s article_title LIKE '%".$search['query']."%'
		OR article_text LIKE '%".$search['query']."%'
		OR article_exptext LIKE '%".$search['query']."%' ".$category_s_e."
		ORDER BY id DESC
		LIMIT $page_start, $items_per_page");

    return $searchres;
}

function load_config($name) //for loading single values from db
{
    global $databaseinfo; //for table prefix
    $name = clean_data($name);
    $data = general_query("SELECT * FROM ".$databaseinfo['prefix']."gconfig WHERE name='$name'", true);
    return $data;
}
function change_config($name, $value) //for loading single values from db
{
    global $databaseinfo; //for table prefix
    $name = clean_data($name);
    $value = clean_data($value);
    //if we need to use v3 instead of v1l
    if ($name == "timestamp_format" || $name == "def_comlimit" || $name == "def_rsslimit" || $name == "def_rsstitle" || $name == "def_rssdesc" || $name == "global_message") {
        $sql = "UPDATE ".$databaseinfo['prefix']."gconfig SET v3='".$value."' WHERE name='".$name."'";
    } else {
        $sql = "UPDATE ".$databaseinfo['prefix']."gconfig SET v1='".$value."' WHERE name='".$name."'";
    }
    $data = general_query($sql);

    //log this action via log_this (will appear in system log)
    log_this('change_config', 'User <i>'.$_SESSION['username'].'</i> has <strong>modified</strong> a configuration value,  "'.$name.'" to "'.$value.'"');

    return $data;
}

function delete($table, $items)
{
    global $databaseinfo; //for table prefix
    $res = general_query("DELETE FROM ".$databaseinfo['prefix']."".$table." WHERE id IN (".$items.")"); //delete all records where the id is in the list

    //log this action via log_this (will appear in system log)
    log_this('delete', 'User <i>'.$_SESSION['username'].'</i> has <strong>deleted</strong> a tables contents. Table: '.$table.'. Items: '.$items);

    return $res;
}

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

function fetch_template() //figure out default template, or use a user defined one.
{
    global $databaseinfo; //for table prefix
    if (!$template) {  //if template is not defined by pre-var include... get default
        global $default_template;

        $res = general_query("SELECT * FROM ".$databaseinfo['prefix']."templates WHERE template_selected='1' LIMIT 1", true);
        //update default_template var
        $default_template = $res['id'];
        return $res; //return default template (changeable in preferences)
    } else {
        $res = general_query("SELECT * FROM ".$databaseinfo['prefix']."templates WHERE id=".$template." LIMIT 1", true);
        return $res;
    }
}

function translate_comment($item, $template, $type)
{
    global $id;
    global $timestamp_format;
    $template = decode_data($template);
    if ($type == "html_comment") {
        $item['timestamp'] = date($timestamp_format['v3'], $item['timestamp']);
        $item['comment_text'] = nl2br($item['comment_text']);
        $template = str_replace('{author}', $item['comment_author'], $template);
        $template = str_replace('{timestamp}', $item['timestamp'], $template);
        $template = str_replace('{comment}', $item['comment_text'], $template);
        $template = str_replace('{website}', $item['website'], $template);
        $template = str_replace('{ip}', $item['ip'], $template);
        return $template;
    }
}

function log_this($task, $description)
{
    global $globalvars;
    global $databaseinfo; //for table prefix
    //clean data
    $task = clean_data($task);
    $description = clean_data($description);
    $page = clean_data($page);
    $page = $globalvars['full_page'];

    //form sql query and execute
    $log = general_query("INSERT INTO ".$databaseinfo['prefix']."syslog (task,description,user,page,timestamp) VALUES
		('".$task."','".$description."','".$_SESSION[userID]."','".$page."','".time()."')");
    //done adding log entry
}

function log_form()
{

    //global all the vars we need.
    global $log_rows;
    global $prev_page;
    global $next_page;
    global $globalvars;
    global $page_start;
    global $items_per_page;
    global $do;
    global $sort;
    global $databaseinfo; //for table prefix

    if (!$sort) { //if no sorting option exists.
        $sort = 'timestamp/asc';
    }

    if ($sort) {
        //decide what to inverse
        $sort_r = split("/", $sort);
        //$sort_r[0] = ($sort_r[0] == "id") ? $sort_r[0] : 'id';
        $sort_r[1] = ($sort_r[1] == "desc") ? 'asc' : 'desc';
        $sort_sql = $sort_r;
        $sort_r = $sort_r[1];
    }


    $lres = general_query('SELECT * FROM '.$databaseinfo['prefix'].'syslog ORDER BY '.$sort_sql[0].' '.$sort_sql[1].' LIMIT '.$page_start.','.$items_per_page); //fetch query
    while ($lrow = mysql_fetch_assoc($lres)) { //get arrays
        $row_bg = ($row_bg == '#ffffff') ? '#F5F5F5' : '#ffffff'; //switch row colors
        $usernamerow = mysql_fetch_assoc(general_query('SELECT user_name FROM '.$databaseinfo['prefix'].'users WHERE id='.$lrow[user].'')); //fetch user
        $lrow['user'] = $usernamerow['user_name'];
        if ($lrow['user'] == null) {
            $lrow['user'] = "<span style=\"color:red;font-weight:bold;\">N/A</span>";
        }
        $lrow['page'] = wordwrap($lrow['page'], 30, "<br />\n", true);
        $lrow['timestamp'] = date($globalvars['time_format'], $lrow['timestamp']);
        $log_rows .= '
					<tr bgcolor="'.$row_bg.'">
						<td><strong>'.$lrow['task'].'</strong></td>
						<td>'.decode_data($lrow['description']).'</td>
						<td>'.$lrow['user'].'</td>
						<td>'.$lrow['timestamp'].'</td>
						<td>'.$lrow['page'].'</td>
					</tr>';
    }


    $form = '
		<h3>Log list</h3>


		<table style="text-align: left; width: 100%;" border="1"
		 cellpadding="3" cellspacing="2">
		  <tbody>
		    <tr class="toprow">
		      <td style="width: 200px; text-align: left;"><a href="?do=syslog&sort=task/'.$sort_r.'"><strong>Task</strong></a></td>
		      <td><a href="?do=syslog&sort=description/'.$sort_r.'"><strong>Description</strong></a></td>
		      <td><a href="?do=syslog&sort=user/'.$sort_r.'"><strong>User</strong></a></td>
		      <td><a href="?do=syslog&sort=timestamp/'.$sort_r.'"><strong>Timestamp</strong></a></td>
		      <td style="width: 50px"><a href="?do=syslog&sort=page/'.$sort_r.'"><strong>Page</strong></a></td>
		    </tr>
		    '.$log_rows.'
		  </tbody>
		</table>
		<div style="text-align: right; width: 400px; float: right;"><input type="submit" id="submit" value="Delete Selected" /></div>

		<div><button class="previous" OnClick="window.location = \'?do=syslog&page='.$prev_page.'&sort='.$sort.''.$a_js.'\';">Previous ('.$prev_page.')</button> <button class="next" OnClick="window.location = \'?do=syslog&page='.$next_page.'&sort='.$sort.''.$a_js.'\';">Next ('.$next_page.')</button>
		</div>
		';

    return $form;
}

/*
NEWS MANAGEMENT FUNCTIONS
The following functions are used for news management globally for phpns.
##############################################
##############################################
*/

function gen_categories($format, $display)
{
    global $data;
    global $databaseinfo; //for table prefix
    $row_bg = '#ffffff';
    $cat_res = general_query("SELECT * FROM ".$databaseinfo['prefix']."categories WHERE cat_parent=''"); //select categories
    while ($cat_row = mysql_fetch_assoc($cat_res)) {
        if ($format == "option") {
            //make the current category selected
            if ($data['article_cat'] == $cat_row['id']) {
                $cat_list = $cat_list.
                '<option selected="selected" value="'.$cat_row['id'].'">'.$cat_row['cat_name'].'</option>';
            } else {
                $cat_list = $cat_list.
                '<option value="'.$cat_row['id'].'">'.$cat_row['cat_name'].'</option>';
            }
            if ($display != 'top') {
                //while we get each "top" level categories (without a parent, get the subcategories, and list them BELOW each main cat.
                $cat_sqlres = general_query("SELECT * FROM ".$databaseinfo['prefix']."categories WHERE cat_parent=".$cat_row['id']."");
                while ($catsub_row = mysql_fetch_assoc($cat_sqlres)) {
                    if ($data['article_cat'] == $catsub_row['id']) { //if subcat selected
                        $cat_list = $cat_list.'
							 <option value="'.$catsub_row['id'].'" selected="selected">&nbsp;&nbsp;&nbsp;&nbsp;--'.$catsub_row['cat_name'].'</option>';
                    } else { //else not selected
                        $cat_list = $cat_list.'
								<option value="'.$catsub_row['id'].'">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'.$catsub_row['cat_name'].'</option>';
                    }
                }
            }

        } elseif ($format = "row") {
            $row_bg = ($row_bg == '#ffffff') ? '#F5F5F5' : '#ffffff';
            $cat_row['timestamp'] = date("D M d, Y", $cat_row['timestamp']);
            $cat_list = $cat_list.
            '<tr bgcolor="'.$row_bg.'"><td><a href="preferences.php?do=categories&amp;action=edit&amp;id='.$cat_row['id'].'"><strong>'.$cat_row['cat_name'].'</strong></a></td><td><strong>'.$cat_row['cat_parent'].'</strong></td><td>'.$cat_row['cat_desc'].'</td><td>'.$cat_row['timestamp'].'</td><td><input type="checkbox" value="'.$cat_row['id'].'" name="'.$cat_row['id'].'" /></td></tr>
				';
            $cat_sqlres = general_query("SELECT * FROM ".$databaseinfo['prefix']."categories WHERE cat_parent=".$cat_row['id']."");
            while ($catsub_row = mysql_fetch_assoc($cat_sqlres)) {
                $catsub_row['timestamp'] = date("D M d, Y", $catsub_row['timestamp']);
                $cat_list = $cat_list.
                '<tr bgcolor="#ccc" ><td bgcolor="#999999"><em> - '.$catsub_row['cat_name'].'</em></td><td>This is a sub-category.</td> <td> '.$catsub_row['cat_desc'].'</td><td>'.$catsub_row['timestamp'].'</td><td><input type="checkbox" value="'.$cat_row['id'].'" name="'.$cat_row['id'].'" /></td></tr>
				';
            }
        }
    } //end while
    return $cat_list;
}

function gen_templates()
{
    global $databaseinfo; //for table prefix
    $t_res = general_query("SELECT * FROM ".$databaseinfo['prefix']."templates"); //select categories
    while ($t_row = mysql_fetch_assoc($t_res)) {
        $template_list .=
        '<option value="'.$t_row['id'].'">'.$t_row['template_name'].'</option>';
    } //end while
    return $template_list;
}

function article_form()
{
    global $data;
    global $error_message;
    global $globalvars;
    global $do;
    global $news_id;
    $data['cat_list'] = gen_categories('option', '');
    //define form HTML display for new items.
    if (!$do || $do == "p" || $do == "preview") {
        $action = '?&amp;do=p';
    } else {
        $action = '?id='.$data['id'].'&amp;do=editp';
    }
    if ($do == "edit") {
        $hidden_f = '<input type="hidden" id="id" name="id" value="'.$news_id.'" />';
        if ($data['approved'] == 0 && $globalvars['rank'][12] == 1) {
            $needs_to_be_approved = '<button class="activate" OnClick="window.location = \'?do=activate&amp;id='.$data['id'].'\';"><strong>Click here to approve this article</strong></button>';
        }
        $comment_b = '<div>'.$needs_to_be_approved.' <button class="activate" OnClick="window.location = \'?do=comments&amp;id='.$data['id'].'\';"><strong>View commens for this item</strong></button></div>';
    }

    //if there is an image in the db, display that above the upload form.
    if ($data['article_imgid']) {
        $image_view = '<a href="'.$data['article_imgid'].'"><img class="image_uploaded" src="'.$data['article_imgid'].'" /></a>';
    }

    //define warning if you need approval
    if ($globalvars['rank'][10] == 2) {
        $rank_message = '<div class="warning">You have permission to create new articles, however, you need approval before it actually becomes publically viewable.</div>';
    }

    $form_display = '		
			'.$comment_b.'
			'.$rank_message.'
		<div class="form">
				'.$error_message.'
				<form id="articleform" method="post" enctype="multipart/form-data" action="'.$action.'" onsubmit="return validate_form(this)">
					<label for="title">Article title</label><input type="text" id="title" name="article_title" value="'.$data['article_title'].'" /><br />
					<label for="subtitle">Sub-title *</label><input type="text" id="subtitle" name="article_subtitle" value="'.$data['article_subtitle'].'"  /><br />
					<label for="category">Category (<a href="preferences.php?do=categories" onClick="return confirm(\'Are you sure you want to leave this page, to edit categories?\\n\\nYou will loose all progress on your article.\');">edit</a>)</label>
					<select name="article_cat" id="category">
						<option value="all">All categories</option>
						<optgroup label="Categories">
						'.$data['cat_list'].'
						</optgroup>
					</select><br />
					<label class="for_textarea" for="main">Main article <a href="javascript:togglewysiwyg(\'main\');">wysiwyg on/off</a> <a href="javascript:expandwysiwyg(\'main\');">expand editor</a></label><textarea name="article_text" id="main" onkeypress="checkTab(event);">'.$data['article_text'].'</textarea><br />
					<h4>Extended article (<a href="javascript:expand(\'advanced\');">expand/collapse</a>)</h4>	
					<div id="advanced" class="advanced advanced_extended" style="display: none;">
						<label class="for_textarea" for="full">Extended* <a href="javascript:togglewysiwyg(\'full\');">wysiwyg on/off</a> <a href="javascript:expandwysiwyg(\'full\');">expand editor</a></label><textarea name="article_exptext" id="full" onkeypress="checkTab(event);">'.$data['article_exptext'].'</textarea><br />
					</div>
					
					<h4>Image options (<a href="javascript:expand(\'image_options\');">expand/collapse</a>)</h4>	
					<div id="image_options" class="advanced" style="display: none;">
						'.$image_view.'
						<label for="image">Article image</label><input type="file" name="image" id="image" /><br />
						<div class="clear"></div>
					</div>
					
					<h4>Additional Options (<a href="javascript:expand(\'add_options\');">expand/collapse</a>)</h4>
					<div id="add_options" class="advanced" style="display: none;">
												<label for="start">Start date *</label><input type="text" name="start_date" id="start"  value="'.$data['start_date'].'" /> (mm/dd/yyyy) <em>(time on server: '.date('m/d/Y').')</em><br />
						<label for="end">End date *</label><input type="text" name="end_date" id="end" value="'.$data['end_date'].'" /> (mm/dd/yyyy)<br />
						<label for="comments" class="nofloat"><input type="checkbox" value="0" name="acchecked" id="comments"'.$data['acchecked_check'].' /> Disable comments</label><br /><br />
						<label for="active" class="nofloat"><input type="checkbox" value="0" name="achecked" id="active"'.$data['achecked_check'].' /> Save as draft (unactive)</label><br />
					</div>
					'.$hidden_f.'
					<div class="alignr">
						<input type="submit" id="submit" name="submit" value="Save article" />
						<input type="submit" id="preview" name="preview" value="Preview article" />
					</div>
				</form>

		</div>';

    return $form_display;
}

function manage_form()
{
    //global all the vars we need.
    global $table_rows;
    global $prev_page;
    global $next_page;
    global $globalvars;
    global $search;
    global $do;
    global $sort;
    global $search;
    //generate categories as an option list (<option>...</option)
    $category_list = gen_categories('option', '')
    ;
    if ($globalvars['page_name'] == "search") { //things to do if we're searching
        $s_value = $search['query']; //get the query
        $s_cat = gen_cat_name($search['category']); //turn cat number into human readable label
        $a_js = '&amp;q='.$search['query'].'&amp;c='.$search['category'].'&amp;do=search'; //to put in URL if we're searching
        //determine selected category
        $cat_selected = '<optgroup label="Selected:">
							<option selected="selected" value="'.$search['category'].'">'.$s_cat.'</option>
						</optgroup>';

    } else {
        $s_value = "click here to start the search..."; //default
        $script = ' onfocus="if
	(this.value==this.defaultValue) this.value=\'\';"'; //enable click/delete script
    }

    if (!$sort) { //if no sorting option exists.
        $sort = 'timestamp/desc';
    }

    if ($sort) {
        //decide what to inverse
        $sort_r = split("/", $sort);
        $sort_r[1] = ($sort_r[1] == "desc") ? 'asc' : 'desc';
        $sort_r = $sort_r[1];
    }

    $form = '
		
		<form action="manage.php?do=search" method="post">
			<div class="form">
				<h4>Search (<a href="javascript:expand(\'search\');">expand/collapse</a>)</h4>
				<div class="advanced" id="search" style="display: none">
					<input type="text" id="search" name="query" value="'.$s_value.'" class="searchbox"'.$script.' />
					<select name="category" class="searchelements" id="category" name="category">
						<option value="all">All Categories</option>
							'.$cat_selected.'
						<optgroup label="Categories">
							'.$category_list.'
						</optgroup>
					</select>
					<input type="submit" class="searchbutton" value="Search!" />
				</div>
			</div>
		</form>
		
		<h3>Article list</h3>
		<form action="manage.php" method="get" class="category_wrap">
			<select name="v" onchange="submit();" class="cat_navigation">
				<option value="" class="notice">Return to full viewing</option>
				<option value="" selected="selected">View articles in the category ...</option>
				<optgroup label="Categories" selected="selected">
				'.$category_list.'
				</optgroup>
			</select>
		</form>
		<form action="manage.php?do=deleteitems" method="post" onsubmit="return confirm(\'Are you sure you want to delete the selected items?\');">
			<table style="text-align: left; width: 100%;" border="1"
			 cellpadding="3" cellspacing="2">
			  <tbody>
			    <tr class="toprow">
			      <td style="width: 200px; text-align: left;"><a href="?sort=article_title/'.$sort_r.'"><strong>Title</strong></a></td>
			      <td><a href="?sort=article_cat/'.$sort_r.'"><strong>Category</strong></a></td>
			      <td><a href="?sort=timestamp/'.$sort_r.'"><strong>Date</strong></a></td>
			      <td><a href="?sort=article_author/'.$sort_r.'"><strong>Author</strong></a></td>
			      <td style="width: 50px"><a href="?sort=active/'.$sort_r.'"><strong>Active</strong></a></td>
			      <td style="width: 10px; text-align: center;"><strong><input type="checkbox" onClick="Checkall(this.form);" /></strong></td>
			    </tr>
			    '.$table_rows.'
			  </tbody>
			</table>
			<div style="text-align: right; width: 400px; float: right;"><input type="submit" id="submit" value="Delete Selected" /></div>
		</form>
		<div><button class="previous" OnClick="window.location = \'?page='.$prev_page.'&sort='.$sort.''.$a_js.'\';">Previous ('.$prev_page.')</button> <button class="next" OnClick="window.location = \'?page='.$next_page.'&sort='.$sort.''.$a_js.'\';">Next ('.$next_page.')</button>
		</div>
		';

    return $form;
}


function new_item($data, $author)
{
    //globalize timestamps
    global $unixtime;
    global $globalvars;
    global $databaseinfo; //for table prefix

    $news_ip = $_SERVER['REMOTE_ADDR'];
    //form SQL query
    $new_res = general_query('INSERT INTO '.$databaseinfo['prefix'].'articles
                    (article_title,
                    article_subtitle,
                    article_author,
                    article_cat,
                    article_text,
                    article_exptext,
                    article_imgid,
                    allow_comments,
                    start_date,
                    end_date,
                    active,
                    approved,
                    timestamp,
                    ip)
              VALUES ("'.$data['article_title'].'",
                      "'.$data['article_subtitle'].'",
                      "'.$author.'",
                      "'.$data['article_cat'].'",
                      "'.$data['article_text'].'",
                      "'.$data['article_exptext'].'",
                      "http://'.$globalvars['path_to_uri'].'/'.$data['image'].'",
                      "'.$data['acchecked'].'",
                      "'.$unixtime['start']['unix'].'",
                      "'.$unixtime['end']['unix'].'",
                      "'.$data['achecked'].'",
                      "'.$data['approved'].'",
                      "'.$globalvars['time'].'",
                      "'.$news_ip.'");');

    //log this action via log_this (will appear in system log)
    log_this('new_item', 'User <i>'.$_SESSION['username'].'</i> has <strong>created</strong> a new article titled "'.$data['article_title'].'"');
}

function edit_item($data, $username)
{
    //globalize timestamps
    global $unixtime;
    global $globalvars;
    global $databaseinfo; //for table prefix
    //define some misc vars (timestamp, ip)

    //decide if we're uploading a new image. If yes, then add to the query.
    if ($data['image']) {
        $upload_image_sql_add = 'article_imgid="http://'.$globalvars['path_to_uri'].'/'.$data['image'].'",';
    }

    $news_ip = $_SERVER['REMOTE_ADDR'];
    //form SQL query
    $edit_res = general_query('UPDATE '.$databaseinfo['prefix'].'articles SET
                    article_title="'.$data['article_title'].'",
                    article_subtitle="'.$data['article_subtitle'].'",
                    article_author="'.$username.'",
                    article_cat="'.$data['article_cat'].'",
                    article_text="'.$data['article_text'].'",
                    article_exptext="'.$data['article_exptext'].'",
                    '.$upload_image_sql_add.'
                    allow_comments="'.$data['acchecked'].'",
                    start_date="'.$unixtime['start']['unix'].'",
                    end_date="'.$unixtime['end']['unix'].'",
                    active="'.$data['achecked'].'",
                    ip="'.$news_ip.'"
                    WHERE id="'.$data['id'].'"');

    //log this action via log_this (will appear in system log)
    log_this('edit_item', 'User <i>'.$_SESSION['username'].'</i> has <strong>modified</strong> article titled "'.$data['article_title'].'" (ID: '.$data['id'].')');
}

function upload_image($file)
{

    //define the default path to upload
    $target_path = "images/uploads/";

    //define the random prefix to the name
    $random = rand(0, 99999);

    //now, this is where we decide what filename, and directory this will be stored at.
    $target_path = $target_path.$random.basename($file['name']);

    if ($file['type'] == 'image/gif' || $file['type'] == 'image/jpeg' || $file['type'] == 'image/jpg' || $file['type'] == 'image/png' || $file['type'] == 'image/bmp' || $file['type'] == 'image/tiff' ||  $file['type'] == 'image/tff') {
        if (@move_uploaded_file($file['tmp_name'], $target_path)) { //if we moved the file succesfully to target_path
            chmod($target_path, 0644); //chmod it so we can access it later.
            return $target_path; //return the target path to the manage.php
            echo $target_path;
        } else { //if we didn't move the file / error
            return false; //return false
        }
    } else {
        return false;
    }
}


function approve($id)
{
    //form SQL query
    $edit_res = general_query('UPDATE '.$databaseinfo['prefix'].'articles SET
                    approved="1"
                    WHERE id="'.$id.'"');
    return true;
}


//generate category name from id
function gen_cat_name($catid)
{
    global $databaseinfo; //for table prefix

    if ($catid != "all") {
        $catname = general_query("SELECT * FROM ".$databaseinfo['prefix']."categories WHERE id='$catid' LIMIT 1", true);
        return $catname['cat_name'];
    } else {
        return "<strong>All Categories</strong>";
    }
}

function clean_data($data)
{
    if (is_array($data)) {
        foreach ($data as $key => $value) {
            if(ini_get('magic_quotes_gpc')) {
                $data[$key] = stripslashes($value);
            }
            $data[$key] = htmlspecialchars($value, ENT_QUOTES);
        }
    } else {
        if(ini_get('magic_quotes_gpc')) {
            $data = stripslashes($data);
        }
        $data = htmlspecialchars($data, ENT_QUOTES);
    }

    return $data;
}

function validate_date($data, $rawtype)
{
    global $error_message;
    global $proceed;
    //determine type (start or end)
    if ($rawtype == "start") {
        $type = "start_date";
    } elseif ($rawtype == "end") {
        $type = "end_date";
    }
    if (eregi('^[0-9]{2}/[0-9]{2}/[0-9]{4}$', $data[$type])) { //if start date is formed correctly
        $unixtime['format'] = true; //so the rest of the program knows it's a valid date
        $data[$type] = split("/", $data[$type]); //split mm/dd/yyyy
        if (!checkdate($data[$type][0], $data[$type][1], $data[$type][2])) { //if invalid
            $proceed = "no";
            $error_message = $error_message.'<li>The '.$rawtype.' date is not a valid date.</li>
						';
        } else {
            //check if date is too extreme (too far in future or past)
            if (mktime(0, 0, 0, $data[$type][0], $data[$type][1], $data[$type][2])) {
                $unixtime['valid'] = true;
                $unixtime['unix'] = mktime(0, 0, 0, $data[$type][0], $data[$type][1], $data[$type][2]);
            } else { //if it is too extreme...
                $proceed = "no";
                $unixtime['unix'] = join("/", $data[$type]);
                $error_message = $error_message.'<li>The '.$rawtype.' date timestamp could not be created. It may be too far in the future...</li>
							';
            }
        }
    } else {
        $proceed = "no";
        $error_message = $error_message.'<li>The '.$rawtype.' date is not in a valid format. The correct format is: MM/DD/YYYY.</li>
					';
    }
    return $unixtime;
}


/*
USER PAGE FUNCTIONS
The following functions are used for user operations
##############################################
##############################################
*/
function fetch_ranks($view='option')
{
    global $databaseinfo;
    $rankres = general_query('SELECT * FROM '.$databaseinfo['prefix'].'ranks');
    while ($rr = mysql_fetch_assoc($rankres)) {
        $options .= '<option value="'.$rr['id'].'">'.$rr['rank_title'].'</option>
				';
    }
    return $options;
}

function user_form($data=null)
{
    global $error_message;
    global $do;
    if ($do == "new" || $do == "newp") { //if this is a new process
        $u_action = 'newp';
    } elseif ($do == "edit" || $do == "editp") {
        $u_action = 'editp';
        $u_hiddenid = '<input type="hidden" name="id" value="'.$data['id'].'" />
				<input type="hidden" name="original_username" value="'.$data['user_name'].'" />';
    }
    //define form HTML display for new items.
    $form_display = '		
		<h3>New user</h3>
		<div class="form">
				'.$error_message.'
				<form id="userform" method="post" action="user.php?do='.$u_action.'">
				<div id="columnright">
				<h3>Rank</h3>
				<select name="rank" id="rank" class="highlight">
					'.fetch_ranks().'
				</select>
			</div>
					<label for="username_">Username</label><input type="text" id="username_" class="highlight" name="username_" value="'.$data['user_name'].'" /><br />
					<label for="fullname">Full name</label><input type="text" id="fullname" class="highlight" name="fullname" value="'.$data['full_name'].'" /><br />
					<label for="password_">Password</label><input type="password" id="password_" class="highlight" name="password_" /><br />(Leave blank if you don\'t want to change the password)<br />
					<label for="cpassword_">Confirm Pass</label><input type="password" id="cpassword_" class="highlight" name="cpassword_" /><br />(Leave blank if you don\'t want to change the password)<br />
					<label for="email">Email*</label><input type="text" id="email" name="email" value="'.$data['email'].'" /><br />
				
					<label for="msn">MSN*</label><input type="text" id="msn" name="msn" value="'.$data['msn'].'" /><br />
					<label for="aim">AIM*</label><input type="text" id="aim" name="aim" value="'.$data['aim'].'" /><br />
					<label for="yahoo">Yahoo*</label><input type="text" id="yahoo" name="yahoo" value="'.$data['yahoo'].'" /><br />
					<label for="skype">Skype*</label><input type="text" id="skype" name="skype" value="'.$data['skype'].'" /><br />
					'.$u_hiddenid.'
					<div class="alignr">
					<input type="submit" id="submit" value="Save user" />
					</div>
				</form>
			</div>
		</div>';

    return $form_display;
}

function new_user($data)
{
    global $globalvars;
    global $databaseinfo; //for table prefix

    $data['user_ip'] = $_SERVER['REMOTE_ADDR']; //ip
    //form SQL query
    $new_res = general_query('INSERT INTO '.$databaseinfo['prefix'].'users
                    (user_name,
                    full_name,
                    email,
                    password,
                    timestamp,
                    ip,
                    msn,
                    aim,
                    yahoo,
                    skype,
                    display_picture,
                    rank_id)
              VALUES ("'.$data['username_'].'",
                      "'.$data['fullname'].'",
                      "'.$data['email'].'",
                      "'.$data['password_'].'",
                      "'.$globalvars['time'].'",
                      "'.$data['user_ip'].'",
                      "'.$data['msn'].'",
                      "'.$data['aim'].'",
                      "'.$data['yahoo'].'",
                      "'.$data['skype'].'",
                      " ",
                      "'.$data['rank'].'");');

    //log this action via log_this (will appear in system log)
    log_this('new_user', 'User <i>'.$_SESSION['username'].'</i> has <strong>created</strong> a new user account named <i>'.$data['username_'].'</i> ('.$data['fullname'].') with the rank of '.$data['rank']);
}

function edit_user($data)
{
    global $globalvars;
    global $databaseinfo; //for table prefix

    $data['user_ip'] = $_SERVER['REMOTE_ADDR']; //ip

    if ($data['password_'] != null) {
        $data['password_'] = sha1($data['password_']);
        $password_p = 'password="'.$data['password_'].'",';
    }


    //form SQL query
    $edit_res = general_query('UPDATE '.$databaseinfo['prefix'].'users SET
                    user_name="'.$data['username_'].'",
                    full_name="'.$data['fullname'].'",
                    email="'.$data['email'].'",
                    '.$password_p.'
                    ip="'.$data['user_ip'].'",
                    msn="'.$data['msn'].'",
                    aim="'.$data['aim'].'",
                    yahoo="'.$data['yahoo'].'",
                    skype="'.$data['skype'].'",
                    display_picture="",
                    rank_id="'.$data['rank'].'"
              WHERE id="'.$data['id'].'"
              ');

    //log this action via log_this (will appear in system log)
    log_this('edit_user', 'User <i>'.$_SESSION['username'].'</i> has <strong>modified</strong> '.$data['username_']);
}

function gen_rank_name($rankid)
{
    global $databaseinfo; //for table prefix
    $rname = general_query("SELECT * FROM ".$databaseinfo['prefix']."ranks WHERE id='$rankid' LIMIT 1", true);
    return $rname['rank_title'];
}

function rank_form($data=null) //form for new ranks and editing ranks, function so it can be reused with variables inside.
{
    global $do;
    global $databaseinfo; //for table prefix
    global $error_message;
    if ($do == 'newrank' || $do == 'nrankp') {
        $action = 'nrankp';
    } elseif ($do == 'editrank' || $do == 'erankp') {
        $action = 'erankp';
        $hidden = '<input type="hidden" name="id" value="'.$data['id'].'" />';
    }


    //form
    $content = '
		'.$error_message.'
		<h3>Rank form</h3>
		<form action="user.php?do='.$action.'" method="post">
			<label for="rank_title">Rank title</label><input type="text" id="rank_title" name="rank_title" value="'.$data['rank_title'].'" /><br />
			<label for="rank_desc">Rank description</label><input type="text" id="rank_desc" name="rank_desc" value="'.$data['rank_desc'].'" /><br /><br />
			
			<div id="columnright">
				<br />
				<label for="createranks">Create ranks</label>
				<select name="createranks">
					<optgroup label="Selected:">
						<option selected="selected" value="'.$data['createranks'].'">'.$data['createranks'].'</option>
					</optgroup>
					<optgroup label="Choose an order:">
					<option value="allow">allow</option>
					<option value="disallow">disallow</option>
					</optgroup>
				</select>
				<br />
				
				<label for="manageranks">Manage ranks</label>
				<select name="manageranks">
					<optgroup label="Selected:">
				<option selected="selected" value="'.$data['manageranks'].'">'.$data['manageranks'].'</option>
					</optgroup>
					<optgroup label="Choose an order:">
					<option value="allow">allow</option>
					<option value="disallow">disallow</option>
					</optgroup>
				</select>
				<br />
				
				<label for="loginrecords">Login records</label>
				<select name="loginrecords">
					<optgroup label="Selected:">
						<option selected="selected" value="'.$data['loginrecords'].'">'.$data['loginrecords'].'</option>
					</optgroup>
					<optgroup label="Choose an order:">
					<option value="allow">allow</option>
					<option value="disallow">disallow</option>
					</optgroup>
				</select>
				<br />
				
				<label for="preferences">Preferences</label>
				<select name="preferences">
					<optgroup label="Selected:">
						<option selected="selected" value="'.$data['preferences'].'">'.$data['preferences'].'</option>
					</optgroup>
					<optgroup label="Choose an order:">
					<option value="allow">allow</option>
					<option value="disallow">disallow</option>
					</optgroup>
				</select>
				<br />
			</div>
			<label for="loggingin">Logging in</label>
			<select name="loggingin">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['loggingin'].'">'.$data['loggingin'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="createarticles">Create articles</label>
			<select name="createarticles">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['createarticles'].'">'.$data['label'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="allowapp">allow w/ approval</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="approve">approve articles</label>
			<select name="approve">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['approve'].'">'.$data['approve'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="editarticles">Edit articles</label>
			<select name="editarticles">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['editarticles'].'">'.$data['editarticles'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="deletearticles">delete articles</label>
			<select name="deletearticles">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['deletearticles'].'">'.$data['deletearticles'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="createusers">Create users</label>
			<select name="createusers">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['createusers'].'">'.$data['createusers'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="editusers">Edit users*</label>
			<select name="editusers">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['editusers'].'">'.$data['editusers'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			
			<label for="deleteusers">Delete users*</label>
			<select name="deleteusers">
				<optgroup label="Selected:">
					<option selected="selected" value="'.$data['deleteusers'].'">'.$data['deleteusers'].'</option>
				</optgroup>
				<optgroup label="Choose an order:">
				<option value="allow">allow</option>
				<option value="disallow">disallow</option>
				</optgroup>
			</select>
			<br />
			'.$hidden.'
			<div class="alignr">
				<input type="submit" id="submit" value="Save rank" />
			</div>
		</form>
			';
    return $content;
}

function new_rank($rank, $permissions_string, $author)
{
    //creating a new rank
    global $globalvars;
    global $databaseinfo; //for table prefix

    $res = general_query("INSERT INTO ".$databaseinfo['prefix']."ranks
		(rank_title,
		rank_desc,
		rank_author,
		permissions,
		timestamp)
		VALUES (
		'".$rank['rank_title']."',
		'".$rank['rank_desc']."',
		'".$author."',
		'".$permissions_string."',
		'".time()."')");

    $success = mysql_affected_rows();  //count affected rows

    //log this action via log_this (will appear in system log)
    log_this('new_rank', 'User <i>'.$_SESSION['username'].'</i> has <strong>created</strong> a new rank named '.$rank['rank_title'].'. Rank description "'.$rank['rank_desc'].'". Permissions: '.$permissions_string);

    return $success;
}

function edit_rank($rank, $permissions_string, $id)
{
    //edit rank sql
    global $databaseinfo; //for table prefix

    $res = general_query("UPDATE ".$databaseinfo['prefix']."ranks SET
		rank_title='".$rank['rank_title']."',
		rank_desc='".$rank['rank_desc']."',
		permissions='".$permissions_string."'
		WHERE id='".$id."'
		");
    $success = mysql_affected_rows();  //count affected rows

    //log this action via log_this (will appear in system log)
    log_this('edit_rank', 'User <i>'.$_SESSION['username'].'</i> has <strong>modified</strong> rank named '.$rank['rank_title'].'. Rank description "'.$rank['rank_desc'].'". Permissions: '.$permissions_string);

    return $success;
}

function loginrec_form()
{
    global $table_rows;
    global $prev_page;
    global $next_page;
    global $globalvars;
    global $search;
    global $do;
    global $error_message;
    global $sort;
    global $search;

    $form = '
		'.$error_message.'
		<h3>Options</h3>
		<ul>
			<li><a href="?do=loginrec&amp;action=delall" onClick="return confirm(\'Are you sure you want to delete the selected items?\');">delete all login records</a></li>
		</ul>
		<h3>Login records list</h3>
		<form action="manage.php?do=deleteitems" method="post" onsubmit="return confirm(\'Are you sure you want to delete the selected items?\');">
			<table style="text-align: left; width: 100%;" border="1"
			 cellpadding="3" cellspacing="2">
			  <tbody>
			    <tr class="toprow">
			      <td style="width: 200px; text-align: left;"><strong>Username</strong></td>
			      <td><strong>Rank</strong></td>
			      <td><strong>Date</strong></td>
			      <td><strong>IP Address</strong></td>
			      <td style="width: 10px; text-align: center;"><strong><input type="checkbox" onClick="Checkall(this.form);" /></strong></td>
			    </tr>
			    '.$table_rows.'
			  </tbody>
			</table>
			<div style="text-align: right; width: 400px; float: right;"><input type="submit" id="submit" value="Delete Selected" /></div>
		</form>
		<div><button class="previous" OnClick="window.location = \'?do=loginrec&amp;page='.$prev_page.''.$s_js.'\';">Previous ('.$prev_page.')</button> <button class="next" OnClick="window.location = \'?do=loginrec&amp;page='.$next_page.''.$s_js.'\';">Next ('.$next_page.')</button></div>
		';

    return $form;
}




/*
PREFERENCES FUNCTIONS
The following functions are used on the preferences.php file.
##############################################
##############################################
*/

function new_category($data, $author)
{
    //if all is well...
    global $globalvars;
    global $databaseinfo; //for table prefix

    $ip = $_SERVER['REMOTE_ADDR'];
    $cat_res = general_query("INSERT INTO ".$databaseinfo['prefix']."categories (cat_name,cat_parent,cat_author,cat_desc,timestamp,ip) VALUES
				('".$data['name']."',
				'".$data['parent']."',
				'".$author."',
				'".$data['description']."',
				'".$globalvars['time']."',
				'".$ip."')");

    //log this action via log_this (will appear in system log)
    log_this('new_category', 'User <i>'.$_SESSION['username'].'</i> has <strong>created</strong> a new category named '.$data['name'].'. Category description "'.$data['description']);
}

function template_form($data=null)
{
    global $error_message;
    global $databaseinfo; //for table prefix
    global $action;

    if ($action == 'edit' || $action == 'editp') {
        $action = 'editp';
        $hiddenid = '<input type="hidden" name="id" value="'.$data['id'].'" />';
    } else {
        $action = 'newp';
    }
    //clean data, html entities


    //form the... well... form. :)
    $new_form = '
			'.$error_message.'
			<h3>Template form</h3>
			<div class="form">
				<form action="preferences.php?do=templates&amp;action='.$action.'" method="post" id="template">
					<label for="template_name">Template name</label><input type="text" id="template_name" name="template_name" value="'.$data['template_name'].'" /><br />
					<label for="template_desc">Temp. Description</label><input type="text" id="template_desc" name="template_desc" value="'.$data['template_desc'].'" /><br /><br />
					<label class="for_textarea" for="html_article">Main article <a href="javascript:togglewysiwyg(\'html_article\');">wysiwyg on/off</a> <a href="javascript:expandwysiwyg(\'html_article\');">expand editor</a></label><textarea name="html_article" class="code" id="html_article" onkeypress="checkTab(event);">'.$data['html_article'].'</textarea><br />
					<label class="for_textarea_alt" for="html_comment">Comment(s) <a href="javascript:togglewysiwyg(\'html_comment\');">wysiwyg on/off</a> <a href="javascript:expandwysiwyg(\'html_comment\');">expand editor</a></label><textarea name="html_comment" class="code" id="html_comment" onkeypress="checkTab(event);">'.$data['html_comment'].'</textarea><br />
					<label class="for_textarea_alt" for="html_form">Comment Form <a href="javascript:togglewysiwyg(\'html_form\');">wysiwyg on/off</a> <a href="javascript:expandwysiwyg(\'html_form\');">expand editor</a></label><textarea class="code" name="html_form" id="html_form" onkeypress="checkTab(event);">'.$data['html_form'].'</textarea><br />
					<label class="for_textarea_alt" for="html_pagination">Article pagination <a href="javascript:togglewysiwyg(\'html_pagination\');">wysiwyg on/off</a> <a href="javascript:expandwysiwyg(\'html_pagination\');">expand editor</a></label><textarea class="code" name="html_pagination" id="html_pagination" onkeypress="checkTab(event);">'.$data['html_pagination'].'</textarea><br />
					'.$hiddenid.'
					* You can leave these fields empty, just for freedom\'s sake. We don\'t recommend it though.
					<div class="alignr"><input type="submit" name="submit" id="submit" value="Save template" /></div>
				</form>
			</div>
			';
    return $new_form;
}

function new_template($data, $author)
{
    //creating a new template
    global $globalvars;
    global $databaseinfo; //for table prefix

    $data = clean_data($data);

    $sql = general_query("INSERT INTO ".$databaseinfo['prefix']."templates 
		(template_name,
		template_desc,
		template_author,
		timestamp,
		html_article,
		html_comment,
		html_form,
		html_pagination)
		VALUES (
		'".$data['template_name']."',
		'".$data['template_desc']."',
		'".$author."',
		'".$globalvars['time']."',
		'".$data['html_article']."',
		'".$data['html_comment']."',
		'".$data['html_form']."',
		'".$data['html_pagination']."')");

    $success = mysql_affected_rows();  //count affected rows

    //log this action via log_this (will appear in system log)
    log_this('new_template', 'User <i>'.$_SESSION['username'].'</i> has <strong>created</strong> a new template named '.$data['template_name'].'. Template description "'.$data['template_desc']);

    return $success;
}

function edit_template($data, $author)
{
    //creating a new template
    global $databaseinfo; //for table prefix

    $data = clean_data($data);

    $sql = general_query("UPDATE ".$databaseinfo['prefix']."templates SET
		template_name='".$data['template_name']."',
		template_desc='".$data['template_desc']."',
		html_article='".$data['html_article']."',
		html_comment='".$data['html_comment']."',
		html_form='".$data['html_form']."',
		html_pagination='".$data['html_pagination']."'
		WHERE
		id='".$data['id']."'");

    $success = mysql_affected_rows();  //count affected rows

    //log this action via log_this (will appear in system log)
    log_this('edit_template', 'User <i>'.$_SESSION['username'].'</i> has <strong>modified</strong> template named '.$data['template_name'].'. Template description "'.$data['template_desc']);

    return $success;
}

function switch_template($id)
{
    global $databaseinfo; //for table prefix

    $st_res = general_query("UPDATE ".$databaseinfo['prefix']."templates SET template_selected=''");
    if ($st_res) {
        $st_res = general_query("UPDATE ".$databaseinfo['prefix']."templates SET template_selected='1' WHERE id=".$id."");
        log_this('template_switch', 'User <i>'.$_SESSION['username'].'</i> has <strong>switched the default template</strong> to ID: '.$id.'');
        return true;
    }
}

function ban($data, $by)
{
    //creating a new template
    global $globalvars;
    global $databaseinfo; //for table prefix

    $data = clean_data($data);

    $sql = general_query("INSERT INTO ".$databaseinfo['prefix']."banlist
		(ip,
		banned_by,
		reason,
		timestamp)
		VALUES (
		'".$data['ip']."',
		'".$by."',
		'".$data['reason']."',
		'".$globalvars['time']."')");

    $success = mysql_affected_rows();  //count affected rows

    //log this action via log_this (will appear in system log)
    log_this('edit_template', 'User <i>'.$_SESSION['username'].'</i> has <strong>banned</strong> user at the IP of: '.$data['ip'].'. Reason:  "'.$data['reason']);

    return $success;
}


/*
ABOUT PAGE FUNCTIONS
The following functions are used on the about.php file. Version checking, rss...
##############################################
##############################################
*/
function version_check($input)  //version checking off phpns site
{
    global $globalvars;
    $version_info = 'Version installed: <strong>'.$globalvars['version'].'</strong><br />Latest version: <script type="text/javascript" src="http://phpns.com/version.php?v='.$globalvars['version'].'"></script><br /><br />';
    return $version_info;
}

function phpns_rss()  //rss grabbing from phpns.com
{
    @set_time_limit(5);
    //variable for rss url, feel free to change it to any RSS page...
    $rss_url = "http://phpns.com/rss.php";
    if ($rss_load = $rss_load = @file_get_contents($rss_url)) { //load raw.
        @$rss_xml = new SimpleXmlElement($rss_load);
        $start = 0;
        $list = "<ul>
			";

        foreach ($rss_xml->channel->item as $item) {
            $title = substr($item->title, 0, 30);

            if ($start < 5) {
                $list = $list.
                '<li><a href="'.$item->link.'">'.$title.'</a></li>';
            }
            ++$start;
        }

        $list = $list.'
			</ul>';
        return $list;
    } else {
        return "We can't connect to the phpns server to fetch latest announcements.";
    }
}


/*
MISC FUNCTIONS
Random functions that might aid for development/debugging
##############################################
##############################################
*/
function array_dump($array)
{
    $dump = "<div style=\"background: #eee; border: 1px dashed #333\">";
    foreach ($array as $key=>$value) {
        $dump = $dump."$key: $value<br />";
    }
    $dump = $dump."</div>";
    return $dump;
}

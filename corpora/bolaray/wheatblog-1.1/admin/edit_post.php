<?php

//
// File:    admin/edit_post.php
// License: GNU GPL
// Purpose: Pulls a post via permalink id into an editing interface
//		also pulls comments related to the post into their own editing
//		interfaces passes off form contents to edit_post_002.php for processing
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}

$page_title = 'Editing a Previous Post';
include_once("$wb_inc_dir/header.php");


$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);
$the_id = DB_Quote($_REQUEST['id']);

$result = DB_query("select * from wbtbl_posts where wbtbl_posts.id=$the_id", $db);

// insert form title & navigation
insert_form_heading('Edit post');
insert_navigation();

while($row = DB_fetch_array($result)) {
    $the_day      = $row['day'];
    $the_month    = $row['month'];
    $the_date     = $row['date'];
    $the_year     = $row['year'];
    $the_selected_category = $row['category'];
    $the_showpref = $row['showpref'];
    $the_locked   = $row['locked'];
    $the_title    = $row['title'];
    $the_body     = $row['body'];


    // echo post into a form, for editing
    //
    echo '<div class="subcontent" id="postform">';
    echo '<form id="addpost" method="post" action="edit_post_002.php">';


    // echo the title
    echo '<label>Title of Post</label>';
    echo '<input id="title" type="text" class="wheatblog_input" name="the_title" value="' . $the_title . '" /><br />';

    // echo the body
    echo '<label>Body of Post</label>';
    echo '<textarea id="body" class="wheatblog_textarea" name="the_body">' . $the_body . '</textarea><br />';

    // echo $the_id into a hidden tag
    echo '<input type="hidden" name="the_id" value="' . $the_id . '" />';



    echo '<label>Date, Visibilty, Category and Comment Locking</label><br />';
    // Day of week
    //
    $day = array('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday');
    echo '<select id="weekday" name="the_day">';

    foreach ($day as $i) {
        echo '<option' . ($the_day==$i ? ' selected' : '') . ">$i</option>\n";
    }

    echo '</select>&nbsp;';



    // Month menu
    //
    echo '<select id="month" name="the_month">';
    for ($i=1; $i<13; ++$i) {
        echo '<option' . ($the_month == $i ? ' selected' : '') .  '>' . sprintf("%02s", $i) .'</option>';
    }

    echo '</select>&nbsp;';



    // Date menu
    //
    echo '<select id="day" name="the_date">';
    for ($i=1; $i<32; ++$i) {
        echo '<option' . ($the_date == $i ? ' selected' : '') .  '>' . sprintf("%02s", $i) .'</option>';
    }
    echo '</select>&nbsp;';



    // Year menu
    //
    echo '<select id="year" name="the_year">';
    for ($i=2010; $i>1999; --$i) {
        echo '<option' . ($the_year == $i ? ' selected' : '') .  ">$i</option>\n";
    }
    echo '</select>&nbsp;';



    // Show the category
    //
    echo '<select id="category" name="the_category">';

    // Select categories in the db.  Run 2nd query on wbtbl_categories
    //
    $result_categories = DB_query("select * from wbtbl_categories", $db);


    // Loop through the categories
    //
    while($row_categories = DB_fetch_array($result_categories)) {
        $the_category_id   = $row_categories["id"];
        $the_category_name = $row_categories["category"];

        echo "<option value=\"$the_category_id\" ";

        if ($the_category_id == $the_selected_category) {
            echo("selected");
        }

        echo(">$the_category_name</option>\n");

    }
    echo("</select>&nbsp;&nbsp;&nbsp;\n");



    // Show Preferences
    //
    echo '<select id="show" name="the_showpref">';
    echo '<option value="0"' . ($the_showpref==0 ? 'selected' : '') . '>Hide</option>';
    echo '<option value="1"' . ($the_showpref==1 ? 'selected' : '') . '>Show</option>';
    echo '</select>&nbsp;';


    // Lock Comments
    //
    echo '<select id="lock" name="the_locked">';
    echo '<option value="0"' . ($the_locked==0 ? 'selected' : '') . '>Unocked</option>';
    echo '<option value="1"' . ($the_locked==1 ? 'selected' : '') . '>Locked</option>';
    echo '</select>&nbsp;';


    // add a submit button
    echo '<br /><br /><input  id="submit" type="submit" value="Revise Post" class="otherbutton" />';

    echo '</form><br />';
    echo '</div>';
}

// ---------------------------
// comments
// ---------------------------

// set vars to null
$comment_month = "";
$comment_date = "";
$comment_year = "";
$comment_title = "";
$comment_body = "";
$comment_author_name = "";
$comment_author_email = "";
$comment_author_url = "";
$the_post_id = "";

// select comments for this post
$result_comments = DB_query("select * from wbtbl_comments " .
    "where post_id = $the_id " .
    "order by comment_year, comment_month, comment_date", $db);

// print a comments header
insert_form_heading('Edit Comments');



while($row = DB_fetch_array($result_comments)) {
    $comment_id           = $row['id'];
    $comment_month        = $row['comment_month'];
    $comment_date         = $row['comment_date'];
    $comment_year         = $row['comment_year'];
    $comment_body         = $row['comment_body'];
    $comment_author_name  = $row['comment_author_name'];
    $comment_author_email = $row['comment_author_email'];
    $comment_author_url   = $row['comment_author_url'];


    echo '<div class="subcontent-comment">'."\n";
    echo '<div class="comment-heading">'."\n"; # heading is important, needs to be seperate
    echo '<h2 class="comment-auth"><strong>'.$comment_author_name.'</strong> said:</h2>'."\n";
    echo '<h3 class="comment-date">'.$the_day.', '.$the_month.'.'.$the_date.'.'.$the_year.'</h3>'."\n";
    echo '</div>'."\n";  # closes div.post-heading
    echo '<div class="comment-body">'."\n";
    echo '<form method="post" action="edit_comment.php">'."\n";
    echo '<textarea class="wheatblog_textarea_002" name="comment_body">'.$comment_body.'</textarea>' . "\n<br />";
    echo '<br /><br /><input type="submit" value="revise comment" class="otherbutton" />'."\n" .
         '<input type="hidden" name="comment_id" value="'.$comment_id.'">'."\n" .
         '</form>' .
          '</div>'."\n\n";
    echo '<div class="comment-menu">'."\n".
         '<ul class="postnav">'."\n".
         '<li title="Delete This Comment"><a href="delete_comment.php?post_id='.$the_id.'&amp;id='.$comment_id.'">delete</a></li>'.'|'."\n".
         '<li title="Comment Author"><a href="mailto:'.$comment_author_email.'">'.$comment_author_name.'</a></li>'.'|'."\n".
         '<li title="Comment Author\'s Website"><a href="'.$comment_author_url.'">'.'website</a></li>'."\n".
         '</ul>' ."\n".
         '</div>'."\n".
         '</div>'."\n";


}


//  Only print comments if they exist
//
//  echo '<div class="subcontent-heading">There are no Comments on this post.</div>';



// provides demarkation between comments / comment form
//
echo '<div class="subcontent-heading"></div>';



include_once("$wb_inc_dir/footer.php");

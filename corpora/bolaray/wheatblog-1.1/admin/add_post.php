<?php
//
// File:    admin/add_post.php
// License: GNU GPL
// Purpose: Gets a post from admin/index.php.
//
require_once('../settings.php');
if (! isAdmin()) {
    HariKari('You are not the admin.');
}

$page_title = 'Adding a New Post';
require_once("$wb_dir/includes/header.php");


// We already wrote the post and submitted it.  This code adds it to the
// database and gives feedback if necessary.
//
if (isset($_REQUEST['posted'])) {
    $the_day    = $_POST['the_day'];
    $The_day    = DB_quote($the_day);
    $the_month  = $_POST['the_month'];
    $The_month  = DB_quote($the_month);
    $the_date   = $_POST['the_date'];
    $The_date   = DB_quote($the_date);
    $the_year   = $_POST['the_year'];
    $The_year   = DB_quote($the_year);
    $the_cat    = $_POST['the_category'];
    $The_cat    = DB_quote($the_cat);
    $the_show   = $_POST['the_showpref'];
    $The_show   = DB_quote($the_show);
    $the_locked = $_POST['the_locked'];
    $The_locked = DB_quote($the_locked);
    $the_title  = $_POST['the_title'];
    $The_title  = DB_quote($the_title);
    $the_body   = $_POST['the_body'];
    $The_body   = DB_quote($the_body);
    $timestamp  = date('r');
    $Timestamp  = DB_quote($timestamp);


    // Used only to display the text after the user submits new post.
    $show_body = stripslashes($_POST['the_body']);

    $db->query("insert into wbtbl_posts (id, day, month, date, year, category,
		title, body, showpref, locked, timestamp) values (null, $The_day,
		$The_month, $The_date, $The_year, $The_cat, $The_title, $The_body,
		$The_show, $The_locked, $Timestamp)");

    // Get show_id for the previous insert query so we can use it in feedback.
    //
    $last_post_id = $db->insertId();



    // Post body

    echo
    '<div class="subcontent">' . "\n" .
    '<div class="post-heading"> ' . "\n" . # heading important, must be separate
    '<h2 class="post-title">' . $the_title . '</h2>' . "\n" .
    '<h3 class="post-date">' . $the_day . ', ' . $the_month . '.' . $the_date .
        '.' . $the_year . '</h3>' . "\n" .
    "</div>\n" .  # close div.post-heading
    '<div class="post-body">' . $show_body . "</div>\n\n";

    #links are now unordered list
    echo '<div class="post-menu">'."\n".'<ul class="postnav">'."\n";

    // only difference from  "universal" post display is the ommission of
    // comments and the addition of the show preference.
    //
    if ($the_show == 1) {
        echo '<li>This post is currently <strong>visible</strong>. </li>'."\n";
    } else {
        echo '<li>This post is currently <strong>hidden</strong> .</li>'."\n";
    }


    echo "</ul>\n</div>\n";  # closes list and div.post-menu
    echo "</div>\n\n"; # closes div.indent

    include("$wb_inc_dir/rss.php");
    include("$wb_inc_dir/footer.php");
}



// If we're here, it means we want to add a post but haven't written it yet.
insert_form_heading('Add a New Post');

?>



<div class="subcontent" id="postform">

	<form id="addpost" method="post" action="add_post.php?posted=1">

	  
  <label>Title of Post</label>
  <input id="title" class="wheatblog_input" type="text" name="the_title"><br /><br />


  <label>Body of Post</label>
  <textarea id="body" class="wheatblog_textarea" name="the_body"></textarea><br /><br />


 <label>Date, Visibilty, Category and Comment Locking</label><br />
		<select id="weekday" name="the_day">
		<option value=""> -- </option>
		<option value="Saturday"  <?php if (date('D')=='Sat') {
		    echo 'selected';
		} ?>>Saturday</option>
		<option value="Sunday"    <?php if (date('D')=='Sun') {
		    echo 'selected';
		} ?>>Sunday</option>
		<option value="Monday"    <?php if (date('D')=='Mon') {
		    echo 'selected';
		} ?>>Monday</option>
		<option value="Tuesday"   <?php if (date('D')=='Tue') {
		    echo 'selected';
		} ?>>Tuesday</option>
		<option value="Wednesday" <?php if (date('D')=='Wed') {
		    echo 'selected';
		} ?>>Wednesday</option>
		<option value="Thursday"  <?php if (date('D')=='Thu') {
		    echo 'selected';
		} ?>>Thursday</option>
		<option value="Friday"    <?php if (date('D')=='Fri') {
		    echo 'selected';
		} ?>>Friday</option>
		</select>&nbsp;

  
		
			<select id="month" name="the_month">
<?php
		    // Print month menu list
		    //
		    for ($i=1; $i<13; ++$i) {
		        $m = sprintf("%02d", $i);
		        $this_month = date('m') == $m;
		        echo "<option value=\"$m\"" . ($this_month ? ' selected' : '') . ">$m</option>\n";
		    }
?>
        </select>&nbsp;
     
        <select id="day" name="the_date">
<?php
            // Print date menu list
            //
            for ($i=1; $i<32; ++$i) {
                $day = sprintf("%02d", $i);
                $this_day = date('d') == $day;
                echo "<option value=\"$day\"" . ($this_day ? ' selected' : '') .
                    ">$day</option>\n";
            }
?>
        </select>&nbsp;
    
        <select id="year" name="the_year">
          <option value="2010" <?php if(date("Y")=="2010") {
              echo("selected");
          } ?>>2010</option>
          <option value="2009" <?php if(date("Y")=="2009") {
              echo("selected");
          } ?>>2009</option>
          <option value="2008" <?php if(date("Y")=="2008") {
              echo("selected");
          } ?>>2008</option>
          <option value="2007" <?php if(date("Y")=="2007") {
              echo("selected");
          } ?>>2007</option>
          <option value="2006" <?php if(date("Y")=="2006") {
              echo("selected");
          } ?>>2006</option>
          <option value="2005" <?php if(date("Y")=="2005") {
              echo("selected");
          } ?>>2005</option>
          <option value="2004" <?php if(date("Y")=="2004") {
              echo("selected");
          } ?>>2004</option>
          <option value="2003" <?php if(date("Y")=="2003") {
              echo("selected");
          } ?>>2003</option>
          <option value="2002" <?php if(date("Y")=="2002") {
              echo("selected");
          } ?>>2002</option>
          <option value="2001" <?php if(date("Y")=="2001") {
              echo("selected");
          } ?>>2001</option>
          <option value="2000" <?php if(date("Y")=="2000") {
              echo("selected");
          } ?>>2000</option>
        </select>&nbsp;&nbsp;


       
         <select id="category" name="the_category">

        <?php

    // insert post into the database
    $db->query("SELECT * FROM wbtbl_categories ORDER BY id");

while($row = $db->fetchArray()) {
    $the_category_id   = $row['id'];
    $the_category_name = $row['category'];

    echo("<option value=\"$the_category_id\">" . "$the_category_name" . "</option>\n");
}

?>

        </select>&nbsp;
    

        <select id="show" name="the_showpref">
          <option value="1">show</option>
          <option value="0">hide</option>
        </select>
     
       
	   
	   <!-- this should be a checkbox or a radio button -->
        <select id="lock" name="the_locked">
          <option value="0">Unlock</option>
          <option value="1">Lock</option>
        </select><br /><br />
   
  <input id="submit" type="submit" value="Add this Post"><br />
  </form>
</div>


<?php include("$wb_inc_dir/footer.php"); ?>

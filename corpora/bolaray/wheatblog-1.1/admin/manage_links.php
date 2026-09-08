<?php
//
// File:    admin/manage_links.php
// License: GNU GPL
// Purpose: Presents current blogroll in forms for editing.  Presents a form
//					for adding a new links.  Based on manage_categories.php
//
require_once('../settings.php');

if (! isAdmin()) {
    HariKari('You are not the admin.');
}

$page_title = 'Managing Links';
include_once("$wb_inc_dir/header.php");


insert_navigation();

$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// select categories in the database
// FIXME:  add wbtbl_links to settings and db structure
$result = DB_query("select * from wbtbl_links", $db);

insert_form_heading('Edit Links');
if ($use_sessions == 0) {
    insert_navigation();
}

// loop through the categories
while($row = DB_fetch_array($result)) {
    $the_id = $row["id"];
    $the_link_name = $row["link_name"];
    $the_link_location = $row["link_location"];

    // echo categories into a form, for editing

    ?>
	   
	    <div class="subcontent-form">        
        <form method="post" action="manage_links_002.php">
        <input class="text" name="the_link_name" type="text" value="<?= $the_link_name; ?>">
        <input class="text" name="the_link_location" type="text" value="<?= $the_link_location; ?>" />
		<input name="the_id" type="hidden" value="<?= $the_id; ?>" />
		<input type="submit" value="edit" class="sub" />
        </form>
		<form method="get" action="delete_link.php">
		<input name="the_id" type="hidden" value="<?= $the_id; ?>" />
        <input type="submit" value="delete" class="sub" onclick="return deleteConfirm();" />
		</form>
		</div>
	   
	   
	   <?php

}
// print a form for adding new links

insert_form_heading('Add a New Link');

if ($use_sessions == 0) {

    insert_navigation();
}

// insert form for new categories

// insert form for new categories
?>  
	   
	   <div class="subcontent-form"> 
        <form  method="post" action="add_link.php">
        <input class="text" name="the_link_name" type="text" />
        <input class="text" name="the_link_location" type="text" />
        <input type="submit" value="add" class="otherbutton" />
        </form>
		</div>
		
<?php include_once("$wb_inc_dir/footer.php"); ?>

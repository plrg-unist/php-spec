<?php
//
// File:    admin/manage_categories.php
// License: GNU GPL
// Purpose: Presents current categories in forms for editing.  Presents a form
//					for adding a new category.
//
require_once('../settings.php');
if (! isAdmin()) {
    HariKari('You are not the admin.');
}

$page_title = 'Managing Categories';
include_once("$wb_inc_dir/header.php");


insert_navigation();

$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// select categories in the database
$result = DB_query("select * from wbtbl_categories", $db);

insert_form_heading('Edit Categories');


// loop through the categories
while($row = DB_fetch_array($result)) {
    $the_id = $row['id'];
    $the_category = $row['category'];

    // echo categories into a form, for editing

    ?>
		
        <div class="subcontent-form">        
        <form method="post" action="edit_categories.php">
        <input class="text" name="the_category" type="text" value="<?= $the_category; ?>">
        <input class="text" name="the_id" type="hidden" value="<?=$the_id; ?>" />
		<input type="submit" value="edit" class="otherbutton" />
        </form>
		<form method="post" action="delete_category.php">
		<input name="the_category" type="hidden" value="<?=$the_category; ?>" />
        <input type="submit" value="delete" class="otherbutton" />
		</form>
		</div>

<?php

}


// echo form title
insert_form_heading('Add a New Category');


// insert form for new categories
?>  		  
    
	   <div class="subcontent-form"> 
        <form method="post" action="add_category.php">
        <input class="text" name="the_category" type="text" />
        <input type="submit" value="add" class="otherbutton" />
        </form>
		</div>


<?php include_once("$wb_inc_dir/footer.php"); ?>

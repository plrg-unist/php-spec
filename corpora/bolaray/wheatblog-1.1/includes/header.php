<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<!-- echo the page title passed from the calling page -->
<title><?php echo $blog_title.' - ';
if($page_title != "") {
    echo $page_title;
} else {
    echo $blog_subtitle;
}?></title>
<link rel="stylesheet" type="text/css" href="<?php echo "$wb_url/css/$wb_style.css"; ?>" title="<?php echo "$wb_style.css"; ?>" /> 
<!-- <link rel="alternate stylesheet" type="text/css" href="<?php echo "$wb_url/"; ?>css/dividedsky.css" title="dividedsky.css"/> -->
<!-- <link rel="alternate stylesheet" type="text/css" href="<?php echo "$wb_url/"; ?>css/spacious.css" title="dividedsky.css"/> --> 
<!-- <link rel="alternate stylesheet" type="text/css" href="<?php echo "$wb_url/"; ?>css/autumnsky.css" title="dividedsky.css"/> --> 
<!-- <link rel="alternate stylesheet" type="text/css" href="<?php echo "$wb_url/"; ?>css/metal.css" title="dividedsky.css"/> --> 
<meta http-equiv="pragma" content="no-cache" />
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<meta http-equiv="content-style-type" content="text/css"  />
<?php if ($_SERVER['SCRIPT_FILENAME'] == $wb_dir.'/add_comment.php' || $_SERVER['SCRIPT_FILENAME'] == $wb_dir.'/admin/delete_comment.php') {
    echo '<meta http-equiv="refresh" content="5; url='.$wb_url.'" />';
}
?>
<link rel="index" href="<?php echo $wb_url; ?>" />
<!-- <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" /> -->
<link rel="alternate" type="application/rss+xml" title="<?php echo $name_of_blog; ?> RSS feed" href="<?php echo $wb_url.'/rss.xml'; ?>" /> 
<style type="text/css">
<!--/*--><![CDATA[/*><!--*/
/* import any custom markup - currently unused */
/* @import url("css/custom.css"); */
/*]]>*/-->
</style>
<script type="text/javascript">
    function deleteConfirm() {
      return confirm("Are you sure you want to delete this?");	
    }
  </script>
</head>
<body>
<!-- handle the title block -->
<div id="container">
<?php
  // ==========================================
  // open the proper template:
  // template 3 = the public layer
  // template 4 = the admin layer
  // ==========================================

  if($template == 3) {

      echo '<div id="title">'."\n".'<h1>'.$blog_title.'</h1>'."\n".'<h2>'.$blog_subtitle.'</h2>'."\n".'</div>'."\n";

  } elseif ($template == 4) {
      echo '<div id="title">'."\n".'<h1>'.$blog_title.'</h1>'."\n".'<h2>'.$page_title.'</h2>'."\n".'</div>'."\n";

  // ---------------------------------------------------------------------------
  // else, if no template is specified, try to open up gracefully
  // ---------------------------------------------------------------------------

  } else {

      echo '<div id="title"><h1>'.$name_of_blog.' Legacy Page</h1></div>'."\n";
  }
?>
<!-- close the title block Added (JBE 04/02/05) -->
<?php
// Yes, yes, it's ugly.  But it works.  I'll get around to making it perty.
// Getting all coldfusion-ish with the coding style here...he..he..he

if (! isLoggedIn()) {
    ?>

<div class="access">
	<form name="admin" method="post" action="admin/login.php">
	<label>Username:</label>
	<input id="user" size="12" name="login" type="text" />
	<label>Password:</label>
	<input id="pass" size="12" name="password" type="password" />
	</form>
<a id="login" href="javascript:document.admin.submit();">Login</a>
</div>	

<?php } else { ?>

<div class="access" id="confirmed">
	<span>You are currently logged in as <strong><?php echo $_SESSION['login']; ?></strong>.</span>
	<a id="login" title="Logout" href="<?php echo $wb_admin_url; ?>/login.php?action=logout">Logout</a>
</div>	

<?php } ?>



<!-- closes access block -->

<div id="navigation"><!-- include the navigation -->
<?php
    // side box div, including all the nav functionality moved from footer.php to  (moved JBE 04/02/05)
    function StartNavGroup()
    {
        echo '<ul class="nav-group">'."\n";
    }
    function NavItem($url, $link)
    {
        echo '<li class="nav-item"><a href="' . $url . '">' . $link . '</a></li>'."\n";
    }
    /*
    # conditional navigation element
    function NavItemLocal($self, $file, $link)
    {
     if ( $self == $file) {
            echo '<li class="nav-item-static" title="You are here.">'. $link . '</li>';

        } else {

            echo '<li class="nav-item"><a href="' . $file . '">' . $link . '</a></li>';
        }
    }
    */
    function NavGroupHeading($text)
    {
        echo '<li class="nav-group-heading">' . $text . '</li>'."\n";
    }

    function EndNavGroup()
    {
        echo '</ul>'."\n";
    }
?>

	<?php

        echo '<div id="nav-nav">';
StartNavGroup();
NavGroupHeading(NAVIGATION);
NavItem($wb_url.'/', HOME);
NavItem($wb_url.'/view_by_title.php', POST_INDEX);
NavItem($wb_url.'/registration.php', REGISTER_ACCOUNT);
EndNavGroup();
echo '</div>'."\n";

// list the categories:  start


// select recent posts in the database
//
$db->query("select * from wbtbl_categories order by category");

// output the current categories
// open up a div for the output
echo '<div id="nav-cats">';
StartNavGroup();
NavGroupHeading(CATEGORIES);

// loop through results and list each category
while($row = $db->fetchArray()) {
    $the_category = $row['id'];
    $the_category_name = $row['category'];
    NavItem($wb_url.'/view_by_category.php?the_category='.$the_category, $the_category_name);
}

// close the output ul
EndNavGroup();
echo '</div>'."\n";
// list the categories: stop


if (isAdmin()) {
    echo '<div id="nav-admin">';
    StartNavGroup();
    NavGroupHeading(ADMINISTRATION);
    NavItem("$wb_admin_url/index.php", 'admin page');
    NavItem("$wb_admin_url/add_post.php", 'add post');
    NavItem("$wb_admin_url/manage_posts.php", 'manage posts');
    NavItem("$wb_admin_url/manage_categories.php", 'manage categories');
    NavItem("$wb_admin_url/manage_links.php", 'manage links');
    NavItem("$wb_admin_url/manage_users.php", 'manage users');
    EndNavGroup();
    echo '</div>'."\n";
}


// nav group for dynamic links
echo '<div id="nav-links">';
StartNavGroup();
NavGroupHeading(LINKS);


// select all links in the database
$db->query("select * from wbtbl_links order by link_name");

// loop through results and echo links
while($row = $db->fetchArray()) {
    $the_id = $row['id'];
    $the_link_name = $row['link_name'];
    $the_link_location = $row['link_location'];

    // echo the links
    NavItem("$the_link_location", "$the_link_name");
}

EndNavGroup();
echo '</div>'."\n";
?>
</div><!-- close navigation -->

<!-- open the main_box -->
<div id="content">
<!-- JBE possible expansion <div class="heading"></div> -->
	<!-- end of included header -->

<?php




// Print a nicely formatted message and die.
//
function HariKari($msg)
{
    echo '<div style="width: 40%; padding: 10px; border: 1px solid #000; ' .
     'background: #EEF; margin: auto;">' .
      '<h2 style="font: bold 14px Tahoma, Verdana, Helvetica, sans-serif;">' .
      'wheatblog error:</h2>' .
      '<hr />' .
      '<p style="font: 14px Tahoma, Verdana, Helvetica, sans-serif;">' .
      $msg .
      '</p></div>';

    exit(0);
}





// Implodes an associative array (PJS)
//
function Ass_Implode($glue, $array)
{
    $keys = array_keys($array);
    $vals = array_values($array);

    return implode($glue, $keys).$glue.implode($glue, $vals);
}


// Explodes an associative array (PJS)
//
function Ass_Explode($glue, $str)
{
    $array = explode($glue, $str);

    $size = count($array);

    for ($i=0; $i < $size/2; $i++) {
        $out[$array[$i]]=$array[$i+($size/2)];
    }

    return($out);
}



function insert_navigation()
{
    echo '<div class="adminbar">'."\n".'<ul>'."\n";
    echo '<li><a href="add_post.php">Add a Post</a></li>'."\n";
    echo '<li><a href="manage_posts.php">Manage Posts</a></li>'."\n";
    echo '<li><a href="manage_categories.php">Manage Categories</a></li>'."\n";
    echo '<li><a href="manage_links.php">Manage Links</a></li>'."\n";
    echo '<li><a href="manage_users.php">Manage Users</a></li>'."\n";
    echo "\n".'</ul>'."\n".'</div>'."\n";  # closes list and div.post-menu
}



function insert_form_heading($heading)
{
    echo '<div class="form-heading">'."\n".'<h3>' . $heading .'</h3>'."\n".'</div>'."\n";
}



function insert_tagline()
{
    global $wb_url, $wb_rss;

    echo "\n\n" . '<div id="wb-tag">' . "\n" .
    '<ul>'. "\n" .
    '<li>powered by <a href="http://wheatblog.sourceforge.net" ' .
    'title="blogware for the rest of us">wheatblog</a>&nbsp;&middot;&nbsp;</li>' . "\n" .
    '<li><a href="http://jigsaw.w3.org/css-validator/validator?uri=http://' .
        $_SERVER['HTTP_HOST'] .  $_SERVER['PHP_SELF'].'" title="Valid CSS">CSS' .
        '</a>&nbsp;&middot;&nbsp;</li>' . "\n" .
    '<li><a href="http://validator.w3.org/check?uri=http://' .
        $_SERVER['HTTP_HOST'] . $_SERVER['PHP_SELF'] . '" title="Valid XHTML' .
        ' 1.0">XHTML</a>&nbsp;&middot;&nbsp;</li>' . "\n" .
    '<li><a href="'.$wb_url.'/'.$wb_rss.'" title="RSS 2.0 Syndication">RSS' .
        '</a></li>'."\n" .
    '</ul>
	</div>';
}

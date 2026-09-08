<?php

// FIXME
// We need a way to protect this file from being run.  But we can't use
// sessions for a number of reasons.  How do we do this?



$action = (isset($_REQUEST['action'])) ? $_REQUEST['action'] : 0;
$debug = 1;




if ($action == 0) {
    myheader();

    ?>
	<h2>Welcome to Wheatblog!</h2>

	<p>Congratulations on installing Wheatblog.  Before you begin blogging, we
	first need to set a few variables.  After you set these variables, the
	first thing you should do is log in to the blog with your admin account
	and navigate to the admin page.</p>

	<p>I'm going to assume that you obtained the full Wheatblog source code,
	and that source code is sitting somewhere on your hard drive.  I'm also
	going to assume that you have some kind of database like MySQL, SQLite or
	pgSQL.</p>

	<p>Installation of Wheatblog will procede in 4 easy steps:</p>
	
	<ol>
	<li>Details of your database</li>
	<li>The location of Wheatblog's installation</li>
	<li>User accounts
	<li>General configuration options</li>
	</ol>

	<form method="post" action="<?= $_SERVER['PHP_SELF'] . '?action=1' ?>">
	<input type="submit" value="continue" />
	</form>
	<?php

    myfooter();
}





if ($action == 1) {
    myheader();

    ?>
	<h3>Step 1: Database Variables</h3>

	<form method="post" action="<?= $_SERVER['PHP_SELF'] . '?action=2' ?>">

	<p>I first need to know what database you plan to use.  Please select the
	database you plan on using:
	<select name="db">
	<option value="MySQL">MySQL</option>
	<option value="SQLite">SQLite</option>
	<option value="pgSQL">pgSQL</option>
	</select></p>

	<p>What host is this database located on?  If you don't know how to answer
	this question, keep the default value.
	<input type="text" name="site" value="localhost" /></p>

	<p>I need to create a database for you.  If you use a full RDBMS like
	MySQL or pgSQL, this database should be named something like "wheatblog".
	If you use SQLite, you must change this value to point to your database file,
	for example <tt>/usr/local/wheatblog.db</tt>.  If you don't understand
	this, and aren't using SQLite, then just leave the default value as is:
	<input type="text" name="dbname" value="wheatblog" /></p>

	<p>Lastly, I need a user and account to access your database.  SQLite
	users will want to keep these two fields blank since SQLite doesn't use
	usernames and passwords.
	<p>Enter your DB username: <input type="text"     name="user" /></p>
	<p>Enter your DB password: <input type="password" name="pass"  /></p>

	<input type="submit" value="continue" />
	</form>
	<?php

    myfooter();
    exit(0);
}




if ($action == 2) {
    myheader();

    // Get the variables from step 1
    //
    $db_type    = (isset($_POST['db'])) ? $_POST['db'] : '';
    $database   = (isset($_POST['dbname'])) ? $_POST['dbname'] : '';
    $adminlogin = (isset($_POST['dblogin'])) ? $_POST['dblogin'] : '';
    $adminpass  = (isset($_POST['dbpass'])) ? $_POST['dbpass'] : '';

    // adminlogin and adminpass are allowed to be null for SQLite users.
    //
    if      ($db_type == '') {
        die('db_type was null.  Wierd error!');
    } elseif ($database == '') {
        die('database was null.');
    }

    if ($user == '' && $db != 'SQLite') {
        die('You must give me a username to access your database.');
    }

    if ($pass  == '' && $db != 'SQLite') {
        die('You must give me a password to access your database.');
    }


    $vars = array(
        'db'     => $db,
        'dbname' => $dbname,
        'user'   => $user,
        'pass'   => $pass,
    );
    $var = Ass_Implode(',', $vars);

    ?>
	<h3>Step 2: Location of Wheatblog</h3>

	<form method="post" action="<?= $_SERVER['PHP_SELF'] . '?action=3' ?>">

	<p>Give the full pathname of the Wheatblog directory (not the URL).
	Do not add a traling slash or backslash.
	<input type="text" name="wb_dir"></p>

	<p>What is the URL for your blog?
	<input type="text"   value="http://"     name="wb_url" /></p>
	<input type="submit" value="continue" />
	<input type="hidden" value="<?= $var ?>" name="var" />
	</form>
	<?php

    if ($debug) {
        echo '<table border="1">';
        foreach ($vars as $key) {
            echo "<tr><td>$key</td><td>$vars[$key]</td></tr>";
        }
        echo '</table>';
    }

    myfooter();
    exit(0);
}






if ($action = 3) {
    myheader();


    $wb_dir = (isset($_POST['wb_dir'])) ? $_POST['wb_dir'] : '';
    $wb_url = (isset($_POST['wb_url'])) ? $_POST['wb_url'] : '';

    // wb_dir and wb_url *must* not be NULL.
    //
    if      ($wb_dir  == '') {
        die('wb_dir was null.');
    } elseif ($wb_url  == '') {
        die('wb_url was null.');
    }

    // Add the new variables to the array.
    //
    $vars = Ass_Explode(',', $_POST['var']);
    $vars['wb_dir']       = $wb_dir;
    $vars['wb_url']       = $wb_url;
    $vars['wb_admin_dir'] = '$wb_dir/admin';
    $vars['wb_admin_url'] = '$wb_url/admin';

    // Pack up the array to ship it to action 4.
    //
    $var = Ass_Implode(',', $vars);

    ?>
	<h3>Step 3: Wheatblog Account</h3>

	<form method="post" action="<?= $_SERVER['PHP_SELF'] . '?action=4' ?>">

	<p>You need an administrative account.  This will be the account that you
	post from and do all blog-administrative things that need to be done.</p>

	<p>Enter your admin login name: <input type="text" name="adminlogin" /></p>
	<p>Enter your admin password: <input type="password" name="adminpassword" /></p>

	<input type="hidden" value="<?= $var ?>" name="var" />
	<input type="submit" value="continue" />
	</form>
	<?php


    if ($debug) {
        echo '<table border="1">';
        foreach ($vars as $key) {
            echo "<tr><td>$key</td><td>$vars[$key]</td></tr>";
        }
        echo '</table>';
    }

    myfooter();
    exit(0);
}





if ($action == 4) {
    myheader();

    // Add the new variables to the array.
    //
    $vars = Ass_Explode(',', $_POST['var']);
    $vars['adminlogin']    = $adminlogin;
    $vars['adminpassword'] = $adminpassword;

    // Technically, they didn't HAVE to set an admin login and password, but
    // it'll make life much simpler if they do.
    //
    if      ($adminlogin    == '') {
        die('adminlogin was null.');
    } elseif ($adminpassword == '') {
        die('adminpassword was null.');
    }

    // Pack up the array to ship it to action 4.
    //
    $var = Ass_Implode(',', $vars);

    ?>
	<h3>Step 4: General Configuration</h3>

	<form method="post" action="<?= $_SERVER['PHP_SELF'] . '?action=5' ?>">

	<p>Don't Panic.  If the information from the first 3 steps is correct,
	you'll be able to change any configuration item at a later date by using
	the configure option from the Wheatblog admin interface.  And even if that
	information is incorrect, you can always run Wheatblog installer again.
	No harm done.</p>



	<input type="submit" value="continue" />
	</form>
	<?php
    myfooter();
    exit(0);
}






if ($action == 5) {
    myheader();

    ?>
	<h3>Step 5: General Configuration Options</h3>

	<form method="post" action="<?= $_SERVER['PHP_SELF'] . '?action=6' ?>">

	<input type="submit" value="continue" />
	</form>
	<?php

    // Write the settings.php file

    // Create the database.

    // Create .htaccess file.

    // touch rss.xml and change its permissions.

    myfooter();
}





if ($action == 6) {
    header("Location: $wb_url");
}





function Create_Settings($vars)
{
    $fp = fopen("$wb_dir/settings.php", 'w');
    fwrite(
        $fp,
        "<php\n" .
    "// database connection variables\n" .
    "//\n" .
    '$site = ' . $vars['site'] . "\n" .
    '$user = ' . $vars['user'] . "\n" .
    '$pass = ' . $vars['pass'] . "\n" .
    "\n\n" .

    "// SQLite users: This is a file on your filesystem (wheatblog.db).\n" .
    "// Everyone else: This is the name of a database.\n" .
    "//\n" .
    '$database       = ' . $vars['wheatblog']        . "\n" .
    "\n\n" .

    "// Database tables.  Do not change.\n"           . "\n" .
    "//\n" .
    '$tblPosts       = ' . $vars['wbtbl_posts']      . "\n" .
    '$tblUsers       = ' . $vars['wbtbl_users']      . "\n" .
    '$tblComments    = ' . $vars['wbtbl_comments']   . "\n" .
    'wbtbl_categories  = ' . $vars['wbtbl_categories'] . "\n" .
    'wbtbl_links       = ' . $vars['wbtbl_links']      . "\n" .
    "\n\n" .

    "// Database Backend.\n".
    "//\n" .
    "include('includes/backend_" . $vars['db_type'] . ".php');\n" .
    "// include('includes/backend_sqlite.php');\n".
    "// include('includes/backend_pgsql.php');\n".
    "// include('includes/backend_mysql.php');\n".
    "\n\n" .

    "// Chose a language file (Uncomment appropriate line)\n" .
    "//\n" .
    '$ui_language = ' . $vars['language'] . ".php';\n".
    "\n\n" .

    "// Posts on front page\n" .
    '$front_page_max = ' . $vars['front_page_max'] . "\n" .
    "\n\n" .

    "// blog directory url\n" .
    "//\n" .
    '$wb_url = ' . $vars['wb_url'] . "\n" .
    "\n\n" .


    "// blog admin directory url\n" .
    "//\n" .
    '$wb_admin_url = ' . $vars['wb_admin_url'] . "\n" .
    "\n\n" .

    "// blog install directory\n" .
    "//\n" .
    '$wb_dir = ' . $vars['wb_dir'] . "\n" .
    "\n\n" .


    "// blog admin install directory\n" .
    "//\n" .
    '$wb_admin_dir = ' . $vars['wb_admin_dir'] . "\n" .
    "\n\n"
    );

}




function myheader()
{
    echo '<html><head><title>Wheatblog Installer</head><body>';
}


function myfooter()
{
    echo '</body></html>';
}

?>

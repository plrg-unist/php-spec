<?php

// require_once('../settings.php');  FIXME   please remove me.


function DB_error($db)
{
    echo(mysql_errno($db) . ": " . mysql_error($db) . "\n");
}



function DB_connect($site, $user, $pass)
{
    $retval = mysql_connect($site, $user, $pass)
        or die('<h2>Could not connect to database server</h2>' .
            '<p>Check passwords and sockets</p>');

    return $retval;
}



function DB_select_db($database, $db)
{
    mysql_select_db($database, $db)
        or die("<h2>Could not select database $database</h2>" .
            '<p>Check database name</p>' .
            '<p>MySQL reports: ' . DB_error($db));
}



function DB_insert_id($db)
{
    $retval = mysql_insert_id($db)
        or die('<p>Error in DB_insert_id.</p>' .
            'MySQL reports: ' . DB_error($db));

    return $retval;
}



function DB_num_rows($arg)
{
    return mysql_num_rows($arg);
}



function DB_fetch_array($args)
{
    return mysql_fetch_array($args);
}



function DB_query($sql, $db)
{
    $retval = mysql_query($sql, $db)
        or die('DB_query:' . DB_error($db));

    return $retval;
}


function DB_quote($arg)
{
    if (get_magic_quotes_gpc()) {
        $arg = stripslashes($arg);
    }

    if (is_numeric($arg)) {
        return $arg;
    }

    return "'" . mysql_real_escape_string($arg) . "'";
}


function DB_debug($arg)
{
    echo "\n$arg\n";
    exit;
}

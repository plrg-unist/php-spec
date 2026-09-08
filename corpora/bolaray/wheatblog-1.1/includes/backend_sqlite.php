<?php



function DB_error($db)
{
    return sqlite_error_string(sqlite_last_error($db));
}



function DB_connect($site, $user, $pass)
{
    global $database;

    $db = sqlite_open($database)
        or die('<h2>Could not connect to database server</h2>' .
            '<p>Check passwords and sockets</p>');

    return $db;
}



function DB_select_db($database, $db)
{
}



function DB_insert_id($db)
{
    $retval = sqlite_last_insert_rowid($db)
        or die('DB_insert_id error: ' . DB_error($db));

    return $retval;
}



function DB_num_rows($arg)
{
    return sqlite_num_rows($arg);
}



function DB_fetch_array($args)
{
    return sqlite_fetch_array($args);
}



function DB_query($sql, $db)
{
    $retval = sqlite_query($db, $sql)
        or die('DB_query:' . DB_error($db));

    return $retval;
}

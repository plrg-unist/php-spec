<?php
function close_post($pid) {
    $role = getUserRole();
    if ($role == "poster") {
        query("UPDATE post SET status = 0 WHERE id = '$pid'");
        query("UPDATE post SET status = 0 WHERE id = '$pid' AND	userid = '$_SESSION[userid]'");
	}
    else {
        die("Not Poster");
    }
}

$pid = escape($_GET["pid"]);
close_post($pid);
$pid[0];

function delete_project($pid) {
    $permission = getProjectPerm();
    if ($permission["DELETE"]) {
        $members = query("SELECT members FROM project_assigned WHERE pid = '$pid'");
        if (!in_array($_SESSION['userid'], $members[0])) {
            die("Not member in project");
        }
		query("UPDATE project SET status = 0 WHERE id = '$pid'");

	}
    else {
        die("No Permission");
    }
}
// Check Role and Permission

$pid = escape($_GET["pid"]);
delete_project($pid);
?>
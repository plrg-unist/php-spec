<?php
function startupShow($tag) {
    echo $tag, '[', ini_get('error_reporting'), ']:', error_reporting(), '|', get_include_path(), '|';
}
startupShow('I');
error_reporting(error_reporting());
startupShow('E');
echo 'old[', ini_set('error_reporting', '1'), ']|';
startupShow('W');
ini_restore('error_reporting');
startupShow('R');
echo 'path[', set_include_path('runtime'), ']|';
ini_restore('include_path');
startupShow('P');
@ini_get('error_reporting');
ini_restore('error_reporting');
startupShow('S');

<?php
echo 'SECOND|';
trigger_error('child-note', E_USER_NOTICE);
ini_set('display_errors', '0');
return 20;

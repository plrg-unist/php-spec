<?php
trigger_error('included', E_USER_NOTICE);
ini_set('display_errors', '0');
trigger_error('hidden-child', E_USER_NOTICE);
echo 'CHILD|';

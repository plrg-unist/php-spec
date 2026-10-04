<?php
echo 'BEFORE|';
trigger_error('fatal', E_USER_ERROR);
echo 'AFTER';

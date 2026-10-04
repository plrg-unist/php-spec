<?php
$v=NAN; $assigned='kept';
set_error_handler(function($level,$message) { global $v; $v='changed'; echo 'H|'; throw new Exception('stop'); });
try { $assigned=(object)$v; } catch (Exception $e) { echo $e->getMessage(), '|'; echo $e->getTraceAsString(), '|'; }
echo $assigned, ':', $v, '|END';

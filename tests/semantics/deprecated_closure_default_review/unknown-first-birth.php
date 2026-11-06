<?php
#[Deprecated] const X = [];
eval('function make188() { return function($value = X) { echo "E|"; }; } $early = make188();');
set_error_handler(function() { echo 'H|'; return true; });
$early();
$early = null;
$later = make188();
$later();

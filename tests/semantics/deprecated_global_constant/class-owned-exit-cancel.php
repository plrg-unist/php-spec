<?php
#[Deprecated] const X = [];
class Box194 { const VALUE = X; }
class Local194 { function __destruct() { echo 'D|'; throw new Exception('cancel'); } }
function stop194() { $local = new Local194(); echo 'H|'; exit(7); }
function notice194() { echo 'H|'; return true; }
set_error_handler('stop194');
try { echo Box194::VALUE === [] ? 'E|' : 'N|'; } catch (Exception $error) { echo 'K|'; }
set_error_handler('notice194');
echo Box194::VALUE === [] ? 'E|' : 'N|';

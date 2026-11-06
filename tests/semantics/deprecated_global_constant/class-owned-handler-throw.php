<?php
#[Deprecated] const X = [];
class Box194 { const VALUE = X; }
function stop194() { echo 'H|'; throw new Exception('stop'); }
function notice194() { echo 'H|'; return true; }
set_error_handler('stop194');
try { echo Box194::VALUE === [] ? 'E|' : 'N|'; } catch (Exception $error) { echo 'K|'; }
set_error_handler('notice194');
echo Box194::VALUE === [] ? 'E|' : 'N|';
echo Box194::VALUE === [] ? 'E|' : 'N|';

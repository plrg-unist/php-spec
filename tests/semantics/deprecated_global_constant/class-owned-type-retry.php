<?php
#[Deprecated] const X = [];
class Box194 { const int VALUE = X; }
function notice194() { echo 'H|'; return true; }
set_error_handler('notice194');
try { echo Box194::VALUE; } catch (TypeError $error) { echo 'T|'; }
try { echo Box194::VALUE; } catch (TypeError $error) { echo 'T|'; }

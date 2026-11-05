<?php
#[Deprecated('old',since:'8.5')]
const X=7;
error_reporting(0);$v=constant("X");$e=error_get_last();echo $e["type"],"|",$e["message"],"|",$v,"|";

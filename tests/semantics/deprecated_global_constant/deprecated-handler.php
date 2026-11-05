<?php
#[Deprecated('old',since:'8.5')]
const X=7;
#[Deprecated("callback")]function h(){echo "H|",constant("X"),"|";return true;}set_error_handler("h");echo X,"|";

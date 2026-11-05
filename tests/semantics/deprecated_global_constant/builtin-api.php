<?php
set_error_handler(function($n,$m){echo $n,"|",$m,"|";return true;});echo constant("E_STRICT"),"|",defined("E_STRICT")?"yes|":"no|";

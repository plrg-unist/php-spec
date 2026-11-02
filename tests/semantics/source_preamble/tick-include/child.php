#!/usr/bin/env php
<?php declare(ticks=1); register_tick_function(function(){ echo "T|"; }); echo "C|"; return 5;

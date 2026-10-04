<?php
$value='V';$name='value';$a=['K'];
echo "${value}
${$name}
${a[0]}|";
echo "L
${value}
${$name}|";
echo "{$a[
0]}
${value}
${$name}|";
echo "${'value'}{$value}{${$name}}|END";

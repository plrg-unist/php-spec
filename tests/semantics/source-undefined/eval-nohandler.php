<?php
echo 'A:', eval($cvPlain), '|';
echo 'B:', @eval($cvSilenced), '|';
echo 'C:', eval($cvPlain), '|END';

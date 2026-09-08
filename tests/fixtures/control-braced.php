<?php
label: ;
if ($a) { echo 1, 2; } elseif ($b) { print 3; } else { $x = 4; }
while ($a) { if ($b) break 2; continue; }
do { --$a; } while ($a);
for ($i=0,$j=1; $i<10,$j<20; $i++,$j+=2) { continue 1; }
foreach ($xs as $k => &$v) { unset($v); }
switch ($a) { case 0: break; case 1; echo 1; default: goto label; }
try { throw new E; } catch (E|F $e) { echo $e; } catch (G) {} finally { echo 0; }
return;

<?php

print<<<EOT
<h1>
   $subject
</h1>
<p>
   $time by <a href="mailto:$email">$username</a>
</p>
<p>
   <em>$titletext</em>
</p>
<p>
   $maintext
</p>
EOT;

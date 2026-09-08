<?php

print<<<EOT
<h1 id="ni$news[id]">
   $subject
</h1>
<p>
   $time by <a href="mailto:$email">$username</a> in $category. $caticon
</p>
<p>
   <strong>$titletext</strong>
</p>
<p>
   $maintext | $comments | $sendtofriend | $views views
</p>
<hr />
<br />
EOT;

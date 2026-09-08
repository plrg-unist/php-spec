<?php

print<<<EOT
<h2>
   Add a Comment:
</h2>
<table>
   <tr>
      <td>
         <label for="name">Name:</label>
      </td>
      <td>
         <input id="name" name="name" type="text" />
      </td>
   </tr>
   <tr>
      <td>
         <label for="email">E-Mail:</label>
      </td>
      <td>
         <input id="email" name="email" type="text" />
         (optional)
      </td>
   </tr>
   <tr>
      <td>
         <label for="website">WebSite:</label>
      </td>
      <td>
         <input id="website" name="website" type="text"
         value="http://" /> (optional)
      </td>
   </tr>
   </table>
   <p>
      <textarea cols="32" rows="6" name="message"></textarea><br />
      <input type="submit" name="submit" value="Add Comment" />
      <input type="reset" name="reset" value="Reset" />
</p>
EOT;

<?php

print<<<EOT
<fieldset>
   <legend>Send to a friend</legend>
   <table style="width:100%;">
      <tr>
         <td>
            <label for="fromname">Your Name:</label>
         </td>
         <td>
            <input id="fromname" name="fromname" type="text" />
         </td>
      </tr>
      <tr>
         <td>
            <label for="fromemail">Your EMail:</label>
         </td>
         <td>
            <input id="fromemail" name="fromemail" type="text" />
         </td>
      </tr>
      <tr>
         <td>
            <label for="toemail">Your Friends EMail:</label>
         </td>
         <td>
            <input id="toemail" name="toemail" type="text" />
         </td>
      </tr>
      <tr valign="top">
         <td>
            <label for="message">Message:</label>
         </td>
         <td>
            <textarea id="message" name="message" type="text"
            rows="5" cols="32">Check out this news posting I found!</textarea>
         </td>
      </tr>
   </table>
   <p class="center" style="padding-bottom:5px;">
      <input type="submit" value="Send to Friend" name="Submit" />
      <input type="reset" name="reset" value="Reset" />
   </p>
</fieldset>
EOT;

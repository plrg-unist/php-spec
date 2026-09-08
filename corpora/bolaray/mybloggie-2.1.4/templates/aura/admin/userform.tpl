<center>
<form action="{USERACTIONFILENAME}" method="post" name="post" onsubmit="return checkForm(this)">
<table width="100%" class="tableborder" cellspacing="2" cellpadding="3"  border="0">
   <tr>
     <td colspan="2" class="tdhead"><center>{FORMHEADER}</center></td></tr>
   <tr>
   <tr>
     <td colspan="2" height="10"></td></tr>
   <tr>
      <td align="left" class="formfont"><b>{L_NAME}</b></td>
      <td align="left" class="formfont">
         <input type="text" name="user" size="45" maxlength="60" style="width:200px" tabindex="2" value="{USER}" />
      </td></tr>
   <!-- BEGIN pass -->
   <tr>
      <td align="left" class="formfont"><b>{pass.L_PASSWORD}</b></td>
      <td align="left" class="formfont">
         <input type="text" name="password" size="45" maxlength="60" style="width:200px" tabindex="2" value="{pass.PASSWORD}" />
      </td></tr>
   <tr>
      <td align="left" class="formfont"><b>{pass.L_REENTER_PASS}</b></td>
      <td align="left" class="formfont">
        <input type="text" name="repassword" size="45" maxlength="60" style="width:200px" tabindex="2" value="{pass.PASSWORD}" />
      </td></tr>
  <!-- END pass -->
   <tr>
      <td align="left" class="formfont"><b>{L_LEVEL}</b></td>
      <td align="left" class="formfont">
      <select name="level" tabindex="2">
          <option value="1">Administrator</option>
          <option value="2">Normal User</option>
      </select>
      </td></tr>
     <td colspan="2">
        <div align="center">
        <input type="submit" value="Submit" name="submit" />
     </div>
     </td>
   </tr>
</table>
</form></center>
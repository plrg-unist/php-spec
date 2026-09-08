<center>

<table width="100%" class="tableborder" cellspacing="2" cellpadding="3"  border="0">
  <tr>
     <td colspan="4" class="tdhead">{CAT_HEAD}</center></td></tr>
   <tr>
   <tr>
     <td align="left" class="formfont"><u>{L_CAT_ID}</u></td>
     <td align="left" class="formfont"><u>{L_CAT_NAME}</u></td>
     <td align="left" class="formfont"><u>{CAT_EDIT}</u></td>
     <td align="left" class="formfont"><u>{CAT_DEL}</u></td>
   </tr>
<!-- BEGIN parsecat -->
   <tr>
     <td{parsecat.ALT_CLR} align="left">{parsecat.CAT_ID}</td>
     <td{parsecat.ALT_CLR} align="left" >{parsecat.CAT_NAME}</td>
     <td{parsecat.ALT_CLR} align="left"><center>{parsecat.CAT_EDIT}</center></td>
     <td{parsecat.ALT_CLR} align="left"><center>{parsecat.CAT_DEL}</center></td>
   </tr>
<!-- END parsecat -->
</table>
<br />
<form action="{USERACTIONFILENAME}" method="post" name="post" onsubmit="return checkForm(this)">
<table width="100%" class="tableborder" cellspacing="2" cellpadding="3"  border="0">
   <tr>
     <td colspan="2" class="tdhead"><center>{FORMHEADER}</center></td></tr>
   <tr>
      <td align="left" class="formfont"><b>{L_CATEGORY}</b></td>
      <td align="left"><input type="text" name="cat_desc" size="45" maxlength="60" style="width:200px" tabindex="2" value="{CAT_DESC}" /></td>
   </tr>
   <tr>
     <td colspan="2">
        <div align="center">
        <input type="submit" value="Submit" name="submit" />
     </div>
     </td>
   </tr>
</table>

</form></center>
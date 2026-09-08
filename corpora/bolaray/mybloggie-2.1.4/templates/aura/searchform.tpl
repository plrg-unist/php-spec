<script language="JavaScript" type="text/javascript">
<!--
function checkForm() {
  formErrors = false;
  if (document.search.keyword.value.length < 2){
    formErrors = "You must enter a Keyword .";
  }
  if (formErrors) {
    alert(formErrors);
    return false;
  } else {
    //bbstyle(-1);
    //formObj.preview.disabled = true;
    //formObj.submit.disabled = true;
    return true;
  }
}
//-->
</script>
<table width="100%" border="0" cellpadding="1" cellspacing="2">
    <tr>
      <td class="header">{L_SEARCH}</td>
    </tr>
  <tr>
     <td>
    <form action="{SEARCH_ACTION_FILE}" method="post" name="search" onsubmit="return checkForm(this)"><center><input type="text" name="keyword" size="12"> <input type="submit" value="Go"></center></form>
    </td>
  </tr>
</table>

  <!-- BEGIN preview -->
  <center>
  <table width="98%" class="tableborder" cellspacing="2" cellpadding="0" border="0">
   <tr>
     <td class="tdhead"><center>{preview.L_PREVIEW}</center></td></tr>
  </table></center>
  <!-- END preview -->
  <table width="100%"  border="0" cellpadding="1" cellspacing="2">
    <!-- BEGIN search -->
    <tr><td colspan="3" class="spacer3"></td></tr>
    <tr><td colspan="3" bgcolor="#C0C0C0"><span class="subject">{search.KEYWORD}</span></td></tr>
    <!-- END search -->
    <!-- BEGIN blogparse -->
    <tr><td colspan="3" class="spacer3"></td></tr>
    <tr><td colspan="3" class="date">{blogparse.DATE} &nbsp;&nbsp;<span class="f10pxgrey">{blogparse.TIME}</span></td></tr>
    <tr><td colspan="3" class="subject">{blogparse.PERMALINK} {blogparse.SUBJECT}</td></tr>
    <tr><td colspan="3" class="horizontaldot"></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="message">{blogparse.MESSAGE}</td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td></td><td>{blogparse.ADMIN_MENU}</td><td align="right">
    <span class="f10pxgrey">{blogparse.L_CATEGORY} : {blogparse.U_CATEGORY}
    | {blogparse.L_POSTED_BY} : <b>{blogparse.USER_NAME}</b> | <img src="./templates/{STYLE}/images/comment.gif" alt="" /> <a class="std" href="{blogparse.U_COMMENT}">{blogparse.L_COMMENT}</a>{blogparse.COMMENT_NO} | <img src="./templates/{STYLE}/images/trackback.gif" /> <a class="std" href="{blogparse.U_TRACKBACK}">{blogparse.L_TRACKBACK}</a> {blogparse.TRACKBACK_NO} </span></td></tr>
    <tr><td colspan="3" class="spacer3"></td></tr>
    <!-- END blogparse -->
    <tr><td colspan="3" height="50">&nbsp;</td></tr>
    <tr><td colspan="3" class="spacer3" align="right"><span class="f10pxgrey">{PAGE}</span></td></tr>
  </table>
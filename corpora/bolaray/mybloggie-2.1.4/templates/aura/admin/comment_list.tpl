  <center>
  <table width="100%" class="tableborder" cellspacing="1" cellpadding="0"  border="0">
   <tr>
      <td class="tdhead">
       <center>{L_LIST}</center>
      </td>
   </tr>
   <tr>
     <td>

  <center>
  <table width="98%" border="0" cellpadding="0" cellspacing="1">
     <tr><td class="spacer3" colspan="7"></td></tr>
     <tr>
     <td><span class="stdfont"><b>{L_DATE}<b></span></td>
     <!--td><span class="stdfont"><b>{L_TIME}<b></span></td-->
     <td><span class="stdfont"><b>{L_SUBJECT}<b></span></td>
     <td><span class="stdfont"><b>{L_CATEGORY}<b></span></td>
     <td><span class="stdfont"><b>{L_POSTED_BY}<b></span></td>
     <td><span class="stdfont"><b>{L_COMMENTS}<b></span></td>
     <td><span class="stdfont"><b><b></td>
     <td><span class="stdfont"><b><b></td>
     </tr>

     <tr>
     <td{ALT_CLR}><span class="smallfont">{DATE}<br />{TIME}</span></td>
     <!--td{ALT_CLR}><span class="smallfont">{TIME}</span></td-->
     <td{ALT_CLR}><span class="smallfont">{SUBJECT}</span></td>
     <td{ALT_CLR}><span class="smallfont">{CATEGORY}</span></td>
     <td{ALT_CLR}><span class="smallfont">{USER_NAME}</span></td>
     <td{ALT_CLR} align="center" valign="middle"><span class="smallfont">{COMMENTS}</span></td>
     <td{ALT_CLR}><span class="smallfont">{U_EDIT}</span></td>
     <td{ALT_CLR}><span class="smallfont">{U_DELETE}</span></td>
     </tr>
    <tr><td class="spacer6" colspan="7"></td></tr>
    <tr><td colspan="7"><b><u>{L_COMMENTS}</u></b></td></tr>
    <tr><td class="spacer6" colspan="7"></td></tr>
    <!-- BEGIN listing -->
    <tr><td colspan="7" class="spacer3"></td></tr>
    <tr><td colspan="7" class="date">{listing.COM_DATE}</td></tr>
    <tr><td colspan="7" class="commentsubject"><u>{listing.COM_SUBJECT}</u></b>
      <!-- BEGIN admin -->
        <span class="f10pxgrey">&nbsp;&nbsp;&nbsp;&nbsp;Admin menu : {listing.admin.ADMIN}</span>
      <!-- END admin -->
      </td></tr>
    <tr><td colspan="7" align="left" class="ident10">
    <span class="f10pxgrey">
    {listing.L_BY} : <b>{listing.POSTER}</b> @ {listing.L_TIME} : {listing.COM_TIME} {listing.COM_EMAIL} {listing.COM_HOME}</span></td></tr>
    <tr><td colspan="7" class="spacer6"></td></tr>
    <tr><td colspan="7" class="spacer6"></td></tr>
    <tr><td colspan="7" class="message">{listing.COMMENTS}</td></tr>
    <tr><td colspan="7" class="spacer6"></td></tr>
    <tr><td colspan="7" class="spacer3"></td></tr>
    <!-- END listing -->
    <tr><td colspan="7" align="right"><span class="smallfont">{PAGE}</span></td></tr>
  </table></center>
    </td></tr>
  </table>
  </center>
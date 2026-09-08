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
  <table width="98%" border="0" cellpadding="2" cellspacing="1">
     <tr><td class="spacer3" colspan="7"></td></tr>
     <tr>
     <td height="18"><span class="stdfont">{L_DATE}</span></td>
     <td><span class="stdfont">{L_SUBJECT}</span></td>
     <td><span class="stdfont">{L_CATEGORY}</span></td>
     <td><span class="stdfont">{L_POSTED_BY}</span></td>
     <td><span class="stdfont">{L_COMMENTS}</span></td>
     <td><span class="stdfont">{L_EDIT}</span></td>
     <td><span class="stdfont">{L_DEL}</span></td>
     </tr>
    <!-- BEGIN listing -->
     <tr>
     <td{listing.ALT_CLR}>{listing.DATE}<br />{listing.TIME}</td>
     <td{listing.ALT_CLR}>{listing.SUBJECT}</td>
     <td{listing.ALT_CLR}>{listing.CATEGORY}</td>
     <td{listing.ALT_CLR}>{listing.POSTER_NAME}</td>
     <td{listing.ALT_CLR}>{listing.COMMENTS}</td>
     <td{listing.ALT_CLR}>{listing.U_EDIT}</td>
     <td{listing.ALT_CLR}>{listing.U_DELETE}</td>
     </tr>
    <!-- END listing -->
    <tr><td class="spacer6" colspan="7"></td></tr>
    <tr><td colspan="7" align="right"><span class="smallfont">{PAGE}</span></td></tr>
  </table></center>
    </td></tr>
  </table>
  </center>
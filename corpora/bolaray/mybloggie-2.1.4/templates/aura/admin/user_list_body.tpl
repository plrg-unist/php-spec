  <center>
  <table width="100%" class="tableborder" cellspacing="2" cellpadding="0"  border="0">
   <tr>
     <td class="tdhead"><center>{L_USER_LIST}</center></td></tr>
     <td align="center"><br />
  <table width="100%" border="0" cellpadding="1" cellspacing="2">
     <tr><td class="spacer3" colspan="5"></td></tr>
     <tr>
     <td width="10%"><b>{L_UID}</b></td>
     <td><b>{L_NAME}</b></td>
     <td width="15%"><b>{L_LEVEL}</b></td>
     <td width="10%"><b>{OTHERS2}</b></td>
     <td width="10%"><b>{OTHERS3}</b></td>
     </tr>
    <!-- BEGIN listing -->
     <tr>
     <td{listing.ALT_CLR}>{listing.UID}</td>
     <td{listing.ALT_CLR}>{listing.NAME}</td>
     <td{listing.ALT_CLR}>{listing.LEVEL}</td>
     <td{listing.ALT_CLR}>{listing.U_EDIT}</td>
     <td{listing.ALT_CLR}>{listing.U_DELETE}</td>
     </tr>
    <!-- END listing -->
  </table>
  </td></tr>
</table></center>
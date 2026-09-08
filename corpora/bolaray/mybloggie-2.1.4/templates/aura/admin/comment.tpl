   <table width="100%" border="0" cellpadding="1" cellspacing="2">
      <tr><td class="comment">
      <div>
      <h4>{L_COMMENT_HEADER}</h4>
      <form action="{COMMENT_ACTION}" method="post" name="post" onsubmit="return checkForm(this)">
      {L_SUBJECT}<br/>
      <input type="text" name="commentsubject" style="width:300px; font-size:13px" value="{COMMENTSUBJECT}"/><br/>
      {L_COMMENT} <br/>
<!--Modified for 2.1.2 ( BBcode for comment )-->
      <div>
          <input type="button" class="button" accesskey="b" name="addbbcode0" value=" B " style="font-weight:bold; width: 25px" onclick="bbstyle(0)"  />
          <input type="button" class="button" accesskey="i" name="addbbcode2" value=" i " style="font-style:italic; width: 25px" onclick="bbstyle(2)"  />
          <input type="button" class="button" accesskey="u" name="addbbcode4" value=" u " style="text-decoration: underline; width: 25px" onclick="bbstyle(4)"  />
          <input type="button" class="button" accesskey="q" name="addbbcode6" value="Quote" style="width: 40px" onclick="bbstyle(6)"  />
          <input type="button" class="button" accesskey="c" name="addbbcode8" value="Code" style="width: 40px" onclick="bbstyle(8)"  />
          <input type="button" class="button" accesskey="w" name="addbbcode16" value="URL" style="text-decoration: underline; width: 35px" onclick="bbstyle(16)" />
      </div>
<!--End -->
      <textarea name="commenttext" rows="10" cols="50"  style="width:300px; font-size:11px;" onselect="storeCaret(this);" onclick="storeCaret(this);" onkeyup="storeCaret(this);">{COMMENTTEXT}</textarea><br/>
      {L_NAME}<br/>
       <input type="text" name="commentname" value="{COMMENTNAME}" /><br/>
      {L_EMAIL_ADD} ({L_OPTIONAL})<br/>
      <input type="text" name="commentemail" value="{COMMENTEMAIL}"/><br/>
      {L_HOME_PAGE} ({L_OPTIONAL})<br/>
      <input type="text" name="commenthome" value="{COMMENTHOME}"/><br/>
<!--Validation Code-->
      <!-- BEGIN scodeswitch -->
      {scodeswitch.SECURITY_CODE}
      <br/>{scodeswitch.SHOW_IMAGE_CODE}<br/>
      {scodeswitch.SECURITY_PROMPT} :<br/>
      <input name="check_code" type="text" id="check_code" value="" size="10" maxlength="5"><br/><br/>
      <input name="hidden_code" type="hidden" id="hidden_code" value="{scodeswitch.SHOW_CODE}">
      <!-- END scodeswitch -->
<!--End Validation-->
      <input type="submit" value="Submit" name="submit" /><br/>
      <!-- BEGIN redirectswitch -->
      <input type="hidden" name="redirect" value="{redirectswitch.REDIRECT}"/>
      <!-- END redirectswitch -->
      <input type="hidden" name="post_id" value="{POST_ID}"/>
      <input type="hidden" name="comment_id" value="{COMMENT_ID}"/>
      </form>
      </div>
      </td>
      </tr>
  </table>
<!--script language="JavaScript" type="text/javascript"-->
<!--
// Check for Browser & Platform for PC & IE specific bits
// More details from: http://www.mozilla.org/docs/web-developer/sniffer/browser_type.html
var clientPC = navigator.userAgent.toLowerCase(); // Get client info
var clientVer = parseInt(navigator.appVersion); // Get browser version

var is_ie = ((clientPC.indexOf("msie") != -1) && (clientPC.indexOf("opera") == -1));
var is_nav = ((clientPC.indexOf('mozilla')!=-1) && (clientPC.indexOf('spoofer')==-1)
                && (clientPC.indexOf('compatible') == -1) && (clientPC.indexOf('opera')==-1)
                && (clientPC.indexOf('webtv')==-1) && (clientPC.indexOf('hotjava')==-1));
var is_moz = 0;

var is_win = ((clientPC.indexOf("win")!=-1) || (clientPC.indexOf("16bit") != -1));
var is_mac = (clientPC.indexOf("mac")!=-1);

function checkForm() {
  formErrors = false;
  if (document.post.commentname.value.length < 2){
    formErrors = "You must enter a Name when posting.";
  }
  if (document.post.commenttext.value.length < 2){
    formErrors = "You must enter a Comment when posting.";
  }
  if (document.post.commentsubject.value.length < 2){
    formErrors = "You must enter a Subject when posting.";
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
<!--/script-->
  <table width="100%" border="0" cellpadding="1" cellspacing="2">
    <tr><td colspan="3" class="spacer3" id="trackback"></td></tr>
    <tr><td colspan="3" class="date">{DATE} <span class="f10pxgrey">{TIME}</span></td></tr>
    <tr><td colspan="3" class="subject">{PERMALINK} {SUBJECT}</td></tr>
    <tr><td colspan="3" class="horizontaldot"></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="message">{MESSAGE}</td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td></td><td></td><td align="right">
    <span class="f10pxgrey">{L_CATEGORY} : <a class="std" href="{U_CATEGORY}">{CATEGORY}</a>
    | {L_POSTED_BY} : <b>{USER_NAME}</b> | <img src="./templates/{STYLE}/images/comment.gif" /> <a class="std" href="{U_COMMENT}">{L_COMMENT}</a> {COMMENT_NO} | <img src="./templates/{STYLE}/images/trackback.gif" /> <a class="std" href="{U_TRACKBACK}">{L_TRACKBACK}</a> {TRACKBACK_NO}</span></td></tr>
    <tr><td colspan="3" class="spacer6"><div>{TB_RDF}</div></td></tr>
    <tr><td colspan="3" class="horizontaldot3" width="90%"></td></tr>
  </table>
<!--Added Trackback--->
  <table width="100%" border="0" cellpadding="1" cellspacing="2">
    <tr><td colspan="3" class="header"><div id="trackback">{L_TRACKBACK}</div></td></tr>
    <tr><td width="5%"></td><td class="box"><span class="ftb">{L_TB_URL_DESC}</span><br /><center><span class="ftburl">{TRACKBACK_URL}</span></center></td><td width="5%"></td></tr>
    <!-- BEGIN trackback -->
    <tr><td colspan="3" class="spacer3"></td></tr>
    <tr><td colspan="3" class="date">{trackback.COM_DATE}</td></tr>
    <tr><td colspan="3" class="commentsubject"><u>{trackback.COM_SUBJECT}</u></b>
      <!-- BEGIN admin -->
        <span class="f10pxgrey">&nbsp;&nbsp;&nbsp;&nbsp;Admin menu : {trackback.admin.ADMIN}</span>
      <!-- END admin -->
      </td></tr>
    <tr><td colspan="3" align="left" class="ident10">
    <span class="f10pxgrey">
    {trackback.L_BY} : <b>{trackback.POSTER}</b> @ {trackback.L_TIME} : {trackback.COM_TIME} {trackback.COM_EMAIL} {trackback.COM_HOME}</span></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="message">{trackback.COMMENTS}</td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="spacer3"></td></tr>
    <!-- END trackback -->
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="horizontaldot3" width="90%"></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
   </table>
<!--End Added Trackback--->

  <table width="100%" border="0" cellpadding="1" cellspacing="2">
    <tr><td colspan="3" class="header"><div id="comment">{L_COMMENT}</div></td></tr>
    <!-- BEGIN comment -->
    <tr><td colspan="3" class="spacer3"></td></tr>
    <tr><td colspan="3" class="date">{comment.COM_DATE}</td></tr>
    <tr><td colspan="3" class="commentsubject"><u>{comment.COM_SUBJECT}</u>
      <!-- BEGIN admin -->
        <span class="f10pxgrey">&nbsp;&nbsp;&nbsp;&nbsp;Admin menu : {comment.admin.ADMIN}</span>
      <!-- END admin -->
      </td></tr>
    <tr><td colspan="3" align="left" class="ident10">
    <span class="f10pxgrey">
    {comment.L_BY} : <b>{comment.POSTER}</b> @ {comment.L_TIME} : {comment.COM_TIME} {comment.COM_EMAIL} {comment.COM_HOME}</span></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="message">{comment.COMMENTS}</td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="spacer3"></td></tr>
    <!-- END comment -->

    <tr><td colspan="3" class="spacer6"></td></tr>
    <tr><td colspan="3" class="horizontaldot3" width="90%"></td></tr>
    <tr><td colspan="3" class="spacer6"></td></tr>
   </table>
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
      <input type="hidden" name="post_id" value="{POST_ID}"/>
      <input type="hidden" name="comment_id" value="{COMMENT_ID}"/>
      </form>
      </div>
      </td>
      </tr>
  </table>
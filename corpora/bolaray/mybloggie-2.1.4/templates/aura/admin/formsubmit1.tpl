<center>
<form action="{ACTIONFILENAME}" method="post" name="post" onsubmit="return checkForm(this)">
<table width="100%" class="tableborder" cellspacing="2" cellpadding="3"  border="0">

  <tr>
    <td align="center">
      <table width="98%" border="0" cellpadding="3" cellspacing="1">
        <tr>
           <td>{FORMHEADER}</td></tr>
        <tr>
          <td height="10"><b></b></td></tr>
        <tr>
          <td align="left"><b>{L_NAME} : <u>{USER_NAME}</u></b> </td>
        </tr>
        <tr>
          <td><b></b></td>
        </tr>
        <tr>
          <td align="left"><b>Subject</b></td>
        </tr>
        <tr>
          <td>
             <input type="text" name="subject" size="48" maxlength="60" style="width:98%; height : 18px;"  tabindex="2" value="{SUBJECT}" />
          </td>
        </tr>
        <tr>
          <td align="left"><b>{L_CATEGORY}</b> <select name="category" tabindex="2">
            <!-- BEGIN option -->
            <option value="{option.DB_CAT_ID}">{option.DB_CATEGORY}</option>
            <!-- END option -->
            <!-- BEGIN optionselected -->
            <option value="{optionselected.DB_CAT_ID}" selected>{optionselected.DB_CATEGORY}</option>
            <!-- END optionselected -->
             </select>
          </td>
        </tr>
        <tr>
          <td valign="top" align="center">
                <div>
                  <input type="button" class="button" accesskey="b" name="addbbcode0" value=" B " style="font-weight:bold; width: 25px" onclick="bbstyle(0)" onmouseover="helpline('b')" />

                  <input type="button" class="button" accesskey="i" name="addbbcode2" value=" i " style="font-style:italic; width: 25px" onclick="bbstyle(2)" onmouseover="helpline('i')" />
                   <input type="button" class="button" accesskey="u" name="addbbcode4" value=" u " style="text-decoration: underline; width: 25px" onclick="bbstyle(4)" onmouseover="helpline('u')" />

                   <input type="button" class="button" accesskey="q" name="addbbcode6" value="Quote" style="width: 40px" onclick="bbstyle(6)" onmouseover="helpline('q')" />
                   <input type="button" class="button" accesskey="c" name="addbbcode8" value="Code" style="width: 40px" onclick="bbstyle(8)" onmouseover="helpline('c')" />
                   <input type='button' accesskey='oa' value='ol=a' onclick='tag_lista()' name="List=a" onmouseover="helpline('oa')" />
                   <input type='button' accesskey='o1' value='ol=1' onclick='tag_list1()' name="List=1" onmouseover="helpline('oa')" />
                   <input type='button' accesskey='l' value='li' onclick='tag_list()' name="List" onmouseover="helpline('l')" />

                   <input type="button" class="button" accesskey="p" name="addbbcode14" value="Img" style="width: 40px"  onclick="bbstyle(14)" onmouseover="helpline('p')" />
                   <input type="button" class="button" accesskey="pr" name="addbbcode22" value="Imgr" style="width: 40px"  onclick="bbstyle(22)" onmouseover="helpline('pr')" />
                   <input type="button" class="button" accesskey="pl" name="addbbcode24" value="Imgl" style="width: 40px"  onclick="bbstyle(24)" onmouseover="helpline('pl')" />
                   <!--input type="button" class="button" accesskey="th" name="addbbcode26" value="tmb" style="width: 40px"  onclick="bbstyle(26)" onmouseover="helpline('th')" /-->
                   <input type="button" class="button" accesskey="w" name="addbbcode16" value="URL" style="text-decoration: underline; width: 35px" onclick="bbstyle(16)" onmouseover="helpline('w')" />
               </div>
               <div>
                   <input type="text" name="helpbox" size="45" maxlength="100" style="width:96%; font-size:10px" value="Tip: Apply style to the selected text" />
               </div>
           </td>
        </tr>
        <tr>
          <td valign="top" align="center">
               <div>
                 <a href="javascript:emoticon(':D')"><img src="images/smilies/icon_biggrin.gif" border="0" alt="Very Happy" title="Very Happy" /></a>
                 <a href="javascript:emoticon(':)')"><img src="images/smilies/icon_smile.gif" border="0" alt="Smile" title="Smile" /></a>
                 <a href="javascript:emoticon(':(')"><img src="images/smilies/icon_sad.gif" border="0" alt="Sad" title="Sad" /></a>
                 <a href="javascript:emoticon(':o')"><img src="images/smilies/icon_surprised.gif" border="0" alt="Surprised" title="Surprised" /></a>
                 <a href="javascript:emoticon(':shock:')"><img src="images/smilies/icon_eek.gif" border="0" alt="Shocked" title="Shocked" /></a>
                 <a href="javascript:emoticon(':?')"><img src="images/smilies/icon_confused.gif" border="0" alt="Confused" title="Confused" /></a>
                 <a href="javascript:emoticon('8)')"><img src="images/smilies/icon_cool.gif" border="0" alt="Cool" title="Cool" /></a>
                 <a href="javascript:emoticon(':lol:')"><img src="images/smilies/icon_lol.gif" border="0" alt="Laughing" title="Laughing" /></a>
                 <a href="javascript:emoticon(':x')"><img src="images/smilies/icon_mad.gif" border="0" alt="Mad" title="Mad" /></a>
                 <a href="javascript:emoticon(':P')"><img src="images/smilies/icon_razz.gif" border="0" alt="Razz" title="Razz" /></a>
                 <a href="javascript:emoticon(':redface:')"><img src="images/smilies/icon_redface.gif" border="0" alt="Embarassed" title="Embarassed" /></a>
                 <a href="javascript:emoticon(':cry:')"><img src="images/smilies/icon_cry.gif" border="0" alt="Crying or Very sad" title="Crying or Very sad" /></a>
                 <a href="javascript:emoticon(':evil:')"><img src="images/smilies/icon_evil.gif" border="0" alt="Evil or Very Mad" title="Evil or Very Mad" /></a>
                 <a href="javascript:emoticon(':twisted:')"><img src="images/smilies/icon_twisted.gif" border="0" alt="Twisted Evil" title="Twisted Evil" /></a>
                 <a href="javascript:emoticon(':roll:')"><img src="images/smilies/icon_rolleyes.gif" border="0" alt="Rolling Eyes" title="Rolling Eyes" /></a>
                 <a href="javascript:emoticon(':wink:')"><img src="images/smilies/icon_wink.gif" border="0" alt="Wink" title="Wink" /></a>
                 <a href="javascript:emoticon(':!:')"><img src="images/smilies/icon_exclaim.gif" border="0" alt="Exclamation" title="Exclamation" /></a>
                 <a href="javascript:emoticon(':?:')"><img src="images/smilies/icon_question.gif" border="0" alt="Question" title="Question" /></a>
                 <a href="javascript:emoticon(':idea:')"><img src="images/smilies/icon_idea.gif" border="0" alt="Idea" title="Idea" /></a>
                 <a href="javascript:emoticon(':arrow:')"><img src="images/smilies/icon_arrow.gif" border="0" alt="Arrow" title="Arrow" /></a>
               </div>

          </td>
        </tr>
        <tr>
          <td align="left"><b>{L_MESSAGE}</b><br />
          <div><textarea name="message" rows="16" cols="70"  style="width:98%;" tabindex="3" onselect="storeCaret(this);" onclick="storeCaret(this);" onkeyup="storeCaret(this);">{MESSAGE}</textarea>
          </div>
          </td>
        </tr>
        <tr>
          <td align="left">{L_DATE_POST}<br />
             <div>
             {L_EDIT_TIMESTAMP} <input name="edit_date" value="1" tabindex="13" type="checkbox" {CHECKED} />&nbsp;
             <input name="dd" value="{POST_DATE}" size="2" maxlength="2" tabindex="4" type="text" />

             <select name="mm" tabindex="15">
                 <!-- BEGIN monthoption -->
                  {monthoption.MTH_OPTION}
                 <!-- END monthoption -->
             </select>

             <input name="yy"  value="{POST_YEAR}" size="4" maxlength="5" tabindex="5" type="text" />
             <input name="hh"  value="{POST_HOUR}" size="2" maxlength="2" tabindex="6" type="text" />:
             <input name="min" value="{POST_MIN}" size="2" maxlength="2" tabindex="7" type="text" />:
             <input name="sec" value="{POST_SEC}" size="2" maxlength="2" tabindex="8" type="text" />
             </div>
          </td>
        </tr>
        <!-- BEGIN showtrackback -->
        <tr>
            <td align="left">{showtrackback.L_TRACKBACK_URLS}</b><br />
             <input type="text" name="trackback_url" style="width:98%; height:18px;" tabindex="9" value="{showtrackback.TRACKBACK_URL}" />
            </td>
        </tr>
        <!-- END showtrackback -->
        <tr>
          <td>
             <div align="center">
              <input type="submit" value="Preview" name="preview" />
              <input type="submit" value="Submit" name="submit" />
            </div>
          </td>
        </tr>
       </table>
     </td>
   </tr>
</table>
</form></center>
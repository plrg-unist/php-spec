<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html dir="{CONTENT_DIRECTION}" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-EU" lang="en-EU">
<head>
<meta http-equiv="Content-Type" content="text/html; charset={CHAR_SET}" />
<meta http-equiv="Content-Style-Type" content="text/css" />
<title>myBloggie - by myWebland {ADMIN_TITLE}</title>
<link rel="stylesheet" title="{STYLE}" href="templates/{STYLE}/{STYLE}.css" type="text/css" />
<style type="text/css">
.menubar {
background: url(templates/{STYLE}/images/dawnlight_04.gif) center ;
background-repeat:no-repeat;
height : 21px;
}
.leftshadow {
      background : url(templates/{STYLE}/images/lshadow.gif);

}
.rightshadow {
      background : url(templates/{STYLE}/images/rshadow.gif);
}
.topshadow {
      background : url(templates/{STYLE}/images/tshadow.gif);
}
.btmshadow {
      background : url(templates/{STYLE}/images/bshadow.gif);
}
.topleftshadow {
      background : url(templates/{STYLE}/images/tlshadow.gif);
}
.toprightshadow {
      background : url(templates/{STYLE}/images/trshadow.gif);
}
.btmrightshadow {
      background : url(templates/{STYLE}/images/brshadow.gif);
}
.btmleftshadow {
      background : url(templates/{STYLE}/images/blshadow.gif);
}
.header1 {
      background : url(templates/{STYLE}/images/header_01.gif);
}
.header2 {
      background : url(templates/{STYLE}/images/header_02.gif);
}
.blogbackground {
      background : url(templates/{STYLE}/images/bg.jpg);
      background-repeat:no-repeat;
}
.errorbackground {
      background : url(templates/{STYLE}/images/error.gif);
      background-repeat:no-repeat;
      background-position: center center ;
}
.oops_msg {
    font-family: Verdana, Arial, Helvetica, sans-serif;
    font-size: 12px;
    margin-bottom: 50px;
    margin-top: 50px;
    text-align : left;
}

</style>

</head>
<body bgcolor="#ffffff" background="templates/{STYLE}/images/diagonal.gif">
<center>

<table border="0" cellpadding="0" cellspacing="0">
  <tr>
   <td class="topleftshadow" height="12"></td>
   <td class="topshadow" height="12"></td>
   <td class="toprightshadow" height="12"></td>
  </tr>
  <tr>
   <td class="leftshadow" width="12"></td>
   <td width="740" bgcolor="#ffffff" class="blogcontent">

  <table width="740" cellpadding="0" cellspacing="0" border="0" class="border">
     <tr>
        <td class="header1" width="270" height="80" align="center">
        <font style='font-family : ITC Garamond, georgia, arial; font-size : 24px; color : #ffffff; font-weight : bold;'>{BLOG_NAME}</font></td>
        <td class="header2" width="470" height="80" valign="bottom" align="right">
               {OWNER}&nbsp;&nbsp;&nbsp;</td>
     </tr>
     <tr>
        <td class="menubar" width="270">
               <span class="f10pxwhite">&nbsp;{TIME}</span></td>
        <td class="menubar" width="470" align="right">
               <span class="f10pxwhite"> | <a class="menu" href="./index.php">Home
               </a> | <a class="menu" href="http://www.mywebland.com">myWebland
               </a>&nbsp;
               </span></td>
     </tr>
     <tr>
        <td colspan="2" valign="middle"  align="center">
        <br /><br />
           <table width="80%" class="tableborder" cellspacing="1" cellpadding="2"  border="0">
              <tr>
                 <td class="header"><center>Error Page</center></td></tr>
              <tr>
                 <td valign="middle" align="center">
                 <table width=70% class="errorbackground" cellspacing="0" cellpadding="0"  border="0">
                    <tr>
                      <td class="oops_msg">
                        {ERROR_MSG}
                        <br />
                     </td></tr>
                 </table>
                 </td></tr>
              <tr>
                 <td class="f10pxblack " align="center"><a class="std" href="index.php">myBloggie Home</a>  | <a class="std" href="javascript:history.back()">Back</a><br /><br /></td></tr>
          </table>
        <br /><br />
        </td>
      </tr>
      <tr>
        <td colspan="2" valign="middle"  align="center">
        <div id="credit"><span class="f10pxblack">
          <!--
          We request you to retain the full copyright notice & link below. Thank you.
          // -->
          Template theme : {STYLE}<br />
          Powered by <a class="copyright" href="http://mybloggie.mywebland.com">myBloggie </a> Copyright &copy; 2004 2005<br/>
          -- <a class="copyright" href="http://www.mywebland.com">myWebland</a> --
          <br/>
          </span></div><br/>
        </td>
      </tr>
  </table>

   <td class="rightshadow" width="12"></td>
</tr>
<tr>
  <td class="btmleftshadow" height="12"></td>
  <td class="btmshadow" height="12"></td>
  <td class="btmrightshadow" height="12"></td>
</tr>
</table>
</body>
</html>
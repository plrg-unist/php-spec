<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html dir="{CONTENT_DIRECTION}" xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-EU" lang="en-EU">
<head>
<meta http-equiv="Content-Type" content="text/html; charset={CHAR_SET}" />
<meta http-equiv="Content-Style-Type" content="text/css" />
{META}
<title>{VERSION} - by myWebland {ADMIN_TITLE}</title>
<link rel="stylesheet" title="{STYLE}" href="templates/{STYLE}/{STYLE}.css" type="text/css" />
<style type="text/css">
.menubar {
background: url(templates/{STYLE}/admin/images/titlebar.gif) center ;
background-repeat: repeat-x;
height : 24px;
}
.grayborder {
      border : medium #a0a0a0;
      border-style : solid; 
      border-top-width : 1px; 
      border-right-width : 1px; 
      border-bottom-width : 1px; 
      border-left-width : 1px; 
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
.banner2 {
      background : url(templates/{STYLE}/admin/images/banner2.gif);
      background-repeat:repeat-x;
}
.header_shade {
      background : url(templates/{STYLE}/admin/images/header_shade.gif);
}
.banner1 {
      background : url(templates/{STYLE}/admin/images/banner1.gif);
}
.blogbackground {
      background : url(templates/{STYLE}/images/bg.jpg);
      background-repeat:no-repeat;
}
.hshade {
      background : url(templates/{STYLE}/admin/images/hshade.gif);
      background-repeat: repeat-x;
}

/********************/

ul.menu_tab {
    margin:0;
    clear: both;
    padding: 0.1ex 0.5em 0;
    list-style: none;
    border-bottom: 0px solid #ffffff;
}
ul.menu_tab li {
    float:left;
    background:url("templates/{STYLE}/admin/images/tab_left.gif") no-repeat left top;
    margin:0;
    padding: 0px 0px 0 10px;
    border-bottom: 0px solid #ffffff;

}
ul.menu_tab li a {
    float:left;
    display:block;
    white-space:nowrap;
    background: url("templates/{STYLE}/admin/images/tab_right.gif") no-repeat right top;
/*    padding:4px 11px 3px 2px;  */
    padding: 0px 8px 0px 8px;
    text-decoration:none;
    color:#fefefe;
    font-size: 10px;
    font-family : verdana;
    line-height : 22px;
    font-weight: bold;
}
ul.menu_tab li.current {
    background-position:0% -44px;
    border-width:0;
}
ul.menu_tab li.current a {
    background-position:100% -44px;
    color:#505050;
    padding-bottom: 0px;
}
ul.menu_tab li.current a:hover {
    text-decoration: normal;
    color:#505050;
}

/* Commented Backslash Hack: hides rule from IE5-Mac \*/
ul.menu_tab li a {float:none;}
/* End IE5-Mac hack */

ul.menu_tab li a:hover {
    color:#000000;
    text-decoration: underline;        /* for IE */
    }

ul.menu_tab li:hover {            /* Won't work in IE */
    background-position:0% -22px;
    color:#505050;
}
ul.menu_tab li:hover a {            /* Won't work in IE */
    background-position: 100% -22px;
    color:#505050;
    /* text-decoration: none; */
}

li, dd {
  margin-bottom: 6px;
}

p, li, dl, dd, dt {
  line-height: 130%;
}

#adminmenu2 .current{
  font-weight: bold;
}

#adminmenu2 li {
  display: inline;
  line-height: 200%;
  list-style: none;
  text-align: center;
}

#adminmenu2 {
  background: #bdbdbd;
  border-bottom: none;
  margin: 0;
  padding: 3px 2em 0;
}

#adminmenu2 .current {
  background: url(templates/{STYLE}/admin/images/bg_body.gif);
  border-top: 0px solid #a0a0a0;
  border-right: 2px solid #a0a0a0;
  color: #000;
}

#adminmenu2 a {
  border: none;
  color: #fefefe;
  font-size: 10px;
  padding: 0.3em .4em .9em;
}

#adminmenu2 a:hover {
  background: #f0f0f0;
  color: #393939;
}

#adminmenu2 li {
  line-height: 170%;
}

/****************************/

.tdhead { font-family: Verdana, Arial, Helvetica, sans-serif;
                  font-weight: bold;
                  font-size: 12px;
                  text-align: center;
                  letter-spacing: 0.09em;
                  height: 24px;
                  color: #f0f0f0;
                  background-image: url("templates/{STYLE}/admin/images/admintitlebar.gif");
}
.greybg {
    background : url(templates/{STYLE}/admin/images/titlebar.jpg);
    /**background: #eaeaea;**/
    /**border: 1px solid #a0a0a0;**/
    /**color: #171717; **/

}
.whitebg {
    background: #ffffff;
    /**border: 1px solid #a0a0a0;**/
    /**color: #171717; **/
}
.admin {
     font-family :  Verdana, Arial, Helvetica, sans-serif;
     font-size : 14px;
     color : #909090;
}
.smallfont {
     font-family : Verdana, Arial, Helvetica, sans-serif;
     font-size : 10px;
     color : #303030;
     padding-right : 3px;
     padding-left : 3px;
}
.stdfont {
     font-family : Verdana, Arial, Helvetica, sans-serif;
     font-size : 11px;
     color : #303030;
     padding-right : 3px;
     padding-left : 3px;
}
.blogcontent  {
    padding-top : 3px;
    padding-right : 3px;
    padding-bottom : 3px;
    padding-left : 3px;
}
#header {
    border-right: #fff 0px solid; padding-right: 0px; border-top: #fff 0px solid; padding-left: 0px;  background: url(templates/{STYLE}/admin/images/bg_top.gif)  /**left bottom **/; padding-bottom: 0px; margin: 0px auto; border-left: #fff 0px solid; padding-top: 0px; border-bottom: #fff 0px solid; height: 60px
}
#adminbanner {
    border-right: #fff 0px solid; padding-right: 0px; border-top: #fff 0px solid; padding-left: 0px;  background: url(templates/{STYLE}/admin/images/bg_top.gif); padding-bottom: 0px; margin: 0px auto; border-left: #fff 0px solid; width :180px;  padding-top: 0px; border-bottom: #fff 0px solid; height: 60px
}
#bg_tab{
    border-right: #fff 0px solid; padding-right: 0px; border-top: #fff 0px solid; padding-left: 0px; background: url(templates/{STYLE}/admin/images/bg_top.gif) ; padding-bottom: 0px; margin: 0px auto; border-left: #fff 0px solid;  padding-top: 0px; border-bottom: #fff 0px solid; height: 24px
}

#bg_body{
    border-right: #fff 0px solid; padding-right: 0px; border-top: #fff 0px solid; padding-left: 0px; background: url(templates/{STYLE}/admin/images/bg_body.gif) ; padding-bottom: 0px; margin: 0px auto; border-left: #fff 0px solid;  padding-top: 0px; border-bottom: #fff 0px solid; height: 24px
}

fieldset {
  border: 1px solid #bdbdbd;
  background : #ffffff;
  -moz-border-radius: 5px;
  padding: 6px;
  font-family : verdana;
  font-size : 12px;
}
a.block, a.block:hover, a.lblock {
  border-bottom: none;
  display: block;
  padding: 5px 5px 5px 0px;
  line-height : 100%;
  text-align : center;
}

a.block:hover, a.lblock:hover {
  padding: 5px 5px 5px 0px;
  background: #ccc;
  line-height : 100%;
}

a.lblock {
  text-align : left;
  }

td {
  font-family : verdana;
  font-size : 11px;
}

a { text-decoration: none;}
a:hover { text-decoration : underline; }

input,select {
  font-size: 11px;
  font-family: Verdana;
  border-style: solid;
  border-width: 1px;
  border-color: #aaaaaa;
  background: #f0f0f0;
  border-width: 1px ;
  margin: 2px;
}
textarea
{
  font-size: 12px;
  font-family: Georgia;
  border-style: solid;
  border-width: 1px;
  border-color: #aaaaaa;
  background: #f0f0f0;
  border-width: 1px ;
  margin: 2px;
}

</style>

<script type="text/javascript">
//<![CDATA[

function customToggleLink() {
  // TODO: Only show link if there's a hidden row
  document.write('<small>(<a href="javascript:;" id="customtoggle" onclick="toggleHidden()">Show hidden</a>)</small>');
  // TODO: Rotate link to say "show" or "hide"
  // TODO: Use DOM
}

function toggleHidden() {
  var allElements = document.getElementsByTagName('tr');
  for (i = 0; i < allElements.length; i++) {
    if ( allElements[i].className.indexOf('hidden') != -1 ) {
       allElements[i].className = allElements[i].className.replace('hidden', '');
    }
  }
}


//]]>
</script>

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
   <td bgcolor="#ffffff" class="blogcontent">
  <center>
  <table width="760" cellpadding="0" cellspacing="0" border="0" class="grayborder">
    <tr>
     <td id="adminbanner" width="280" height="60" valign="middle" align="center"><img src="templates/{STYLE}/admin/images/logo.gif" /></td>
     <td id="header" width="480" height="60"><img src="templates/{STYLE}/admin/images/admin.gif" /></td>
     </tr>
   <tr>
     <td colspan="2" valign="bottom" id="bg_tab">
       <ul class="menu_tab">
         <li>{MENU_HOME}</li>
         <li{CURRENT_ADD}>{MENU_ADD}</li>
         <li{CURRENT_EDIT}>{MENU_EDIT}</li>
         <li{CURRENT_CAT}>{MENU_CAT}</li>
         <li{CURRENT_USER}>{MENU_USER}</li>
         <li{CURRENT_TOOLS}>{MENU_TOOLS}</li>
         <!-- BEGIN logoff -->
           <li>{logoff.L_LOGOFF}</b></li>
         <!-- END logoff -->
       </ul>
     </td>
   </tr>
   <tr>
     <td colspan="2" align="left" height="32" bgcolor="#bdbdbd">
       <!-- BEGIN editsubmenu --><br />
       <ul id="adminmenu2">
         <li>{editsubmenu.SUBMENU_1}</li>
         <li>{editsubmenu.SUBMENU_2}</li>
       </ul>
       <!-- END editsubmenu -->
       <!-- BEGIN usersubmenu -->
       <ul id="adminmenu2">
         <li>{usersubmenu.SUBMENU_1}</li>
         <li>{usersubmenu.SUBMENU_2}</li>
         <li>{usersubmenu.SUBMENU_3}</li>
       </ul>
       <!-- END usersubmenu -->
       <!-- BEGIN toolssubmenu -->
       <ul id="adminmenu2">
         <li>{toolssubmenu.SUBMENU_1}</li>
       </ul>
       <!-- END toolssubmenu -->

     </td>
   </tr>

   <!--tr>
     <td class="hshade" height="7" colspan="2"></td>
   </tr-->
   <tr>
     <td colspan="2"  id="bg_body"><center>
     <!--Admin body starts here-->
       <table width="95%" border="0" cellpadding="2" cellspacing="1">
         <tr>
            <td valign="top">
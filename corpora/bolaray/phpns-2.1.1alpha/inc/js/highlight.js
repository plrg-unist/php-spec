/**************************************************************************
 *                                                                        *
 *  JAVASCRIPT MENU HIGHLIGHTER v.1.0 (051123)                            *
 * --------------------------------------------                           *
 * ©2005 Media Division (www.MediaDivision.com)                           *
 *                                                                        *
 * Written by Marius Smarandoiu & Armand Niculescu                        *
 *                                                                        *
 * You are free to use, modify and distribute this file, but please keep  *
 * this header and credits                                                *
 *                                                                        *
 * Usage:                                                                 *
 * - the script will apply the .current class to the <a> and its parent   *
 *   <li> that is contained in the element with id="primarynav" and points*
 *   to the current URL                                                   *
 * - works in IE6, Firefox and Opera                                      *
 **************************************************************************/
function extractPageName(hrefString)
{
	var arr = hrefString.split('.');
	arr = arr[arr.length-2].split('/');
	return arr[arr.length-1].toLowerCase();		
}

function setActiveMenu(arr, crtPage)
{
	for(var i=0; i < arr.length; i++)
		if(extractPageName(arr[i].href) == crtPage)
		{
			arr[i].className = "current";
			arr[i].parentNode.className = "current";
		}
}

function setPage()
{
	if(document.location.href) 
		hrefString = document.location.href;
	else
		hrefString = document.location;

	if (document.getElementById("tabs")!=null) 
		setActiveMenu(document.getElementById("tabs").getElementsByTagName("a"), extractPageName(hrefString));
}

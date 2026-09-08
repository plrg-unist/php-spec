

<?php
#########################################################################
# File:    rss.php
# License: GNU GPL
#
# ----------------------------------------------------------------------
# based on RSSify 0.1 by Steven Jarvis, 2002.  Used by permission.
# ----------------------------------------------------------------------
#
# JBE - updated 03/29/05
#
# wheat - updated 07/03/06
#
# Purpose: Creates an up-to-date RSS file for Wheatblog.
#
# This script is used to generate an RSS 2.0-compliant file using XML.
# It reads in a list of the most recent posts* and outputs them into
# file readable by RSS news aggregators.  It gives them title, description,
# RFC2822** Date and a permanent link to the full article.
# This file is only an include, and should not be called from a URL.
# File defined in settings.php needs to be writeable.
#
#
#  * This file will use the $front_page_max variable found in settings.php
#    as a count.
# ** See http://www.faqs.org/rfcs/rfc2822.html form more information.
#
#
# Called by:
#
# edit_post
# delete_post
# add_post
#
#########################################################################

    // Grab the date
    $todaysdate = date('r');

// Set the looped variable to null, for safety's sake
//
$rssfeedMIDDLE = "";


// Connect to the DB and select the database
//
$db = DB_connect($site, $user, $pass);
DB_select_db($database, $db);

// select recent posts in the database
// Use the number of posts commonly displayed on the index page as a count
//
$result = DB_query("select * from wbtbl_posts where showpref = '1'  
        order by year DESC, month DESC, date DESC, id DESC 
        limit $front_page_max", $db);

$num_results = DB_num_rows($result);


for($i=0; $i < $num_results; $i++) {


    while ($row = DB_fetch_array($result)) {

        $the_id       = $row['id'];
        $the_showpref = $row['showpref'];
        $raw_title    = $row['title'];
        $raw_body     = $row['body'];
        $timestamp    = $row['timestamp'];

        // Show something more diginfied than a blank title, ffs.
        //
        if (empty($raw_title)) {

            $raw_title = "Untitled";

        }

        // Remove undesirable tags to ensure valid XML CDATA strings
        //
        $the_title = strip_tags($raw_title);
        //$raw_lead  = strip_tags($raw_body);
        $raw_lead = htmlentities($raw_body);
        // truncates $the_lead to an appropriate length
        //
        //$the_lead  = substr($raw_lead, 0, 70) . " . . .";
        $the_lead = $raw_lead;

        // Loop through, creating individual _items_ within file
        //
        $rssfeedMIDDLE .= '<item>'."\n" .
            '<title>'.$the_title.'</title>'."\n".
            '<description>'.$the_lead.'</description>'."\n".
            '<link>'.$wb_url.'/view_by_permalink.php?the_id='.$the_id.'</link>'."\n".
               '<pubDate>'.$timestamp.'</pubDate>'."\n".
            '</item>'."\n";

    }

}


// Obtain the time the file was last updated.
// Avoid error if creating RSS file for the first time.
//
if  (file_exists($wb_dir.'/'.$wb_rss)) {

    $lastBuildDate = date("r", filemtime($wb_dir.'/'.$wb_rss));

} else {

    $lastBuildDate = $todaysdate;
}

// Generate the top of the RSS feed.
//
$rssfeedTOP =
'<?xml version="1.0" encoding="UTF-8"?>'."\n".
// If you would like to include an XSL Transform,
// uncomment this line and establish a correct path to the stylesheet
// <?xml-stylesheet type="text/xsl" href="path_to_stylesheet.xsl"
'<rss version="2.0">'."\n".
'<channel>'."\n".
'<title>RSS feed for '.$name_of_blog.'</title>'."\n".
'<link>'.$wb_url.'</link>'."\n".
'<description>'.$description_of_blog.'</description>'."\n".
'<language>'.$wb_rss_lang.'</language>'."\n".
'<lastBuildDate>'.$lastBuildDate.'</lastBuildDate>'."\n";



// This closes Channel and RSS document elements
//
$rssfeedBOTTOM = '</channel>'."\n".'</rss>'."\n";

// concatenate the info
//
$rssfeedTOTAL = $rssfeedTOP .  $rssfeedMIDDLE . $rssfeedBOTTOM;

// use me for testing
// echo $rssfeedTOTAL;

// Name the file to write
//
$handle = $wb_dir.'/'.$wb_rss;

// Make sure the file can be opened.
//
if(!($fp = fopen($handle, "w"))) {
    die('<div class="subcontent" id="rss">'."\n".
         '<span>Sorry, I could not open '.$handle.'.</span>
				 '."\n".'</div>');
}


// Upon successful write, echo confirmation to user
//
if(fwrite($fp, $rssfeedTOTAL)) {

    echo '<div class="subcontent" id="rss">'."\n";
    echo '<span>RSS updated successfully!  Would you like to </span>'."\n";
    echo '<a href="'.$wb_url.'/'.$wb_rss.'" target="_blank">View it?</a>'."\n";
    echo '</div>'."\n"; // Closes div.access#rss

} else {

    // Tell the user if the write fails.
    echo '<div class="subcontent" id="rss">'."\n";
    echo '<span>Sorry, I Could not write the RSS file.  Check '.$wb_rss.'\'s  permissions.</span>'."\n";
    echo '</div>'."\n"; // Closes div.access#rss
}

// Close the RSS file.
//
fclose($fp);


?>	
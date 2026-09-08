<?php

//---------------------------------------------------------------
//This program is free software; you can redistribute it and/or
//modify it under the terms of the GNU General Public License
//as published by the Free Software Foundation; either version 2
//of the License, or (at your option) any later version.
//
//This program is distributed in the hope that it will be useful,
//but WITHOUT ANY WARRANTY; without even the implied warranty of
//MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//GNU General Public License for more details.
//
//Meezerk's CAPTCHA - A Computer Assisted Program for Telling
//                    Computers and Humans Apart
//Copyright (C) 2004  Daniel Foster  dan_software@meezerk.com
//---------------------------------------------------------------

//Select size of image
$size_x = "144";
$size_y = "25";

//generate random string
$code = mt_rand("100000", "999999");

//store captcha code in session vars
session_start();
$_SESSION['captcha_code'] = $code;

//create image to play with
$image = imageCreate($size_x, $size_y);


//add content to image
//------------------------------------------------------


//make background white - first colour allocated is background
$background = imageColorAllocate($image, 255, 255, 255);



//select grey content number
$text_number1 = mt_rand("0", "150");
$text_number2 = mt_rand("0", "150");
$text_number3 = mt_rand("0", "150");

//allocate colours
$white = imageColorAllocate($image, 255, 255, 255);
$black = imageColorAllocate($image, 0, 0, 0);
$text  = imageColorAllocate($image, $text_number1, $text_number2, $text_number3);



//get number of dots to draw
$total_dots = ($size_x * $size_y)/15;

//draw many many dots that are the same colour as the text
for($counter = 0; $counter < $total_dots; $counter++) {
    //get positions for dot
    $pos_x = mt_rand("0", $size_x);
    $pos_y = mt_rand("0", $size_y);

    //draw dot
    imageSetPixel($image, $pos_x, $pos_y, $text);
};



//draw border
imageRectangle($image, 0, 0, $size_x-1, $size_y-1, $black);



//get coordinates of position for string
//on the font 5 size, each char is 15 pixels high by 9 pixels wide
//with 6 digits at a width of 9, the code is 54 pixels wide
$pos_x = bcmod($code, $size_x-60) +3;
$pos_y = bcmod($code, $size_y-15);

//draw random number
imageString($image, 5, $pos_x, $pos_y, $code, $text);


//------------------------------------------------------
//end add content to image


//send browser headers
header("Content-Type: image/jpeg");


//send image to browser
echo imageJPEG($image);


//destroy image
imageDestroy($image);

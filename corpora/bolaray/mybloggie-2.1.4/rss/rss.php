<?php
define('IN_MYBLOGGIE', true);
$mybloggie_root_path = trim('../');
include_once($mybloggie_root_path.'config.php');
include_once($mybloggie_root_path.'includes/db.php');
include_once($mybloggie_root_path.'includes/function.php');

if  (isset($_SERVER['PHP_SELF']) && isset($_SERVER['HTTP_HOST'])) {
    $me = $_SERVER['PHP_SELF'];
    $path_pieces = explode("/", $me);
    $trim1= array_pop($path_pieces);
    $trim2 = array_pop($path_pieces);
    $pathweb = implode("/", $path_pieces);
    $mybloggie_url = "http://".$_SERVER['HTTP_HOST'].$pathweb;
} elseif (isset($_SERVER['PHP_SELF']) && isset($_SERVER['SERVER_NAME'])) {
    $me = $_SERVER['PHP_SELF'];
    $path_pieces = explode("/", $me);
    $trim1= array_pop($path_pieces);
    $trim2 = array_pop($path_pieces);
    $pathweb = implode("/", $path_pieces);
    $mybloggie_url = 'http://'.$_SERVER['SERVER_NAME'].$pathweb;
}
$sql = "SELECT ".POST_TBL.".post_id, ".POST_TBL.".subject,  ".POST_TBL.".timestamp FROM ".POST_TBL."
  Order by  ".POST_TBL.".timestamp DESC
  LIMIT 0, 5 ";

if(!($result = $db->sql_query($sql))) {
    $sql_error = $db->sql_error();
    echo $sql_error['message'];
}

$result = $db->sql_query($sql) ;

//include_once($mybloggie_root_path.'language/'.$language);
header("Content-type: application/xml");
echo "<?xml version=\"1.0\"?".">";



?>
<!-- generator="mybloggie/<?php echo $mb_version ?>" -->
<rss version="0.92">
  <channel>
     <title><?php echo $myblogname    ?></title>
    <link><?php   if (isset($_SERVER['HTTP_HOST'])) {
        echo "http://".$_SERVER['HTTP_HOST'];
    } elseif (isset($_SERVER['SERVER_NAME'])) {
        echo "http://".$_SERVER['SERVER_NAME'];
    }
?></link>
    <description><?php echo $blog_desc ?></description>
    <docs>http://backend.userland.com/rss092</docs>
    <?php //while( $Item = $MainList->get_item() ) {
   while ($row = $db->sql_fetchrow($result)) {
       ?>
    <item>
      <title><?php echo $row['subject']  ?></title>
      <link><?php echo $mybloggie_url."/index.php?mode=viewid&amp;post_id=".$row['post_id'] ?></link>
    </item>
    <?php } ?>
  </channel>
</rss>


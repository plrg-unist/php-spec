<?php
/*
Template: Table List

*/

//pid


global $data, $wpdb;
$file_list = $data;

$pid = $file_list['pid'];
#echo'<pre>';
##print_r($file_list);
#echo '</pre>';

do_action('spcdm/community/file_list/above');
do_action('spdm_file_responsive_top', $pid);
do_action('spdm_file_list_column_before_sort');
?>
<table id="cdm_data_table" class="display">
<thead><tr>
	<th>Image</th>	
		<th>File Name</th>	
	<th>Modified Date</th>	
	</tr>
</thead>
	<tbody>


        
			
			<?php
#Start output the back button
if ($pid != 0) { ?>
            <tr >
            <?php #do_action('spdm_file_list_column_before_folder_back');?>
           		
				<td><a href="javascript:sp_cdm_load_project(<?php echo intval($file_list['current_folder']['parent']); ?>)"><img src="<?php echo esc_attr($file_list['back_image']); ?>" width="42"> &laquo; <?php echo __("Go Back", "sp-client-document-manager"); ?></a>
				</td>
				<td></td>
				<td></td>
            </tr>
            <?php
} #END output the back button
?>
        
        	
            
            <?php
#Start output the projects
$r_projects = $file_list['projects'];
# print_r($r_projects);
if (count($r_projects) > 0) {
    for ($i = 0;$i < count($r_projects);$i++) {

        if (($r_projects[$i]['project_name'] != "") or get_option('sp_cu_release_the_kraken') == 1 or cdm_folder_permissions($r_projects[$i]['pid']) == 1) {

            if (cdm_contains_viewable($r_projects[$i]['pid']) == 1 or get_option('sp_cu_release_the_kraken') == 1) {
                if (cdm_folder_permissions($r_projects[$i]['pid']) == 1 or get_option('sp_cu_release_the_kraken') == 1) {
                    ?>	
						<tr>
                            <td>
                            <?php do_action('spdm_file_list_column_before_folder', $r_projects[$i]['pid']); ?>
                            <a href="javascript:sp_cdm_load_project(<?php echo $r_projects[$i]['pid']; ?>)"><img src="<?php echo $file_list['folder_image']; ?>" width="42"></a>
                            </td>
                            
                            <td>
                            <strong><?php echo esc_attr(stripslashes($r_projects[$i]['project_name'])); ?></strong>
                            </td>
                            <td></td>
						</tr>
                        <?php
                }
            }
        }
    }
} #END output the projects

?>
             
			  <?php
#Start output the files
$r = $file_list['files'];
for ($i = 0;$i < count($r);$i++) { #start file loop


    $ext = preg_replace('/^.*\./', '', $r[$i]['file']);
    $r_cat = $wpdb->get_results("SELECT name  FROM " . $wpdb->prefix . "sp_cu_cats   where id = '" . $r[$i]['cid'] . "' ", ARRAY_A);
    if (@$r_cat[0]['name'] == '') {
        $cat = stripslashes(@$r_cat[0]['name']);
    } else {
        $cat = '';
    }
    if (cdm_var('search', $file_list) != "" && sp_cdm_get_project_name(@$r[$i]['pid']) != false) {
        $project_name = ' <em>(' . sp_cdm_folder_name() . ': ' . sp_cdm_get_project_name(@$r[$i]['pid']) . ')</em> ';
    } else {
        $project_name = '';
    }

    if (get_option('sp_cu_file_direct_access') == 1) {
        $file_link = 'window.open(\'' . esc_attr(cdm_download_file_link(base64_encode($r[$i]['id'] . '|' . $r[$i]['date'] . '|' . $r[$i]['file']), get_option('sp_cu_js_redirect'))) . '\'); void(0)';
        ;
    } else {
        $file_link = 'cdmViewFile(' . intval($r[$i]['id']) . ')';
    }

    if ((@in_array($r[$i]['pid'], $file_list['current_user_projects']) && cdm_folder_permissions($r[$i]['pid']) == 1) or $r[$i]['pid'] == 0 or get_option('sp_cu_release_the_kraken') == 1) {

        echo '<tr ><td>';

        if (sp_cdm_is_featured_disabled('premium', 'file_image') == false) {


            do_action('spdm_file_list_column_before_file', $r[$i]['id']);
            $file_link = apply_filters('spcdm/file_list/link', $file_link, $r[$i]);
            echo ' <a href="javascript:' . esc_attr($file_link) . '">';
            do_action('sp_cdm/community/file_list/image', $r[$i], 100);
            echo '</a> 
			';
        } else {
            echo '<div >';
            do_action('spdm_file_list_column_before_file', $r[$i]['id']);
            echo '</div>';
        }
        echo '</td>';
        echo '<td ><a href="javascript:' . $file_link . '">			
			';

        do_action('spcdm/files/responsive/before', $r[$i]['id']);
        if (sp_cdm_is_featured_disabled('premium', 'file_list_name') == false) {
            echo cdm_community_limit_filename(apply_filters('spcdm/community/files/responsive/file_name', '<strong>' . esc_attr(stripslashes($r[$i]['name'])) . ' ' . $project_name . '', $r));
        }
        echo '</a></td><td>';
        if (sp_cdm_is_featured_disabled('premium', 'file_meta_info') == false) {
            echo '</strong>';
            if (sp_cdm_is_featured_disabled('premium', 'file_list_date') == false) {
                echo apply_filters('spcdm/files/responsive/file_date', '<span class="sp-cdm-rc-file-date">' . esc_attr(cdm_datetime($r[$i]['date'])) . '</span> ', $r);
            }

        }


        echo '</td></tr>
		';
    }

} #end file loop

?>
   

</tbody>
	</table>


<script type="text/javascript">

jQuery(document).ready( function ($) {
    $('#cdm_data_table').DataTable();
} );

</script>


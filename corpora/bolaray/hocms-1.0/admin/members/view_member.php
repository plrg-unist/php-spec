<?php
if(isset($_GET['id']) && $_GET['id'] > 0) {
    $qry = $conn->query("SELECT m.*,p.name as `phase`,CONCAT(m.firstname, ' ', COALESCE(m.middlename,''), m.lastname) as fullname from `member_list` m inner join phase_list p on m.phase_id = p.id where m.id = '{$_GET['id']}' and m.delete_flag = 0 ");
    if($qry->num_rows > 0) {
        foreach($qry->fetch_assoc() as $k => $v) {
            $$k=$v;
        }
    } else {
        echo "<script> alert('Unkown Member ID.'); location.replace('./?page=members') </script>";
        exit;
    }
}
?>
<style>
    .collection_text p{
        margin: unset !important;
    }
</style>
<div class="content py-3">
    <div class="card card-outline card-primary rounded-0 shadow">
        <div class="card-header">
            <h5 class="card-title">Member Detais</h5>
            <div class="card-tools">
                <button class="btn btn-flat btn-sm btn-primary" id="edit_data"><i class="fa fa-edit"></i> Edit</button>
                <button class="btn btn-flat btn-sm btn-danger" id="delete_data"><i class="fa fa-trash"></i> Delete</button>
                <a class="btn btn-flat btn-sm btn-light border" href="./?page=members"><i class="fa fa-angle-left"></i> Back</a>
            </div>
        </div>
        <div class="card-body">
            <div class="containder-fluid">
                <div class="row">
                    <div class="col-lg-4 col-md-5 col-sm-12">
                        <div class="callout callout-info rounded-0 shadow">
                            <dl>
                                <dt class="text-muted">Fullname</dt>
                                <dd class="pl-3"><b><?= isset($fullname) ? ucwords($fullname) : 'N/A' ?></b></dd>
                                <dt class="text-muted">Gender</dt>
                                <dd class="pl-3"><b><?= isset($gender) ? $gender : 'N/A' ?></b></dd>
                                <dt class="text-muted">Contact #</dt>
                                <dd class="pl-3"><small><?= isset($contact) ? $contact : 'N/A' ?></small></dd>
                                <dt class="text-muted">Phase</dt>
                                <dd class="pl-3"><b><?= isset($phase) ? format_num($phase) : 'N/A' ?></b></dd>
                                <dt class="text-muted">Block</dt>
                                <dd class="pl-3"><b><?= isset($block) ? format_num($block) : 'N/A' ?></b></dd>
                                <dt class="text-muted">Lot</dt>
                                <dd class="pl-3"><b><?= isset($lot) ? format_num($lot) : 'N/A' ?></b></dd>
                                <dt class="text-muted">Status</dt>
                                <dd class="pl-3">
                                    <?php if($status == 1): ?>
                                        <span class="badge badge-success bg-gradient-success rounded-pill px-3">Active</span>
                                    <?php else: ?>
                                        <span class="badge badge-danger bg-gradient-danger rounded-pill px-3">Inactive</span>
                                    <?php endif; ?>
                                </dd>
                            </dl>
                        </div>
                    </div>
                    <div class="col-lg-8 col-md-7 col-sm-12">
                        <div class="d-flex mb-2 align-items-end">
                            <div class="col-auto flex-shrink-1 flex-grow-1"><h4>Collection(s)</h4></div>
                            <div class="col-auto">
                                <button class="btn btn-flat btn-sm btn-default bg-navy" id="new_collection"><i class="fa fa-plus"></i> Add Collection</button>
                            </div>
                        </div>
                        <hr>
                        <div class="list-group" id="collection-list">
                            <?php
                            if(isset($id)):
                                $collection = $conn->query("SELECT * FROM `collection_list` where member_id = '{$_GET['id']}' order by date(date_collected) desc");
                                while($row = $collection->fetch_assoc()):
                                    ?>
                            <div class="list-group-item collection-item">
                                <div class="d-flex align-items-top">
                                    <div class="col-auto flex-shrink-1 flex-grow-1">
                                        <div class="collection_text text-muted"><?= date("D F d, Y", strtotime($row['date_collected'])) ?></div>
                                    </div>
                                    <div class="col-auto">
                                        <div class="dropleft">
                                            <a class="text-reset text-decoration-one" type="button" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                                <i class="fa fa-ellipsis-v"></i>
                                            </a>
                                            <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                                                <a class="dropdown-item view_collection" href="javascript:void(0)" data-id="<?= isset($row['id']) ? $row['id'] : '' ?>">View</a>
                                                <a class="dropdown-item edit_collection" href="javascript:void(0)" data-id="<?= isset($row['id']) ? $row['id'] : '' ?>">Edit</a>
                                                <a class="dropdown-item delete_collection" href="javascript:void(0)" data-id="<?= isset($row['id']) ? $row['id'] : '' ?>">Delete</a>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="d-flex align-items-top">
                                    <div class="col-auto flex-shrink-1 flex-grow-1">
                                        <div class="collection_text h4"><?= ($row['code']) ?></div>
                                    </div>
                                    <div class="col-auto">
                                        <div class="text-right font-weight-bolder h4"><?= format_num($row['total_amount']) ?></div>
                                    </div>
                                </div>
                            </div>
                            <?php endwhile; ?>
                            <?php endif; ?>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<script>
    $(function(){
        $('#edit_data').click(function(){
			uni_modal('Update Member Details - <b><?= isset($code) ? $code : "" ?></b>',"members/manage_member.php?id=<?= isset($id) ? $id : '' ?>",'mid-large')
		})
		$('#delete_data').click(function(){
			_conf("Are you sure to delete <b><?= isset($code) ? $code : "" ?></b> Member permanently?","delete_member",['<?= isset($id) ? $id : '' ?>'])
		})
        $('#new_collection').click(function(){
			uni_modal('New Collection',"collections/manage_collection.php?mid=<?= isset($id) ? $id : '' ?>",'large')
        })
        $('.view_collection').click(function(){
			uni_modal('View Collection',"collections/view_collection.php?mid=<?= isset($id) ? $id : '' ?>&id="+$(this).attr('data-id'),'mid-large')
        })
        $('.edit_collection').click(function(){
			uni_modal('Edit Collection',"collections/manage_collection.php?mid=<?= isset($id) ? $id : '' ?>&id="+$(this).attr('data-id'),'large')
        })
        $('.delete_collection').click(function(){
			_conf("Are you sure to delete this Collection permanently?","delete_collection",[$(this).attr('data-id')])
		})
    })
    function delete_member($id){
		start_loader();
		$.ajax({
			url:_base_url_+"classes/Master.php?f=delete_member",
			method:"POST",
			data:{id: $id},
			dataType:"json",
			error:err=>{
				console.log(err)
				alert_toast("An error occured.",'error');
				end_loader();
			},
			success:function(resp){
				if(typeof resp== 'object' && resp.status == 'success'){
					location.href = './?page=members';
				}else{
					alert_toast("An error occured.",'error');
					end_loader();
				}
			}
		})
	}
    function delete_collection($id){
		start_loader();
		$.ajax({
			url:_base_url_+"classes/Master.php?f=delete_collection",
			method:"POST",
			data:{id: $id},
			dataType:"json",
			error:err=>{
				console.log(err)
				alert_toast("An error occured.",'error');
				end_loader();
			},
			success:function(resp){
				if(typeof resp== 'object' && resp.status == 'success'){
					location.reload();
				}else{
					alert_toast("An error occured.",'error');
					end_loader();
				}
			}
		})
	}
</script>
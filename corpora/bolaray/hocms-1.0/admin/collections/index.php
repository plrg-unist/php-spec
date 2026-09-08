<?php if($_settings->chk_flashdata('success')): ?>
<script>
	alert_toast("<?php echo $_settings->flashdata('success') ?>",'success')
</script>
<?php endif;?>
<div class="card card-outline card-primary">
	<div class="card-header">
		<h3 class="card-title">List of Collections</h3>
		<div class="card-tools">
			<a href="javascript:void(0)" id="create_new" class="btn btn-flat btn-primary"><span class="fas fa-plus"></span>  Add New</a>
		</div>
	</div>
	<div class="card-body">
		<div class="container-fluid">
        <div class="container-fluid">
			<table class="table table-bordered table-stripped">
				<colgroup>
					<col width="5%">
					<col width="15%">
					<col width="15%">
					<col width="30%">
					<col width="20%">
					<col width="15%">
				</colgroup>
				<thead>
					<tr class="bg-gradient-secondary">
						<th>#</th>
						<th>Date Created</th>
						<th>Date Collected</th>
						<th>Member</th>
						<th>Amount</th>
						<th>Action</th>
					</tr>
				</thead>
				<tbody>
					<?php
                    $i = 1;
$phases = $conn->query("SELECT * FROM `phase_list` where id in (SELECT phase_id FROM `member_list` where id in (SELECT member_id FROM collection_list))");
$phase_arr = array_column($phases->fetch_all(MYSQLI_ASSOC), 'name', 'id');
$qry = $conn->query("SELECT c.*,CONCAT(m.firstname, ' ', COALESCE(m.middlename,''), ' ', m.lastname) as fullname, m.phase_id,m.block,m.lot from `collection_list` c inner join member_list m on c.member_id = m.id order by date(c.date_collected) desc,(CONCAT(m.firstname, ' ', COALESCE(m.middlename,''), ' ', m.lastname)) asc ");
while($row = $qry->fetch_assoc()):
    ?>
						<tr>
							<td class="text-center"><?php echo $i++; ?></td>
							<td><?php echo date("Y-m-d H:i", strtotime($row['date_created'])) ?></td>
							<td><?php echo date("D F d, Y", strtotime($row['date_collected'])) ?></td>
							<td>
								<div><?php echo ucwords($row['fullname']) ?></div>
								<small class="text-muted"><?= ucwords((isset($phase_arr[$row['phase_id']]) ? $phase_arr[$row['phase_id']] : "N/A").' Block '.$row['block'].' Lot '.$row['lot']) ?></small>
							</td>
							<td class="text-right"><?php echo format_num($row['total_amount']) ?></td>
							<td align="center">
								 <button type="button" class="btn btn-flat btn-default btn-sm dropdown-toggle dropdown-icon" data-toggle="dropdown">
				                  		Action
				                    <span class="sr-only">Toggle Dropdown</span>
				                  </button>
				                  <div class="dropdown-menu" role="menu">
								  	<a class="dropdown-item view_data" href="javascript:void(0)" data-id="<?= $row['id'] ?>"><span class="fa fa-eye text-dark"></span> View</a>
				                    <div class="dropdown-divider"></div>
				                    <a class="dropdown-item edit_data" href="javascript:void(0)" data-id="<?php echo $row['id'] ?>"><span class="fa fa-edit text-primary"></span> Edit</a>
				                    <div class="dropdown-divider"></div>
				                    <a class="dropdown-item delete_data" href="javascript:void(0)" data-id="<?php echo $row['id'] ?>"><span class="fa fa-trash text-danger"></span> Delete</a>
				                  </div>
							</td>
						</tr>
					<?php endwhile; ?>
				</tbody>
			</table>
		</div>
		</div>
	</div>
</div>
<script>
	$(document).ready(function(){
		$('#create_new').click(function(){
			uni_modal('Add New Collection',"collections/manage_collection.php","large")
		})
		$('.view_data').click(function(){
			uni_modal('View Collection Details',"collections/view_collection.php?id="+$(this).attr('data-id'),"mid-large")
		})
		$('.edit_data').click(function(){
			uni_modal('Update Collection Details',"collections/manage_collection.php?id="+$(this).attr('data-id'),"large")
		})
		$('.delete_data').click(function(){
			_conf("Are you sure to delete this Collection permanently?","delete_collection",[$(this).attr('data-id')])
		})
		$('table th, table td').addClass('align-middle px-2 py-1')
		$('.table').dataTable();
	})
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
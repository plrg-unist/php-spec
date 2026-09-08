<?php
require_once('./../../config.php');
if(isset($_GET['id']) && $_GET['id'] > 0) {
    $qry = $conn->query("SELECT c.*,CONCAT(m.lastname,', ', m.firstname,' ',COALESCE(m.middlename,'')) as fullname from `collection_list` c inner join member_list m on c.member_id = m.id where c.id = '{$_GET['id']}' ");
    if($qry->num_rows > 0) {
        foreach($qry->fetch_assoc() as $k => $v) {
            $$k=$v;
        }
    } else {
        ?>
		<center>Unknown collection</center>
		<style>
			#uni_modal .modal-footer{
				display:none
			}
		</style>
		<div class="text-right">
			<button class="btn btndefault bg-gradient-dark btn-flat" data-dismiss="modal"><i class="fa fa-times"></i> Close</button>
		</div>
		<?php
                exit;
    }
}
?>
<style>
	#uni_modal .modal-footer{
		display:none
	}
</style>
<div class="container-fluid">
	<div class="row">
		<div class="col-md-6">
			<dl>
				<dt class="text-muted">Ref. Code</dt>
				<dd class="pl-3"><?= isset($code) ? $code : "" ?></dd>
				<dt class="text-muted">Date Collected</dt>
				<dd class="pl-3"><?= isset($date_collected) ? date("D F d, Y", strtotime($date_collected)) : "" ?></dd>
				<dt class="text-muted">Collected By</dt>
				<dd class="pl-3"><?= isset($collected_by) ? ($collected_by) : "" ?></dd>
				<dt class="text-muted">Member</dt>
				<dd class="pl-3"><?= isset($fullname) ? ($fullname) : "" ?></dd>
			</dl>
		</div>
		<div class="col-md-6">
			<table class="table table-stripped table-bordered">
				<thead>
					<tr>
						<th class="text-center">Category</th>
						<th class="text-center">Fee</th>
					</tr>
				</thead>
				<tbody>
					<?php
                    $collection = $conn->query("SELECT i.*,c.name as `category` FROM `collection_items` i inner join category_list c on i.category_id = c.id where i.collection_id = '{$_GET['id']}' ");
while($row = $collection->fetch_assoc()):
    ?>
					<tr>
						<td class="px-2 py-1 align-middle"><?= $row['category'] ?></td>
						<td class="px-2 py-1 align-middle text-right"><?= format_num($row['fee']) ?></td>
					</tr>
					<?php endwhile; ?>
				</tbody>
				<tfoot>
					<tr>
						<th class="px-1 py-1 text-center">Total</th>
						<th class="px-1 py-1 text-right"><?= format_num($total_amount) ?></th>
					</tr>
				</tfoot>
			</table>
		</div>
	</div>
	<div class="clear-fix mb-3"></div>
	<div class="text-right">
		<button class="btn btn-default bg-gradient-dark btn-sm btn-flat" type="button" data-dismiss="modal"><i class="fa f-times"></i> Close</button>
	</div>
</div>

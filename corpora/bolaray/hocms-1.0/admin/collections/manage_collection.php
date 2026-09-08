<?php
require_once('./../../config.php');
if(isset($_GET['id']) && $_GET['id'] > 0) {
    $qry = $conn->query("SELECT * from `collection_list` where id = '{$_GET['id']}'");
    if($qry->num_rows > 0) {
        foreach($qry->fetch_assoc() as $k => $v) {
            $$k=$v;
        }
    } else {
        ?>
		<center>Unknown Collection ID</center>
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

<div class="container-fluid">
	<form action="" id="collection-form">
		<input type="hidden" name ="id" value="<?php echo isset($id) ? $id : '' ?>">
        <div class="row">
            <div class="col-md-6">
                <div class="form-group">
                    <label for="date_collected" class="control-label">Date Collected</label>
                    <input name="date_collected" id="date_collected" type="date"class="form-control form-control-sm rounded-0" value="<?php echo isset($date_collected) ? $date_collected : ''; ?>" required>
                </div>
                <div class="form-group">
                    <label for="collected_by" class="control-label">Collected By</label>
                    <input name="collected_by" id="collected_by" type="text"class="form-control form-control-sm rounded-0" value="<?php echo isset($collected_by) ? $collected_by : ''; ?>" required>
                </div>
                <?php if(isset($_GET['mid'])): ?>
                    <input type="hidden" name="member_id" value="<?= $_GET['mid'] ?>">
                <?php else: ?>
                <div class="form-group">
                    <label for="member_id" class="control-label">Member</label>
                    <select name="member_id" id="member_id" class="form-control form-control-sm rounded-0 select2" required>
                        <option value="" disabled <?= !isset($member_id) ? "selected" : "" ?>></option>
                        <?php
                        $member = $conn->query("SELECT *,CONCAT(firstname, ' ',COALESCE(middlename,''), ' ' ,lastname) as fullname FROM `member_list` where delete_flag = 0 and `status` = 1 ".(!isset($memeber_id) ? "" : " or memeber_id = '{$member_id}' ")." order by CONCAT(firstname, ' ',COALESCE(middlename,''), ' ' ,lastname) asc ");
                    while($row = $member->fetch_assoc()):
                        ?>
                        <option value="<?= $row['id'] ?>" <?= isset($member_id) && $member_id == $row['id'] ? "selected" : "" ?>><?= $row['fullname'] ?></option>
                        <?php endwhile; ?>
                    </select>
                </div>
                <?php endif; ?>
            </div>
            <div class="col-md-6">
                <table class="table table-stripped table-bordered">
                    <thead>
                        <tr>
                            <th class="text-center">
                                <div class="custom-control custom-checkbox">
                                    <input class="custom-control-input custom-control-input-primary custom-control-input-outline" type="checkbox" id="checkall">
                                    <label for="checkall" class="custom-control-label">All</label>
                                </div>
                            </th>
                            <th class="text-center">Category</th>
                            <th class="text-center">Fee</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php
                        $collection_item = [];
if(isset($id)) {
    $collection_qry = $conn->query("SELECT * FROM `collection_items` where collection_id = '{$_GET['id']}' ");
    while($row = $collection_qry->fetch_assoc()) {
        $collection_item[$row['category_id']] = $row;
    }
}
$category = $conn->query("SELECT * FROM `category_list` where delete_flag = 0 and `status` = 1 ".(isset($id) ? " or id in (SELECT category_id FROM `collection_items` where collection_id = '{$id}') " : "")." order by `name` asc ");
while($row = $category->fetch_assoc()):
    ?>
                        <tr>
                            <td class="px-2 py-1 align-middle text-center">
                                <input type="hidden" class="fee" name="fee[<?= $row['id'] ?>]" value="<?= (isset($collection_item[$row['id']])) ? ($collection_item[$row['id']]['fee']) : ($row['fee']) ?>">
                                <div class="custom-control custom-checkbox">
                                    <input name ="category_id[<?= $row['id'] ?>]" class="custom-control-input custom-control-input-primary custom-control-input-outline check-item" type="checkbox" id="cat_<?= $row['id'] ?>" value="<?= $row['id'] ?>" <?= (isset($collection_item[$row['id']])) ? 'checked' : '' ?>>
                                    <label for="cat_<?= $row['id'] ?>" class="custom-control-label"></label>
                                </div>
                            </td>
                            <td class="px-2 py-1 align-middle"><?= $row['name'] ?></td>
                            <td class="px-2 py-1 align-middle"><?= (isset($collection_item[$row['id']])) ? format_num($collection_item[$row['id']]['fee']) : format_num($row['fee']) ?></td>
                        </tr>
                        <?php endwhile; ?>
                    </tbody>
                </table>
                <div class="form-group">
                    <label for="total_amount" class="control-label">Total Collection</label>
                    <input name="total_amount" id="total_amount" type="text"class="form-control form-control-sm rounded-0" value="<?php echo isset($total_amount) ? $total_amount : 0; ?>" readonly tabindex="-1">
                </div>
            </div>
        </div>
	</form>
</div>
<script>
    function _checkAll(){
        var total = $('.check-item').length
        var checked = $('.check-item:checked').length
        if(total == checked){
            $('#checkall').prop('checked',true)
        }else{
            $('#checkall').prop('checked',false)
        }
    }
    function calc_total(){
        var total= 0;
        $('.check-item:checked').each(function(){
            var tr = $(this).closest('tr')
            var fee = tr.find('input.fee').val()
            total += parseFloat(fee)
        })
        $('#total_amount').val(total)
    }
	$(document).ready(function(){
		$('#uni_modal').on('shown.modal.bs',function(){
			$('.select2').select2({
				placeholder:'Please Select Here',
				width:'100%',
				dropdownParent:$('#uni_modal')
			})
		})
        _checkAll()
        calc_total();
        $('.check-item').change(function(){
            _checkAll();
            calc_total();
        })
        $('#checkall').change(function(){
            if($(this).is(':checked') == true){
                $('.check-item').prop('checked',true).trigger('change')
            }else{
                $('.check-item').prop('checked',false).trigger('change')
            }
            _checkAll();
            calc_total();
        })
		$('#uni_modal #collection-form').submit(function(e){
			e.preventDefault();
            var _this = $(this)
			 $('.err-msg').remove();
			var el = $('<div>')
				el.addClass("alert err-msg")
				el.hide()
            if(_this[0].checkValidity() == false){
                _this[0].reportValidity();
                return false;
			 }
            if( $('.check-item:checked').length <=0){
                alert_toast("Please Select at least 1 category first.",'error');
                return false;
            }
			start_loader();
			$.ajax({
				url:_base_url_+"classes/Master.php?f=save_collection",
				data: new FormData($(this)[0]),
                cache: false,
                contentType: false,
                processData: false,
                method: 'POST',
                type: 'POST',
                dataType: 'json',
				error:err=>{
					console.error(err)
					el.addClass('alert-danger').text("An error occured");
					_this.prepend(el)
					el.show('.modal')
					end_loader();
				},
				success:function(resp){
					if(typeof resp =='object' && resp.status == 'success'){
						location.reload();
					}else if(resp.status == 'failed' && !!resp.msg){
                        el.addClass('alert-danger').text(resp.msg);
						_this.prepend(el)
						el.show('.modal')
                    }else{
						el.text("An error occured");
                        console.error(resp)
					}
					$("html, body").scrollTop(0);
					end_loader()

				}
			})
		})

        $('.summernote').summernote({
		        height: 200,
		        toolbar: [
		            [ 'style', [ 'style' ] ],
		            [ 'font', [ 'bold', 'italic', 'underline', 'strikethrough', 'superscript', 'subscript', 'clear'] ],
		            [ 'fontname', [ 'fontname' ] ],
		            [ 'fontsize', [ 'fontsize' ] ],
		            [ 'color', [ 'color' ] ],
		            [ 'para', [ 'ol', 'ul', 'paragraph', 'height' ] ],
		            [ 'table', [ 'table' ] ],
		            [ 'view', [ 'undo', 'redo', 'fullscreen', 'codeview', 'help' ] ]
		        ]
		    })
	})
</script>
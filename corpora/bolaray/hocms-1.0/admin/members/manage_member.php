<?php
require_once('./../../config.php');
if(isset($_GET['id']) && $_GET['id'] > 0) {
    $qry = $conn->query("SELECT * from `member_list` where id = '{$_GET['id']}' and delete_flag = 0 ");
    if($qry->num_rows > 0) {
        foreach($qry->fetch_assoc() as $k => $v) {
            $$k=$v;
        }
    } else {
        ?>
		<center>Unknown Member ID</center>
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
	<form action="" id="member-form">
		<input type="hidden" name ="id" value="<?php echo isset($id) ? $id : '' ?>">
		<div class="form-group">
			<label for="firstname" class="control-label">First Name</label>
			<input name="firstname" id="firstname" type="text"class="form-control form-control-sm rounded-0" value="<?php echo isset($firstname) ? $firstname : ''; ?>" required>
		</div>
		<div class="form-group">
			<label for="middlename" class="control-label">Middle Name</label>
			<input name="middlename" id="middlename" type="text"class="form-control form-control-sm rounded-0" value="<?php echo isset($middlename) ? $middlename : ''; ?>" placeholder="optional">
		</div>
		<div class="form-group">
			<label for="lastname" class="control-label">Last Name</label>
			<input name="lastname" id="lastname" type="text"class="form-control form-control-sm rounded-0" value="<?php echo isset($lastname) ? $lastname : ''; ?>" required>
		</div>
		<div class="form-group">
			<label for="gender" class="control-label">Gender</label>
			<select name="gender" id="gender" class="custom-select selevt" required>
			<option <?php echo isset($gender) && $gender == "Male" ? 'selected' : '' ?>>Male</option>
			<option <?php echo isset($gender) && $gender == "Female" ? 'selected' : '' ?>>Female</option>
			</select>
		</div>
		<div class="form-group">
			<label for="contact" class="control-label">Contact #</label>
			<input name="contact" id="contact" type="text"class="form-control form-control-sm rounded-0" value="<?php echo isset($contact) ? $contact : ''; ?>" required>
		</div>
		<div class="form-group">
			<label for="phase_id" class="control-label">Phase</label>
			<select name="phase_id" id="phase_id" class="form-control form-control-sm rounded-0 select2" required>
				<option value="" disabled <?= !isset($phase_id) ? "selected" : "" ?>></option>
				<?php
                $phase= $conn->query("SELECT * FROM `phase_list` where delete_flag = 0 and `status` = 1 ".(isset($phase_id) ? " or id = '{$phase_id}'" : "")." order by `name` asc");
while($row = $phase->fetch_assoc()):
    ?>
				<option value="<?= $row['id'] ?>" <?php echo isset($phase_id) && $phase_id == $row['id'] ? 'selected' : '' ?>><?= $row['name'] ?></option>
				<?php endwhile; ?>
			</select>
		</div>
		<div class="form-group">
			<label for="block" class="control-label">Block #</label>
			<input name="block" id="block" type="text"  class="form-control form-control-sm rounded-0 text-right" value="<?php echo isset($block) ? $block : ''; ?>" required>
		</div>
		
		<div class="form-group">
			<label for="lot" class="control-label">Lot #</label>
			<input name="lot" id="lot" type="text"  class="form-control form-control-sm rounded-0 text-right" value="<?php echo isset($lot) ? $lot : ''; ?>" required>
		</div>
		<div class="form-group">
			<label for="status" class="control-label">Status</label>
			<select name="status" id="status" class="custom-select selevt" required>
			<option value="1" <?php echo isset($status) && $status == 1 ? 'selected' : '' ?>>Active</option>
			<option value="0" <?php echo isset($status) && $status == 0 ? 'selected' : '' ?>>Inactive</option>
			</select>
		</div>
		
	</form>
</div>
<script>
  
	$(document).ready(function(){
		$('#uni_modal').on('shown.modal.bs',function(){
			$('.select2').select2({
				placeholder:'Please Select Here',
				width:'100%',
				dropdownParent:$('#uni_modal')
			})
		})
		$('#uni_modal #member-form').submit(function(e){
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
			start_loader();
			$.ajax({
				url:_base_url_+"classes/Master.php?f=save_member",
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
						location.href = "./?page=members/view_member&id="+resp.eid;
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
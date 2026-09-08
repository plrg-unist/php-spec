<?php
global $post;
function community_custom_lostpass_url($lostpassword_url)
{
    return '#lost-password';
}
add_filter('lostpassword_url', 'community_custom_lostpass_url');


?>
<?php
if(get_option('sp_cdm_recaptcha_enable') == 1) {
    ?>
   <script src="https://www.google.com/recaptcha/api.js?render=<?php echo sanitize_text_field(get_option('sp_cdm_recaptcha_site_key')); ?>"></script>

<?php } ?>

<script type="text/javascript">
jQuery(document).ready(function ($) {

jQuery("#cdm-login-tabs").tabs();

$('.login-button').on('click',function(event){
	 event.preventDefault();
		$.removeCookie('pid', { path: '/' }); 
		$.removeCookie('cdm_group_id', { path: '/' }); 
		$.removeCookie('cdm_client_id', { path: '/' }); 
	cdm_community_load_ajax('#login-form','login','.login-message');
	
});

$( document ).on( "click", ".reset-button", function(event) {
	 event.preventDefault();
	cdm_community_load_ajax('#reset-form','reset-password','.login-message');

});


});


</script> 
<div id="content">
	
<div id="cdm-login-tabs">
<ul  class="nav nav-tabs" data-tabs="tabs">
<li class="active"><a href="#tab-login" data-toggle="tab" data-value="#tab-login">Login</a></li>
<?php if(get_option('users_can_register') != 0) { ?><li><a href="#tab-register" data-toggle="tab" data-value="#tab-register">Register</a></li><?php } ?>

</ul>
<div id="my-tab-content" class="tab-content">
<div class="tab-pane active" id="tab-login">
<h1>Login</h1>
<div class="login-message">
</div>
<form role="form" id="login-form">
	<?php wp_nonce_field('cdm_community_login'); ?>
<input type="hidden" name="action" value="cdm_community_login" />
  <div class="cdm-form-group">
    <label for="exampleInputEmail1">Username</label>
    <input type="text" name="username" class="form-control" id="exampleInputEmail1" placeholder="Enter username">
  </div>
  <div class="cdm-form-group">
    <label for="exampleInputPassword1">Password</label>
    <input type="password" name="password" class="form-control" id="exampleInputPassword1" placeholder="Password">
  </div>
 
  <button type="submit" class="btn btn-success login-button"><i class="fa fa-user"></i> Login</button> <a href="" style="margin-left:20px" class="btn btn-warning reset-password"><i class="fa fa-info-circle"></i> Reset password</a>
</form>


</div>


</div>
<?php if(get_option('users_can_register') != 0) { ?>
<div class="tab-pane" id="tab-register">
<h1>Register</h1>
 <script type="text/javascript">
	  jQuery(document).ready(function () { 
		   jQuery('.register-user').on('click',function(event){
			   	 event.preventDefault();
			   cdm_community_load_ajax('#register-form','register','.register-message');
		return false;
			});
	  });
	   </script>
       <div class="register-message">
</div>
<form role="form" id="register-form">
		<?php wp_nonce_field('cdm_community_register'); ?>
 <input type="hidden" name="action"  value="cdm_community_register" />
  <div class="cdm-form-group">
    <label for="register_username">Username</label>
    <input name="register_username" type="text" class="form-control" id="register_username" placeholder="Enter An Username">
  </div>
    <div class="cdm-form-group">
    <label for="register_exampleInputPassword1">Email</label>
    <input name="register_email" type="email" class="form-control" id="register_exampleInputPassword1" placeholder="Enter An Email">
  </div>

   <div class="cdm-form-group">
    <label for="register_exampleInputPassword1">Password</label>
    <input name="register_password1" type="password" class="form-control" id="register_exampleInputPassword1" placeholder="Password">
  </div>
  <div class="cdm-form-group">
    <label for="register_exampleInputPassword2">Enter your password again</label>
    <input name="register_password2" type="password" class="form-control" id="register_exampleInputPassword2" placeholder="Enter your password again">
  </div>
	<?php do_action('sp_cdm/register/form_fields'); ?>
 <div style="clear:both"></div>
  <button type="submit" class="btn btn-success register-user"><i class="fa fa-user"></i> Register</button>
</form>
	</div></div>
<?php } ?>
</div>
</div>
 
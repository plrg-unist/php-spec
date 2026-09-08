<?php $month = isset($_GET['month']) ? $_GET['month'] : date("Y-m"); ?>
<div class="content py-3 mt-3">
    <div class="card card-outline card-navy shadow rounded-0">
        <div class="card-header">
            <h5 class="card-title">Monthly Collection Reports</h5>
        </div>
        <div class="card-body">
            <div class="container-fluid">
                <div class="callout callout-primary shadow rounded-0">
                    <form action="" id="filter">
                        <div class="row align-items-end">
                            <div class="col-lg-3 col-md-4 col-sm-12">
                                <div class="form-group">
                                    <label for="month" class="control-label">Month</label>
                                    <input type="month" name="month" id="month" value="<?= $month ?>" class="form-control rounded-0" required>
                                </div>
                            </div>
                            <div class="col-lg-3 col-md-4 col-sm-12">
                                <div class="form-group">
                                    <button class="btn btn-primary btn-flat btn-sm"><i class="fa fa-filter"></i> Filter</button>
                                    <button class="btn btn-light border btn-flat btn-sm" type="button" id="print"><i class="fa fa-print"></i> Print</button>
                                </div>
                            </div>
                        </div>
                    </form>
                    <div class="clear-fix mb-3"></div>
                    <div id="outprint">
                    <table class="table table-bordered table-stripped">
                        <colgroup>
                            <col width="5%">
                            <col width="15%">
                            <col width="15%">
                            <col width="15%">
                            <col width="30%">
                            <col width="20%">
                        </colgroup>
                        <thead>
                            <tr class="">
                                <th class="text-center align-middle py-1">#</th>
                                <th class="text-center align-middle py-1">Date Created</th>
                                <th class="text-center align-middle py-1">Date Collected</th>
                                <th class="text-center align-middle py-1">Collected By</th>
                                <th class="text-center align-middle py-1">Member</th>
                                <th class="text-center align-middle py-1">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php
                            $i = 1;
$total = 0;
$phases = $conn->query("SELECT * FROM `phase_list` where id in (SELECT phase_id FROM `member_list` where id in (SELECT member_id FROM collection_list where  date_format(date_collected,'%Y-%m') = '{$month}'))");
$phase_arr = array_column($phases->fetch_all(MYSQLI_ASSOC), 'name', 'id');
$qry = $conn->query("SELECT c.*,CONCAT(m.firstname, ' ', COALESCE(m.middlename,''), ' ', m.lastname) as fullname, m.phase_id,m.block,m.lot from `collection_list` c inner join member_list m on c.member_id = m.id where date_format(c.date_collected,'%Y-%m') = '{$month}' order by date(c.date_collected) desc,(CONCAT(m.firstname, ' ', COALESCE(m.middlename,''), ' ', m.lastname)) asc ");
while($row = $qry->fetch_assoc()):
    $total += $row['total_amount'];
    ?>
                                <tr>
                                    <td class="text-center align-middle px-2 py-1"><?php echo $i++; ?></td>
                                    <td class="align-middle px-2 py-1"><?php echo date("Y-m-d H:i", strtotime($row['date_created'])) ?></td>
                                    <td class="align-middle px-2 py-1"><?php echo date("D F d, Y", strtotime($row['date_collected'])) ?></td>
                                    <td class="align-middle px-2 py-1"><?php echo ucwords($row['collected_by']) ?></td>
                                    <td class="align-middle px-2 py-1">
                                        <div><?php echo ucwords($row['fullname']) ?></div>
                                        <small class="text-muted"><?= ucwords((isset($phase_arr[$row['phase_id']]) ? $phase_arr[$row['phase_id']] : "N/A").' Block '.$row['block'].' Lot '.$row['lot']) ?></small>
                                    </td>
                                    <td class="text-right align-middle px-2 py-1"><?php echo format_num($row['total_amount']) ?></td>
                                </tr>
                            <?php endwhile; ?>
                        </tbody>
                        <tfoot>
                            <tr>
                                <th class="text-center px-1 py-1 align-middel" colspan="5">Total</th>
                                <th class="text-right px-1 py-1 align-middel"><?= format_num($total) ?></th>
                            </tr>
                        </tfoot>
                    </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<noscript id="print-header">
<style>
    #sys_logo{
        width:5em !important;
        height:5em !important;
        object-fit:scale-down !important;
        object-position:center center !important;
    }
</style>
<div class="d-flex align-items-center">
    <div class="col-auto text-center pl-4">
        <img src="<?= validate_image($_settings->info('logo')) ?>" alt=" System Logo" id="sys_logo" class="img-circle border border-dark">
    </div>
    <div class="col-auto flex-shrink-1 flex-grow-1 px-4">
        <h4 class="text-center m-0"><?= $_settings->info('name') ?></h4>
        <h3 class="text-center m-0"><b>Collection Report</b></h3>
        <h5 class="text-center m-0">For the Month of</h5>
        <h5 class="text-center m-0"><?= date("F Y", strtotime($month)) ?></h5>
    </div>
</div>
<hr>
</noscript>
<script>
    $(function(){
        $('#filter').submit(function(e){
            e.preventDefault()
            location.href = "./?page=reports/collections&"+$(this).serialize();
        })
        $('#print').click(function(){
            start_loader();
            var head = $('head').clone()
            var p = $('#outprint').clone()
            var el = $('<div>')
            var header =  $($('noscript#print-header').html()).clone()
            head.find('title').text("Collection Montly Report - Print View")
            el.append(head)
            el.append(header)
            el.append(p)
            var nw = window.open("","_blank","width=1000,height=900,top=50,left=75")
                    nw.document.write(el.html())
                    nw.document.close()
                    setTimeout(() => {
                        nw.print()
                        setTimeout(() => {
                            nw.close()
                            end_loader()
                        }, 200);
                    }, 500);
        })
    })
</script>
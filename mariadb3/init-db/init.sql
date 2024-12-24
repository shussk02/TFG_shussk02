STOP SLAVE;
RESET SLAVE;
SET GLOBAL gtid_slave_pos='';
CHANGE MASTER TO master_host='mariadb1_host', master_port=3306, master_user='repl_user', master_password='shussk02', master_use_gtid=current_pos;
START SLAVE;
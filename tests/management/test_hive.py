#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.management import hive


@mock.patch('marvin_python_toolbox.management.hive.json')
def test_hive_generateconf_write_file_with_json(mocked_json):
    default_conf = [{
        "origin_host": "xxx_host_name",
        "origin_db": "xxx_db_name",
        "origin_queue": "marvin",
        "target_table_name": "xxx_table_name",
        "sample_sql": "SELECT * FROM XXX",
        "sql_id": "1"
    }]

    mocked_open = mock.mock_open()
    with mock.patch('marvin_python_toolbox.management.hive.open', mocked_open, create=True):
        hive.hive_generateconf(None)

    mocked_open.assert_called_once_with('hive_dataimport.conf', 'w')
    mocked_json.dump.assert_called_once_with(default_conf, mocked_open(), indent=2)


@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.reset_remote_tables')
def test_hive_resetremote_call_HiveDataImporter_reset_remote_tables(reset_mocked): 
    hive.hive_resetremote(ctx=None, host="test", engine="test", queue="test")
    reset_mocked.assert_called_once_with()


@mock.patch('marvin_python_toolbox.management.hive.read_config')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.__init__')
def test_hive_dataimport_without_config(init_mocked, read_config_mocked):
    read_config_mocked.return_value = None

    ctx = conf = sql_id = engine = \
        skip_remote_preparation = force_copy_files = validate = force =\
        force_remote = max_query_size = destination_host = destination_port =\
        destination_host_username = destination_host_password = destination_hdfs_root_path = None

    hive.hive_dataimport(
        ctx, conf, sql_id, engine, 
        skip_remote_preparation, force_copy_files, validate, force,
        force_remote, max_query_size, destination_host, destination_port,
        destination_host_username, destination_host_password, destination_hdfs_root_path
    )

    init_mocked.assert_not_called()


@mock.patch('marvin_python_toolbox.management.hive.read_config')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.__init__')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.table_exists')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.import_sample')
def test_hive_dataimport_with_config(import_sample_mocked, table_exists_mocked, init_mocked, read_config_mocked):
    read_config_mocked.return_value = [{'origin_db': 'test', 'target_table_name': 'test'}]
    init_mocked.return_value = None

    ctx = sql_id = engine = \
        skip_remote_preparation = force_copy_files = validate =\
        force_remote = max_query_size = destination_port =\
        destination_host_username = destination_host_password = destination_hdfs_root_path = None

    force = True
    conf = '/path/to/conf'
    destination_host = 'test'

    hive.hive_dataimport(
        ctx, conf, sql_id, engine, 
        skip_remote_preparation, force_copy_files, validate, force,
        force_remote, max_query_size, destination_host, destination_port,
        destination_host_username, destination_host_password, destination_hdfs_root_path
    )

    init_mocked.assert_called_once_with(
        max_query_size=max_query_size,
        destination_host=destination_host,
        destination_port=destination_port,
        destination_host_username=destination_host_username,
        destination_host_password=destination_host_password,
        destination_hdfs_root_path=destination_hdfs_root_path,
        origin_db='test',
        target_table_name='test',
        engine=engine,
    )
    import_sample_mocked.assert_called_once_with(
        create_temp_table=True,
        copy_files=None,
        validate_query=None,
        force_create_remote_table=None
    )


@mock.patch('marvin_python_toolbox.management.hive.read_config')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.__init__')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.table_exists')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.import_sample')
def test_hive_dataimport_with_config_sql_id(import_sample_mocked, table_exists_mocked, init_mocked, read_config_mocked):
    read_config_mocked.return_value = [
        {'origin_db': 'test', 'target_table_name': 'test', 'sql_id': 'test'},
        {'origin_db': 'bla', 'target_table_name': 'bla', 'sql_id': 'bla'},
    ]
    init_mocked.return_value = None

    ctx = sql_id = engine = \
        skip_remote_preparation = force_copy_files = validate =\
        force_remote = max_query_size = destination_port =\
        destination_host_username = destination_host_password = destination_hdfs_root_path = None

    sql_id= 'test'
    force = True
    conf = '/path/to/conf'
    destination_host = 'test'

    hive.hive_dataimport(
        ctx, conf, sql_id, engine, 
        skip_remote_preparation, force_copy_files, validate, force,
        force_remote, max_query_size, destination_host, destination_port,
        destination_host_username, destination_host_password, destination_hdfs_root_path
    )

    init_mocked.assert_called_once_with(
        max_query_size=max_query_size,
        destination_host=destination_host,
        destination_port=destination_port,
        destination_host_username=destination_host_username,
        destination_host_password=destination_host_password,
        destination_hdfs_root_path=destination_hdfs_root_path,
        origin_db='test',
        target_table_name='test',
        sql_id='test',
        engine=engine,
    )
    import_sample_mocked.assert_called_once_with(
        create_temp_table=True,
        copy_files=None,
        validate_query=None,
        force_create_remote_table=None
    )


@mock.patch('marvin_python_toolbox.management.hive.read_config')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.table_exists')
@mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.import_sample')
def test_hive_dataimport_with_config_force_false(import_sample_mocked, table_exists_mocked, read_config_mocked):
    table_exists_mocked.return_value = False
    read_config_mocked.return_value = [{
        'origin_db': 'test',
        'target_table_name': 'test',
        'origin_queue':'test',
        'origin_host':'test',
        'sample_sql':'test',
        'sql_id':'test'
    }]

    ctx = sql_id = engine = \
        skip_remote_preparation = force_copy_files = validate =\
        force_remote = max_query_size = destination_port =\
        destination_host_username = destination_host_password = destination_hdfs_root_path = None

    force = False
    conf = '/path/to/conf'
    destination_host = 'test'

    hdi = hive.HiveDataImporter(
        max_query_size=max_query_size,
        destination_host=destination_host,
        destination_port=destination_port,
        destination_host_username=destination_host_username,
        destination_host_password=destination_host_password,
        destination_hdfs_root_path=destination_hdfs_root_path,
        origin_db='test',
        target_table_name='test',
        engine=engine,
        sql_id='test',
        origin_host='test',
        origin_queue='test',
        sample_sql='test',
    )

    with mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter', return_value=hdi):
        hive.hive_dataimport(
            ctx, conf, sql_id, engine, 
            skip_remote_preparation, force_copy_files, validate, force,
            force_remote, max_query_size, destination_host, destination_port,
            destination_host_username, destination_host_password, destination_hdfs_root_path
        )

        table_exists_mocked.assert_called_once_with(
            host=hdi.destination_host, db=hdi.origin_db, table=hdi.target_table_name
        )

        import_sample_mocked.assert_called_once_with(
            create_temp_table=True,
            copy_files=None,
            validate_query=None,
            force_create_remote_table=None
        )


@mock.patch('marvin_python_toolbox.management.hive.json')
@mock.patch('marvin_python_toolbox.management.hive.os.path')
def test_read_config_with_existing_path(path_mocked, json_mocked):
    path_mocked.exists.return_value = True
    path_mocked.join.return_value = 'test.conf'

    mocked_open = mock.mock_open()
    with mock.patch('marvin_python_toolbox.management.hive.open', mocked_open, create=True):
        hive.read_config("test.conf")

    mocked_open.assert_called_once_with('test.conf', 'r')
    json_mocked.load.assert_called_once_with(mocked_open())


@mock.patch('marvin_python_toolbox.management.hive.json')
@mock.patch('marvin_python_toolbox.management.hive.os.path')
def test_read_config_with_not_existing_path(path_mocked, json_mocked):
    path_mocked.exists.return_value = False
    path_mocked.join.return_value = 'test.conf'

    mocked_open = mock.mock_open()
    with mock.patch('marvin_python_toolbox.management.hive.open', mocked_open, create=True):
        hive.read_config("test.conf")

    mocked_open.assert_not_called()
    json_mocked.load.assert_not_called()


class TestHiveDataImporter:

    def setup(self):
        self.hdi = hive.HiveDataImporter(
            max_query_size=13,
            destination_host='test',
            destination_port=None,
            destination_host_username=None,
            destination_host_password=None,
            destination_hdfs_root_path='/tmp',
            origin_db='test',
            target_table_name='test',
            engine='test',
            sql_id='test',
            origin_host='test',
            origin_queue='test',
            sample_sql='test',
        )

        self.mock_methods = {
            'get_createtable_ddl': mock.DEFAULT,
            'get_partitions': mock.DEFAULT,
            'has_partitions': mock.DEFAULT,
            'create_database': mock.DEFAULT,
            'table_exists': mock.DEFAULT,
            'drop_table': mock.DEFAULT,
            'create_table': mock.DEFAULT,
            'populate_table': mock.DEFAULT,
            'get_table_location': mock.DEFAULT,
            'generate_table_location': mock.DEFAULT,
            'hdfs_dist_copy': mock.DEFAULT,
            'create_external_table': mock.DEFAULT,
            'refresh_partitions': mock.DEFAULT,
            'drop_view': mock.DEFAULT,
            'create_view': mock.DEFAULT,
            'validade_query': mock.DEFAULT,
            'get_connection': mock.DEFAULT,
            'print_finish_step': mock.DEFAULT,
            'print_start_step': mock.DEFAULT
        }

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.count_rows')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_connection')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.retrieve_data_sample')
    def test_validade_query(self, retrieve_mocked, connection_mocked, count_rows_mocked):
        count_rows_mocked.return_value = 1
        connection_mocked.return_value = 'connection_mocked'
        retrieve_mocked.return_value = {'estimate_query_mean_per_line': 42}

        self.hdi.validade_query()

        connection_mocked.assert_called_once_with(
            host=self.hdi.origin_host, 
            db=self.hdi.origin_db, 
            queue=self.hdi.origin_queue
        )
        count_rows_mocked.assert_called_once_with(conn='connection_mocked', sql=self.hdi.sample_sql)
        retrieve_mocked.assert_called_once_with(conn='connection_mocked', full_table_name=self.hdi.full_table_name)

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_connection')
    def test_table_exists_table_not_exists(self, connection_mocked, show_log_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = []
        connection_mocked.return_value = conn

        table_exists = self.hdi.table_exists(host='host', db='db', table='table')

        show_log_mocked.assert_called_once_with(cursor)
        assert table_exists is False

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_connection')
    def test_table_exists_table_exists(self, connection_mocked, show_log_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = ['test']
        connection_mocked.return_value = conn

        table_exists = self.hdi.table_exists(host='host', db='db', table='table')

        show_log_mocked.assert_has_calls([mock.call(cursor)] * 2)
        assert table_exists is True

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.drop_table')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.delete_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_connection')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._get_ssh_client')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.generate_table_location')
    def test_reset_remote_tables_without_valids_tables(self, tb_loc_mock, ssh_cli_mock, conn_mock, 
        delete_mock, drop_mock, log_mock):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = []
        conn_mock.return_value = conn

        self.hdi.reset_remote_tables()

        conn_mock.assert_called_once_with(
            host=self.hdi.origin_host, 
            db=self.hdi.temp_db_name, 
            queue=self.hdi.origin_queue
        )
        log_mock.assert_called_once_with(cursor)

        drop_mock.assert_not_called()
        tb_loc_mock.assert_not_called()
        delete_mock.assert_not_called()
        ssh_cli_mock.assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.drop_table')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.delete_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_connection')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._get_ssh_client')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.generate_table_location')
    def test_reset_remote_tables_with_valids_tables(self, tb_loc_mock, ssh_cli_mock, 
        conn_mock, delete_mock, drop_mock, log_mock):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [['test']]
        conn_mock.return_value = conn

        tb_loc_mock.return_value = 'test'
        ssh_cli_mock.return_value = 'test'

        self.hdi.reset_remote_tables()

        conn_mock.assert_called_once_with(
            host=self.hdi.origin_host, 
            db=self.hdi.temp_db_name, 
            queue=self.hdi.origin_queue
        )
        log_mock.assert_called_once_with(cursor)

        drop_mock.assert_called_once_with(conn=conn, table_name="marvin.test")
        tb_loc_mock.assert_called_once_with(
            self.hdi.destination_hdfs_root_path,
            self.hdi.origin_host,
            self.hdi.temp_db_name + '.db',
            "test"
        )
        delete_mock.assert_called_once_with('test', 'test')
        ssh_cli_mock.assert_called_once_with(
            self.hdi.origin_host,
            self.hdi.destination_host_username,
            self.hdi.destination_host_password
        )

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.validade_query')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_connection')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.print_finish_step')
    def test_import_sample_with_invalid_query_and_flag_true_stop(self, finish_step_mock, conn_mock, val_query_mock):
        val_query_mock.return_value = False

        self.hdi.import_sample(validate_query=True)

        val_query_mock.assert_called_once_with()
        finish_step_mock.assert_called_once_with()
        conn_mock.assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.print')
    def test_import_sample_with_invalid_query_and_flag_false_dont_stop(self, print_mocked):
        with mock.patch.multiple('marvin_python_toolbox.management.hive.HiveDataImporter',
            **self.mock_methods
        ) as mocks:

            self.hdi.import_sample(validate_query=False)

            assert mocks['print_finish_step'].call_count == 6
            assert mocks['get_connection'].call_count == 5
            
            mocks['validade_query'].assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.print')
    def test_import_sample_with_partitions_stop(self, print_mocked):
        with mock.patch.multiple('marvin_python_toolbox.management.hive.HiveDataImporter',
            **self.mock_methods
        ) as mocks:

            conn = mock.MagicMock()
            mocks['has_partitions'].return_value = True
            mocks['get_connection'].return_value = conn

            self.hdi.import_sample(validate_query=True)

            assert mocks['get_connection'].call_count == 2
            mocks['get_createtable_ddl'].assert_called_once_with(
                conn=conn,
                origin_table_name=self.hdi.target_table_name,
                dest_table_name=self.hdi.temp_table_name
            )
            mocks['get_partitions'].assert_called_once_with(
                mocks['get_createtable_ddl'].return_value
            )
            mocks['create_database'].assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.print')
    def test_import_sample_with_create_temp_table_false_dont_call_create_table(self, print_mocked):
        with mock.patch.multiple('marvin_python_toolbox.management.hive.HiveDataImporter',
            **self.mock_methods
        ) as mocks:

            self.hdi.import_sample(create_temp_table=False)

            mocks['table_exists'].assert_not_called()
            mocks['drop_table'].assert_not_called()
            mocks['create_table'].assert_not_called()
            mocks['populate_table'].assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.print')
    def test_import_sample_with_create_temp_table_true_call_create_table(self, print_mocked):
        with mock.patch.multiple('marvin_python_toolbox.management.hive.HiveDataImporter',
            **self.mock_methods
        ) as mocks:

            mocks['has_partitions'].return_value = False
            self.hdi.import_sample(create_temp_table=True, force_create_remote_table=True)

            assert mocks['drop_table'].call_count == 2
            assert mocks['create_table'].call_count == 1
            assert mocks['populate_table'].call_count == 1

    @mock.patch('marvin_python_toolbox.management.hive.print')
    def test_import_sample(self, print_mocked):
        with mock.patch.multiple('marvin_python_toolbox.management.hive.HiveDataImporter',
            **self.mock_methods
        ) as mocks:

            mocks['validade_query'].return_value = True
            mocks['has_partitions'].return_value = False
            self.hdi.import_sample()

            assert mocks['print_finish_step'].call_count == 6
            assert mocks['get_connection'].call_count == 5

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.clean_ddl')
    def test_get_createtable_ddl(self, clean_ddl_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        cursor.fetchall.return_value = [['l1'], ['l2']]
        dll = mock.MagicMock()
        clean_ddl_mocked.return_value = dll

        self.hdi.get_createtable_ddl(conn, 'marvin', 'test')

        cursor.execute.assert_called_once_with("SHOW CREATE TABLE marvin")
        clean_ddl_mocked.assert_called_once_with('l1l2', remove_formats=False, remove_general=True)
        dll.replace.assert_called_once_with('marvin', 'test')
        cursor.close.assert_called_once_with()

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    def test_execute_db_command(self, show_log_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        command = "bla bla bla"

        self.hdi._execute_db_command(conn, command)

        cursor.execute.assert_called_once_with(command)
        show_log_mocked.assert_called_once_with(cursor)
        cursor.close.assert_called_once_with()

    @mock.patch('marvin_python_toolbox.management.hive.hive')
    def test_get_connection(self, pyhive_mocked):
        host = 'test'
        self.hdi.get_connection(host, db='DEFAULT', queue='default')

        pyhive_mocked.connect.assert_called_once_with(
            host=host, database='DEFAULT',
            configuration={'mapred.job.queue.name': 'default',
                ' hive.exec.dynamic.partition.mode': 'nonstrict'}
        )

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    def test_retrieve_data_sample(self, show_log_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor
        cursor.description = [('table.col', 'type')]
        cursor.fetchall.return_value = ['test']

        full_table_name = 'test'
        sample_limit = 10

        data = self.hdi.retrieve_data_sample(conn, full_table_name, sample_limit)
        
        sql = "SELECT * FROM {} TABLESAMPLE ({} ROWS)".format(full_table_name, sample_limit)

        cursor.execute.assert_called_once_with(sql)
        assert data['data_header'][0]['col'] == 'col'
        assert data['data_header'][0]['table'] == 'table'
        assert data['data_header'][0]['type'] == 'type'
        assert data['total_lines'] == 1
        assert data['data'] == ['test']

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    def test_count_rows(self, show_log_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        cursor.fetchone.return_value = [42]
        conn.cursor.return_value = cursor

        sql = "SELECT COL1, COL2 FROM TABLE"
        count = self.hdi.count_rows(conn, sql)

        assert count == 42
        cursor.execute.assert_called_once_with("SELECT COUNT(1) FROM TABLE")
        show_log_mocked.assert_called_once_with(cursor)
        cursor.close.assert_called_once_with()

    @mock.patch('marvin_python_toolbox.management.hive.logger')
    def test_show_log(self, logger_mocked):
        cursor = mock.MagicMock()
        cursor.fetch_logs.return_value = ['log log log']

        self.hdi.show_log(cursor)

        logger_mocked.debug.assert_called_once_with('log log log')

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.show_log')
    def test_save_data(self, show_log_mocked):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        conn.cursor.return_value = cursor

        table = 'test'
        data = {
            'total_lines': 2,
            'data_header': [
                {'col': 'test_col_1'},
                {'col': 'test_col_2'},
            ],
            'data': [
                'header',
                'test_val_1',
                'test_val_2',
            ]
        }
        self.hdi.save_data(conn, table, data)

        dml = "INSERT INTO test (test_col_1, test_col_2) VALUES (%s, %s)"
        cursor.executemany.assert_called_once_with(dml, [('test_val_1',), ('test_val_2',)])
        show_log_mocked.assert_called_once_with(cursor)
        cursor.close.assert_called_once_with()

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._execute_db_command')
    def test_populate_table_with_partitions(self, exec_comm_mock):
        conn = None
        table_name = 'test'
        sql = 'bla bla bla'
        partitions = [{'col': 'test1'}, {'col': 'test2'}]

        self.hdi.populate_table(conn, table_name, partitions, sql)

        dml = "INSERT OVERWRITE TABLE test PARTITION (test1, test2) bla bla bla"
        exec_comm_mock.assert_called_once_with(conn, dml)

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._execute_db_command')
    def test_populate_table_without_partitions(self, exec_comm_mock):
        conn = None
        table_name = 'test'
        sql = 'bla bla bla'
        partitions = []

        self.hdi.populate_table(conn, table_name, partitions, sql)

        dml = "INSERT OVERWRITE TABLE test  bla bla bla"
        exec_comm_mock.assert_called_once_with(conn, dml)

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._execute_db_command')
    def test_create_view(self, exec_comm_mock):
        conn = None
        view_name = 'view_test'
        table_name = 'table_test'

        self.hdi.create_view(conn, view_name, table_name)

        dml = "CREATE VIEW {0} AS SELECT * FROM {1}".format(view_name, table_name)
        exec_comm_mock.assert_called_once_with(conn, dml)

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._execute_db_command')
    def test_refresh_partitions(self, exec_comm_mock):
        conn = None
        table_name = 'table_test'

        self.hdi.refresh_partitions(conn, table_name)

        sttmt = "MSCK REPAIR TABLE {0}".format(table_name)
        exec_comm_mock.assert_called_once_with(conn, sttmt)

    def test_get_table_location(self):
        cursor = mock.MagicMock()
        conn = mock.MagicMock()
        cursor.fetchall.return_value = [[' location: ', ' hdfs://test ']]
        conn.cursor.return_value = cursor
        table_name = 'test'

        loc = self.hdi.get_table_location(conn, table_name)

        cursor.execute.assert_called_once_with("DESCRIBE FORMATTED test")
        assert loc == 'hftp://test'

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._hdfs_commands')
    def test_delete_files(self, cmd_mocked):
        ssh = 'ssh'
        url = 'test.com'
        self.hdi.delete_files(ssh, url)

        cmd = "hdfs dfs -rm -R 'test.com'"
        cmd_mocked.assert_called_once_with(ssh, cmd)

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._hdfs_commands')
    def test_copy_files(self, cmd_mocked):
        ssh = 'ssh'
        origin = "/home/"
        dest = "/tmp/"
        self.hdi.copy_files(ssh, origin, dest)

        cmd = "hadoop distcp --update '/home/' '/tmp/'"
        cmd_mocked.assert_called_once_with(ssh, cmd)

    @mock.patch('marvin_python_toolbox.management.hive.logger')
    def test_hdfs_commands(self, logger_mocked):
        i = mock.MagicMock()
        o = mock.MagicMock()
        e = mock.MagicMock()
        ssh = mock.MagicMock()
        o.readlines.return_value = 'output'
        e.readlines.return_value = 'error'
        ssh.exec_command.return_value = (i, o, e)
        cmd = "command"

        out, err = self.hdi._hdfs_commands(ssh, cmd)

        assert (out, err) == ('output', 'error')
        logger_mocked.debug.assert_any_call("Executing remote command: command")
        logger_mocked.debug.assert_any_call("output")
        logger_mocked.debug.assert_any_call("error")

    @mock.patch('marvin_python_toolbox.management.hive.AutoAddPolicy', spec=True)
    @mock.patch('marvin_python_toolbox.management.hive.SSHClient.connect')
    @mock.patch('marvin_python_toolbox.management.hive.SSHClient.set_missing_host_key_policy')
    def test_get_ssh_client(self, set_missing_mocked, connect_mocked, AutoAddPolicyMocked):
        hdfs_host = 'hdfs://test.com'
        hdfs_port = '1234'
        username = 'user'
        password = 'pass'
        self.hdi._get_ssh_client(hdfs_host, hdfs_port, username, password)

        set_missing_mocked.assert_called_once_with(AutoAddPolicyMocked.return_value)
        connect_mocked.assert_called_once_with(
            hostname=hdfs_host, port=hdfs_port, username=username, password=password
        )

    @mock.patch('marvin_python_toolbox.management.hive.sys')
    @mock.patch('marvin_python_toolbox.management.hive.logger')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.copy_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.delete_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._hdfs_commands')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._get_ssh_client')
    def test_hdfs_dist_copy(self, ssh_cli_mock, hdfs_comm_mock, del_files_mock, copy_mock, logger_mock, sys_mock):
        hdfs_comm_mock.return_value = (42, None)
        copy_mock.return_value = (None, None)
        ssh = mock.MagicMock()
        ssh_cli_mock.return_value = ssh

        force = False
        hdfs_host = 'hdfs://test.com'
        hdfs_port = 1234
        origin = '/home/'
        dest = '/tmp/'

        self.hdi.hdfs_dist_copy(force, hdfs_host, hdfs_port, origin, dest, username=None, password=None)

        ssh_cli_mock.assert_called_once_with(hdfs_host, hdfs_port, None, None)
        del_files_mock.assert_not_called()
        hdfs_comm_mock.assert_any_call(ssh, "hdfs dfs -ls -R '/home/' | grep -E '^-' | wc -l")
        hdfs_comm_mock.assert_any_call(ssh, "hdfs dfs -ls -R '/tmp/' | grep -E '^-' | wc -l")
        logger_mock.debug.assert_not_called()
        sys_mock.exit.assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.sys')
    @mock.patch('marvin_python_toolbox.management.hive.logger')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.copy_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.delete_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._hdfs_commands')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._get_ssh_client')
    def test_hdfs_dist_copy_with_force(self, ssh_cli_mock, hdfs_comm_mock, del_files_mock, copy_mock, logger_mock, sys_mock):
        hdfs_comm_mock.return_value = (42, None)
        copy_mock.return_value = (None, None)
        ssh = mock.MagicMock()
        ssh_cli_mock.return_value = ssh

        force = True
        hdfs_host = 'hdfs://test.com'
        hdfs_port = 1234
        origin = '/home/'
        dest = '/tmp/'

        self.hdi.hdfs_dist_copy(force, hdfs_host, hdfs_port, origin, dest, username=None, password=None)

        ssh_cli_mock.assert_called_once_with(hdfs_host, hdfs_port, None, None)
        del_files_mock.assert_called_once_with(ssh, dest)
        hdfs_comm_mock.assert_any_call(ssh, "hdfs dfs -ls -R '/home/' | grep -E '^-' | wc -l")
        hdfs_comm_mock.assert_any_call(ssh, "hdfs dfs -ls -R '/tmp/' | grep -E '^-' | wc -l")
        logger_mock.debug.assert_not_called()
        sys_mock.exit.assert_not_called()

    @mock.patch('marvin_python_toolbox.management.hive.sys')
    @mock.patch('marvin_python_toolbox.management.hive.logger')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.copy_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.delete_files')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._hdfs_commands')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter._get_ssh_client')
    def test_hdfs_dist_copy_error_copy(self, ssh_cli_mock, hdfs_comm_mock, del_files_mock, copy_mock, logger_mock, sys_mock):
        hdfs_comm_mock.side_effect = [(42, None), (13, None)]
        copy_mock.return_value = (None, ['error'])
        ssh = mock.MagicMock()
        ssh_cli_mock.return_value = ssh

        force = False
        hdfs_host = 'hdfs://test.com'
        hdfs_port = 1234
        origin = '/home/'
        dest = '/tmp/'

        self.hdi.hdfs_dist_copy(force, hdfs_host, hdfs_port, origin, dest, username=None, password=None)

        ssh_cli_mock.assert_called_once_with(hdfs_host, hdfs_port, None, None)
        del_files_mock.assert_not_called()
        hdfs_comm_mock.assert_any_call(ssh, "hdfs dfs -ls -R '/home/' | grep -E '^-' | wc -l")
        hdfs_comm_mock.assert_any_call(ssh, "hdfs dfs -ls -R '/tmp/' | grep -E '^-' | wc -l")
        logger_mock.debug.assert_called_once_with('error')
        sys_mock.exit.assert_called_once_with("Stoping process!")

    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.clean_ddl')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.create_table')
    @mock.patch('marvin_python_toolbox.management.hive.HiveDataImporter.get_table_format')
    def test_create_external_table(self, table_formar_mock, create_table_mock, clean_ddl_mock):
        table_formar_mock.return_value = 'test'
        conn = None
        temp_table_name = 'temp'
        ddl = "CREATE TABLE bla bla bla"
        parquet_file_location = "/tmp/"
        clean_ddl_mock.return_value = ddl

        self.hdi.create_external_table(conn, temp_table_name, ddl, parquet_file_location)

        table_formar_mock.assert_called_once_with(ddl)
        clean_ddl_mock.assert_called_once_with(ddl, remove_formats=True, remove_general=False)
        ddl = "CREATE EXTERNAL TABLE bla bla bla STORED AS test LOCATION '/tmp/'"
        create_table_mock.assert_called_once_with(conn=conn, table_name=temp_table_name, ddl=ddl)
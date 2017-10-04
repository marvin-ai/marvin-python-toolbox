#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import click
import time
import os
import re
import sys
import json
from paramiko import SSHClient, AutoAddPolicy
from pyhive import hive
from slugify import slugify
import hashlib

from .._logging import get_logger


logger = get_logger('management.hive')


@click.group('hive')
def cli():
    pass


@cli.command('hive-generateconf', help='Generate default configuration file')
@click.pass_context
def hive_generateconf(ctx):
    default_conf = [{
        "origin_host": "xxx_host_name",
        "origin_db": "xxx_db_name",
        "origin_queue": "marvin",
        "target_table_name": "xxx_table_name",
        "sample_sql": "SELECT * FROM XXX",
        "sql_id": "1"
    }]

    with open('hive_dataimport.conf', 'w') as outfile:
        json.dump(default_conf, outfile, indent=2)

    print("Done!!!")


@cli.command('hive-resetremote', help='Drop all remote tables from informed engine on host')
@click.option('--host', '-h', default='marvin-hadoop')
@click.option('--queue', '-h', default='default')
@click.option('--engine', default=(os.path.relpath(".", "..")), help='Marvin engine name (default is the current folder)')
@click.pass_context
def hive_resetremote(ctx, host, engine, queue):
    hdi = HiveDataImporter(
        engine=engine,
        origin_host=host,
        origin_queue=queue,
        origin_db=None,
        target_table_name=None,
        sample_sql=None,
        max_query_size=None,
        destination_host=None,
        destination_host_username='vagrant',
        destination_host_password='vagrant',
        destination_hdfs_root_path='/user/hive/warehouse/',
        sql_id=None
    )
    hdi.reset_remote_tables()


@cli.command(
    'hive-dataimport',
    help='Export and import data samples from a hive databse to the hive running in this toolbox, cloning same data structure (db and table).')
@click.option('--destination-hdfs-root-path', '-hdfs', default='/user/hive/warehouse/')
@click.option('--destination-host-password', '-p', default='vagrant')
@click.option('--destination-host-username', '-u', default='vagrant')
@click.option('--destination-host', '-dh', default='marvin-hadoop')
@click.option('--destination-port', '-dp', default=22)
@click.option('--max-query-size', '-s', default=(50 * 1024 * 1024), help='Max query size in bytes')
@click.option('--force', is_flag=True, help='Force table creation even table already exists in destination')
@click.option('--force-remote', is_flag=True, help='Force remote temp table creation even table already exists in origin')
@click.option('--validate', is_flag=True, help='Validate the query sample')
@click.option('--force-copy-files', is_flag=True, help='Force the hdfs files copy procedure')
@click.option('--skip-remote-preparation', is_flag=True, help='Skip the creation of remote temp table')
@click.option('--engine', default=(os.path.relpath(".", "..")), help='Marvin engine name (default is the current folder)')
@click.option('--sql-id', '-q', help='If informed the process will be applied exclusivelly for this sample sql')
@click.option('--conf', '-c', default='hive_dataimport.conf', help='Hive data import configuration file')
@click.pass_context
def hive_dataimport(
    ctx, conf, sql_id, engine, skip_remote_preparation, force_copy_files, validate, force,
    force_remote, max_query_size, destination_host, destination_port, destination_host_username, destination_host_password,
    destination_hdfs_root_path
):

    initial_start_time = time.time()

    confs = read_config(filename=conf)

    if confs:
        print(chr(27) + "[2J")

        if sql_id:
            confs = [x for x in confs if x['sql_id'] == sql_id]

        for conf in confs:
            hdi = HiveDataImporter(
                max_query_size=max_query_size,
                destination_host=destination_host,
                destination_port=destination_port,
                destination_host_username=destination_host_username,
                destination_host_password=destination_host_password,
                destination_hdfs_root_path=destination_hdfs_root_path,
                engine=engine,
                **conf)

            if force:
                table_exists = False

            else:
                table_exists = hdi.table_exists(host=hdi.destination_host, db=hdi.origin_db, table=hdi.target_table_name)

            if not table_exists:
                hdi.import_sample(
                    create_temp_table=(not skip_remote_preparation),
                    copy_files=force_copy_files,
                    validate_query=validate,
                    force_create_remote_table=force_remote,
                )

            else:
                print ("Table {} already exists, skiping data import. Use --force flag to force data importation".format(hdi.full_table_name))

        print("Total Time : {:.2f}s".format(time.time() - initial_start_time))

        print("\n")


def read_config(filename):
    fname = os.path.join("", filename)
    if os.path.exists(fname):
        with open(fname, 'r') as fp:
            return json.load(fp)
    else:
        print("Configuration file {} doesn't exists...".format(filename))
        return {}


class HiveDataImporter(object):
    def __init__(
        self, origin_host, origin_db, origin_queue, target_table_name, sample_sql, engine,
        max_query_size, destination_host, destination_port, destination_host_username, destination_host_password,
        destination_hdfs_root_path, sql_id
    ):

        self.sql_id = sql_id
        self.origin_host = origin_host
        self.origin_db = origin_db
        self.origin_queue = origin_queue
        self.target_table_name = target_table_name
        self.sample_sql = sample_sql
        self.engine = engine
        self.destination_host = destination_host
        self.destination_port = destination_port
        self.destination_host_username = destination_host_username
        self.destination_host_password = destination_host_password
        self.destination_hdfs_root_path = destination_hdfs_root_path

        self.temp_db_name = 'marvin'
        self.max_query_size = max_query_size

        self.supported_format_types = {
            'TextInputFormat': 'TEXTFILE',
            'SequenceFileInputFormat': 'SEQUENCEFILE',
            'OrcInputFormat': 'ORC',
            'MapredParquetInputFormat': 'PARQUET',
            'AvroContainerInputFormat': 'AVRO',
            'RCFileInputFormat': 'RCFILE'
        }

        print("\n------------------------------------------------------------------------------")
        print("Initializing process for sql_id [{}]:".format(self.sql_id))
        print("     Origin -->")
        print("         Host:       [{}]".format(self.origin_host))
        print("         DataBase:   [{}]".format(self.origin_db))
        print("         Table Name: [{}]".format(self.target_table_name))
        print("         Sample SQL: [{}]".format(self.sample_sql))
        print("\n")
        print("     Destination -->")
        print("         Host:       [{}]".format(self.destination_host))
        print("         DataBase:   [{}]".format(self.origin_db))
        print("         Table Name: [{}]".format(self.target_table_name))
        print("\n")

    def validade_query(self):
        # creating connections
        print("Connecting with {} database on {} .. ".format(self.origin_db, self.origin_host))
        conn_origin = self.get_connection(host=self.origin_host, db=self.origin_db, queue=self.origin_queue)

        print("Counting sample sql ...")
        total_rows = self.count_rows(conn=conn_origin, sql=self.sample_sql)
        print("Found [{}] rows!".format(total_rows))

        print("Retrieve data sample for query estimation reasons...")
        data_sample = self.retrieve_data_sample(conn=conn_origin, full_table_name=self.full_table_name)
        print("Calculated [{}] bytes per row!".format(data_sample['estimate_query_mean_per_line']))

        estimated_size = data_sample['estimate_query_mean_per_line'] * total_rows

        print ("Estimated query size is : {} bytes".format(estimated_size))
        print ("Max permited query size is: {} bytes".format(self.max_query_size))

        return estimated_size <= self.max_query_size

    def table_exists(self, host, db, table):
        print("Verifiying if table {}.{} exists on {} ...".format(db, table, host))
        local_conn = self.get_connection(host=host)
        cursor = local_conn.cursor()

        cursor.execute("SHOW DATABASES LIKE '{}'".format(db))
        dbs = cursor.fetchall()
        self.show_log(cursor)

        if not len(dbs) == 1:
            table_exists = False
        else:
            cursor.execute("USE {} ".format(db))

            cursor.execute("SHOW TABLES LIKE '{}'".format(table))
            tbs = cursor.fetchall()
            self.show_log(cursor)

            if not len(tbs) == 1:
                table_exists = False
            else:
                table_exists = True

        cursor.close()
        return table_exists

    def reset_remote_tables(self):
        self.print_start_step(name="Reset Remote Tables for {}".format(self.temp_table_prefix), step_number=1, total_steps=1)

        print("Connecting with {} database on {} .. ".format(self.temp_db_name, self.origin_host))
        remote_temp_db_conn = self.get_connection(host=self.origin_host, db=self.temp_db_name, queue=self.origin_queue)

        cursor = remote_temp_db_conn.cursor()
        cursor.execute("SHOW TABLES LIKE '{}*'".format(self.temp_table_prefix))
        tbs = cursor.fetchall()
        self.show_log(cursor)
        cursor.close()

        valid_tbs = [tb[0] for tb in tbs]

        if valid_tbs:
            print("Found {} tables for deletion....".format(len(tbs)))

            for tb in valid_tbs:
                table_name = "{}.{}".format(self.temp_db_name, tb)
                print("Dropping table {} on {} .. ".format(table_name, self.origin_host))
                self.drop_table(conn=remote_temp_db_conn, table_name=table_name)

                hdfs_location = self.generate_table_location(self.destination_hdfs_root_path, self.origin_host, self.temp_db_name + '.db', tb)
                print("Removing hdfs files from {} .. ".format(hdfs_location))

                ssh = self._get_ssh_client(self.origin_host, self.destination_host_username, self.destination_host_password)
                self.delete_files(ssh, hdfs_location)

        else:
            print("No table found! Skiping reset remote tables process!!")

        self.print_finish_step()

    def print_finish_step(self):
        print("\n                                               STEP TAKES {:.4f} (seconds) ".format((time.time() - self.start_time)))

    def print_start_step(self, name, step_number, total_steps):
        print("\n------------------------------------------------------------------------------")
        print("MARVIN DATA IMPORT - STEP ({}) of ({}) - [{}]".format(step_number, total_steps, name))
        print("------------------------------------------------------------------------------\n")
        self.start_time = time.time()

    def import_sample(self, create_temp_table=True, copy_files=True, validate_query=True, force_create_remote_table=False):
        #
        #################################################################################
        # Step 1 - Query validation
        self.print_start_step(name="Query Validation", step_number=1, total_steps=6)

        is_valid = self.validade_query() if validate_query else True

        if not is_valid:
            print("Informed sample query is not valid!")
            self.print_finish_step()
            return

        self.print_finish_step()

        #
        ##################################################################################
        # Step 2 - Testing remote connecitons and getting table schema
        self.print_start_step(name="Table Schema Achievement", step_number=2, total_steps=6)

        # creating connections
        print("Connecting with {} database on {} .. ".format(self.origin_db, self.origin_host))
        conn_origin = self.get_connection(host=self.origin_host, db=self.origin_db, queue=self.origin_queue)

        print("Connecting with {} database on {} .. ".format(self.temp_db_name, self.origin_host))
        remote_temp_db_conn = self.get_connection(host=self.origin_host, db=self.temp_db_name, queue=self.origin_queue)

        # getting ddl from real table
        print("Getting DDL from {} table ".format(self.target_table_name))
        ddl = self.get_createtable_ddl(conn=conn_origin, origin_table_name=self.target_table_name, dest_table_name=self.temp_table_name)

        # validanting if partitions is used in query statement
        partitions = self.get_partitions(ddl)

        if validate_query and self.has_partitions(self.sample_sql, [p['cols'] for p in partitions]):
            print("Informed sample query doesn't have valid partitions in the clausule where!!!! Informe at lest one partition.")
            print("To disable the query validation use --skip-validation flag.")
            self.print_finish_step()
            return

        print("Connecting with DEFAULT database on {} .. ".format(self.destination_host))
        local_conn = self.get_connection(host=self.destination_host)

        # creating databases if not exists
        print("Creating database {} ...".format(self.origin_db))
        self.create_database(conn=local_conn, db=self.origin_db)

        print("Connecting with {} database on {} .. ".format(self.origin_db, self.destination_host))
        local_conn = self.get_connection(host=self.destination_host, db=self.origin_db)

        # creating databases if not exists
        print("Creating database {} ...".format(self.temp_db_name))
        self.create_database(conn=local_conn, db=self.temp_db_name)

        print("Connecting with {} database on {} .. ".format(self.temp_db_name, self.destination_host))
        local_temp_db_conn = self.get_connection(host=self.destination_host, db=self.temp_db_name)

        self.print_finish_step()

        #
        ##################################################################################
        # Step 3 - Remote Table Preparation
        self.print_start_step(name="Remote Table Preparation", step_number=3, total_steps=6)

        if create_temp_table:

            if force_create_remote_table:
                remote_table_exists = False

            else:
                remote_table_exists = self.table_exists(host=self.origin_host, db=self.temp_db_name, table=self.temp_table_name)

            # verify if remote table alredy exists
            if not remote_table_exists:
                print("Dropping table {} on {} .. ".format(self.full_temp_table_name, self.origin_host))
                self.drop_table(conn=remote_temp_db_conn, table_name=self.full_temp_table_name)

                print("Creating table {} on {} .. ".format(self.full_temp_table_name, self.origin_host))
                self.create_table(conn=remote_temp_db_conn, table_name=self.full_temp_table_name, ddl=ddl)

                # insert from select
                print("Populating table {} on {} using informed sample sql.. ".format(self.full_temp_table_name, self.origin_host))
                self.populate_table(conn=conn_origin, table_name=self.full_temp_table_name, partitions=partitions, sql=self.sample_sql)

            else:
                print("Table {} on {} already exists ...".format(self.full_temp_table_name, self.origin_host))

        self.print_finish_step()

        #
        ##################################################################################
        # Step 4 - Copying remote hdfs files
        self.print_start_step(name="Copying HDFS Files", step_number=4, total_steps=6)

        # get temp location
        print("Getting hdfs files location from {} table ...".format(self.full_temp_table_name))
        temp_table_location = self.get_table_location(conn=remote_temp_db_conn, table_name=self.full_temp_table_name)

        # copy hdfs files for local hdfs
        external_table_location = self.generate_table_location(
            host=self.destination_host,
            root_path=self.destination_hdfs_root_path,
            db_name=self.temp_db_name, table_name=self.temp_table_name)

        print("Copying files from [{}] to [{}]".format(temp_table_location, external_table_location))
        self.hdfs_dist_copy(force=copy_files,
                            hdfs_host=self.destination_host,
                            hdfs_port=self.destination_port,
                            origin=temp_table_location,
                            dest=external_table_location,
                            password=self.destination_host_password,
                            username=self.destination_host_username)

        self.print_finish_step()
        #
        ##################################################################################
        # Step 5 - External table creation using hdfs files
        self.print_start_step(name="Local Temporary Table Creation", step_number=5, total_steps=6)

        # creating external table using parquet files in hdfs
        print("Dropping temp table {} on {} .. ".format(self.full_temp_table_name, self.destination_host))
        self.drop_table(conn=local_temp_db_conn, table_name=self.full_temp_table_name)

        # create temp table
        print("Creating temp table {} using imported hdfs files from [{}] ...".format(self.full_temp_table_name, external_table_location))
        self.create_external_table(conn=local_temp_db_conn,
                                   temp_table_name=self.full_temp_table_name,
                                   ddl=ddl,
                                   parquet_file_location=external_table_location)

        print("Refreshing table {} partitions on {} ..".format(self.full_temp_table_name, self.destination_host))
        self.refresh_partitions(conn=local_temp_db_conn, table_name=self.full_temp_table_name)

        self.print_finish_step()

        #
        ##################################################################################
        # Step 6 - Destination table creation from external table
        self.print_start_step(name="Table population", step_number=6, total_steps=6)

        # create view
        print("Dropping table view {} on {} .. ".format(self.full_table_name, self.destination_host))
        self.drop_view(conn=local_conn, view_name=self.full_table_name)

        print("Creating table view {} ... ".format(self.full_table_name, self.destination_host))
        self.create_view(conn=local_conn, view_name=self.full_table_name, table_name=self.full_temp_table_name)

        self.print_finish_step()

        print("Procedure done!!!!")

    @property
    def temp_table_prefix(self):
        return "{}".format(slugify(self.engine).replace('-', '_'))

    @property
    def temp_table_name(self):
        return "{}_{}_{}_{}".format(self.temp_table_prefix, self.origin_db, self.target_table_name, hashlib.sha1(slugify(self.sample_sql)).hexdigest())

    @property
    def full_table_name(self):
        return "{}.{}".format(self.origin_db, self.target_table_name)

    @property
    def full_temp_table_name(self):
        return "{}.{}".format(self.temp_db_name, self.temp_table_name)

    def generate_table_location(self, root_path, host, db_name, table_name):
        return "hdfs://{}:8020{}".format(host, os.path.join(root_path, db_name, table_name))

    def clean_ddl(self, ddl, remove_formats=True, remove_general=True):
        if remove_general:
            # Removing LOCATION statement
            regex = "(LOCATION\s+'(.*?)')"
            result = re.search(regex, ddl)
            ddl = ddl.replace(result.group(1), " ") if result else ddl

            # Removing TBLPROPERTIES statement
            regex = "(TBLPROPERTIES\s+(.*?)\))"
            result = re.search(regex, ddl)
            ddl = ddl.replace(result.group(1), " ") if result else ddl

            # Removing WITH SERDEPROPERTIES statement
            regex = "(WITH SERDEPROPERTIES\s+(.*?)\))"
            result = re.search(regex, ddl)
            ddl = ddl.replace(result.group(1), " ") if result else ddl

        if remove_formats:
            # Removing STORED AS INPUTFORMAT statement
            regex = "(STORED AS INPUTFORMAT\s+'(.*?)')"
            result = re.search(regex, ddl)
            ddl = ddl.replace(result.group(1), " ") if result else ddl

            # Removing OUTPUTFORMAT statement
            regex = "(OUTPUTFORMAT\s+'(.*?)')"
            result = re.search(regex, ddl)
            ddl = ddl.replace(result.group(1), " ") if result else ddl

        return ddl

    def get_table_format(self, ddl):
        regex = "(STORED AS INPUTFORMAT\s+'(.*?)')"
        result = re.search(regex, ddl)
        input_format = result.group(2)
        return self.supported_format_types[input_format.split(".")[-1]]

    def get_database_info(self, ddl):
        regex = "CREATE TABLE `((.*?)\.)?(.*?)`\("
        result = re.search(regex, ddl)
        if result:
            groups = result.groups()
            if groups[0]:
                # found db name
                return {'db': groups[1], 'table': groups[2]}
            else:
                {'db': None, 'table': groups[2]}
        return {'db': None, 'table': None}

    def get_createtable_ddl(self, conn, origin_table_name, dest_table_name):
        cursor = conn.cursor()
        cursor.execute("SHOW CREATE TABLE " + origin_table_name)
        _lines = [_line[0] for _line in cursor.fetchall()]
        ddl = ''.join(_lines)
        ddl = self.clean_ddl(ddl, remove_formats=False, remove_general=True)
        ddl = ddl.replace(origin_table_name, dest_table_name)
        cursor.close()
        return ddl

    def create_database(self, conn, db):
        self._execute_db_command(conn, "CREATE DATABASE IF NOT EXISTS " + db)

    def drop_table(self, conn, table_name):
        self._execute_db_command(conn, 'DROP TABLE IF EXISTS ' + table_name)

    def drop_view(self, conn, view_name):
        self._execute_db_command(conn, 'DROP VIEW ' + view_name)

    def create_table(self, conn, table_name, ddl):
        self._execute_db_command(conn, ddl)

    def _execute_db_command(self, conn, command):
        cursor = conn.cursor()
        cursor.execute(command)
        self.show_log(cursor)
        cursor.close()

    def get_connection(self, host, db='DEFAULT', queue='default'):
        return hive.connect(host=host,
                            database=db,
                            configuration={'mapred.job.queue.name': queue,
                                           ' hive.exec.dynamic.partition.mode': 'nonstrict'})

    def retrieve_data_sample(self, conn, full_table_name, sample_limit=100):
        cursor = conn.cursor()

        sql = "SELECT * FROM {} TABLESAMPLE ({} ROWS)".format(full_table_name, sample_limit)

        cursor.execute(sql)
        data_header = [{'col': line[0].split('.')[1], 'table': line[0].split('.')[0], 'type': line[1]} for line in cursor.description]
        data = [row for row in cursor.fetchall()]
        self.show_log(cursor)
        cursor.close()
        return {'data_header': data_header,
                'total_lines': len(data),
                'data': data,
                'estimate_query_size': sys.getsizeof(data),
                'estimate_query_mean_per_line': sys.getsizeof(data) / len(data)}

    def count_rows(self, conn, sql):
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(1) " + sql[sql.upper().rfind("FROM"):])
        size = cursor.fetchone()[0]
        self.show_log(cursor)
        cursor.close()
        return size

    def show_log(self, cursor):
        for l in cursor.fetch_logs():
            logger.debug(l)

    def save_data(self, conn, table, data):
        cursor = conn.cursor()
        print('Inserting {} rows in {} table...'.format(data['total_lines'], table))
        cols = [v['col'] for v in data['data_header']]
        dml = "INSERT INTO {0} ({1}) VALUES ({2})".format(table, ", ".join(cols), ", ".join(['%s' for col in cols]))
        cursor.executemany(dml, [(v,) for v in data['data'][1:10]])
        self.show_log(cursor)
        cursor.close()

    def get_partitions(self, ddl):
        regex = "(PARTITIONED BY\s+\((.*?)\))"
        result = re.search(regex, ddl)
        if result:
            p_cols = result.group(2).strip().replace('`', '').split(",")
            return [{'col': p_col.split()[0], 'type': p_col.split()[1]} for p_col in p_cols]
        else:
            return []

    def has_partitions(self, sql, partitions):
        regex = "WHERE(.*?)(" + "|".join(partitions).upper() + ")"
        result = re.search(regex, sql.upper())

        if result:
            return True
        else:
            return False

    def populate_table(self, conn, table_name, partitions, sql):
        partitions = [p['col'] for p in partitions]
        partitions_statement = "PARTITION ({})".format(", ".join(partitions)) if partitions else ""
        dml = "INSERT OVERWRITE TABLE {0} {1} {2}".format(table_name, partitions_statement, sql)
        self._execute_db_command(conn, dml)

    def create_view(self, conn, view_name, table_name):
        dml = "CREATE VIEW {0} AS SELECT * FROM {1}".format(view_name, table_name)
        self._execute_db_command(conn, dml)

    def refresh_partitions(self, conn, table_name):
        refresh_statement = "MSCK REPAIR TABLE {0}".format(table_name)
        self._execute_db_command(conn, refresh_statement)

    def get_table_location(self, conn, table_name):
        cursor = conn.cursor()
        cursor.execute("DESCRIBE FORMATTED {}".format(table_name))
        location = [key[1].strip() for key in cursor.fetchall() if key[0] and key[0].strip().upper() == 'LOCATION:'][0].replace('hdfs://', 'hftp://')
        cursor.close()
        return location

    def delete_files(self, ssh, url):
        cmd = "hdfs dfs -rm -R '{}'".format(url)
        self._hdfs_commands(ssh, cmd)

    def copy_files(self, ssh, origin, dest):
        cmd = "hadoop distcp --update '{}' '{}'".format(origin, dest)
        return self._hdfs_commands(ssh, cmd)

    def _hdfs_commands(self, ssh, cmd):
        logger.debug("Executing remote command: {}".format(cmd))
        i, o, e = ssh.exec_command(cmd)
        errors = e.readlines()
        output = o.readlines()
        logger.debug(output)
        logger.debug(errors)
        return output, errors

    def _get_ssh_client(self, hdfs_host, hdfs_port, username, password):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(hostname=hdfs_host, port=hdfs_port, username=username, password=password, )
        return ssh

    def hdfs_dist_copy(self, force, hdfs_host, hdfs_port, origin, dest, username=None, password=None):
        # connecting with hdfs host
        ssh = self._get_ssh_client(hdfs_host, hdfs_port, username, password)

        if force:
            print("Removing old hdfs files if necessary. To force copy remote files use --force-copy-files flag.")

            # delete files from dest
            self.delete_files(ssh, dest)

        else:
            print("Using old hdfs files to complete the procedure. If necessary to copy files again use --force-copy-files flag.")

        # copy files from origin to destination
        _, copy_errors = self.copy_files(ssh, origin, dest)

        # validate copy
        cmd_template = "hdfs dfs -ls -R '{}' | grep -E '^-' | wc -l"
        cmd = cmd_template.format(origin)
        result1, _ = self._hdfs_commands(ssh, cmd)

        cmd = cmd_template.format(dest)
        result2, _ = self._hdfs_commands(ssh, cmd)

        if result1 == result2:
            print("Files {} successfully transferred!!".format(result1))
        else:
            print("Errors during hdfs files copy process!!")
            for e_l in copy_errors:
                logger.debug(e_l)
            sys.exit("Stoping process!")

    def create_external_table(self, conn, temp_table_name, ddl, parquet_file_location):
        format_type = self.get_table_format(ddl)
        ddl = self.clean_ddl(ddl, remove_formats=True, remove_general=False)
        ddl = ddl.replace("CREATE TABLE", "CREATE EXTERNAL TABLE")
        ddl = "{} STORED AS {} LOCATION '{}'".format(ddl, format_type, parquet_file_location)
        self.create_table(conn=conn, table_name=temp_table_name, ddl=ddl)

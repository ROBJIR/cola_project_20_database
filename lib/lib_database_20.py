#
# lib_database.py
# version: 2.0, 2026-06-22, robert.jiranek@gmail.com
#
import sys
import os
from operator import truediv

import math
from unittest import case

import psycopg2
from psycopg2.extras import RealDictCursor
import oracledb
import logging
# my librares
from lib.lib_config_file import ConfigurationFile
from lib.lib_log import *

class Database ():
    def __init__(self):
        # initialize logfile for database
        self.database_logfile = LogFile()
        self.database_logfile.logfile_init("database")

        self.cfgfile = ConfigurationFile()

        self.client_islocal = False
        self.client_lib_dir = ""
        self.client_isdsn = False
        self.client_tns_admin_path = ""

        self.database_default_connection = self.cfgfile.parameter_get("connections", "connections", "default_connection")

        self.database_connect_string = ""
        self.database_host = ""
        self.database_port = ""
        self.database_name = ""
        self.database_user_username = ""
        self.database_user_password = ""
        self.database_schema = ""

        self.current_database_connection = ""
        self.current_database_model = ""
        self.current_database_detail = ""

        self.current_database_version = ""
        self.current_database = ""
        self.current_user_username = ""
        self.current_schema = ""
        self.session_id = ""

        self.ddl_alter_session_set_current_schema = ""
        self.sel_select_current_schema = ""

        self.dbadm_syslog_table = ""
        self.dbadm_session_info_query = ""

        self.dbadm_logging_sysinfo    = self.cfgfile.parameter_get("databases", "logging" ,"logging_sysinfo").lower() == "true"
        self.dbadm_logging_sqlcommand = self.cfgfile.parameter_get("databases","logging","logging_sqlcommand").lower() == "true"
        self.dbadm_select_current_schema = ""
        self.dbadm_alter_session_set_current_schema = ""

    def sys_error(self, modul: str = "", message: str = "", errno: int=0 ,err: str = "", dblog: bool = True, logfile: bool = True, screen: bool = True, sysexit: bool = True, parameters: str = "", sqlcommand : str =""):
        msg=f"{self.current_database}: {modul} [{str(errno)}] - {str(err)}"

        if screen or sysexit:
            print (f"\n{msg}\n")

        if not message:
            msg = f"{msg}\n{message}"
        if not parameters:
            msg = f"{msg}\n--- parameters ----------------------------------\n{parameters}"
        if not sqlcommand:
            msg = f"{msg}\n--- sqlcommand ----------------------------------\n{sqlcommand}"

        if logfile:
            self.database_logfile.error(f"{msg}")

        if dblog and self.dbadm_logging_sysinfo:
            self.sys_dbadm_log(modul, message,  parameters, "---", "ERROR", sqlcommand, errno, err)

        if sysexit:
            sys.exit(errno)

        return msg

    def sys_info(self, modul: str = "", message: str = "", dblog: bool = True, logfile: bool = True, screen: bool = False, parameters: str = "", sqlcommand  : str =""):
        msg = f"{self.current_database}: {modul} "

        if screen:
            print(f"\n{msg}\n")

        if message:
            msg = f"{msg} - {message}"
        if parameters:
            msg = f"{msg}\n--- parameters ----------------------------------\n{parameters}"
        if sqlcommand:
            msg = f"{msg}\n--- sqlcommand ----------------------------------\n{sqlcommand}"

        if logfile:
            self.database_logfile.info(f"{msg}")

        if dblog and self.dbadm_logging_sysinfo:
            self.sys_dbadm_log(modul, message, parameters, "---", "INFO", sqlcommand)

        return msg


    def connect(self, connection: str = ""):
        try:
            if connection:
                self.current_database_connection=connection.lower()
            else:
                self.current_database_connection=self.database_default_connection.lower()
            self.current_database_model = self.cfgfile.parameter_get("connections", self.current_database_connection,"database_model").lower()
            self.database_connect_string = self.cfgfile.parameter_get("connections", self.current_database_connection,"dsn")
            self.database_host = self.cfgfile.parameter_get("connections", self.current_database_connection, "host")
            self.database_port = self.cfgfile.parameter_get("connections", self.current_database_connection, "port")
            self.database_name = self.cfgfile.parameter_get("connections", self.current_database_connection, "database")
            self.database_user_username = self.cfgfile.parameter_get("connections", self.current_database_connection,"user")
            self.database_user_password = self.cfgfile.parameter_get("connections", self.current_database_connection,"password")
            self.database_schema = self.cfgfile.parameter_get("connections", self.current_database_connection, "schema")

            self.dbadm_syslog_table = self.cfgfile.parameter_get("databases", self.current_database_model ,"dbadm_syslog_table")
            self.dbadm_session_info_query = self.cfgfile.parameter_get("databases", self.current_database_model ,"dbadm_session_info_query")

            self.dbadm_select_current_schema = self.cfgfile.parameter_get("databases", self.current_database_model ,"dbadm_select_current_schema")
            self.dbadm_alter_session_set_current_schema = self.cfgfile.parameter_get("databases", self.current_database_model ,"dbadm_alter_session_set_current_schema")

            self.current_database_detail = f"database_connection = {self.current_database_connection}\ndatabase = {self.current_database_model}"
            match self.current_database_model:
                case "postgresql":
                    self.connect_postgresql()
                case "oracle":
                    self.connect_oracle()
                case _:
                    self.sys_error("database.connect", f"database {self.current_database_model} is not supported!", 74, "", False)

            self.sys_database_info_get()
            self.current_database_detail = f"{self.current_database_detail}\nsession ID = {self.session_id}"
            self.sys_info("database.connect", f"connected to {self.database_name} database")
            self.sys_info("database.connect", f"connection details\n{self.current_database_detail}")

            if self.database_schema:
                self.schema_set(self.database_schema)
                self.current_database_detail = f"{self.current_database_detail}\nschema = {self.database_schema}"

            return True
        except Exception as err:
            self.sys_error("database.connect", f"connected to {self.database_name} database", 75, err, False)

    def connect_postgresql(self):
        try:
            db_conn = psycopg2.connect(
                host=self.database_host,
                port=self.database_port,
                database=self.database_name,
                user=self.database_user_username,
                password=self.database_user_password
            )
            self.conn = db_conn
            self.current_database_detail = f"{self.current_database_detail}\nhost:port = {self.database_host}:{self.database_port}\ndatabase_name = {self.database_name}\nusername = {self.database_user_username}"

        except Exception as err:
            self.sys_error("database.connect_postgresql", "",76, err, False)


    def connect_oracle(self):
        try:
            self.client_islocal = self.cfgfile.parameter_get("databases", self.current_database_model, "client_lib_dir") != ""
            self.client_lib_dir = self.cfgfile.parameter_get("databases", self.current_database_model, "client_lib_dir")
            self.client_isdsn = self.cfgfile.parameter_get("databases", self.current_database_model,"client_tns_admin") != ""
            self.client_tns_admin_path = self.cfgfile.parameter_get("databases", self.current_database_model, "client_tns_admin")

            # local client - is defined lib dir
            if self.client_islocal:
                oracledb.init_oracle_client(lib_dir=self.client_lib_dir)
                self.current_database_detail = f"{self.current_database_detail}\nlib_dir={self.client_lib_dir}"

            if self.client_isdsn:
                os.environ["TNS_ADMIN"] = self.client_tns_admin_path
                self.current_database_detail = f"{self.current_database_detail}\ntns_admin={self.client_tns_admin_path}"

            if self.database_connect_string:

                db_conn = oracledb.connect(
                    dsn=self.database_connect_string,
                    user=self.database_user_username,
                    password=self.database_user_password
                )
                self.conn = db_conn
                self.current_database_detail = f"{self.current_database_detail}\nconnect_string = {self.database_connect_string}\nusername = {self.database_user_username}"

            else:

                db_conn = oracledb.connect(
                    host=self.database_host,
                    port=self.database_port,
                    service_name=self.database_name,
                    user=self.database_user_username,
                    password=self.database_user_password
                )
                self.conn = db_conn
                self.current_database_detail = f"{self.current_database_detail}\nhost:port = {self.database_host}:{self.database_port}\nservice_name = {self.database_name}\nusername = {self.database_user_username}"

        except Exception as err:
            self.sys_error("database.connect_oracle", "",77, err, False)

    def close(self):
        try:
            self.sys_info("database.close", f"close database {self.database_name}")
            self.conn.close()

            self.client_islocal = False
            self.client_lib_dir = ""
            self.client_isdsn = False
            self.client_tns_admin_path = ""

            self.database_connect_string = ""
            self.database_host = ""
            self.database_port = ""
            self.database_name = ""
            self.database_user = ""
            self.database_user_password = ""
            self.database_schema = ""

            self.current_database_connection = ""
            self.current_database_model = ""
            self.current_database_detail = ""

            self.current_database_version = ""
            self.current_database = ""
            self.current_schema = ""
            self.session_id = ""

            self.dbadm_syslog_table = ""
            self.dbadm_session_info_query = ""

            return True
        except Exception as err:
            self.sys_error("database.close", "", 78, err)

        return True

    def schema_set(self, schema: str = ""):
        try:
            if schema:
                self.current_schema = schema
            else:
                if self.database_schema:
                    self.current_schema =  self.database_schema

            sqlcommand = self.dbadm_alter_session_set_current_schema.replace("<<schema>>", self.current_schema)

            cur = self.conn.cursor()
            cur.execute(sqlcommand)
            self.conn.commit()
            cur.close()

            self.sys_info("database.schema_set", f"{sqlcommand}")

            return True

        except Exception as err:
            self.sys_error("database.schema_set", "", 72, err)

    def schema_get(self):
        try:
            cur = self.conn.cursor()
            cur.execute(self.dbadm_select_current_schema)
            schema = cur.fetchone()[0]
            cur.close()
            return schema

        except Exception as err:
            self.sys_error("database.schema_get", "", 73, err)

    def sys_logging_set(self,status: bool = True, type: str = "sqlcommand"):
        try:
            match type.lower():
                case "sqlcommand":
                    self.dbadm_logging_sqlcommand = status
                case "sysinfo":
                    self.dbadm_logging_sysinfo = status
                case _:
                    pass

            self.sys_info("database.sys_logging_set",f"set: type={type}, status={str(status)} - settings: for execote_command={str(self.dbadm_logging_sqlcommand)}, for sysinfo={str(self.dbadm_logging_sysinfo)}")

            return True

        except Exception as err:
            self.sys_error("database.sys_logging_set", "", 71, err, False)

    def sys_database_info_get(self):
        try:
            data = self.execute_sqlcommand(sqlcommand = self.dbadm_session_info_query, iscommit = False, logging = "no")
            for row in data:
                self.current_database = row["current_database"]
                self.current_user_username = row["current_user"]
                self.current_database_version = row["version"]
                self.session_id = row["sid"]

        except Exception as err:
            self.sys_error("database.sys_database_info_get", "", 79, err)

    def sys_database_info_show(self, screen: bool = False):
        ili = {"version": f"{self.current_database_version}", "database": f"{self.current_database}",
               "schema": f"{self.current_schema}",
               "user": f"{self.current_user_username}",
                "sid": f"{self.session_id}"
               }
        if screen:
            tli = ""
            for i in ili:
                tli = (f"{tli}{i}: {ili[i]} / ")
            print(f"{82*"-"}\n{tli[:-3]}\n{82*"-"}")
        return ili

    def sys_attribute_show(self):
        print(f"--- key : value --------------------------------")
        for key, value in sorted(self.__dict__.items()):
            print(f"{key}: {value}")
        print(f"--- end ----------------------------------------")
        return True

    def sys_dbadm_log(self,modul: str = "", message: str = "", parameters: str = "", step: str = "", status_code: str = "INFO", sqlcommand: str = "", error_number: int = 0, error_message: str = "" , islogging: bool = True):
        try:
            if self.dbadm_logging_sysinfo and islogging:
                str_message = str(message).replace("'", "''")
                str_error_message = str(error_message).replace("'", "''")
                str_err_sqlcommand = str(sqlcommand).replace("'", "''")
                str_error_number = str(error_number).replace("0", "")
                sqlcommlog = f"""
                    INSERT INTO {self.dbadm_syslog_table}
                    (database_type,database_name,sid,user_name,schema_name,modul_code,message,parameters,step_code
                    ,status_code,sql_command,error_number,error_message)
                    VALUES
                    ('{self.current_database_model}','{self.current_database}','{self.session_id}','{self.current_user_username}','{self.current_schema}','{modul}','{str_message}','{parameters}','{step}'
                    ,'{status_code}','{str_err_sqlcommand}','{str_error_number}','{str_error_message}')
                    """
                sqlcommlog = sqlcommlog.replace(",''", ",null")
                cur_log = self.conn.cursor()
                cur_log.execute(sqlcommlog)
                cur_log.close()
                self.conn.commit()
            return True

        except Exception as err:
            print(f"{68*"*"}\nERROR: database.sys_dbadm_log [80] - {err}\n-- sqlcommand ----------------------------------\n{sqlcommlog}'\n{68*"*"}")
            sys.exit(80)

    def execute_sqlcommand(self,sqlcommand: str, iscommit: bool = True, logging: str = "auto"):
        try:


            data = None
            """ only for PostgreSQL
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur_sqlcommand:
                cur_sqlcommand.execute(sqlcommand)
                data = cur_sqlcommand.fetchall()
            cur_sqlcommand.close()
            self.conn.commit()
            """

            finalcommit=iscommit

            cur = self.conn.cursor()
            cur.execute(sqlcommand)

            if sqlcommand.lower().split()[0] == "select":

                finalcommit=False

                columns = [col[0].lower() for col in cur.description]

                data = [
                    dict(zip(columns, row))
                    for row in cur.fetchall()
                ]

            cur.close()

            if finalcommit:
                self.conn.commit()

            sqlparameters=f"commit/finalcommit is {str(iscommit).lower()}/{str(finalcommit).lower()} - logging is {logging.lower()} - set dbadm_logging_sqlcommand is {str(self.dbadm_logging_sqlcommand)}"
            sqlcommand69=f"{sqlcommand[:69] + ("..." if len(sqlcommand) > 69 else "")}"

            if (logging.lower()=="yes" or (logging.lower()=="auto" and self.dbadm_logging_sqlcommand)):
                self.sys_info("database.execute_sqlcommand", sqlcommand69, True, True, False, sqlparameters, sqlcommand)

            return data

        except Exception as err:
            cur.close()
            self.conn.rollback()
            self.sys_error("database.execute_sqlcommand", sqlcommand69, 70, err, False, True, True, True, sqlparameters, sqlcommand)





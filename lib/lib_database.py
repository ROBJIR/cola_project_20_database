# created: 2026-06-16 10:43
# robert.jiranek@gmail.com
#
# lib_database.lib
#
import sys

import psycopg2
from psycopg2.extras import RealDictCursor
import oracledb
from configparser import ConfigParser

class Database ():
    def __init__(self):
        self.dbadm_logging_sysinfo = self.get_database_cfg("databases.cfg","logging","logging_sysinfo").lower() == "true"
        self.dbadm_logging_sqlcommand = self.get_database_cfg( "databases.cfg","logging","logging_sqlcommand").lower() == "true"
        self.dbadm_syslog_table_name = ""
        self.dbadm_session_info_query = ""
        self.info_current_database = ""
        self.info_session_id = 0
        self.info_current_user = ""
        self.info_current_schema = ""
        self.info_database_version = ""

    # loading values from the configuration file
    def error_message(self,modul: str= "??", errorno: int = 0, err: str="", type: str = "error", output: str="scr", sysexit: bool=True, dbsname: str = "??"):

        if self.info_current_database:
            dbsname=self.info_current_database
        elif self.cfg_database:
            dbsname=self.cfg_database
        else:
            dbsname = '??'

        if "scr" in output.lower():
            print(f"\n-> {dbsname} - {type} [{errorno}] - {modul} -  {err}\n")

        if sysexit:
            sys.exit(errorno)


    # loading values from the configuration file
    def get_database_cfg(self,filename:str,section:str,key:str):
        filename=f"./cfg/{filename}"
        cfgfile = ConfigParser()
        cfgfile.read(filename)
        cfgparameter = cfgfile[section][key]
        if cfgparameter.startswith('"') and cfgparameter.endswith('"'):
            cfgparameter = cfgparameter[1:-1]
        return cfgparameter

    def connect(self,connection: str = ""):
        try:
            # loading connectins parameters from the configuration file connections.cfg
            if connection.lower() == "":
                self.cfg_connection = self.get_database_cfg("connections.cfg","connections","default_connection")
            else:
                self.cfg_connection = connection.lower()
            self.cfg_client_type = self.get_database_cfg("connections.cfg",self.cfg_connection,"client_type")
            self.cfg_host = self.get_database_cfg("connections.cfg",self.cfg_connection,"host")
            self.cfg_port = self.get_database_cfg("connections.cfg",self.cfg_connection,"port")
            self.cfg_database = self.get_database_cfg("connections.cfg",self.cfg_connection,"database")
            self.cfg_user = self.get_database_cfg("connections.cfg",self.cfg_connection,"user")
            self.cfg_password = self.get_database_cfg("connections.cfg",self.cfg_connection,"password")
            self.cfg_schema = self.get_database_cfg("connections.cfg",self.cfg_connection,"schema")

            # select connector according to database type
            self.info_database_details = f"client type={self.cfg_client_type}\nhost:port={self.cfg_host}:{self.cfg_port}\ndatabase={self.cfg_database}\nuser={self.cfg_user} / pwd=***"

            match self.cfg_client_type:
                case "postgresql":

                    self.dbadm_session_info_query = self.get_database_cfg("databases.cfg", "postgresql", "dbadm_session_info_query").replace(";", "")
                    self.dbadm_syslog_table_name = self.get_database_cfg("databases.cfg", "postgresql","dbadm_syslog_table_name")

                    db_conn = psycopg2.connect(
                        host=self.cfg_host,
                        port=self.cfg_port,
                        database=self.cfg_database,
                        user=self.cfg_user,
                        password=self.cfg_password
                    )
                case "oracle":

                    self.dbadm_session_info_query = self.get_database_cfg("databases.cfg", "oracle", "dbadm_session_info_query").replace(";", "")
                    self.dbadm_syslog_table_name = self.get_database_cfg("databases.cfg", "oracle", "dbadm_syslog_table_name")

                    # set Thin or thick mode for client
                    if self.get_database_cfg("databases.cfg",self.cfg_client_type,"lib_dir") != "":
                        oracledb.init_oracle_client(lib_dir=self.get_database_cfg("databases.cfg",self.cfg_client_type,"lib_dir"))

                    db_conn = oracledb.connect(
                        host=self.cfg_host,
                        port=self.cfg_port,
                        service_name=self.cfg_database,
                        user = self.cfg_user,
                        password = self.cfg_password
                    )
                    # write ditails about datababse, database client ... into  self.info_database_details
                    if oracledb.is_thin_mode():
                        self.info_database_details = self.info_database_details+f"\nthin client version: {oracledb.__version__}"
                    else:
                        self.info_database_details = self.info_database_details + f"\nthick client version {oracledb.clientversion()} on path: {self.get_database_cfg("databases.cfg",self.cfg_client_type,"lib_dir")}"

                case _:
                    self.error_message(modul="connect", errorno=72, err=f"database type {self.cfg_client_type} is not supported!")

            # connet to datababse
            self.conn = db_conn
            # get database
            self.dbadm_database_info_get()
            # log
            self.dbadm_log(modul_code="database.connect",parameter=f"{self.info_database_details}")

            # print(f"\n-> {self.cfg_database} - connect to database successfull")
            # print(f"database details \n{self.info_database_details}")

            # set schema in datababse
            self.schema_set(self.cfg_schema)

            return db_conn

        except Exception as err:
            print(f"\n-> {self.cfg_database} - [71] - connection error: {err}\n")
            self.error_message(modul="connect",errorno=71,err=err)


    def close(self):
        try:
            self.dbadm_log(modul_code="database.close", parameter=f"close database: {self.cfg_database}")
            self.conn.close()
            return True

        except Exception as err:
            self.error_message(modul="database.close", errorno=79, err=err)

    def schema_set(self, schema: str):
        try:
            if schema != "":
                match self.cfg_client_type:
                    case "postgresql":
                        sqlcommand = f"SET search_path TO {schema}"
                    case "oracle":
                        sqlcommand = f"ALTER SESSION SET CURRENT_SCHEMA = {schema}"
                    case _:
                        self.error_message(modul="connect", errorno=74, err=f"database type {self.cfg_client_type} is not supported!")

                cur = self.conn.cursor()
                cur.execute(sqlcommand)
                self.conn.commit()
                cur.close()
                self.info_current_schema = schema
                self.dbadm_log(modul_code="database.set_schema",parameter=f"set schema to {schema}",sqlcommand=sqlcommand)
                # print(f"\n-> switch default schema to {schema}\n")
            return True

        except Exception as err:
            self.dbadm_log(modul_code="database.schema_set",parameter=f"set schema to {schema}",status_code="ERROR",sqlcommand=sqlcommand,error_number=75, error_message=err)
            self.error_message(modul="database.schema_set", errorno=75,err=err)

    def schema_get(self):
        try:
            sqlcommand=f"SELECT current_schema()"
            match self.cfg_client_type:
                case "postgresql":
                    sqlcommand=f"SELECT current_schema()"
                case "oracle":
                    sqlcommand=f"SELECT SYS_CONTEXT ('USERENV', 'SESSION_USER') FROM dual"
                case _:
                    self.error_message(modul="database.schema_get", errorno=76, err=f"database type {self.cfg_client_type} is not supported!")

            cur = self.conn.cursor()
            cur.execute(sqlcommand)
            schema = cur.fetchone()[0]
            cur.close()
            # print(f"\n-> default schema si {schema}\n")
            return schema

        except Exception as err:
            self.dbadm_log(modul_code="database.schema_get",status_code="ERROR",sqlcommand=sqlcommand,error_number=77, error_message=err)
            self.error_message(modul="database.schema_set", errorno=77,err=err)

    def dbadm_database_info_get(self):
        try:
            data = self.execute_sqlcommand(sqlcommand = self.dbadm_session_info_query, islogging="no")
            for row in data:
                self.info_current_database = row["current_database"]
                self.info_current_user = row["current_user"]
                self.info_database_version = row["version"]
                self.info_session_id = row["sid"]

        except Exception as err:
            self.error_message(modul="database.schema_set", errorno=78,err=err)

    def dbadm_database_info_show(self):
        print(f"\n{92*"-"}\ndatabase: {self.info_current_database} | schema: {self.info_current_schema} | pid: {self.info_session_id}  | user: {self.info_current_user} | {self.info_database_version}\n{92*"-"}\n")

    def dbadm_logging_set(self,status: bool = True, type: str = "sqlcommand"):
        if type == "sqlcommand":
            self.dbadm_logging_sqlcommand = status
        elif status == "sysinfo":
            self.dbadm_logging_sysinfo = status
        else:
            pass
        print (f"--> set: type={type}, status={str(status)} - settings: for execote_command={str(self.dbadm_logging_sqlcommand)}, for sysinfo={str(self.dbadm_logging_sysinfo)}")
        return True

    def dbadm_log(self,modul_code: str = "", parameter: str = "", step_code: str = "", status_code: str = "SUCCESS", sqlcommand: str = "", error_number: int = 0, error_message: str = "" , islogging: bool = True):
        try:
            if self.dbadm_logging_sysinfo and islogging:
                if type(error_message) != "str":
                    str_err_message = str(error_message)
                str_err_message = str(error_message).replace("'", "''")
                str_err_sqlcommand = str(sqlcommand).replace("'", "''")
                sqlcommlog = f"""
                            INSERT INTO {self.dbadm_syslog_table_name}
                            (database_type,database_name,sid,user_name,schema_name,modul_code,parameter,step_code
                            ,status_code,sql_command,error_number,error_message)
                            VALUES
                            ('{self.cfg_client_type}','{self.info_current_database}',{self.info_session_id},'{self.info_current_user}','{self.info_current_schema}','{modul_code}','{parameter}','{step_code}'
                            ,'{status_code}','{str_err_sqlcommand}',{error_number},'{str_err_message}')
                            """

                cur_log = self.conn.cursor()
                cur_log.execute(sqlcommlog)
                cur_log.close()
                self.conn.commit()
            return True

        except Exception as err:
            self.error_message(modul="database.schema_set", errorno=78, err=err)

    def execute_sqlcommand(self,sqlcommand: str, iscommit: bool = False, islogging: str = "auto"):
        try:
            data = None
            """ only for PostgreSQL
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur_sqlcommand:
                cur_sqlcommand.execute(sqlcommand)
                data = cur_sqlcommand.fetchall()
            cur_sqlcommand.close()
            self.conn.commit()
            """

            cur = self.conn.cursor()
            cur.execute(sqlcommand)

            columns = [col[0].lower() for col in cur.description]

            data = [
                dict(zip(columns, row))
                for row in cur.fetchall()
            ]
            if iscommit:
                self.conn.commit()

            if islogging.lower()=="yes":
                self.dbadm_log(modul_code="database.execute_sqlcommand",
                               parameter=f"is commit: {str(iscommit).lower()}", sqlcommand=sqlcommand, islogging=True)
            elif islogging.lower()=="auto":
                if self.dbadm_logging_sqlcommand:
                    self.dbadm_log(modul_code="database.execute_sqlcommand",
                               parameter=f"is commit: {str(iscommit).lower()}", sqlcommand=sqlcommand, islogging=True)
            else:
                pass

            return data

        except Exception as err:
            cur.close()
            self.conn.rollback()
            self.dbadm_log(modul_code="database.execute_sqlcommand",status_code="ERROR",parameter=f"is commit: {str(iscommit).lower()} / is logging: {str(islogging).lower()}",sqlcommand=sqlcommand,error_number=80,error_message=err)
            self.error_message(modul="database.schema_set", errorno=80, err=err)

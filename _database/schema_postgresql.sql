#
# connect to postgres
sudo -u postgres psql

\du

# init settings for database
#
# create role
CREATE ROLE robert WITH LOGIN PASSWORD '<pwd>';
# create user
ALTER USER robert WITH PASSWORD '<pwd>';

ALTER ROLE robert CREATEDB;
ALTER ROLE robert SUPERUSER;
ALTER ROLE robert CREATEROLE;

CREATE DATABASE robert OWNER robert;
GRANT ALL PRIVILEGES ON DATABASE robert TO robert;

# test connection on Ubuntu
psql -U robert -d robert -W <pwd>

# create CASSIOPEIADB database
CREATE ROLE cassiopeia WITH LOGIN PASSWORD '<pwd>';
ALTER ROLE cassiopeia CREATEDB;
ALTER ROLE cassiopeia CREATEROLE;

ALTER ROLE cassiopeia  SET search_path TO cassiopeia;

CREATE DATABASE cassiopeiaDB OWNER cassiopeia;
GRANT CONNECT ON DATABASE cassiopeiaDB TO cassiopeia;
GRANT ALL PRIVILEGES ON DATABASE cassiopeiadb TO cassiopeia;

ALTER USER cassiopeia WITH PASSWORD '<pwd>';

# test connection on Ubuntu
psql -U cassiopeia -d cassiopeiadb -W <pwd>

# create schemas
#
create schema dbadm;
create schema alpha;
create schema beta;
create schema gama;
create schema delta;

# table DBADM.SYS_LOG

DROP TABLE dbadm.sys_log;
CREATE TABLE dbadm.sys_log (
	timepoint timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	database_type varchar(126) NULL,
	database_name varchar(126) NULL,
	sid int4 NULL,
	pid int4 NULL,
	user_name varchar(126) NULL,
	schema_name varchar(126) NULL,
	modul_code varchar(126) NULL,
	"parameter" varchar(4000) NULL,
	step_code varchar(126) NULL,
	status_code varchar(48) DEFAULT 'SUCCESS'::character varying NULL,
	sql_command text NULL,
	error_number int4 NULL,
	error_message text NULL,
	id serial4 NOT NULL,
	CONSTRAINT sys_log_pk PRIMARY KEY (id)
);

# create view DBADM.SESSION_INFO_V
drop view dbadm.session_info_v;
create or replace view dbadm.session_info_v
as
SELECT current_database() as current_database,
       current_user as current_user,
       substr(version(),1,position('(' in version())-1) as version,
       pg_backend_pid() as sid;



# created: 2026-06-13 12:00
# robert.jiranek@gmail.com
#
# cola_project_20_database
#

import sys

# my librares
from lib.lib_database import Database

# main body
try:
    print(f"{92 * "="}")
    #
    dbs = Database()
    # dbs.connect()

    # _ALL databases_
    # dbs.connect("cassiopeia")
    # dbs.connect("library_db")
    # dbs.connect('ora26free')
    # dbs.connect('alb_ora_mon2db')

    # postgreSQL databases:
    # dbs.connect("cassiopeia")
    # dbs.connect("library_db")
    # Oracle Datababse
    # dbs.connect('ora26free')
    # dbs.connect('alb_ora_mon2db')

    dbs.connect()
    dbs.dbadm_database_info_show()
    # dbs.close()
    #
    # ... tady muzeme neco delat s databazi ...
    #
    #
    # sqlcommand = "SELECT name, id FROM author ORDER BY name"
    # print (f"command: {sqlcommand}")
    print(f"*** Authors: {20*"*"}")
    data = dbs.execute_sqlcommand("SELECT name, id FROM author ORDER BY name")
    for row in data:
        print(f"* {row["name"]} [{row["id"]}]")

    dbs.close()

    #ora = database()
    #ora.connect('ora26free')
    #ora.dbadm_database_info_show()
    #ora.close()
    #
    print(f"{92*"="}")

except Exception as err:
    print(f"ERROR: {err}")
    sys.exit(22)
# created: 2026-06-13 12:00
# robert.jiranek@gmail.com
#
# cola_project_20_database
#
import sys
# my librares
from lib.lib_database_20 import *


# main body
try:

    print(f"{92 * "="}")

    dbs = Database()
    # dbs.sys_attribute_show()
    dbs.connect()
    dbs.sys_database_info_show(True)
    # dbs.dbadm_database_info_show("show")

    data = dbs.execute_sqlcommand("SELECT ranking, mountain_name, elevation_meters, mountain_range, countries FROM alpha.mountain_8000 WHERE ranking<3 ORDER BY ranking")
    for row in data:
        print(f"{row["ranking"]}/ {row["mountain_name"]} - {row["elevation_meters"]}m.n.m - mountains {row["mountain_range"]} in country {row["countries"]}")
    #
    # dbs.close()
    #dbs.sys_attribute_show()
    dbs.close()
    print(f"{92*"="}")

except Exception as err:
    print(f"ERROR: {err}")
    sys.exit(22)
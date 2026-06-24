# created: 2026-06-13 12:00
# robert.jiranek@gmail.com
#
# cola_project_20_database
#
import sys
from configparser import ConfigParser
# my librares
from lib.lib_config_file import ConfigurationFile
from lib.lib_database_20 import *
from lib.lib_log import *
# from lib.lib_compare_data import CompareTables

# main body


print(f"{92 * "="}")

dbs = Database()
# dbs.sys_attribute_show()
dbs.connect()
dbs.sys_database_info_show(True)
# dbs.dbadm_database_info_show("show")

data = dbs.execute_sqlcommand("SELECT ranking, mountain_name, elevation_meters FROM alpha.mountain_8000 WHERE ranking<4 ORDER BY ranking")
# print (data)
print (type(data))
html=""
html=f"{html}<table>\n"
html=f"{html}  <tr>\n"
for tabheader in data[0].keys():
    html=f"{html}    <th>{tabheader}</th>\n"
html=f"{html}  </tr>\n"
html=f"{html}  <tr>\n"
for row in data:
    for key, value in row.items():
        match key
            case "mountain_name":
                f"{html}    <td><strong>{value}</strong></td>\n"
            case _:
                f"{html}    <td>{value}</td>\n"

html=f"{html}  </tr>\n"
html=f"{html}</table>\n"
print(html)
    # print(f"{row["ranking"]}/ {row["mountain_name"]} - {row["elevation_meters"]}m.n.m - mountains {row["mountain_range"]} in country {row["countries"]}")
#
# dbs.close()
# dbs.sys_attribute_show()
dbs.close()
print(f"{92*"="}")


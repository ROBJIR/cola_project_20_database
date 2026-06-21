
import sys
import logging

logging.basicConfig(
    filename='log/tst.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def error_message(log_err):
    # log into file

    # logging.error(str(err))
    logging.exception("ERRR")
    # logging.error("moje zprava")

    # formated meessage on screen
    print(f"error: {err}")
    return True

try:

    x = 10/0

except Exception as err:
    # logging.error(str(err))
    error_message(err)
    sys.exit(22)
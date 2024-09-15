import os
import getpass

user = os.environ.get("PYTHON_USER", "admin")

dsn = os.environ.get("PYTHON_CONNECT_STRING", "127.0.0.1:1522/FREE")


pw = os.environ.get("PYTHON_PASSWORD")
if pw is None:
    pw = getpass.getpass("Enter password for %s: " % user)

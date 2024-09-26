import os
import getpass

user = os.environ.get("PYTHON_USER", "admin")

dsn = os.environ.get("PYTHON_CONNECT_STRING", "127.0.0.1:1522/FREE")


pw = os.environ.get("PYTHON_XXXXXX")
if pw is None:
    pw = getpass.getpass("Enter XXXXXX for %s: " % user)

rabbitmq_host = os.environ.get("rabbitmq_host", '127.0.0.1')
rabbitmq_port = os.environ.get("rabbitmq_port", "5672")
rabbitmq_user = os.environ.get("rabbitmq_user", "arul")
rabbitmq_XXXXXX = os.environ.get("rabbitmq_password", "XXXXXX")


pg_host = os.environ.get("pg_host", "127.0.0.1")
pg_port = os.environ.get("pg_port", "5432")
pg_database = os.environ.get("pg_database","postgres")
pg_user = os.environ.get("pg_user", "arul")
pg_XXXXXX = os.environ.get("pg_password", "XXXXXX")


MODEL = os.environ.get("MODEL", "llama3.1")
LLM_URL = os.environ.get("LLM_URL", "http://localhost:11434")

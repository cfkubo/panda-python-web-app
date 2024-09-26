# panda-python-web-app

<p align="center">
<img src="templates/panda.png" width="800" alt="Online Web Application" />
</p>


# Requirements:
1. postgres db to run the postgres project
2. oracle db to run the oracle project
3. Rabbitmq to run the data generator and loaders project.



# Running the Oracle Project:
1. linux vm to run oracle docker image
2. Deploy an oracle db using docker
```
docker run -d -p 1521:1521 -e ORACLE_PASSWORD=XXXXX -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe
```

# Panda-Company-feature
1. Provides data generator that genrates random data for various jobs
2. Provides data loaders that can load the data to postgres db


<p align="center">
<img src="static/panda-arch.png" width="800" alt="Online Web Application" />
</p>

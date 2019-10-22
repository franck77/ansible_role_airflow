Role Name
=========

This repository contains Ansible roles and examples playbooks to install Airflow Server on Linux System

| Redhat | CentOs | Ubuntu               |
|--------|--------|----------------------|
| V      | V      | V (bug with systemd) |

Requirements
------------

No special requirements; note that this role requires root access, so either run it in a playbook with a global become: yes, or invoke the role in your playbook like:
```
- hosts: airflow_host
  roles:
    - role: role_ariflow
      become: true
```

Note: If you want use Postgresql for Airflow's backend, you have to install Postgresql in prerequisites.

Role Variables
--------------

Available variables are listed below : 

Defaults variables :

```
role_airflow_pip_version: Pip version installed and used

role_airflow_systemd_dir: Directory where the service systemd file are hosted
role_airflow_root_dir: Directory where airflow will be installed - By default, this path is the airflow's home directory
role_airflow_database_path: Path to the sqlite database - If you use another database, it's useless
role_airflow_bin_airflow: Path to airflow binary

role_airflow_executor_type: Executor type - Sequential Executor by default
role_airflow_database_type: Database used - By default is sqlite
role_airflow_broker: Information on the broker - By default is sqlite
role_airflow_backend: Information on the database backend - sqlite by default
role_airflow_ssl: Security information with certificats - desactivated by default
role_airflow_load_examples: Dags examples includes - By default they are included
role_airflow_log_fetch_timeout_sec: "5"
```

Variables setted :

```
role_airflow_packages_requirements_redhat: Packages requirements for Redhat / Centos
role_airflow_python_packages: Python packages requirements


role_airflow_cfg_file: Path to the Airflow configuration file 
role_airflow_dags_dir: Path to dags directory
role_airflow_plugins_dir: Path to plugins directory
role_airflow_run_dir: Path to run directory

role_airflow_logs_dir: Path to Airflow's logs directory
role_airflow_logs_webserver_dir: Webserver logs directory
role_airflow_logs_webserver_error_file: Webserver error log file
role_airflow_logs_webserver_access_file: Webserver log file
role_airflow_logs_worker_dir: Worker logs directory
role_airflow_logs_worker_log: Worker log file
role_airflow_logs_worker_log_stdout: Worker stdout log file
role_airflow_logs_worker_log_stderr: Worker error log file
role_airflow_logs_scheduler_dir: Scheduler logs directory 
role_airflow_logs_scheduler_log: SCheduler log file
role_airflow_logs_scheduler_log_stdout: Scheduler stdout log file
role_airflow_logs_scheduler_log_stderr: Scheduler error log file
role_airflow_logs_test_scripts: Directory where the dags deployed will be tested
```

Dependencies
------------

By default none.

Example Playbook
----------------

If you want install airflow in localhost to test with default vars, you can use the playbook in playbook/simple/main.yml and run it with the following command :
```
ansible-playbook ./playbook/simple/main.yml -i ./playbook/simple/my_inventory.yml -e "state=role_airlow_whole_install"
```

If you want install airflow in localhost with specific backend (Postgresql + Rabbitmq + Celery), you can use the playbook in playbook/postgresql_rabbitmq_celery/main.yml and run it with the following command :
```
ansible-playbook ./playbook/postgresql_rabbitmq_celery/install.yml -i ./playbook/postgresql_rabbitmq_celery/my_inventory.yml -e "env=local"
```

License
-------

Keyrus

Author Information
------------------

Badr Bakkou, Antoine Deblonde & Franck Vieira

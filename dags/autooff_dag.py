from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import boto3
import logging



def create_logger(logfile='') :

	""" this function create a nice logger object """

	if logfile == '' :
		logfile = os.getcwd()
		logfile = os.path.join(logfile,'autooff_dag.log')

	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	# create a file handler
	handler = logging.FileHandler(logfile)
	handler.setLevel(logging.INFO)

	# create a console handler
	stdout_handler = logging.StreamHandler(sys.stdout)
	stdout_handler.setLevel(logging.INFO)

	# create a logging format
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)

	# add the handlers to the logger
	logger.addHandler(handler)
	logger.addHandler(stdout_handler)

	logger.info('Logger created')

	return logger

def temp_credentials_for_role(logger, aws_user_creds, role_arn, direct_login) :

	""" this function creates temporary AWS API keys for the role_arn, provided user credentials associated with this role """
	if direct_login :
		client = boto3.client("sts",
		region_name=aws_user_creds['aws_region'])
	else :
		client = boto3.client('sts', 
			aws_access_key_id=aws_user_creds['aws_acces_key_id'],
			aws_secret_access_key=aws_user_creds['aws_secret_access_key'],
			region_name=aws_user_creds['aws_region']
		)

	temp_creds = client.assume_role(
		RoleArn = role_arn,
		RoleSessionName = 'S3_downloading',
		DurationSeconds = 3600
	)

	aws_temp_creds = {
		'aws_acces_key_id' : temp_creds['Credentials']['AccessKeyId'],
		'aws_secret_access_key' : temp_creds['Credentials']['SecretAccessKey'],
		'aws_session_token' : temp_creds['Credentials']['SessionToken'],
		'aws_region' : aws_user_creds['aws_region']
	}

	return aws_temp_creds

def create_s3_connection(logger, aws_creds) :

	""" this function create the S3 connection client associated with AWS creds """

	client = boto3.client(
		's3',
		aws_access_key_id=aws_creds['aws_acces_key_id'],
		aws_secret_access_key=aws_creds['aws_secret_access_key'],
		aws_session_token=aws_creds['aws_session_token'],
		region_name=aws_creds['aws_region']
	)

	return client

def create_ec2_client(logger, aws_creds) :

	""" this function create the EC2 connection client associated with AWS creds """

	client = boto3.client(
		'ec2',
		aws_access_key_id=aws_creds['aws_acces_key_id'],
		aws_secret_access_key=aws_creds['aws_secret_access_key'],
		aws_session_token=aws_creds['aws_session_token'],
		region_name=aws_creds['aws_region']
	)

	return client

def main(aws_acces_key_id, aws_secret_access_key, aws_region, role_arn, direct_login=False) :

	logger = create_logger('{{ role_airflow_logs_test_scripts }}/autooff_dag.log')

	aws_creds = {
		'aws_acces_key_id' : aws_acces_key_id,
		'aws_secret_access_key' : aws_secret_access_key,
		'aws_region' : aws_region,
		'aws_session_token' : None
	}

	ec2_client = create_ec2_client(logger, aws_creds)

	# s3_client = create_s3_connection(logger, aws_creds)

	logger.info("Created EC2 client")

	running_instances = ec2_client.describe_instances(
		Filters=[
			{'Name': 'instance-state-name', 'Values': ['running']}
		]
	)
	logger.info("Listing EC2 instances")

	logger.info("Shutting down AutoOff instances")
	for reservation in running_instances['Reservations'] :
		for instance in reservation['Instances'] :
			if 'Tags' in instance.keys() :
				instance_name = "none"
				do_stop = False
				for tag in instance['Tags']:
					if (tag['Key'] == 'AutoOff') & (tag['Value'] == 'True') :
						do_stop = True
					if (tag['Key'] == 'Name') :
						instance_name = tag['Value']
				if do_stop == True :
					ec2_client.stop_instances(InstanceIds=[instance['InstanceId']])
					logger.info("Instance %s, ID %s stopped" % (instance_name, instance['InstanceId']))

	logger.info("Finished shutting down AutoOff instances")

default_args = {
	'owner': 'airflow',
	'depends_on_past': False,
	'start_date': datetime(2019, 7, 22, 19, 0),
	'email': ['airflow@example.com'],
	'email_on_failure': False,
	'email_on_retry': False,
	'retries': 0,
	'retry_delay': timedelta(minutes=5),
	'concurrency' : 1
	# 'queue': 'bash_queue',
	# 'pool': 'backfill',
	# 'priority_weight': 10,
	# 'end_date': datetime(2016, 1, 1),
}

with DAG('instances_auto_off',
	catchup=False,
	default_args=default_args,
	schedule_interval="0 17 * * *"
	) as dag :
	opr_startup = PythonOperator(
		task_id='shutdown', 
		python_callable=main,
		op_kwargs={
			'aws_acces_key_id': '{{ aws_access_key_id }}',
			'aws_secret_access_key': '{{ aws_secret_key }}',
			'aws_region' : '{{ aws_region }}',
			'role_arn' : '{{ aws_role_arn }}',
			'direct_login' : True
		}
	)
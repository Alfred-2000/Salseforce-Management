# SALSEFORCE-MANAGEMENT
#Execute inside postgresql to create database:
---------------------------------------------------------------------------------
DROP DATABASE IF EXISTS salseforce;
CREATE DATABASE salseforce;
CREATE USER salseforceuser WITH PASSWORD 'password';
ALTER ROLE salseforceuser SET client_encoding TO 'utf8';
ALTER DATABASE salseforce SET timezone TO 'Asia/Kolkata';
ALTER ROLE salseforceuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE salseforceuser SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE salseforce TO salseforceuser;
\c salseforce
GRANT CREATE ON SCHEMA public TO salseforceuser;


#Create virtual environment and activate it:
---------------------------------------------------------------------------------
python3 -m venv virtual-env

source virtual-env/bin/activate

pip install -r requirements.txt


#Create django project:
---------------------------------------------------------------------------------
django-admin startproject salseforce


#Create django app:
---------------------------------------------------------------------------------
python manage.py startapp accounts


---------------------------------------------------------------------------------
for x in accounts; do rm -rf $x/migrations; mkdir $x/migrations; touch $x/migrations/__init__.py; done

python manage.py makemigrations

python manage.py migrate

python manage.py runserver


---------------------------------------------------------------------------------


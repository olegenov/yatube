# yatube
yatube
![CI](https://github.com/olegenov/yatube/workflows/CI/badge.svg?branch=master&event=push)

# **FOODGRAM**
### Social networking site gor bloggers.

#### Deploy locally:
* create an environment
``` python3 -m venv venv ```
* run the environment
``` source venv/bin/activate ```
* install requirement files
``` python3 -m pip install -r requirements.txt ```
* make migrations
``` python3 manage.py makemigrstions ```
``` python3 manage.py migrate ```
* go http:\\127.0.0.1:8000

#### Create a superuser:
* run
``` python3 manage.py createsuperuser ```

# Projet_WEB


## Project
Website for navigating on genome, protein and cds.

## Prerequisite
```
samtools
virtualenv
```


## Installation
Start by installing the environment: `bash install-virtual-env.sh`  
Activate it: `source .env/bin/activate`  
Load the base data: `python manage.py launch ./downloaded_data/`  
You can now launch the server with: `python manage.py runserver`
## Virtual environment
Our virtual environment consist of : 
```
asgiref==3.7.2
biopython==1.79
black==23.12.1
click==8.1.7
crispy-bootstrap5==2023.10
Django==5.0
django-stubs==4.2.7
django-stubs-ext==4.2.7
django-crispy-forms==2.1
django-phonenumber-field[phonenumberslite]
flake8==7.0.0
mccabe==0.7.0
mypy-extensions==1.0.0
numpy==1.23.5
packaging==23.2
pathspec==0.12.1
platformdirs==4.1.0
pycodestyle==2.11.1
pyflakes==3.2.0
sqlparse==0.4.4
types-pytz==2023.3.1.1
types-PyYAML==6.0.12.12
typing_extensions==4.9.0
prody==2.4.1
requests==2.31.0
snipgenie==0.6.0
```

## Config files
**.flake8**  
put the limit to 125 characters a line

**pyproject.toml**  
put the limit to 125 characters to black formater

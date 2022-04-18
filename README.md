# Deploy a Python (Django) web app with PostgreSQL in Azure

This is a Python web app using the Django framework and the Azure Database for PostgreSQL relational database service. The Django app is hosted in a fully managed Azure App Service. This app is designed to be be run locally and then deployed to Azure. For more information on how to use this web app, see the tutorial [*Deploy a Python (Django or Flask) web app with PostgreSQL in Azure*](https://docs.microsoft.com/en-us/azure/app-service/tutorial-python-postgresql-app).

If you need an Azure account, you can [create on for free](https://azure.microsoft.com/free/).

A Flask sample application is also available for the article at https://github.com/Azure-Samples/msdocs-flask-postgresql-sample-app.

## Requirements

The [requirements.txt](./requirements.txt) has the following packages:

| Package | Description |
| ------- | ----------- |
| [Django](https://pypi.org/project/Django/) | Web application framework. |
| [pyscopg2-binary](https://pypi.org/project/psycopg-binary/) | PostgreSQL database adapter for Python. |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Read key-value pairs from .env file and set them as environment variables. In this sample app, those variables describe how to connect to the database locally. <br><br> This package is used in the [manage.py](./manage.py) file to load environment variables. |
| [whitenoise](https://pypi.org/project/whitenoise/) | Static file serving for WSGI applications, used in the deployed app. <br><br> This package is used in the [azureproject/production.py](./azureproject/production.py) file, which configures production settings. |

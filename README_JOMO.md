### Deploy a Python (Django or Flask) web app with PostgreSQL in Azure
- Follow instructions to create a web app and database on Azure
- By the end of the tutorial, my webapp is up and running here: https://msdocs-python-postgres-xyz.azurewebsites.net/
- How to link the github actions project to my local project:
    - browse to the folder of the local git project
    - run this command to see what is linked
        - ```git remote -v```
    - run to link it to github actions project
        - ```git remote set-url origin https://github.com/jomoglobal/msdocs-django-postgresql-sample-app```
- How to create a django admin superuser
    - Start SSH Session with App Service Container
    - run ```python manage.py createsuperuser```
    - login at ```<<webpage>>/admin```
    - my login is ```jomo``` ```jomo```

### Django Project Structure 
Here's a brief explanation of the folders and files in your Django project:
- **CHANGELOG.md, CONTRIBUTING.md, LICENSE.md, README.md:** These files are for documentation purposes. They include the change log, contribution guidelines, license information, and a readme file explaining the project.
- **azure.yaml:** This file is likely related to Azure DevOps CI/CD pipelines or Azure configurations.
- **azureproject:** This is probably your Django project folder. It typically contains settings.py (Django settings), urls.py (project-level URL declarations), and wsgi.py (entry-point for WSGI-compatible web servers).
- **infra:** This folder might contain infrastructure-as-code files, possibly for setting up resources in Azure.
- **manage.py:** A command-line utility that lets you interact with your Django project in various ways (starting the server, running migrations, etc.).
- **requirements.txt:** Lists all Python dependencies of your project. When you set up your project on a new machine, you run pip install -r requirements.txt to install these dependencies.
- **restaurant_review:** This is likely an application within your Django project. Django projects can consist of multiple apps. This folder will contain models, views, templates, and other components of this specific app.
- **screenshot_website.png:** An image file, probably a screenshot of your website.
- **startup.sh:** A shell script used for starting up the application, possibly used in your deployment process.
- **static:** Contains static files like CSS, JavaScript, and images used by your Django application.

### Create a python script that fetches data to populate database
- Create a script called "fetch_azure_data.py" to fetch data from Azure API (put the script in main folder, same as "manage.py")
- Modify template script: https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
- Modify the script to generate a baseline database

### Testing how to view the database files
- Successfully view database detail from ```<<webpage>>/admin```
- Use pgAdmin software
    - Hostname/address: msdocs-python-postgres-xyz-server1.postgres.database.azure.com
    - Port: 5432 (default)
    - Maintenance Database: postgres (default)
    - Username: ytpgamdrbg
    - Password: 60008U8Q7HDYWWSI$
    - I CAN'T CONNECT, PROBABLY DUE TO PUBLIC ACCESS LIMITATIONS


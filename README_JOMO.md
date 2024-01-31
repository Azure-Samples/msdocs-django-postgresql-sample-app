### Deploy a Python (Django or Flask) web app with PostgreSQL in Azure
- Follow instructions to create a web app and database on Azure
- By the end of the tutorial, my webapp is up and running here: https://msdocs-python-postgres-xyz.azurewebsites.net/
- How to link the github actions project to my local project:
    - browse to the folder of the local git project
    - run this command to see what is linked
        - ```git remote -v```
    - run to link it to github actions project
        - ```git remote set-url origin https://github.com/jomoglobal/msdocs-django-postgresql-sample-app```

### Create a python script that fetches data to populate database
- Create a script called "fetch_azure_data.py" to fetch data from Azure API (put the script in main folder, same as "models.py")
- Modify template script: https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices
- Modify the sript to generate different data

### Testing how to view the database files
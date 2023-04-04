# bill_backend
Bill analytics system made using django rest framework and BeautifulSoup

## Dependencies
* Django rest framework
* MongoDB
* BeautifulSoup

## Setup local environment
Run following command in teminal
```powershell
pip install virtualenv

virtualenv venv

venv/Scripts/activate

pip install -r requirements.txt
```
### Setup local database:
Once the requirements are installed we need to setup local database for testing. 
* In order to do this first install MongoDB, Mongosh and MongoDB compass in your system. 
* Once MongoDB is set up connect to you local server. If you have setup you mongoDB for a different port address make sure to change connection string in .env file for "MDB_HOST_DEV".
* Now we need to create a database named "Electricity_bill" and a collection named "bills". Once the database is created we need to migrate our project schema to that database. To do this run following commands in terminal of you project directory. Migrations have already been created for this project. So you don't need to create migrations again.
```powershell
python manage.py migrate
```
If the above command gives an error then please verify the version of pymanogo and djongo
* Now we need to create a superuser for our project. To do this run following command in terminal of your project directory.
```powershell
python manage.py createsuperuser
```
* Now we need to run our project. To do this run following command in terminal of your project directory.
```powershell
python manage.py runserver
```
The server is now up and running in http://localhost:8000/

## API Endpoints
* You can get all the endpoints by Swagger docs integrated in this project. To access the swagger docs go to http://localhost:8000/api/v1/swagger/ in your browser.
* You can also access endpoints docs by going to http://localhost:8000/api/v1/redoc/ in your browser.

## Scrapper:
* The scrapper is a python script which scrapes the data from the website and stores it in the database. To run the scrapper run following command in terminal of your project directory.
```powershell
python bill_app/utils.py
```
* The scrapper is built using BeautifulSoup and requests library. 


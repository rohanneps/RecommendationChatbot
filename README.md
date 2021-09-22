# RECOMMENDATION CHATBOT

This project is a chatbot that recommends products from the **SERP** (Search Engine Results Page) results of marketplaces such as Amazon, Google and Ebay. It uses computer vision and natural language processing to recommend product listing most similar to the input query string-image pair.

## Authors
+ Rohan Man Amatya


## Environment Requirements
+ Python 3.8+
+ beautifulsoup4
+ mysqlclient
+ requests
+ scikit-learn
+ Tensorflow


## Sample
![Sample1](./images/sample1.png)

![Sample2](./images/sample2.png)


## Installation

### Mysql

Install mysql as follows:
```
sudo apt update
sudo apt install mysql-server
```

**Create user and grant privileges to the required database.**

Log the details of the database connection to an .env file

```
# .env file details
DB_NAME=
DB_USER=
DB_PASSWORD=
```

**To install mysqlclient**

```
sudo apt-get install python3.8-dev 
sudo apt-get install mysql-client
sudo apt-get install libmysqlclient-dev
sudo apt-get install libssl-dev
```

### Virtual Environment
**Create virtual environment**
```
python3 -m venv <name_of_virtualenv>
```

**Activate virtual environment**
```
source <name_of_virtualenv>/bin/activate
```

**Install the python dependencies in the virtual environment.**

```
pip install -r requirements.txt
```

### Nltk
```
import nltk
nltk.download('stopwords')
```

### Selenium
To enable selenium webdriver for firefox. Download [geckodriver](https://github.com/mozilla/geckodriver/releases) and place in the **bin** folder of **chatbot** root dir.

### Django

```
# activate virtualenv
python manage.py makemigrations
python manage.py migrate

# create superuser
python manage.py createsuperuser

# collect static files
python manage.py collectstatic
```

## Execution
To start the project. Open a terminal and enter the following commands

### Web Application
```
# activate virtualenv
python manage.py runserver
```

### Celery Worker

Open a new terminal and execute the following command in the root directory.

```
# activate virtualenv
celery -A chatbot worker -l info
```

### Flower
To enable loggig of the asynchronous task. Open a new terminal and execute the following command in the root directory.

```
# activate virtualenv
flower -A chatbot --port=5555
```
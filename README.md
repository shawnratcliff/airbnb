# Los Angeles Airbnb data analysis/visualization app

## Requirements; Getting started

This project uses Python 3 with Virtualenv. To get started, you'll need to clone the repository, setup and activate the virtual environment, and install required packages using pip.

### Step 1: Clone the repo.

    git clone https://github.com/shawnratcliff/airbnb.git

### Step 2: Create a Python 3 virtual environment.

Note: if you are using OS X, the Python executable supplied with the operating system will not work. You'll need to do a separate installation of Python for development purposes. See [Installing Python on Mac OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)

    cd airbnb
    virtualenv -p /path/to/python3 venv # creates virtual env in venv/ 
    source ./venv/bin/activate # activates virtual env for this terminal session

Check that the virtual env is working properly:

    which python # Executable should be located within local project directory
    python --version # Python version 3.5+ expected

### Step 3: Install required pip modules. Remember that you will need to repeat this step each time a new requirement is added to requirements.txt in a future commit.

    pip install -r requirements.txt

**Remember that for each new terminal session, it is necessary to reactivate the virtual environment:**

    source ./venv/bin/activate 
    
### Step 4: Install Postgres.app and create database (local machines only)

This project requires access to a PostgreSQL server. For a local Windows or Mac development machine, the simplest option is to install Postgres.app, which includes the extensions necessary for this project. Remember to set your PATH environment variable as described in the [installation instructions](https://postgresapp.com/). If you are working on the shared server, a database is already available and populated; in this case, skip steps 4 and 5.

After Postgres.app is installed, open psql and create a user and empty database as follows:

    CREATE DATABASE airbnb;
    CREATE USER airbnbuser;
    ALTER USER airbnbuser WITH superuser;
    ALTER USER airbnbuser WITH password '191project';
    GRANT ALL PRIVILEGES ON DATABASE airbnb TO airbnbuser;
    \q

### Step 5: Restore database contents from backup (local machines only)

From the project root, create the backups directory:

    mkdir backups

Download the most recent database backup from Google Drive. Place it in backups/ and decompress it:

    gunzip backups/filename.psql.gz

Apply migrations to establish the correct schema for your new database:

    ./manage.py migrate

Restore the database backup:

    ./manage.py dbrestore

### Step 6: Run the development server

    ./manage.py runserver # Defaults to localhost:8000

## Data API

### Endpoints

The data API is available at [hostname]/api/.
To retrieve a list of all neighborhooods, GET /api/neighborhoods/
To retrieve a list of all Airbnb listings, GET /api/listings/
To retrieve an individual listing, append the id, e.g.: GET /api/listing/33

### Filtering

A JSON query syntax is available to filter list-based requests. Currently, supported filter operations include "numerical_range" and "region". When specifying an attribute name within a filter, be sure to the attribute name as it is declared in main/models.py.

To request filtered data, append /filter/ to the list URL and supply filter parameters in a JSON POST body. For example:

    POST /api/listings/filter/
    {
        'filters': {
            'numerical_range': [
                {
                    'attribute_name': 'price',
                    'min': 175.00,
                    'max': 250.00
                },
                {
                    'attribute_name': 'accommodates',
                    'min': 2,
                    'max': null
                }
            ],
            'region': {
                'region_type': 'neighborhood',
                'id': 35
            }
        }
    }

In this example, we will retrieve only listings that match the following criteria: 1) price between 175-250 per night (inclusive), 2) property accommodates at least 2 people; 3) property is located in Beverly Hills.

Note: your filters object must match the above form exactly, although any particular type of filter is optional and can be omitted. For example, to retrieve all listings in Beverly Hills regardless of other attributes:

    POST /api/listings/filter/
    {
        'filters': {
            'region': {
                'region_type': 'neighborhood',
                'id': 35
            }
        }
    }

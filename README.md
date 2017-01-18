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

### Step 3: Install required pip modules.

    pip install -r requirements.txt

**Remember that for each new terminal session, it is necessary to reactivate the virtual environment:**

    source ./venv/bin/activate 
    

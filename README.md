# Los Angeles Airbnb data analysis/visualization app

## Requirements; Getting started

This project uses Python 3 with Virtualenv. To get started, you'll need to clone the repository, setup and activate the virtual environment, and install required packages using pip.

### Step 1: Clone the repo.

    git clone https://github.com/shawnratcliff/airbnb.git

### Step 2: Create a Python 3 virtual environment.

    cd airbnb
    virtualenv -p python3 venv # creates virtual env in venv/ 
    source ./venv/bin/activate # activates virtual env for this terminal session

Check that the virtual env is working properly:

    which python # Executable should be located within local project directory
    python --version # Python version 3.5.x expected

### Step 3: Install required pip modules.

    pip install -r requirements.txt

**Remember that for each new terminal session, it is necessary to reactivate the virtual environment:**

    source ./venv/bin/activate 
    

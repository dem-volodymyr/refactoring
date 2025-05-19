# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django djangorestframework drf-spectacular

# Create Django project and app
django-admin startproject slot_machine_api
cd slot_machine_api

# Load initial symbols data (after creating fixture)
python manage.py loaddata symbols

# Run the development server
python manage.py runserver
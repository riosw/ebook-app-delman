from setuptools import setup

main_requirements=[
    'werkzeug==2.0.3', # Required because test client throws TypeError: __init__() got an unexpected keyword argument 'as_tuple'
    'Flask==2.0.1',
    'Flask-SQLAlchemy',
    'psycopg2-binary',
    'flask_login',
    'flask_bcrypt',
    'flask-marshmallow',
    'marshmallow-SQLAlchemy',
    'SQLAlchemy_utils',
    'Flask-Migrate',
    'phonenumbers',
    'marshmallow_enum',
]

setup(
    name='ebook-app',
    packages=['flaskr'],
    include_package_data=True,
    install_requires= main_requirements
)
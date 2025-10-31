import sys
from setuptools import setup, find_packages

NAME = "openapi_server"
VERSION = "1.0.0"

# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "connexion>=2.0.2",
    "swagger-ui-bundle>=0.0.2",
    "python_dateutil>=2.6.0"
]

setup(
    name=NAME,
    version=VERSION,
    description="Library Management API",
    author_email="support@library.example.com",
    url="",
    keywords=["OpenAPI", "Library Management API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    package_data={'': ['openapi/openapi.yaml']},
    include_package_data=True,
    entry_points={
        'console_scripts': ['openapi_server=openapi_server.__main__:main']},
    long_description="""\
    A comprehensive library management system API with authentication, book management, and borrowing features.  ## Features - JWT Authentication with access &amp; refresh tokens - HttpOnly Cookie support for enhanced security - Book CRUD operations with search and pagination - Borrowing system with due dates and extensions - Overdue tracking  ## Authentication Most endpoints require JWT authentication. Include the access token in the Authorization header: &#x60;&#x60;&#x60; Authorization: Bearer &lt;access_token&gt; &#x60;&#x60;&#x60; 
    """
)


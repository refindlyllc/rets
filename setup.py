import os
from rets import __version__
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="rets",
    version=__version__,
    packages=["rets"],
    url="https://github.com/homepartners/rets",
    author="REfindly",
    author_email="info@refindly.com",
    description=("RETS Client for Real Estate Data"),
    license="MIT License",
    keywords="rets",
    long_description=read("README.md"),
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests", "xmltodict", "six", "future"],
    dependency_links=[],  # boilerplate for pipenv-setup check
)

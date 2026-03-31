from setuptools import setup, find_packages

setup(
    name = "ndfl-lpn",
    version = "0.0.0",
    long_description="Tax calculator",
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    author="Laptev Pavel",
    author_email="Laptevpavel2007@gmail.com"
)
from setuptools import find_packages
from setuptools import setup

setup(
    name="simple_superhero_service",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["flask", "confuse", "dotenv"],
    extras_require={"test": ["pytest", "coverage"]},
)

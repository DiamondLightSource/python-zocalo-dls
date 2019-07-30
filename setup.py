#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["ispyb", "procrunner", "zocalo"]
setup_requirements = []
test_requirements = ["mock", "pytest"]

setup(
    author="Diamond Light Source",
    author_email="scientificsoftware@diamond.ac.uk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Standard components for automated data processing with Zocalo at Diamond Light Source",
    entry_points={
        "libtbx.precommit": ["zocalo_dls = zocalo_dls"],
        "workflows.service": [
            # to add a service:
            # "user_facing_service_name = zocalo_dls.service.myservice:ServiceClass"
            "ISPyB = zocalo_dls.service.ispybsvc:ISPyB"
        ],
        "zocalo.wrapper": [
            # to add a wrapper:
            # "user_facing_wrapper_name = zocalo_dls.wrapper.mywrapper:WrapperClass"
            "generic_process = zocalo_dls.wrapper.generic:ProcessRegisterWrapper"
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="zocalo dls diamond",
    name="zocalo_dls",
    packages=find_packages(),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/DiamondLightSource/zocalo-python-dls",
    version="0.2.0",
    zip_safe=False,
)

=================
python-zocalo-dls
=================

`Zocalo <https://github.com/DiamondLightSource/python-zocalo/>`_ services and wrappers which can be used across teams at
`Diamond Light Source <https://www.diamond.ac.uk/Home.html/>`_.

There are specialised versions of the services provided by Zocalo, and services
which are useful at Diamond but are not central to Zocalo itself.

Much of the data analysis work at Diamond is directed by and presented to users through `ISPyB <https://ispyb.github.io/ISPyB/>`_.
Therefore, we provide some central services which enable cooperation between the data analysis pipelines and the ISPyB
database at Diamond.

The code in this repository is actively used for processing of `MX data <https://www.diamond.ac.uk/Science/Research/Techniques/Diffraction/MX.htm/>`_
at Diamond.
The hope is that soon it will be used across many areas of science here and perhaps elsewhere.

Please take this code inspiration for how to implement Zocalo at other facilities.

Installation
------------

.. code-block::

    pip install zocalo-dls


This will add several service and wrapper entry points which should appear with:

.. code-block::

    zocalo.service --help
    zocalo.wrap --help


Contributing
------------

This package is maintained by a core team at Diamond Light Source.

To contribute, fork this repository and issue a pull request.

`Pre-commit <https://pre-commit.com//>`_ hooks are provided, please check code against these before submitting.
Install with:

.. code-block::

    pre-commit install

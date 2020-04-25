********************************************************************************
Getting started
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _EPD: https://www.enthought.com/products/epd/

.. highlight:: bash


Installation
============

Released versions of :mod:`compas_pattern` can be installed with *pip*.
With the desired virtual environment activated, do

::

    $ pip install compas-pattern


You can also install directly from the GitHub repo.

::

    $ pip install git+https://github.com/compas-dev/compas_pattern.git


Updates
=======

If you already have :mod:`compas_pattern` installed and you want to upgrade it to the latest version, do

::

    $ pip install compas-pattern --upgrade

|

----


Rhino
=====

:mod:`compas_pattern` is developed independent of the functionality of CAD software.
However, CAD software is still necessary in a computational design environment for visualising and interacting with datastructures and geometrical objects.
For the examples presented in this documentation, `Rhinoceros <https://www.rhino3d.com/>`_ is chosen as the CAD software for user interaction and visualisation of script results.
For a more detailed information on how to install COMPAS and its packages for Rhino, please refer to `Working in Rhino <https://compas-dev.github.io/main/renvironments/rhino.html>`_ page of the COMPAS documentation.

In order to install :mod:`compas_pattern` for Rhino, do

::

    $ python -m compas_rhino.uninstall
    $ python -m compas_rhino.install
    $ python -m compas_rhino.install -p compas_pattern

Every time a new file is opened in Rhino, be sure to reset the Python Scritp Engine before running scripts.


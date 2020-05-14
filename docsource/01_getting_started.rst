********************************************************************************
Getting started
********************************************************************************

.. _Anaconda: https://www.continuum.io/
.. _EPD: https://www.enthought.com/products/epd/

.. highlight:: bash


Installation
============

Released versions of :mod:`compas_singular` can be installed with *pip*.
With the desired virtual environment activated, do

::

    pip install compas_singular


You can also install directly from the GitHub repo.

::

    pip install git+https://github.com/BlockResearchGroup/compas_singular.git


Updates
=======

If you already have :mod:`compas_singular` installed and you want to upgrade it to the latest version, do

::

    pip install compas_singular --upgrade

|

----


Rhino
=====

:mod:`compas_singular` is developed independent of the functionality of CAD software.
However, CAD software is still necessary in a computational design environment for visualising and interacting with datastructures and geometrical objects.
For the examples presented in this documentation, `Rhinoceros <https://www.rhino3d.com/>`_ is chosen as the CAD software for user interaction and visualisation of script results.
For a more detailed information on how to install COMPAS and its packages for Rhino, please refer to `Working in Rhino <https://compas-dev.github.io/main/renvironments/rhino.html>`_ page of the COMPAS documentation.

In order to install :mod:`compas_singular` for Rhino, do

::

    python -m compas_rhino.uninstall
    python -m compas_rhino.install
    python -m compas_rhino.install -p compas_singular

Every time a new file is opened in Rhino, be sure to reset the Python Scritp Engine before running scripts.


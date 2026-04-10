Installation
============

Requirements
------------

* Python 3.11 or later
* PySide6 (Qt6 Python bindings)
* ``jsonpickle``
* ``shapely`` (for universe boundary polygon math)

On Linux, you may also need Qt platform dependencies::

    sudo apt-get install libgl1-mesa-dev libglib2.0-dev

Quick Start
-----------

Clone the repository and install in editable mode::

    git clone <repository-url> stars-reborn
    cd stars-reborn
    pip install -e .

Run the game::

    python stars-reborn.py

Or via the installed entry point::

    stars-reborn

Running Tests
-------------

::

    pip install -e ".[dev]"
    pytest tests/

Building the Docs
-----------------

::

    pip install -e ".[docs]"
    cd docs
    make html
    # Open docs/_build/html/index.html in a browser

Running Under Wine (for analysis)
----------------------------------

The original ``stars.exe`` (Windows 3.x NE format) is included in
``sr-old/original/stars.exe`` for reference and analysis purposes.

To run it under Wine on Linux::

    # Install 32-bit Wine
    sudo apt-get install wine32

    # Create a 32-bit Wine prefix
    WINEPREFIX=~/.wine-stars WINEARCH=win32 winecfg

    # Copy required DLLs
    cp sr-old/original/CTL3DV2.DLL ~/.wine-stars/drive_c/windows/system/

    # Run the game
    WINEPREFIX=~/.wine-stars wine sr-old/original/stars.exe

See ``tools/wine_automation/`` for automated analysis scripts.

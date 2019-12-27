Installation
============

*Loco sound* currently supports multiple platforms, although only OS X is tested,
but it should run on Linux and Microsoft and Raspberry Pi as well.

To run *loco sound* you need to install
`Python 3 <http://python.org>`_ and `git <https://git-scm.com/downloads>`_.

Once this done you need to download the source code of *loco sound* to your
local computer.
The preferred way for this is `git` by simply executing

.. code-block:: shell

	git clone https://my_repo.git

in a shell and change into the newly created directory via

.. code-block:: shell

	cd loco_sound

After this you need to install the python dependencies via

.. code-block:: shell

	pip3 install -r requirements.txt

Then you can test the installation via

.. code-block:: shell

	python3 test_loco_sound.py

Once installed, please proceed to :ref:`configuration`.

.. _configuration:

Configuration
=============

.. todo::

	Provide a web interface for easy configuration


Introduction
------------

In order to map a locomotive address (from now on called *loco address*)
to a specific sound you need to map a loco address to a SoundPack.

This can be done by writing a yaml file which can look like this.

.. code-block:: yaml

    locos:
      5:
        sound_package: steam
        name: 05 001
        sound_package_config:
          - wheel_radius: 2000
            max_speed: 300
            cylinders: 4

      23:
        sound_package: steam
        name: 23 001
        sound_package_config:
          wheel_radius: 1500
          max_speed: 140
          cylinders: 2

This will map the loco addresses ``5`` and ``23`` to the sound package `steam` as well
as some configurations for the sound package you may want to adjust.

Save this file under ``config.yaml`` in the home directory of `loco_sound` and now
you are ready to start by execution

.. code-block:: shell

	python3 start_loco_sound.py

Configure Z21
-------------

By default we assume that you use the standard LAN configuration
of your Z21.
If this is not the case you can overwrite the default settings by adding
the following block to your ``config.yaml`` file.

.. code-block:: yaml

	z21:
		host: 192.168.0.1
		port: 12345


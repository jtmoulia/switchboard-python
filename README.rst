==================
Switchboard Python
==================

Switchboard_ Python provides helpers for writing Switchboard workers
and clients in Python.

.. _Switchboard: http://thusfresh.github.io/switchboard


Installation
============

It's simplest to install this library from [PyPi](https://pypi.python.org/pypi):

    pip install switchboard-python

To build from source:

    # Building
    ./setup.py build

    # Running the tests
    ./setup.py test

    # Development install
    pip install -e .

    # Actual install
    pip install .


Usage
=====

The :code:`switchboard.Client` class is used to interact with both
Switchboard workers and clients.

Assuming that the Switchboard application is running, the following
example opens a connection to the server over the worker interface,
and sends a batch request with a :code:`connect` command (see the
`interfaces guide`_ for command documentation).

.. code:: python

    worker = switchboard.Client("ws://127.0.0.1:8080/workers")
    worker.connect()
    worker.send_cmds(("connect", CONN_SPEC))
    worker.run_forever()

To handle command responses, :code:`send_cmds` returns a promise_ that
is fulfilled by the tuple :code:`(cmds, resps)` when the command's
responses arrive, where :code:`cmds` is the list of commands given to
:code:`send_cmds`, and :code:`resps` is the list of responses returned
by Switchboard.

.. code:: python

    def handle_get_mailboxes((cmds, resps)):
	print "For cmds", cmds, ", received resps:", resps

    worker.send_cmds(("getMailboxes", {}).then(handle_get_mailboxes)


To add commands on connect, and/or handling of unsolicited messages
subclass the base :code:`switchboard.Client` -- an unsolicited message
is not sent in response to a command, but when the server has new
information, such as a new emails arriving

.. code:: python

    class TheWorker(switchboard.Client):
	def opened(self):
	    print "Connected to Switchboard, issuing watchAll cmd."
	    worker.send_cmds(("watchAll", {}))

	def received_unsolicited(resps):
	    print "Received unsolicited resps from server:", resps
	    for resp in resps:
		if resp[0] == 'newMessage':
		    print "New message:", resp[1]


    worker = TheWorker("ws://127.0.0.1:8080/workers")
    worker.connect()
    worker.run_forever()

.. _interfaces guide: http://thusfresh.github.io/switchboard/guide/interfaces
.. _promise: http://promises-aplus.github.io/promises-spec

Examples
========

All examples are located under :code:`/examples`. Each example uses
command line arguments which you can investigate via:

.. code:: shell

    ./examples/example.py --help


listener.py
-----------

This worker provides a simple example of bidirectional communication
using the Switchboard worker interface. It listens for Switchboard
to notify it of new emails, then fetches the raw email and parses
it using the Python :code:`email` module:

.. code:: shell

    ./examples/listener.py


apnsworker.py
-------------

This worker sends new email `Apple Push Notifications`_ to an iOS
client given an APNS certificate, key, and pushtoken.

Note: it *does not* map from account to push token when sending push
notifications -- it only sends the push notifications using the
provided push token:

.. code:: shell

    ./examples/apnsworker.py --cert "path/to/cert.pem" --key "path/to/key.pem" --pushtoken "target users hex pushtoken"

.. _Apple Push Notifications: https://developer.apple.com/notifications/


twilioworker.py
---------------

This worker is similar to :code:`apnsworker.py`, except instead of sending
APNs when a new email arrives, it sends a text message via
Twilio_:

.. code:: shell

    ./examples/twilioworker.py --sid "twilio sid" --token "twilio token" --to "to phone #" --from "from phone #"

.. _Twilio: https://twilio.com

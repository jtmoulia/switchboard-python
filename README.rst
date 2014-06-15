==================
Switchboard Python
==================

[Switchboard](http://thusfresh.github.io/switchboard) Python provides
helpers for writing Switchboard workers and clients in Python.


Installation
============

This should get you running::

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

The `switchboard.Client` class is used to interact with both Switchboard
workers and clients.

Assuming that the Switchboard application is running, the following
example opens a connection to the server over the worker interface,
and sends a batch request with a `connect` command (see the
[interfaces
guide](http://thusfresh.github.io/switchboard/guide/interfaces) for
command documentation)::

    worker = switchboard.Client("ws://127.0.0.1:8080/workers")
    worker.connect()
    worker.send_cmds(("connect", CONN_SPEC))
    worker.run_forever()

To handle command responses, `send_cmds` returns a
[promise](http://promises-aplus.github.io/promises-spec) that is
fulfilled by the tuple `(cmds, resps)` when the command's responses
arrive, where `cmds` is the list of commands given to `send_cmds`, and
`resps` is the list of responses returned by Switchboard::


    def handle_get_mailboxes((cmds, resps)):
	print "For cmds", cmds, ", received resps:", resps

    worker.send_cmds(("getMailboxes", {}).then(handle_get_mailboxes)


To add commands on connect, and/or handling of unsolicited messages
subclass the base `switchboard.Client` --  an unsolicited message
is not sent in response to a command, but when the server has
new information, such as a new emails arriving::

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

Examples
========

All examples are located under `/examples`. Each example uses
command line arguments which you can investigate via::

    ./examples/example.py --help

listener.py
-----------

This worker provides a simple example of bidirectional communication
using the Switchboard worker interface. It listens for Switchboard
to notify it of new emails, then fetches the raw email and parses
it using the Python `email` module::

    ./examples/listener.py


apnsworker.py
-------------

This worker sends new email
[Apple push notifications](https://developer.apple.com/notifications/)
to an iOS client given an APNS certificate, key, and pushtoken.

Note: it *does not* map from account to push token when sending push
notifications -- it only sends the push notifications using the
provided push token::

    ./examples/apnsworker.py --cert "path/to/cert.pem" --key "path/to/key.pem" --pushtoken "target users hex pushtoken"


twilioworker.py
---------------

This worker is similar to `apnsworker.py`, except instead of sending
APNs when a new email arrives, it sends a text message via
[Twilio](https://twilio.com)::

    ./examples/twilioworker.py --sid "twilio sid" --token "twilio token" --to "to phone #" --from "from phone #"



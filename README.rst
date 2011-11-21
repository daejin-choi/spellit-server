Spell It
========

**Spell It** is a simple web-based game that purposes to be runned on Facebook
platform. It has educational purposes as well, is useful for learning
*real world* English words.

Technical details: It is running on Google App Engine platform with Python 2.7
SDK (which is very experimental ;-). It also has several dependencies on
third party libraries. Follow the instruction::

    $ easy_install Jinja2 MarkupSafe
    $ ./pack.sh

Finally, you can run the server program with the following command
(with assuming you already installed `Google App Engine SDK`_)::

    $ dev_appserver.py --port=8081 .

And then, you can play the game in your browser; open http://localhost:8081/!

.. _Google App Engine SDK: http://code.google.com/p/appengine

[![Build Status](https://travis-ci.org/berkeleybop/bbop-client-barista.svg)](https://travis-ci.org/berkeleybop/bbop-client-barista)

# bbop-client-barista

Manager for handling per-model client-to-client and server-to-client
communication via Barista.

Client, not typical "manager", as it does not use typical engines--it
is based on socket.io.

# Documentation

As of version 0.0.6, this module supports socketio v1.4.6 and above.
Prior to version 0.0.6, this module only supported socketio v0.9.16 and below.

Client applications (e.g., Noctua) that use post 1.0 socketio will encounter an error if they use this module prior to 0.0.6.



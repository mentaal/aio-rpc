# AIO-RPC (WIP)
Client and Server implementation of JSON-RPC 2.0 specification using aiohttp and
websockets.

## Motivation
The idea behind this framework is to provide exclusive access to the object
being served. The reason for this is that the object can represent a service
which requires this such as a piece of hardware. An attempt is made to free the
resource during inactivity.

## Server
Server serves up a class object.
Server can host using either http or https protocols.
Server expects client to login and obtain exclusive access to the object being
served.


## Client 
Client needs to login at: '/login'
Client then needs to grab exclusive access at: '/get_access'
Client then upgrades connection to websockets or websockets secure depending on
the server's setup.


## Examples
Example server and client can be seen within the examples directory.

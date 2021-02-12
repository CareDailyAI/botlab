# Utilities

Microservices operate independently of each other. At times, we need one microservice to talk to another microservice. 

In the past, we tried these methods to get one microservice to communicate to another:
1. Allow a microservice to directly discover another microservice in the system and then communicate with it - quite a hack.
2. Bring common microservice functionality into location.py - makes for a cluttered location.py. You'll still find some residual code in this area which would be nice to eventually port into this style of architecture.
3. Send an internal data stream message and maintain strict documentation (on Confluence) about the address and expected parameters.
4. Create a common interface file here to make it easy to enforce the expected parameters as a function call, and automatically create the internal data stream message.

We're on design pattern #4 right now and it seems to be working well. You must simply have some microservice package implemented that accepts the specific data stream message and handles the inbound data. If you don't have that microservice package then the functionality simply doesn't work and nothing breaks.

The only limitation in all of these designs, so far, is this only facilitates one-way communications and does not return values. There are two ways we handle this:
* Passing in a lambda function as an argument - as we do commonly in trends interface to transform some calculated value down below into human-readable text.
* Passing in a callback function - which we've only explored with conversational UI's.




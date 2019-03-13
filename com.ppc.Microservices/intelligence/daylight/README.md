This microservice package will distribute the following datastream messages throughout your local microservices framework:

* **midnight_fired(botengine, content=None)** : It is now midnight locally. This is independent of gateways and is relative only to midnight at the Location. 
* **sunrise_fired(botengine, content={ 'proxy_id' : gateway_proxy_id })** : It is now sunrise where this gateway is located.
* **sunset_fired(botengine, content={ 'proxy_id' : gateway_proxy_id })** : It is not sunset where this gateway is located.

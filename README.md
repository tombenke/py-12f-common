# py-12f-common

[![Quality Check Status](https://github.com/tombenke/py-12f-common/workflows/Quality%20Check/badge.svg)](https://github.com/tombenke/py-12f-common)
![Coverage](./coverage.svg)

## About

This repository holds those infrastructure-level modules,
that every application requires that follows the core 12-factor principles.

This version of the library is compatible with Python versions >=3.8.

You can use pip to install the library from the
[Python Package Index](https://pypi.org/project/py-12f-common/):

```bash
   $ pip install py-12f-common
```

For further information read [the documentation](https://tombenke.github.io/py-12f-common/).

### Health check
Health check is a web service running on localhost, on the configured port and can be called with HTTP GET request on 
`/health` endpoint. It is responsible for providing information about the application state.

It complies with the Kubernetes health check guidelines. The response is compiled according to 
[Health Check Response Format for HTTP APIs](https://datatracker.ietf.org/doc/html/draft-inadarei-api-health-check-06).

In the configuration, `HEALTH_CHECK` (bool) must be included that enables/disables to run health check web service.  
`HEALTH_CHECK_PORT` (int) is optional that is the port number for the web service (default is 8008). 

The initial state is `NOINFO`. Call the `set_state_warm_up` function just before starting the application, it will set 
the state to `WARMUP`. Once the application has started working, call the `set_state_working` function to set the state 
to `WORK`. Call `set_state_shut_down` just before the application shuts down to set the state to `SHUTDOWN`. The 
`set_state_no_info` function can be used to set the state to `NOINFO` if required.

See the examples: [`minimum`](common/examples/minimum/) is without health check and [`asyncq`](common/examples/asyncq/) 
is with health check.

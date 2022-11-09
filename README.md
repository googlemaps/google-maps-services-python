Python Client for Google Maps Services
====================================

![Test](https://github.com/googlemaps/google-maps-services-js/workflows/Test/badge.svg)
![Release](https://github.com/googlemaps/google-maps-services-js/workflows/Release/badge.svg)
[![codecov](https://codecov.io/gh/googlemaps/google-maps-services-python/branch/master/graph/badge.svg)](https://codecov.io/gh/googlemaps/google-maps-services-python)
[![PyPI version](https://badge.fury.io/py/googlemaps.svg)](https://badge.fury.io/py/googlemaps)
![PyPI - Downloads](https://img.shields.io/pypi/dd/googlemaps)
![GitHub contributors](https://img.shields.io/github/contributors/googlemaps/google-maps-services-python)

## Description

Use Python? Want to geocode something? Looking for directions?
Maybe matrices of directions? This library brings the Google Maps Platform Web
Services to your Python application.

The Python Client for Google Maps Services is a Python Client library for the following Google Maps
APIs:

 - Directions API
 - Distance Matrix API
 - Elevation API
 - Geocoding API
 - Geolocation API
 - Time Zone API
 - Roads API
 - Places API
 - Maps Static API
 - Address Validation API

Keep in mind that the same [terms and conditions](https://developers.google.com/maps/terms) apply
to usage of the APIs when they're accessed through this library.

## Support

This library is community supported. We're comfortable enough with the stability and features of
the library that we want you to build real production applications on it. We will try to support,
through Stack Overflow, the public and protected surface of the library and maintain backwards
compatibility in the future; however, while the library is in version 0.x, we reserve the right
to make backwards-incompatible changes. If we do remove some functionality (typically because
better functionality exists or if the feature proved infeasible), our intention is to deprecate
and give developers a year to update their code.

If you find a bug, or have a feature suggestion, please log an issue. If you'd like to
contribute, please read contribute.

## Requirements

 - Python 3.5 or later.
 - A Google Maps API key.

## API Keys

Each Google Maps Web Service request requires an API key or client ID. API keys
are generated in the 'Credentials' page of the 'APIs & Services' tab of [Google Cloud console](https://console.cloud.google.com/apis/credentials).

For even more information on getting started with Google Maps Platform and generating/restricting an API key, see [Get Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started) in our docs.

**Important:** This key should be kept secret on your server.

## Installation

    $ pip install -U googlemaps

Note that you will need requests 2.4.0 or higher if you want to specify connect/read timeouts.

## Usage

This example uses the Geocoding API and the Directions API with an API key:

```python
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='Add Your Key here')

# Geocoding an address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)

# Validate an address with address validation
addressvalidation_result =  gmaps.addressvalidation(['1600 Amphitheatre Pk'], 
                                                    regionCode='US',
                                                    locality='Mountain View', 
                                                    enableUspsCass=True)
```

For more usage examples, check out [the tests](https://github.com/googlemaps/google-maps-services-python/tree/master/tests).

## Features

### Retry on Failure

Automatically retry when intermittent failures occur. That is, when any of the retriable 5xx errors
are returned from the API.


## Building the Project


    # Installing nox
    $ pip install nox

    # Running tests
    $ nox

    # Generating documentation
    $ nox -e docs

    # Copy docs to gh-pages
    $ nox -e docs && mv docs/_build/html generated_docs && git clean -Xdi && git checkout gh-pages

## Documentation & resources

[Documentation for the `google-maps-services-python` library](https://googlemaps.github.io/google-maps-services-python/docs/index.html)

### Getting started
- [Get Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started)
- [Generating/restricting an API key](https://developers.google.com/maps/gmp-get-started#api-key)
- [Authenticating with a client ID](https://developers.google.com/maps/documentation/directions/get-api-key#client-id)

### API docs
- [Google Maps Platform web services](https://developers.google.com/maps/apis-by-platform#web_service_apis)
- [Directions API](https://developers.google.com/maps/documentation/directions/)
- [Distance Matrix API](https://developers.google.com/maps/documentation/distancematrix/)
- [Elevation API](https://developers.google.com/maps/documentation/elevation/)
- [Geocoding API](https://developers.google.com/maps/documentation/geocoding/)
- [Geolocation API](https://developers.google.com/maps/documentation/geolocation/)
- [Time Zone API](https://developers.google.com/maps/documentation/timezone/)
- [Roads API](https://developers.google.com/maps/documentation/roads/)
- [Places API](https://developers.google.com/places/)
- [Maps Static API](https://developers.google.com/maps/documentation/maps-static/)

### Support
- [Report an issue](https://github.com/googlemaps/google-maps-services-python/issues)
- [Contribute](https://github.com/googlemaps/google-maps-services-python/blob/master/CONTRIB.md)
- [StackOverflow](http://stackoverflow.com/questions/tagged/google-maps)

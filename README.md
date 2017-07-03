Python Client for Google Maps Services
====================================

[![Build Status](https://travis-ci.org/googlemaps/google-maps-services-python.svg?branch=master)](https://travis-ci.org/googlemaps/google-maps-services-python)

## Description

Use Python? Want to [geocode][Geocoding API] something? Looking for [directions][Directions API]?
Maybe [matrices of directions][Distance Matrix API]? This library brings the [Google Maps API Web
Services] to your Python application.
![Analytics](https://maps-ga-beacon.appspot.com/UA-12846745-20/google-maps-services-python/readme?pixel)

The Python Client for Google Maps Services is a Python Client library for the following Google Maps
APIs:

 - [Directions API]
 - [Distance Matrix API]
 - [Elevation API]
 - [Geocoding API]
 - [Geolocation API]
 - [Time Zone API]
 - [Roads API]
 - [Places API]

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

If you find a bug, or have a feature suggestion, please [log an issue][issues]. If you'd like to
contribute, please read [How to Contribute][contrib].

## Requirements

 - Python 2.7 or later.
 - A Google Maps API key.

### API keys

Each Google Maps Web Service request requires an API key or client ID. API keys
are freely available with a Google Account at
https://developers.google.com/console. The type of API key you need is a
**Server key**.

To get an API key:

 1. Visit https://developers.google.com/console and log in with
    a Google Account.
 1. Select one of your existing projects, or create a new project.
 1. Enable the API(s) you want to use. The Python Client for Google Maps Services
    accesses the following APIs:
    * Directions API
    * Distance Matrix API
    * Elevation API
    * Geocoding API
    * Geolocation API
    * Places API
    * Roads API
    * Time Zone API
 1. Create a new **Server key**.
 1. If you'd like to restrict requests to a specific IP address, do so now.

For guided help, follow the instructions for the [Directions API][directions-key].
You only need one API key, but remember to enable all the APIs you need.
For even more information, see the guide to [API keys][apikey].

**Important:** This key should be kept secret on your server.

## Installation

    $ pip install -U googlemaps

Note that you will need requests 2.4.0 or higher if you want to specify connect/read timeouts.

## Developer Documentation

View the [reference documentation](https://googlemaps.github.io/google-maps-services-python/docs/)

Additional documentation for the included web services is available at
https://developers.google.com/maps/.

 - [Directions API]
 - [Distance Matrix API]
 - [Elevation API]
 - [Geocoding API]
 - [Geolocation API]
 - [Time Zone API]
 - [Roads API]
 - [Places API]

## Usage

This example uses the [Geocoding API] and the [Directions API] with an API key:

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
```

Below is the same example, using client ID and client secret (digital signature)
for authentication. This code assumes you have previously loaded the `client_id`
and `client_secret` variables with appropriate values.

For a guide on how to generate the `client_secret` (digital signature), see the
documentation for the API you're using. For example, see the guide for the
[Directions API][directions-client-id].

```python
gmaps = googlemaps.Client(client_id=client_id, client_secret=client_secret)

# Geocoding and address
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)
```

For more usage examples, check out [the tests](test/).

## Features

### Retry on Failure

Automatically retry when intermittent failures occur. That is, when any of the retriable 5xx errors
are returned from the API.

### Client IDs

Google Maps APIs Premium Plan customers can use their [client ID and secret][clientid] to authenticate,
instead of an API key.

## Building the Project


    # Installing tox
    $ pip install tox

    # Running tests
    $ tox

    # Generating documentation
    $ tox -e docs

    # Uploading a new release
    $ easy_install wheel twine
    $ python setup.py sdist bdist_wheel
    $ twine upload dist/*

    # Copy docs to gh-pages
    $ tox -e docs && mv docs/_build/html generated_docs && git clean -Xdi && git checkout gh-pages


[apikey]: https://developers.google.com/maps/faq#keysystem
[clientid]: https://developers.google.com/maps/documentation/business/webservices/auth

[Google Maps API Web Services]: https://developers.google.com/maps/documentation/webservices/
[Directions API]: https://developers.google.com/maps/documentation/directions/
[directions-key]: https://developers.google.com/maps/documentation/directions/get-api-key#key
[directions-client-id]: https://developers.google.com/maps/documentation/directions/get-api-key#client-id
[Distance Matrix API]: https://developers.google.com/maps/documentation/distancematrix/
[Elevation API]: https://developers.google.com/maps/documentation/elevation/
[Geocoding API]: https://developers.google.com/maps/documentation/geocoding/
[Geolocation API]: https://developers.google.com/maps/documentation/geolocation/
[Time Zone API]: https://developers.google.com/maps/documentation/timezone/
[Roads API]: https://developers.google.com/maps/documentation/roads/
[Places API]: https://developers.google.com/places/

[issues]: https://github.com/googlemaps/google-maps-services-python/issues
[contrib]: https://github.com/googlemaps/google-maps-services-python/blob/master/CONTRIB.md

Python Client for Google Maps Services
====================================

## Description

Use Python? Want to [geocode][Geocoding API] something? Looking for [directions][Directions API]?
Maybe [matrices of directions][Distance Matrix API]? This library brings the [Google Maps API Web
Services] to your Python application.

The Python Client for Google Maps Services is a Python Client library for the following Google Maps 
APIs:

 - [Directions API]
 - [Distance Matrix API]
 - [Elevation API]
 - [Geocoding API]
 - [Time Zone API]

Keep in mind that the same [terms and conditions](https://developers.google.com/maps/terms) apply
to usage of the APIs when they're accessed through this library.

## Support

This library is community supported. We're comfortable enough with the stability and features of
the library that we want you to build real production applications on it. We will make an effort to
support the public and protected surface of the library and maintain backwards compatibility in the
future; however, while the library is in version 0.x, we reserve the right to make
backwards-incompatible changes. If we do remove some functionality (typically because better
functionality exists or if the feature proved infeasible), our intention is to deprecate and
provide ample time for developers to update their code.

If you find a bug, or have a feature suggestion, please [log an issue][issues]. If you'd like to
contribute, please read [How to Contribute][contrib].

## Requirements

 - Python 2.7 or later.
 - A Google Maps API key.

### API keys

Each Google Maps Web Service requires an API key or Client ID. API keys are
freely available with a Google Account at https://developers.google.com/console.
To generate a server key for your project:

 1. Visit https://developers.google.com/console and log in with 
    a Google Account.
 1. Select an existing project, or create a new project.
 1. Click **Enable an API**.
 1. Browse for the API, and set its status to "On". The Python Client for Google Maps Services 
    accesses the following APIs:
    * Directions API
    * Distance Matrix API
    * Elevation API
    * Geocoding API
    * Time Zone API
 1. Once you've enabled the APIs, click **Credentials** from the left navigation of the Developer
    Console.
 1. In the "Public API access", click **Create new Key**.
 1. Choose **Server Key**.
 1. If you'd like to restrict requests to a specific IP address, do so now.
 1. Click **Create**.

Your API key should be 40 characters long, and begin with `AIza`.

**Important:** This key should be kept secret on your server.

## Installation

    # Installing dependencies:
    $ pip install requests responses

## Developer Documentation

Additional documentation for the included web services is available at 
https://developers.google.com/maps/.

 - [Directions API]
 - [Distance Matrix API]
 - [Elevation API]
 - [Geocoding API]
 - [Time Zone API]

## Usage

This example uses the [Geocoding API].



```python

ctx = googlemaps.Context('Add Your Key here')

# Geocoding and address
geocode_result = googlemaps.geocode(ctx, '1600 Amphitheatre Parkway, '
                                    'Mountain View, CA')

# Look up an address with reverse geocoding
reverse_geocode_result = googlemaps.reverse_geocode(ctx, (40.714224, -73.961452))

# Request directions via public transit
now = datetime.now()
directions_result = googlemaps.directions(ctx,
                                          "Sydney Town Hall",
                                          "Parramatta, NSW",
                                          mode="transit",
                                          departure_time=now)
```



For more usage examples, check out [the tests](test/).

## Features

### Retry on Failure

Automatically retry when intermittent failures occur. That is, when any of the retriable 5xx errors
are returned from the API.

### Keys *and* Client IDs

Maps API for Work customers can use their [client ID and secret][clientid] to authenticate. Free
customers can use their [API key][apikey], too.

## Building the Project

**Note:** You will need an API key or Client ID to run the tests.

    # Generating documentation:
    $ sphinx-build -b html docs docs/html

    # Installing dependencies:
    $ pip install requests responses

    # Running tests:
    $ git submodule update --init
    $ python -m unittest discover


[apikey]: https://developers.google.com/maps/faq#keysystem
[clientid]: https://developers.google.com/maps/documentation/business/webservices/auth

[Google Maps API Web Services]: https://developers.google.com/maps/documentation/webservices/
[Directions API]: https://developers.google.com/maps/documentation/directions
[Distance Matrix API]: https://developers.google.com/maps/documentation/distancematrix
[Elevation API]: https://developers.google.com/maps/documentation/elevation
[Geocoding API]: https://developers.google.com/maps/documentation/geocoding
[Time Zone API]: https://developers.google.com/maps/documentation/timezone

[issues]: https://github.com/googlemaps/google-maps-services-python/issues
[contrib]: https://github.com/googlemaps/google-maps-services-python/blob/master/CONTRIB.md

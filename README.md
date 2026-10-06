Python Client for Google Maps Services
====================================

![Test](https://github.com/googlemaps/google-maps-services-js/workflows/Test/badge.svg)
![Release](https://github.com/googlemaps/google-maps-services-js/workflows/Release/badge.svg)
[![codecov](https://codecov.io/gh/googlemaps/google-maps-services-python/branch/master/graph/badge.svg)](https://codecov.io/gh/googlemaps/google-maps-services-python)
[![PyPI version](https://badge.fury.io/py/googlemaps.svg)](https://badge.fury.io/py/googlemaps)
![PyPI - Downloads](https://img.shields.io/pypi/dd/googlemaps)
![GitHub contributors](https://img.shields.io/github/contributors/googlemaps/google-maps-services-python)

> [!IMPORTANT]
> **Legacy APIs End of Sale & Newer Client Libraries**
>
> Several APIs supported by this library are in [Legacy status](https://developers.google.com/maps/legacy):
> - **Places API (Legacy):** This product is in [Legacy status](https://developers.google.com/maps/legacy). As of October 2026, Places API (Legacy) can no longer be enabled for new Google Cloud projects. Existing projects remain fully supported. For new features and improved performance, [migrate to Places API (New)](https://developers.google.com/maps/documentation/places/web-service/legacy/migrate-overview).
> - **Directions API (Legacy):** This product is in [Legacy status](https://developers.google.com/maps/legacy). As of October 2026, Directions API (Legacy) can no longer be enabled for new Google Cloud projects. Existing projects remain fully supported. For new features and improved performance, [migrate to the Routes API](https://developers.google.com/maps/documentation/routes/migrate-routes).
> - **Distance Matrix API (Legacy):** This product is in [Legacy status](https://developers.google.com/maps/legacy). As of October 2026, Distance Matrix API (Legacy) can no longer be enabled for new Google Cloud projects. Existing projects remain fully supported. For new features and improved performance, [migrate to the Routes API](https://developers.google.com/maps/documentation/routes/migrate-routes).
>
> For our newer APIs, see the [Google Maps Platform APIs in the Cloud Client Libraries for Python](https://github.com/googleapis/google-cloud-python) ([overview](https://docs.cloud.google.com/apis/docs/cloud-client-libraries)):
> - [Places API (New)](https://github.com/googleapis/google-cloud-python/tree/main/packages/google-maps-places)
> - [Routes API](https://github.com/googleapis/google-cloud-python/tree/main/packages/google-maps-routing)
> - [Address Validation API](https://github.com/googleapis/google-cloud-python/tree/main/packages/google-maps-addressvalidation)
> - [Datasets API](https://github.com/googleapis/google-cloud-python/tree/main/packages/google-maps-mapsplatformdatasets)
>
> The new APIs will not be added to this client library.

## Description

Use Python? Want to geocode something? Looking for directions?
Maybe matrices of directions? This library brings the Google Maps Platform Web
Services to your Python application.

The Python Client for Google Maps Services is a Python Client library for the following Google Maps
APIs:

 - Elevation API
 - Geocoding API
 - Geolocation API
 - Time Zone API
 - Roads API
 - Maps Static API
 - Address Validation API

As well as the following legacy APIs:

 - Directions API (Legacy)
 - Distance Matrix API (Legacy)
 - Places API (Legacy)

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

# Get an Address Descriptor of a location in the reverse geocoding response
address_descriptor_result = gmaps.reverse_geocode((40.714224, -73.961452), enable_address_descriptor=True)

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

## Terms of Service

This library uses Google Maps Platform services. Use of Google Maps Platform services through this library is subject to the Google Maps Platform [Terms of Service](https://cloud.google.com/maps-platform/terms).

This library is not a Google Maps Platform Core Service. Therefore, the Google Maps Platform Terms of Service (e.g. Technical Support Services, Service Level Agreements, and Deprecation Policy) do not apply to the code in this library.

### European Economic Area (EEA) developers

If your billing address is in the European Economic Area, effective on 8 July 2025, the [Google Maps Platform EEA Terms of Service](https://cloud.google.com/terms/maps-platform/eea) will apply to your use of the Services. Functionality varies by region. [Learn more](https://developers.google.com/maps/comms/eea/faq).

## Support

This library is offered via an open source [license](LICENSE). It is not governed by the Google Maps Platform Support [Technical Support Services Guidelines](https://cloud.google.com/maps-platform/terms/tssg), the [SLA](https://cloud.google.com/maps-platform/terms/sla), or the [Deprecation Policy](https://cloud.google.com/maps-platform/terms) (however, any Google Maps Platform services used by the library remain subject to the Google Maps Platform Terms of Service).

This library adheres to [semantic versioning](https://semver.org/) to indicate when backwards-incompatible changes are introduced. Accordingly, while the library is in version 0.x, backwards-incompatible changes may be introduced at any time.

If you find a bug, or have a feature request, please [file an issue](https://github.com/googlemaps/google-maps-services-python/issues) on GitHub. If you would like to get answers to technical questions from other Google Maps Platform developers, ask through one of our [developer community channels](https://developers.google.com/maps/developer-community). If you'd like to contribute, please check the [Contributing guide](CONTRIB.md).

You can also discuss this library on our [Discord server](https://discord.gg/hYsWbmk).


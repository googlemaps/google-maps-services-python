[![PyPI](https://img.shields.io/pypi/v/googlemaps.svg)](https://pypi.python.org/pypi/googlemaps)
![Release](https://github.com/googlemaps/google-maps-services-python/workflows/Release/badge.svg)
![Stable](https://img.shields.io/badge/stability-stable-green)
[![Tests/Build](https://github.com/googlemaps/google-maps-services-python/actions/workflows/test.yml/badge.svg)](https://github.com/googlemaps/google-maps-services-python/actions/workflows/test.yml)

[![codecov](https://codecov.io/gh/googlemaps/google-maps-services-python/branch/master/graph/badge.svg)](https://codecov.io/gh/googlemaps/google-maps-services-python)

![Contributors](https://img.shields.io/github/contributors/googlemaps/google-maps-services-python?color=green)
[![License](https://img.shields.io/github/license/googlemaps/google-maps-services-python?color=blue)][license]
[![StackOverflow](https://img.shields.io/stackexchange/stackoverflow/t/google-maps?color=orange&label=google-maps&logo=stackoverflow)](https://stackoverflow.com/questions/tagged/google-maps)
[![Discord](https://img.shields.io/discord/676948200904589322?color=6A7EC2&logo=discord&logoColor=ffffff)][Discord server]

# Python Client for Google Maps Services

## Description

Use Python? Want to [geocode][Geocoding API] something? Looking for [directions][Directions API]? This client library brings the following [Google Maps Platform Web Services APIs] to your server-side Python applications:

- [Maps Static API]
- [Directions API]
- [Distance Matrix API]
- [Elevation API]
- [Geocoding API]
- [Places API]
- [Roads API]
- [Time Zone API]
TODO ? Geolocation API
TODO ? Address Validation API

## Requirements

- [Sign up with Google Maps Platform]
- A Google Maps Platform [project] with the desired API(s) from the above list enabled
- An [API key] associated with the project above
- Python 3.5+

## API Key Security

This client library is designed for use in server-side applications.

In either case, it is important to add [API key restrictions](https://developers.google.com/maps/api-security-best-practices#restricting-api-keys) to improve its security. Additional security measures, such as hiding your key
from version control, should also be put in place to further improve the security of your API key.

Check out the [API Security Best Practices](https://developers.google.com/maps/api-security-best-practices) guide to learn more.

## Installation

    $ pip install -U googlemaps

Note that you will need requests 2.4.0 or higher if you want to specify connect/read timeouts.

## Usage

This example uses the Geocoding API and the Directions API with an API key:

```python
import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='YOUR_API_KEY')

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

## Documentation

For more information, see the reference [documentation].

## Contributing

Contributions are welcome and encouraged! If you'd like to contribute, send us a [pull request] and refer to our [code of conduct] and [contributing guide].

## Terms of Service

This library uses Google Maps Platform services. Use of Google Maps Platform services through this library is subject to the Google Maps Platform [Terms of Service].

This library is not a Google Maps Platform Core Service. Therefore, the Google Maps Platform Terms of Service, e.g., [Technical Support Services Guidelines], Service Level Agreement ["SLA"][SLA], and [Deprecation Policy], do not apply to the code in this library.

## Support

This library is offered via an open source [license]. It is not governed by the Google Maps Platform Support Technical Support Services Guidelines, the SLA, or the Deprecation Policy. However, any Google Maps Platform services used by the library remain subject to the Google Maps Platform Terms of Service.

This library adheres to [semantic versioning] to indicate when backwards-incompatible changes are introduced. Accordingly, while the library is in version 0.x, backwards-incompatible changes may be introduced at any time.

If you find a bug, or have a feature request, please [file an issue] on GitHub. If you would like to get answers to technical questions from other Google Maps Platform developers, ask through one of our [developer community channels]. If you'd like to contribute, please check the [contributing guide].

You can also discuss this library on our [Discord server].

- [Get Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started)

[Google Maps Platform Web Services APIs]: https://developers.google.com/maps/apis-by-platform#web_service_apis
[Maps Static API]: https://developers.google.com/maps/documentation/maps-static
[Directions API]: https://developers.google.com/maps/documentation/directions
[Distance Matrix API]: https://developers.google.com/maps/documentation/distancematrix
[Elevation API]: https://developers.google.com/maps/documentation/elevation
[Geocoding API]: https://developers.google.com/maps/documentation/geocoding
[Places API]: https://developers.google.com/places/web-service
[Roads API]: https://developers.google.com/maps/documentation/roads
[Time Zone API]: https://developers.google.com/maps/documentation/timezone
[Geolocation API]: https://developers.google.com/maps/documentation/geolocation

[API key]: https://developers.google.com/maps/documentation/javascript/get-api-key
[documentation]: https://googlemaps.github.io/google-maps-services-python/docs

[code of conduct]: ?tab=coc-ov-file#readme
[contributing guide]: CONTRIB.md
[Deprecation Policy]: https://cloud.google.com/maps-platform/terms
[developer community channels]: https://developers.google.com/maps/developer-community
[Discord server]: https://discord.gg/hYsWbmk
[file an issue]: https://github.com/googlemaps/google-maps-services-python/issues/new/choose
[license]: LICENSE
[project]: https://developers.google.com/maps/documentation/javascript/cloud-setup#enabling-apis
[pull request]: https://github.com/googlemaps/google-maps-services-python/compare
[semantic versioning]: https://semver.org
[Sign up with Google Maps Platform]: https://console.cloud.google.com/google/maps-apis/start
[similar inquiry]: https://github.com/googlemaps/google-maps-services-python/issues
[SLA]: https://cloud.google.com/maps-platform/terms/sla
[Technical Support Services Guidelines]: https://cloud.google.com/maps-platform/terms/tssg
[Terms of Service]: https://cloud.google.com/maps-platform/terms

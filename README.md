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

## API Keys & Setup

Each request to Google Maps Platform Web Services requires an API key.

### 1. Generating an API Key

1. Go to the [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials) page.
2. Select your Google Cloud project (or create a new project).
3. Click **+ Create Credentials** at the top and select **API key**.
4. Copy the generated API key.

### 2. Enabling Required APIs

Google Maps Platform Web Services are modular. Enable the specific APIs your project needs in the [Google Cloud API Library](https://console.cloud.google.com/apis/library):

- **Places API (New)** (`places.googleapis.com`)
- **Routes API (v2)** (`routes.googleapis.com`)
- **Address Validation API** (`addressvalidation.googleapis.com`)
- **Geocoding API** (`geocoding-backend.googleapis.com`)
- **Isochrones API** (`isochrones.googleapis.com`)
- **Environmental APIs**: Solar (`solar.googleapis.com`), Air Quality (`airquality.googleapis.com`), Pollen (`pollen.googleapis.com`)

### 3. Key Restrictions & Security Best Practices

> ⚠️ **Important Security Rule:** Never hardcode secret API keys directly into public repositories or client-side code.

- **API Restrictions**: In Cloud Console, select your API Key -> **API restrictions** -> choose **Restrict key** -> select only the specific APIs your backend application requires.
- **Application Restrictions**: Limit key usage by server IP address (`IP addresses` restriction) for backend environments.
- **Environment Variables**: Store your key in an environment variable:
  ```bash
  export GOOGLE_MAPS_API_KEY="AIzaSy..."
  ```

For full setup documentation, visit [Get Started with Google Maps Platform](https://developers.google.com/maps/gmp-get-started).

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


## Testing

The project contains unit tests (with mock HTTP responses) and live integration tests (against Google Maps Platform production servers).

### 1. Running Unit Tests (Offline / Mocked)

Run the fast unit test suite using `pytest`:

```bash
# Run all unit tests
pytest

# Run tests with coverage report
pytest --cov=googlemaps --cov-report=term-missing
```

### 2. Running Live Integration Tests

The live integration suite in `tests/test_integration.py` tests actual API requests against Google Maps Platform production endpoints.

#### Running Locally
Set your API key in your shell environment:

```bash
export GOOGLE_MAPS_API_KEY="YOUR_ACTUAL_API_KEY"
pytest tests/test_integration.py
```

#### Running automatically in GitHub Actions CI
To run live integration tests on GitHub Actions:
1. Open your repository on GitHub.
2. Go to **Settings** -> **Secrets and variables** -> **Actions**.
3. Click **New repository secret**.
4. Name: `GOOGLE_MAPS_API_KEY`
5. Value: *your restricted Google Maps Platform API key*.

The `.github/workflows/test.yml` workflow automatically passes `${{ secrets.GOOGLE_MAPS_API_KEY }}` into test runs across Python versions 3.9 through 3.13.

*(Note: If `GOOGLE_MAPS_API_KEY` secret or environment variable is absent, live integration tests are automatically skipped).*

### 3. Running Executable CUJ Samples

Run any of the real-world CUJ sample applications:

```bash
python samples/real_estate_insights.py
python samples/delivery_route_planner.py
python samples/travel_discovery_assistant.py
python samples/isochrone_reachability_cuj.py
```

---

## Building the Project

```bash
# Installing nox
$ pip install nox

# Running full test matrices across Python versions
$ nox
```

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


Generating documentation:

    $ sphinx-build -b html docs docs/html

Installing dependencies:

    $ pip install requests responses

Running tests:

    $ git submodule update --init
    $ python -m unittest discover

Using the API:

1) Get yourself an API Key or Client ID. See
   [API Key documentation](https://developers.google.com/maps/documentation/webservices/client-library#api_keys)
   for more information.

2) Import the `googlemaps` package

    import googlemaps

3) Construct a context with an API Key or Client ID

    c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)


4) Make API calls and use the results

    locations = [(40.714728, -73.998672), (-34.397, 150.644)]
    print googlemaps.elevation(c, locations)
    print googlemaps.elevation(c, (40.714728, -73.998672))

    print googlemaps.elevation_along_path(c, locations, 3)

    geocoded = googlemaps.geocode(c, "48 Pirrama Rd")

    print geocoded

    print googlemaps.reverse_geocode(c, geocoded[0]["geometry"]["location"])

    print googlemaps.reverse_geocode(c,
            latlng=(-33.86536501970851,151.1969187802915),
            result_type=["country", "political"])

    print googlemaps.geocode(c, components={"country": "US"})

    print googlemaps.directions(c,
            "Sydney",
            "Melbourne",
            alternatives=True
    )

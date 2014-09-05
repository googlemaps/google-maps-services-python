"""Samples demonstrating the googlemaps package."""
# TODO(mdr-eng): clean up and replace with tests/move to README file.

import googlemaps

def main():
    c = googlemaps.Context(
            key="AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM",
            timeout=5)

    geocoded = googlemaps.geocode(c, "48 Pirrama Rd")

    print geocoded

    print googlemaps.reverse_geocode(c, geocoded[0]["geometry"]["location"])

    print googlemaps.reverse_geocode(c,
            latlng="-33.86536501970851,151.1969187802915",
            result_type=["country", "political"])

    print googlemaps.geocode(c, components={"country": "US"})

    print googlemaps.directions(c,
            "Sydney",
            "Melbourne",
            alternatives=True
    )

    # "Context-like" object.
    class MyContext():
        pass

    ctx = MyContext()
    ctx.key = "AIzaSyDyZdCabN8GKh786tdj16gq80xalbbfqDM"

    print googlemaps.directions(ctx, "sydney", "melbourne")

if __name__ == '__main__':
    main()

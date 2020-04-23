import googlemaps


PLACES_DETAIL_FIELDS_BASIC = {"address_component", "adr_address", "alt_id", "formatted_address", "geometry",
                              "geometry/location", "geometry/location/lat", "geometry/location/lng",
                              "geometry/viewport", "geometry/viewport/northeast", "geometry/viewport/northeast/lat",
                              "geometry/viewport/northeast/lng", "geometry/viewport/southwest",
                              "geometry/viewport/southwest/lat", "geometry/viewport/southwest/lng", "icon", "id",
                              "name", "permanently_closed", "photo", "place_id", "plus_code", "scope", "type", "url",
                              "utc_offset", "vicinity"}

PLACES_DETAIL_FIELDS_CONTACT = {"formatted_phone_number", "international_phone_number", "opening_hours", "website"}

PLACES_DETAIL_FIELDS_ATMOSPHERE = {"price_level", "rating", "review", "user_ratings_total"}

PLACES_DETAIL_FIELDS = (
    PLACES_DETAIL_FIELDS_BASIC
    ^ PLACES_DETAIL_FIELDS_CONTACT
    ^ PLACES_DETAIL_FIELDS_ATMOSPHERE
)


api_key = 'AIzaasdf'
gmaps = googlemaps.Client(key=api_key)

place_id = 'ChIJN1t_tDeuEmsRUsoyG83frY4'

##can send any of the required fields from the set 'PLACES_DETAIL_FIELDS' In particular phone numbers are of great interest

FormattedPhoneNumber = 0
InternationalPhoneNumber = 0
name = 'Not Mentioned'

k = gmaps.place_details(place_id, fields={'name', 'formatted_phone_number', 'international_phone_number'})
if 'name' in k['result']:
    name = k['result']['name']
if 'formatted_phone_number' in k['result']:
    FormattedPhoneNumber = k['result']['formatted_phone_number']
if 'international_phone_number' in k['result']:
    InternationalPhoneNumber = k['result']['international_phone_number']


print("Name of the place: {}\nFormatted phone number: {}\nInternational phone number: {}".format(name, FormattedPhoneNumber, InternationalPhoneNumber))
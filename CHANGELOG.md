# Changelog
All notable changes to this project will be documented in this file.

## [v4.2.0]
### Added
- Add support for Maps Static API (#344)

## [v4.1.0]
### Added
- Adding support for passing in `experience_id` to Client class (#338)

## [v4.0.0]
### Changed
- Python 2 is no longer supported
- Removed place fields: `alt_id`, `id`, `reference`, and `scope`. Read more about this at https://developers.google.com/maps/deprecations.

## [v3.1.4]
### Changed
- `APIError.__str__` should always return a str (#328)

## [v3.1.3]
### Changed
- deprecation warning for place fields: `alt_id`, `id`, `reference`, and `scope`. Read more about this at https://developers.google.com/maps/deprecations.

## [v3.1.2]
### Added
- Tests for distribution tar as part of CI
- Support for subfields such as `geometry/location` and `geometry/viewport` in Places.

## [v3.1.1]
### Changed
- Added changelog to manifest

## [v3.1.0]
### Changed
- Switched build system to use [nox](https://nox.thea.codes/en/stable/), pytest, and codecov. Added Python 3.7 to test framework.
- Set precision of truncated latitude and longitude floats [to 8 decimals](https://github.com/googlemaps/google-maps-services-python/pull/301) instead of 6.
- Minimum version of requests increased.
- Session token parameter [added](https://github.com/googlemaps/google-maps-services-python/pull/244) to `place()`.
- Fixed issue where headers in `request_kwargs` were being overridden.
### Added
- Automation for PyPi uploads.
- Long description to package.
- Added tests to manifest and tarball.
### Removed
- Removed places `places_autocomplete_session_token` which can be replaced with `uuid.uuid4().hex`.
- Removed deprecated `places_radar`.


**Note:** Start of changelog is 2019-08-27, [v3.0.2].

[Unreleased]: https://github.com/googlemaps/google-maps-services-python/compare/4.2.0...HEAD
[v4.2.0]: https://github.com/googlemaps/google-maps-services-python/compare/4.1.0...4.2.0
[v4.1.0]: https://github.com/googlemaps/google-maps-services-python/compare/4.0.0...4.1.0
[v4.0.0]: https://github.com/googlemaps/google-maps-services-python/compare/3.1.4...4.0.0
[v3.1.4]: https://github.com/googlemaps/google-maps-services-python/compare/3.1.3...3.1.4
[v3.1.3]: https://github.com/googlemaps/google-maps-services-python/compare/3.1.2...3.1.3
[v3.1.2]: https://github.com/googlemaps/google-maps-services-python/compare/3.1.1...3.1.2
[v3.1.1]: https://github.com/googlemaps/google-maps-services-python/compare/3.1.0...3.1.1
[v3.1.0]: https://github.com/googlemaps/google-maps-services-python/compare/3.0.2...3.1.0
[v3.0.2]: https://github.com/googlemaps/google-maps-services-python/compare/3.0.1...3.0.2
[v3.0.1]: https://github.com/googlemaps/google-maps-services-python/compare/3.0.0...3.0.1
[v3.0.0]: https://github.com/googlemaps/google-maps-services-python/compare/2.5.1...3.0.0

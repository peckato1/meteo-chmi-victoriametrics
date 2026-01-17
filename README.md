# CHMI data to VictoriaMetrics

This repository contains scripts and configurations to collect meteorological and hydrological data from the Czech Hydrometeorological Institute (CHMI) and store it in VictoriaMetrics.

## Configuration

Project is configured via environment variables.

| Variable                        | Description                                                                                 | Default Value |
| ------------------------------- | ------------------------------------------------------------------------------------------- | ------------- |
| `CHMI_VM_BASEURL`               | Base URL of VictoriaMetrics instance                                                        | -             |
| `CHMI_FORECAST`                 | Comma separated list of locations for forecast data (see locations below)                   | -             |
| `CHMI_STATION`                  | Comma separated list of locations for meteo stations observation data (see locations below) | -             |
| `CHMI_FORECAST_UPDATE_INTERVAL` | Interval for fetching forecast data (in seconds)                                            | `3600`        |
| `CHMI_STATION_UPDATE_INTERVAL`  | Interval for fetching meteo stations observation data (in seconds)                          | `600`         |
| `CHMI_LOG_LEVEL`                | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)                                       | `INFO`        |

At least one of `CHMI_FORECAST` or `CHMI_STATION` must be set.
The VictoriaMetrics base URL is required.

## Locations

Environment variables `CHMI_FORECAST` and `CHMI_STATION` accept comma-separated lists of location identifiers.
Location identifier is a pair `<id>:<name>`.
Specify multiple locations like this: `id1:name1,id2:name2,id3:name3`.
The names are arbitrary, they are added as labels to VictoriaMetrics data.

The location IDs can be found on the CHMI website.
The forecast data location ID can be found in the URL of the meteogram forecast.
For example, [this city](https://www.chmi.cz/meteogram/256-melnik) has ID `256`.
GPS locations are currently not supported (TBD).

For observation meteo stations, the location ID can again be found in the URL of the station observation page.
For instance, [this station](https://www.chmi.cz/namerena-data/merici-stanice/meteorologicke/c2kaml01-kamenice-nad-lipou-vodna) has ID `c2kaml01`.

## VictoriaMetrics Data

Data is stored in VictoriaMetrics.
Every metric has `weather_chmi` prefix.

The following labels are added:
- `location_name` - the name specified in the configuration
- `location_id` - the CHMI location ID
- `job` - `weather_chmi_forecast` or `weather_chmi_meteo_station`
- `forecast_published` - datetime when the forecast was published (only for forecast data)

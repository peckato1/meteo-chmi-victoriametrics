import csv
import io
import loguru

from .location_entry import LocationEntry
from .chmi import fetch_forecast, fetch_station
from .utils import datetime_to_str, str_to_datetime
from .vm import push as vm_push

TIMEZONE = "Europe/Prague"


def access(d: dict, accessor: str):
    if "." not in accessor:
        return d[accessor]

    parts = accessor.split(".")
    for p in parts:
        if p not in d:
            return None
        d = d[p]
    return d


def create_csv(data, metadata):
    stream = io.StringIO()
    csv_writer = csv.writer(stream, delimiter=",")

    for e in data:
        row = []

        for i, (type_, context, accessor) in enumerate(metadata, 1):
            if type_ == "time":
                dt = str_to_datetime(access(e, accessor), TIMEZONE)

                if context == "unix_s":
                    row.append(int(dt.timestamp()))
                else:
                    raise ValueError(f"Unsupported time type: {type_} {context}")
            elif type_ == "metric":
                row.append(access(e, accessor))
            else:
                raise ValueError(f"Unsupported type: {type_} {context}")

        csv_writer.writerow(row)

    return stream.getvalue().strip(), list(map(lambda x: (x[0], x[1]), metadata))


def _process(msg: str, vmbaseurl: str, fetch_fn, loc: LocationEntry, metadata, extra_labels=None):
    if extra_labels is None:
        extra_labels = dict()

    loguru.logger.info(f"Processing {msg} data for {loc}")
    loguru.logger.debug("Fetching data")
    meteo, _ = fetch_fn(loc.chmi_id)

    for k, v in extra_labels.items():
        extra_labels[k] = v(meteo) if callable(v) else v

    loguru.logger.debug("Transforming data")
    csv_content, csv_meta = create_csv(meteo, metadata)

    loguru.logger.debug("Sending to VictoriaMetrics")
    vm_push(vmbaseurl, csv_content, csv_meta, extra_labels)
    return None


def forecast(location_entry: LocationEntry, vmbaseurl: str):
    return _process(
        "forecast",
        vmbaseurl,
        fetch_forecast,
        location_entry,
        metadata=[
            ("time", "unix_s", "validityTime"),
            ("metric", "weather_chmi_forecast_clouds_total_percent", "cloudsTot"),
            ("metric", "weather_chmi_forecast_pressure_sea_level_hpa", "mslp"),
            ("metric", "weather_chmi_forecast_precipitation_mmh", "prec"),
            ("metric", "weather_chmi_forecast_relative_humidity_2m_percent", "rh2m"),
            ("metric", "weather_chmi_forecast_snow_mm_h", "snow"),
            ("metric", "weather_chmi_forecast_temperature_2m_c", "t2m"),
            ("metric", "weather_chmi_forecast_wind_direction_10m_deg", "windDirection"),
            ("metric", "weather_chmi_forecast_wind_gust_speed_10m_ms", "windGustSpeed"),
            ("metric", "weather_chmi_forecast_wind_speed_10m_ms", "windSpeed"),
            ("metric", "weather_chmi_forecast_weather_icon", "icon"),
            ("metric", "weather_chmi_forecast_wind_level_icon", "windLevelIcon"),
        ],
        extra_labels={
            "forecast_published": lambda data: datetime_to_str(str_to_datetime(min(e["validityTime"] for e in data), TIMEZONE)),
            "job": "weather_chmi_forecast",
            "location_chmi_id": location_entry.chmi_id,
            "location_name": location_entry.name,
        },
    )


def station(location_entry: LocationEntry, vmbaseurl: str):
    return _process(
        "meteo station",
        vmbaseurl,
        fetch_station,
        location_entry,
        [
            ("time", "unix_s", "timestamp"),
            ("metric", "weather_chmi_meteo_temperature_c", "values.T"),
            ("metric", "weather_chmi_meteo_temperature_ground_c", "values.TPM"),
            ("metric", "weather_chmi_meteo_wind_direction_deg", "values.D"),
            ("metric", "weather_chmi_meteo_wind_gust_direction_deg", "values.Dmax"),
            ("metric", "weather_chmi_meteo_wind_speed_ms", "values.F"),
            ("metric", "weather_chmi_meteo_wind_gust_speed_ms", "values.Fmax"),
            ("metric", "weather_chmi_meteo_relative_humidity_percent", "values.H"),
            ("metric", "weather_chmi_meteo_precipitation_10m_mm", "values.SRA10M"),
            ("metric", "weather_chmi_meteo_sunlight_10m_s", "values.SSV10M"),
        ],
        extra_labels={
            "job": "weather_chmi_meteo_station",
            "location_chmi_id": location_entry.chmi_id,
            "location_name": location_entry.name,
        },
    )

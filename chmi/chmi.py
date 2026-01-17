import requests

CHMI_ALADIN_URL = "https://data-provider.chmi.cz/api/graphs/graf.meteogram/{CHMI_LOCATION_ID}"
CHMI_STATION_TEMP_URL = "https://data-provider.chmi.cz/api/graphs/graf.meteo-stanice.teplota-10m/{CHMI_LOCATION_ID}"
CHMI_STATION_WIND_URL = "https://data-provider.chmi.cz/api/graphs/graf.meteo-stanice.vitr-10m/{CHMI_LOCATION_ID}"
CHMI_STATION_CLIM_URL = "https://data-provider.chmi.cz/api/graphs/graf.meteo-stanice.klima-10m/{CHMI_LOCATION_ID}"


def _fetch(uri, can_fail=False):
    resp = requests.get(uri)

    if can_fail and resp.status_code != 200:
        if resp.json()["message"].startswith("No data found"):
            return dict()
        else:
            raise RuntimeError(f"Failed to fetch data from CHMI API: {resp.status_code} {resp.text}")

    resp.raise_for_status()
    return resp.json()


def safe_value_merge(d: dict, key: str, values: dict):
    if key not in d:
        d[key] = dict()

    entry = d[key]
    for k, v in values.items():
        if k in entry and entry[k] != v and entry[k] is not None and v is not None:
            raise ValueError(f"Conflicting values in {key}, value {k}: {entry[k]} != {v}")
        entry[k] = v


def fetch_station(chmi_location_id):
    temp = _fetch(CHMI_STATION_TEMP_URL.format(CHMI_LOCATION_ID=chmi_location_id))
    clim = _fetch(CHMI_STATION_CLIM_URL.format(CHMI_LOCATION_ID=chmi_location_id))
    wind = _fetch(CHMI_STATION_WIND_URL.format(CHMI_LOCATION_ID=chmi_location_id), can_fail=True)

    # merge all the dictionaries into one, mimicking the same structure
    # merge all the data points per timestamp
    d = dict()
    for e in temp.get("dataPoints", []):
        d[e["timestamp"]] = e["values"]
    for e in wind.get("dataPoints", []):
        safe_value_merge(d, e["timestamp"], e["values"])
    for e in clim.get("dataPoints", []):
        safe_value_merge(d, e["timestamp"], e["values"])

    # merge legend
    legend = dict()
    legend.update(temp.get("dial", []))
    legend.update(wind.get("dial", []))
    legend.update(clim.get("dial", []))

    return [{"timestamp": k, "values": v} for k, v in d.items()], legend


def fetch_forecast(chmi_location_id):
    data = _fetch(CHMI_ALADIN_URL.format(CHMI_LOCATION_ID=chmi_location_id))
    return data["data"], data["parameters"]

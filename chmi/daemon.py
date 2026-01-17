import datetime
import loguru
import os
import sched
import sys
import time

from .processor import forecast as run_forecast, station as run_station
from .location_entry import LocationEntry

FORECAST_UPDATE_INTERVAL = 3600
STATION_UPDATE_INTERVAL = 600


def setup_logging(log_level):
    loguru.logger.remove()
    if "JOURNAL_STREAM" in os.environ:
        loguru.logger.add(sys.stdout, level=log_level)
    else:
        loguru.logger.add(sys.stderr, level=log_level)


class CHMIDaemon:
    def __init__(
        self,
        forecast_list,
        station_list,
        vm_baseurl,
        forecast_update_interval=FORECAST_UPDATE_INTERVAL,
        station_update_interval=STATION_UPDATE_INTERVAL,
        log_level="INFO",
    ):
        setup_logging(log_level)

        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._forecast = self._parse(forecast_list)
        self._station = self._parse(station_list)

        if self._forecast == [] and self._station == []:
            loguru.logger.error("No locations configured for forecast or meteo station data. Exiting.")
            sys.exit(1)

        self._forecast_int = int(forecast_update_interval) if forecast_update_interval is not None else FORECAST_UPDATE_INTERVAL
        self._station_int = int(station_update_interval) if station_update_interval is not None else STATION_UPDATE_INTERVAL
        self._vmbaseurl = vm_baseurl
        self._log_welcome()

    def run(self):
        for loc in self._forecast:
            self._scheduler.enter(0, 1, self._sched_forecast, (loc,))
        for loc in self._station:
            self._scheduler.enter(0, 1, self._sched_station, (loc,))

        self._scheduler.run()

    def _sched(self, name: str, fetch_fn, sched_fn, loc: LocationEntry, interval: int):
        loguru.logger.debug(f"Updating {name} data for {loc}")
        fetch_fn(loc, self._vmbaseurl)

        ev = self._scheduler.enter(interval, 1, sched_fn, (loc,))
        loguru.logger.debug(f"Scheduled next {name} update for {loc} at {datetime.datetime.fromtimestamp(ev.time)}")

    def _sched_forecast(self, loc: LocationEntry):
        return self._sched("forecast", run_forecast, self._sched_forecast, loc, self._forecast_int)

    def _sched_station(self, loc: LocationEntry):
        return self._sched("meteo station", run_station, self._sched_station, loc, self._station_int)

    def _parse(self, s: str|None):
        if s is None:
            return []

        elements = map(lambda e: e.split(":"), s.strip().split(","))
        elements = map(lambda e: LocationEntry(chmi_id=e[0], name=e[1]), elements)
        return list(elements)

    def _log_welcome(self):
        loguru.logger.info("Initialized CHMIDaemon")
        loguru.logger.info(f"VictoriaMetrics URL: {self._vmbaseurl}")
        loguru.logger.info(f"Forecast [update interval {self._forecast_int} seconds]")
        for loc in self._forecast:
            loguru.logger.info(f" - {loc}")
        loguru.logger.info(f"Meteo station data [update interval {self._station_int} seconds]")
        for loc in self._station:
            loguru.logger.info(f" - {loc}")

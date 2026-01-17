import chmi
import os

if __name__ == "__main__":
    d = chmi.CHMIDaemon(
        os.environ.get("CHMI_FORECAST", None),
        os.environ.get("CHMI_STATION", None),
        os.environ["CHMI_VM_BASEURL"],
        os.environ.get("CHMI_FORECAST_UPDATE_INTERVAL", None),
        os.environ.get("CHMI_STATION_UPDATE_INTERVAL", None),
        os.environ.get("CHMI_LOG_LEVEL", "INFO"),
    )
    d.run()

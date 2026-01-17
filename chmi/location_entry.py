import dataclasses


@dataclasses.dataclass
class LocationEntry:
    chmi_id: str
    name: str

    def __str__(self):
        return f"{self.name} ({self.chmi_id})"

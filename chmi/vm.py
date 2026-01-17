import requests
import urllib.parse


def url(baseurl: str, path: str):
    return urllib.parse.urljoin(baseurl, path)


def push(baseurl: str, data: str, metadata, labels):
    resp = requests.post(
        url(baseurl, "api/v1/import/csv"),
        data=data,
        params=[
            (
                "format",
                ",".join(f"{idx}:{type_}:{name}" for idx, (type_, name) in enumerate(metadata, 1)),
            ),
            ("extra_label", [f"{k}={v}" for k, v in labels.items()]),
        ],
    )
    resp.raise_for_status()

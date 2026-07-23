"""Testes do adaptador da API pública do F-Droid, sem depender da rede."""

from pathlib import Path
import sys

import httpx
import pytest


SOURCE_ROOT = Path(__file__).parents[1] / "src" / "gravity-store"
sys.path.insert(0, str(SOURCE_ROOT))

from infrastructure.providers.fdroid import FdroidApiError, FdroidClient


def make_client(handler):
    return FdroidClient(
        httpx.Client(transport=httpx.MockTransport(handler)),
        cache_ttl_seconds=300,
    )


def test_search_normalizes_the_official_search_response_and_caches_it() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "apps": [
                    {
                        "name": "Organic Maps",
                        "summary": "Offline maps",
                        "icon": "https://cdn.example/organic.png",
                        "url": "https://f-droid.org/en/packages/app.organicmaps",
                    },
                    {
                        "name": "Organic Maps duplicate",
                        "summary": "Duplicate",
                        "url": "https://f-droid.org/en/packages/app.organicmaps/",
                    },
                    {
                        "name": "Invalid package",
                        "summary": "Ignored",
                        "url": "https://f-droid.org/en/packages/not a package",
                    },
                ]
            },
        )

    client = make_client(handler)
    first_result = client.search("  maps  ")
    cached_result = client.search("MAPS", limit=1)

    assert len(requests) == 1
    assert requests[0].url.host == "search.f-droid.org"
    assert requests[0].url.params["q"] == "maps"
    assert first_result == [
        {
            "package_id": "app.organicmaps",
            "name": "Organic Maps",
            "summary": "Offline maps",
            "icon_url": "https://cdn.example/organic.png",
            "details_url": "https://f-droid.org/en/packages/app.organicmaps",
            "source_provider": "F-Droid",
            "category": "Código aberto",
            "version": None,
            "initials": "OM",
        }
    ]
    assert cached_result == first_result


def test_package_versions_prefers_the_suggested_version_and_caches_it() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "packageName": "org.example.app",
                "suggestedVersionCode": 20,
                "packages": [
                    {"versionName": "1.0.0", "versionCode": 10},
                    {"versionName": "2.0.0", "versionCode": 20},
                    {"versionName": "3.0.0-beta", "versionCode": 30},
                ],
            },
        )

    client = make_client(handler)
    result = client.package_versions("org.example.app")
    cached_result = client.package_versions("org.example.app")

    assert len(requests) == 1
    assert requests[0].url.path == "/api/v1/packages/org.example.app"
    assert result["latest_version"] == "2.0.0"
    assert result["versions"][0]["version_name"] == "3.0.0-beta"
    assert cached_result == result


def test_invalid_package_ids_do_not_generate_requests() -> None:
    client = make_client(lambda request: pytest.fail("a requisição não deveria ser feita"))

    with pytest.raises(FdroidApiError, match="identificador de pacote"):
        client.package_versions("../../etc/passwd")

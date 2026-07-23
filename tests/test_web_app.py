"""Testes de fumaça da interface e da API Flask."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


APP_FILE = Path(__file__).parents[1] / "src" / "gravity-store" / "app.py"
SPEC = spec_from_file_location("gravitystore_web", APP_FILE)
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeFdroidClient:
    def search(self, query: str) -> list[dict[str, str | None]]:
        return [
            {
                "name": "Maps Livre",
                "package_id": "org.example.maps",
                "summary": f"Resultado para {query}",
                "icon_url": None,
                "details_url": "https://f-droid.org/en/packages/org.example.maps",
                "source_provider": "F-Droid",
                "category": "Mapas",
                "version": None,
                "initials": "ML",
            }
        ]

    def package_versions(self, package_id: str) -> dict[str, object]:
        return {
            "package_id": package_id,
            "latest_version": "1.2.0",
            "suggested_version_code": 12,
            "versions": [{"version_name": "1.2.0", "version_code": 12}],
            "details_url": f"https://f-droid.org/en/packages/{package_id}",
        }


def make_client():
    return MODULE.create_app({"TESTING": True, "FDROID_CLIENT": FakeFdroidClient()}).test_client()


def test_homepage_keeps_the_modernized_legacy_sections() -> None:
    response = make_client().get("/")

    assert response.status_code == 200
    assert b"Gravity Store" in response.data
    assert b"Jogos livres" in response.data
    assert b"Organic Maps" in response.data


def test_search_and_version_endpoints_use_the_fdroid_client() -> None:
    client = make_client()

    search_response = client.get("/api/apps?q=mapas")
    version_response = client.get("/api/apps/org.example.maps")
    health_response = client.get("/health")

    assert search_response.status_code == 200
    assert search_response.json["data"][0]["name"] == "Maps Livre"
    assert search_response.json["meta"]["provider"] == "fdroid"
    assert version_response.json["data"]["latest_version"] == "1.2.0"
    assert health_response.status_code == 200
    assert health_response.json["providers"]["fdroid"] == "configured"


def test_search_endpoint_requires_a_query() -> None:
    response = make_client().get("/api/apps")

    assert response.status_code == 400
    assert response.json["error"] == "Informe o parâmetro de busca 'q'."

"""Cliente pequeno e defensivo para os endpoints públicos do F-Droid.

O F-Droid disponibiliza uma API de busca textual e uma API por pacote. A
primeira traz informações adequadas à listagem; a segunda é usada aqui para
consultar as versões publicadas de um pacote específico.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
import re
from threading import RLock
from time import monotonic
from typing import Any
from urllib.parse import urlparse

import httpx


SEARCH_URL = "https://search.f-droid.org/api/search_apps"
PACKAGE_URL = "https://f-droid.org/api/v1/packages/{package_id}"
PACKAGE_PAGE_URL = "https://f-droid.org/en/packages/{package_id}"
PACKAGE_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+$")


class FdroidApiError(RuntimeError):
    """Falha previsível de comunicação ou de contrato com a API do F-Droid."""


class FdroidInputError(FdroidApiError):
    """Parâmetro recebido pelo cliente não atende ao contrato da API."""


class FdroidNotFoundError(FdroidApiError):
    """O pacote solicitado não existe mais no catálogo ativo do F-Droid."""


@dataclass(frozen=True, slots=True)
class FdroidApp:
    """Representação normalizada de um resultado da busca F-Droid."""

    package_id: str
    name: str
    summary: str
    icon_url: str | None
    details_url: str
    source_provider: str = "F-Droid"
    category: str = "Código aberto"
    version: str | None = None

    @property
    def initials(self) -> str:
        words = [word for word in self.name.split() if word]
        return "".join(word[0] for word in words[:2]).upper() or "AP"

    def to_dict(self) -> dict[str, str | None]:
        data = asdict(self)
        data["initials"] = self.initials
        return data


class FdroidClient:
    """Consumidor com cache em memória para evitar consultas repetidas."""

    def __init__(
        self,
        http_client: httpx.Client | None = None,
        *,
        cache_ttl_seconds: float = 300,
    ) -> None:
        self._client = http_client or httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            follow_redirects=True,
            headers={"User-Agent": "GravityStore/0.1 (+https://github.com/)"},
        )
        self._owns_client = http_client is None
        self._cache_ttl_seconds = cache_ttl_seconds
        self._search_cache: dict[str, tuple[float, tuple[FdroidApp, ...]]] = {}
        self._package_cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self._lock = RLock()

    def close(self) -> None:
        """Fecha o cliente HTTP criado internamente, quando houver."""
        if self._owns_client:
            self._client.close()

    def search(self, query: str, *, limit: int = 20) -> list[dict[str, str | None]]:
        """Executa uma busca full-text no catálogo oficial do F-Droid."""
        normalized_query = query.strip()
        if not normalized_query:
            return []

        cache_key = normalized_query.casefold()
        cached = self._cached_search(cache_key)
        if cached is not None:
            return [app.to_dict() for app in cached[: self._clamp_limit(limit)]]

        payload = self._get_json(SEARCH_URL, params={"q": normalized_query})
        raw_apps = payload.get("apps")
        if not isinstance(raw_apps, list):
            raise FdroidApiError("A API de busca do F-Droid retornou um formato inesperado.")

        apps: list[FdroidApp] = []
        seen_packages: set[str] = set()
        for raw_app in raw_apps:
            if not isinstance(raw_app, Mapping):
                continue

            package_id = self._package_id_from_result(raw_app.get("url"))
            if not package_id or package_id in seen_packages:
                continue

            seen_packages.add(package_id)
            name = self._clean_text(raw_app.get("name")) or package_id
            summary = self._clean_text(raw_app.get("summary")) or "Aplicativo de código aberto no F-Droid."
            apps.append(
                FdroidApp(
                    package_id=package_id,
                    name=name,
                    summary=summary,
                    icon_url=self._safe_https_url(raw_app.get("icon")),
                    details_url=PACKAGE_PAGE_URL.format(package_id=package_id),
                )
            )

        self._store_search(cache_key, apps)
        return [app.to_dict() for app in apps[: self._clamp_limit(limit)]]

    def package_versions(self, package_id: str) -> dict[str, Any]:
        """Retorna a versão sugerida e as versões publicadas de um pacote."""
        self._validate_package_id(package_id)
        cached = self._cached_package(package_id)
        if cached is not None:
            return cached

        payload = self._get_json(PACKAGE_URL.format(package_id=package_id))
        response_package_id = self._clean_text(payload.get("packageName"))
        if response_package_id != package_id:
            raise FdroidApiError("A API do F-Droid respondeu com um pacote diferente do solicitado.")

        suggested_version_code = payload.get("suggestedVersionCode")
        raw_versions = payload.get("packages")
        if not isinstance(raw_versions, list):
            raise FdroidApiError("A API de versões do F-Droid retornou um formato inesperado.")

        versions = [
            {
                "version_name": self._clean_text(version.get("versionName")),
                "version_code": version.get("versionCode"),
            }
            for version in raw_versions
            if isinstance(version, Mapping) and self._clean_text(version.get("versionName"))
        ]
        versions.sort(key=lambda version: self._version_code(version["version_code"]), reverse=True)

        suggested = next(
            (version for version in versions if version["version_code"] == suggested_version_code),
            versions[0] if versions else None,
        )
        result: dict[str, Any] = {
            "package_id": package_id,
            "details_url": PACKAGE_PAGE_URL.format(package_id=package_id),
            "suggested_version_code": suggested_version_code,
            "latest_version": suggested["version_name"] if suggested else None,
            "versions": versions,
        }
        self._store_package(package_id, result)
        return result

    def _get_json(self, url: str, *, params: dict[str, str] | None = None) -> Mapping[str, Any]:
        try:
            response = self._client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 404:
                raise FdroidNotFoundError("O aplicativo não foi encontrado no catálogo ativo do F-Droid.") from error
            raise FdroidApiError("Não foi possível consultar o F-Droid no momento.") from error
        except (httpx.RequestError, ValueError) as error:
            raise FdroidApiError("Não foi possível consultar o F-Droid no momento.") from error

        if not isinstance(payload, Mapping):
            raise FdroidApiError("A API do F-Droid retornou um documento inválido.")
        return payload

    def _cached_search(self, key: str) -> tuple[FdroidApp, ...] | None:
        with self._lock:
            cached = self._search_cache.get(key)
            if not cached or monotonic() - cached[0] >= self._cache_ttl_seconds:
                return None
            return cached[1]

    def _store_search(self, key: str, apps: list[FdroidApp]) -> None:
        with self._lock:
            if len(self._search_cache) >= 128:
                self._search_cache.pop(next(iter(self._search_cache)))
            self._search_cache[key] = (monotonic(), tuple(apps))

    def _cached_package(self, package_id: str) -> dict[str, Any] | None:
        with self._lock:
            cached = self._package_cache.get(package_id)
            if not cached or monotonic() - cached[0] >= self._cache_ttl_seconds:
                return None
            return cached[1]

    def _store_package(self, package_id: str, result: dict[str, Any]) -> None:
        with self._lock:
            if len(self._package_cache) >= 128:
                self._package_cache.pop(next(iter(self._package_cache)))
            self._package_cache[package_id] = (monotonic(), result)

    @staticmethod
    def _package_id_from_result(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        path_parts = [part for part in urlparse(value).path.split("/") if part]
        try:
            package_id = path_parts[path_parts.index("packages") + 1]
        except (ValueError, IndexError):
            return None
        return package_id if PACKAGE_ID_PATTERN.fullmatch(package_id) else None

    @staticmethod
    def _clean_text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = " ".join(value.split())
        return cleaned or None

    @staticmethod
    def _safe_https_url(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        parsed = urlparse(value)
        if parsed.scheme != "https" or not parsed.netloc:
            return None
        return value

    @staticmethod
    def _clamp_limit(limit: int) -> int:
        return max(1, min(limit, 50))

    @staticmethod
    def _version_code(value: object) -> int:
        return value if isinstance(value, int) else -1

    @staticmethod
    def _validate_package_id(package_id: str) -> None:
        if not PACKAGE_ID_PATTERN.fullmatch(package_id):
            raise FdroidInputError("O identificador de pacote informado é inválido.")

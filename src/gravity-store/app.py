"""Aplicação web inicial do GravityStore."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import sys
from typing import Any

from flask import Flask, jsonify, render_template, request


PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    # A raiz atual usa ``gravity-store`` (com hífen), que não é importável como
    # pacote Python. Isto permite evoluir os módulos internos sem renomear a
    # estrutura do usuário durante esta etapa.
    sys.path.insert(0, str(PROJECT_ROOT))

from infrastructure.providers.fdroid import FdroidApiError, FdroidClient, FdroidInputError, FdroidNotFoundError


def _featured_app(
    name: str,
    package_id: str,
    category: str,
    summary: str,
) -> dict[str, str | None]:
    return {
        "name": name,
        "package_id": package_id,
        "category": category,
        "summary": summary,
        "icon_url": None,
        "details_url": f"https://f-droid.org/en/packages/{package_id}",
        "source_provider": "F-Droid",
        "version": None,
        "initials": "".join(part[0] for part in name.split()[:2]).upper(),
    }


FEATURED_COLLECTIONS: tuple[dict[str, Any], ...] = (
    {
        "title": "Para descobrir agora",
        "eyebrow": "Mais recentes",
        "description": "Uma seleção inicial enquanto o catálogo cresce.",
        "apps": (
            _featured_app("Organic Maps", "app.organicmaps", "Mapas", "Mapas offline para caminhar, pedalar e viajar."),
            _featured_app("AntennaPod", "de.danoeh.antennapod", "Áudio", "Podcasts, filas e downloads sem uma conta obrigatória."),
            _featured_app("KDE Connect", "org.kde.kdeconnect_tp", "Produtividade", "Integre o Android ao seu computador de forma simples."),
            _featured_app("KeePassDX", "com.kunzisoft.keepass.free", "Segurança", "Um cofre local e seguro para suas credenciais."),
        ),
    },
    {
        "title": "Jogos livres",
        "eyebrow": "Jogos",
        "description": "O espírito da antiga seção de jogos, agora com foco em software livre.",
        "apps": (
            _featured_app("Mindustry", "io.anuke.mindustry", "Estratégia", "Construa, defenda e automatize em um jogo de fábrica."),
            _featured_app("Unciv", "com.unciv.app", "Estratégia", "Um jogo de estratégia por turnos, aberto e expansível."),
        ),
    },
    {
        "title": "Para quem gosta de ajustar tudo",
        "eyebrow": "Avançado",
        "description": "Ferramentas abertas para explorar além do básico.",
        "apps": (
            _featured_app("Termux:API", "com.termux.api", "Ferramentas", "Recursos Android disponíveis para fluxos no Termux."),
            _featured_app("Amaze File Manager", "com.amaze.filemanager", "Arquivos", "Gerenciador de arquivos leve, aberto e direto."),
            _featured_app("Neo Store", "com.machiav3lli.fdroid", "Catálogo", "Outra forma de explorar repositórios F-Droid."),
        ),
    },
)


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Cria a aplicação Flask com busca real via F-Droid."""
    app = Flask(
        __name__,
        root_path=str(PROJECT_ROOT),
        template_folder="web/templates",
        static_folder="web/static",
    )
    app.config.from_mapping(
        APPLICATION_NAME="GravityStore",
        FDROID_CLIENT=None,
    )

    if test_config:
        app.config.update(test_config)

    fdroid_client = app.config["FDROID_CLIENT"] or FdroidClient()
    app.extensions["fdroid_client"] = fdroid_client

    @app.get("/")
    def index() -> str:
        query = request.args.get("q", "").strip()
        apps: list[dict[str, str | None]] = []
        search_error: str | None = None

        if query:
            try:
                apps = fdroid_client.search(query)
            except FdroidApiError:
                search_error = "Não foi possível alcançar o catálogo F-Droid agora. Tente novamente em instantes."

        return render_template(
            "index.html",
            query=query,
            apps=apps,
            collections=FEATURED_COLLECTIONS,
            showing_results=bool(query),
            search_error=search_error,
        )

    @app.get("/api/apps")
    def apps_api() -> Any:
        query = request.args.get("q", "").strip()
        if not query:
            return jsonify({"error": "Informe o parâmetro de busca 'q'."}), 400

        try:
            apps = fdroid_client.search(query)
        except FdroidApiError as error:
            return jsonify({"error": str(error), "provider": "fdroid"}), 502

        return jsonify(
            {
                "data": apps,
                "meta": {"query": query, "provider": "fdroid", "count": len(apps)},
            }
        )

    @app.get("/api/apps/<package_id>")
    def app_versions_api(package_id: str) -> Any:
        try:
            return jsonify({"data": fdroid_client.package_versions(package_id), "provider": "fdroid"})
        except FdroidInputError as error:
            return jsonify({"error": str(error), "provider": "fdroid"}), 400
        except FdroidNotFoundError as error:
            return jsonify({"error": str(error), "provider": "fdroid"}), 404
        except FdroidApiError as error:
            return jsonify({"error": str(error), "provider": "fdroid"}), 502

    @app.get("/health")
    def health() -> Any:
        return jsonify(
            {
                "status": "ok",
                "service": app.config["APPLICATION_NAME"],
                "providers": {"fdroid": "configured"},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    return app


if __name__ == "__main__":
    create_app().run(debug=True)

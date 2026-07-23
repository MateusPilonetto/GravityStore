import asyncio
from typing import List
from gravitystore.src.domain.provider import StoreProvider
from gravitystore.src.domain.entities import App

class GooglePlayProvider(StoreProvider):
    """A mock provider for Google Play."""

    @property
    def name(self) -> str:
        return "google_play"

    async def search(self, query: str) -> List[App]:
        print(f"[{self.name}] Searching for: {query}")
        # In a real implementation, this would use an HTTP client.
        await asyncio.sleep(0.5) # Simulate network latency
        if "maps" in query.lower():
            return [
                App(
                    package_id="com.google.android.apps.maps",
                    name="Google Maps",
                    version="11.124.0101",
                    author="Google LLC",
                    source_provider=self.name
                )
            ]
        return []

    async def details(self, package_id: str) -> App | None:
        print(f"[{self.name}] Getting details for: {package_id}")
        if package_id == "com.google.android.apps.maps":
            return App(package_id=package_id, name="Google Maps", version="11.124.0101", author="Google LLC", source_provider=self.name)
        return None

    async def download(self, package_id: str) -> str:
        print(f"[{self.name}] Downloading: {package_id}")
        return f"https://play.google.com/store/apps/details?id={package_id}"

    async def latest_version(self, package_id: str) -> str | None:
        print(f"[{self.name}] Getting latest version for: {package_id}")
        if package_id == "com.google.android.apps.maps":
            return "11.124.0101"
        return None


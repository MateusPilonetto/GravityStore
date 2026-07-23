# GravityStore

> A modular and extensible Python backend for discovering, searching and downloading Android applications from multiple repositories through a unified API.

<p align="center">
    <img src="docs/assets/logo.svg" alt="GravityStore Logo" width="180">
</p>

---

## Overview

GravityStore is an open-source project that provides a single interface for interacting with multiple Android application repositories.

Instead of implementing support for each repository separately, GravityStore abstracts every source behind a common provider interface, allowing applications to search, retrieve metadata and download apps through a unified API.

The project is designed to be modular, provider-based, and easily extensible.

---

## Goals

- Unified Android app catalog
- Provider-based architecture
- RESTful API
- Server-side rendered web interface
- Easy integration with new repositories
- Clean and maintainable architecture
- Developer-friendly SDK

---

## Supported Providers

| Provider | Status |
|----------|--------|
| Google Play | 🚧 Planned |
| F-Droid | Connected |
| GitHub Releases | 🚧 Planned |
| Custom Repository | 🚧 Planned |

---

# Architecture

```
                Browser
                   │
                   ▼
        Flask Web Application
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
     HTML Pages          REST API
        │                     │
        └──────────┬──────────┘
                   ▼
         Application Services
                   │
                   ▼
          Provider Registry
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
Google Play     F-Droid      GitHub Releases
    │              │              │
    └──────────────┼──────────────┘
                   ▼
             Unified Response
```

---

# Project Structure

```
gravitystore/

├── docs/
├── tests/
├── scripts/
├── src/
│
├── config/
├── domain/
├── application/
├── infrastructure/
├── api/
├── web/
├── cli/
└── shared/
```

---

# Core Components

## Domain

Contains the business entities and interfaces.

Examples:

- App
- Provider
- DownloadJob

No framework-specific code belongs here.

---

## Application

Contains the business logic.

Examples:

- Search applications
- Download applications
- Synchronize repositories
- Retrieve application details

Application services never communicate directly with external services.

---

## Infrastructure

Implements every external dependency.

Examples:

- Providers
- Cache
- Storage
- HTTP Client
- Retry logic

---

## Provider System

Every repository implements the same interface.

```python
class StoreProvider:

    async def search(self, query):
        ...

    async def details(self, package):
        ...

    async def download(self, package):
        ...

    async def latest_version(self, package):
        ...
```

This allows adding new repositories without modifying the application layer.

---

# Search Flow

```
Client

↓

SearchService

↓

ProviderRegistry

↓

Google Play
F-Droid
GitHub

↓

Normalize

↓

Merge

↓

Return Results
```

---

# Download Flow

```
Client

↓

DownloadService

↓

Provider

↓

Resolve APK

↓

Download

↓

Response
```

---

# Features

- Provider abstraction
- Unified search
- Unified metadata
- APK downloads
- Multiple repositories
- REST API
- Server-side rendering
- Modular architecture
- Extensible providers
- Automatic provider registry
- Cache support
- Background tasks

---

# Technologies

## Backend

- Python 3.12+
- Flask
- Werkzeug
- Jinja2

## HTTP

- httpx
- requests

## HTML Parsing

- BeautifulSoup4
- lxml

## Serialization

- Pydantic

## Cache

- Redis (optional)

## Background Tasks

- Celery (optional)

## Testing

- pytest
- pytest-cov

## Formatting

- Ruff
- Black

---

# Future Features

- OAuth authentication
- User accounts
- Favorites
- Download history
- Repository synchronization
- Automatic updates
- Plugin system
- Desktop client
- Android client

---

# Why GravityStore?

Most Android repositories expose different APIs and data formats.

GravityStore provides a unified abstraction layer that allows developers to interact with multiple repositories through a consistent interface.

Instead of learning every provider individually, applications communicate only with GravityStore.

---

# Roadmap

- [ ] Google Play provider
- [ ] F-Droid provider
- [ ] IzzyOnDroid provider
- [ ] GitHub Releases provider
- [ ] REST API
- [ ] Web interface
- [ ] Download manager
- [ ] Background workers
- [ ] Provider plugins
- [ ] Docker deployment

---

# Contributing

Contributions are welcome.

Feel free to open issues, submit pull requests or propose new providers.

---

# License

This project is licensed under the MIT License.
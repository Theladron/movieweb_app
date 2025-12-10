# Docker Setup for Movie Web App

This document explains how to run the Movie Web App in codio.


## Common Commands

### Start services
```bash
docker compose up
```

### Run Tests
```bash
# Run all tests
docker compose run --rm tests
```

### Rebuild containers if corrupted
```bash
docker compose down -v && docker compose up --build
```

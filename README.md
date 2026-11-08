# inventario-lab

Proyecto de clase para CI/CD con Jenkins, Python y GitHub
(Gestion del Software / Prueba y Calidad de Software).

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest --cov
```

- `infra/` : docker-compose con Jenkins + SonarQube
- `Jenkinsfile` : pipeline completo
- Ramas: `feature/*` -> PR a `develop` (staging) -> PR a `main` (produccion con aprobacion)

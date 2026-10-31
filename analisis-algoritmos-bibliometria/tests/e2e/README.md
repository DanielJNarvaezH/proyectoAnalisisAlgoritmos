# Pruebas E2E sobre la aplicacion desplegada

Playwright + pytest contra https://bibliometria-algoritmos.streamlit.app/

## Ejecutar
```bash
cd analisis-algoritmos-bibliometria/tests/e2e
pip install -r requirements-e2e.txt
playwright install chromium
pytest -m "not api"                    # contra el despliegue (APP_URL por defecto)
APP_URL=http://localhost:8501/ pytest  # contra una copia local (streamlit run app.py)
HEADED=1 SLOWMO=300 pytest -k flujo    # ver el navegador
API_URL=https://tu-backend pytest -m api   # opcional: backend Flask
```
Si una prueba falla se guarda una captura en `artifacts/`.

## Cobertura
| Archivo | Que prueba |
|---|---|
| test_modulos_e2e.py | Modulo 1 (similitud, 6 algoritmos), 2 (dendrogramas/particiones), 3 (busqueda), 4 (ranking) y validaciones de entrada |
| test_flujo_integrado.py | Flujo Ranking -> Busqueda -> Similitud -> Clustering en una sola sesion |
| test_api_backend.py | Endpoints Flask (solo con API_URL) |

`golden.py` contiene los valores esperados, calculados con el codigo de `src/`.
Si cambia el corpus o los embeddings, hay que regenerarlos.

## Notas
- Una app dormida en Streamlit Cloud tarda en despertar; el fixture pulsa
  "Yes, get this app back up!" y espera hasta 4 minutos.
- Las tablas `st.dataframe` son canvas y no se pueden leer desde el DOM; por eso
  se verifican mapas de calor, metricas, expanders y el CSV descargable.
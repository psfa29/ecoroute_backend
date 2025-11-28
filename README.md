# EcoRoute - Modo B (EXCLUSIVO: MST + UFDS + DFS)

Implementa la heurística **double-tree** usando **MST (Kruskal + UFDS)** y **recorridos en grafos (DFS)**.
Cumple 100% con la lista de técnicas aceptadas.

## Ejecutar

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Visita: http://127.0.0.1:8000/docs

## Endpoint

### POST /optimize_mst
**Entrada**
```json
{
  "depot": {"lat": -12.0464, "lng": -77.0428, "id": "Deposito"},
  "stops": [
    {"lat": -12.0521, "lng": -77.0455, "id": "C1", "address":"...","distrito":"..."},
    {"lat": -12.0631, "lng": -77.0301, "id": "C2"}
  ],
  "return_to_depot": true,
  "average_speed_kmh": 25.0,
  "liters_per_km": 0.4
}
```

**Salida**
- `order` (índices sobre [depot + stops])
- `legs` (tramos con km y minutos)
- `total_distance_km`, `total_duration_min`, `co2_kg`
- `geojson` (ruta en el orden DFS)
- `mst_geojson` (líneas del MST para tu visual de grafo)

## Cómo integrarlo con React (resumen)
- Filtra por **Distrito** tu CSV.
- Envía al endpoint `depot` + `stops` (solo del distrito).
- Dibuja `geojson` como Polyline (orden de visita).
- Superpone `mst_geojson` como líneas finas (grafo).
- Muestra el resumen: km, min, CO₂.

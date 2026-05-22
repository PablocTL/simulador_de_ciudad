# ARQUITECTURA DEL PROYECTO

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (APP)                        │
│                                                          │
│  Controla:                                             │
│  • Eventos (teclado, ratón)                           │
│  • Renderizado de UI y mapa                           │
│  • Estado de la aplicación                            │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┬─────────────────┬─────────────────┐
    │                 │                 │                 │
    ▼                 ▼                 ▼                 ▼
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
│algorithm│    │  models  │    │city_generator│    │ drawing  │
│         │    │          │    │              │    │  utils   │
│ dijkstra│    │ Grafo    │    │crear_ciudad  │    │glow_line │
│         │    │ Nodo     │    │guardar       │    │glow_circle│
└─────────┘    │ Arista   │    │cargar        │    │draw_text │
               └──────────┘    └──────────────┘    └──────────┘
                    │                │                   │
                    ▼                ▼                   ▼
              ┌──────────────────────────────────┐   ┌──────────┐
              │      config.py (Constantes)     │   │ui_comps  │
              │                                 │   │          │
              │ • Colores                      │   │TextInput │
              │ • FILAS, GRID_SIZE             │   │Button    │
              │ • NODE_*, EDGE_* colores       │   └──────────┘
              └─────────────────────────────────┘

```

## Flujo de Datos

```
Usuario Input (Eventos)
        │
        ▼
  handle_events()
        │
    ┌───┴────┬────────┬──────────────┐
    │        │        │              │
Teclas   Mouse   UI Eventos    Map Interactions
    │        │        │              │
    └───┬────┴────┬──────────┬───────┘
        │         │          │
        ▼         ▼          ▼
  Zoom/Pan  Calc Ruta   City Save/Load
        │         │          │
        └─────┬───┴──────┬───┘
              │          │
              ▼          ▼
         State Update   Dijkstra
              │          │
              └────┬─────┘
                   │
                   ▼
               draw() → Render
                   │
                   ▼
            pygame.display.flip()
```

## Dependencias de Módulos

```
ui_components.py
    ↑
    │ (importa)
    │
main.py ←────────┬────────────┬─────────────────┐
                 │            │                 │
                 ▼            ▼                 ▼
          algorithm.py   models.py         city_generator.py
                 │            │                 │
                 └────┬───────┴────────┬────────┘
                      │                │
                      ▼                ▼
                   config.py      (JSON files)
                      │
                      └─ drawing_utils.py
```

## Estado de la Aplicación

```
App
├── Grafo
│   ├── Nodos []
│   └── Aristas []
│
├── Ruta (ResultadoRuta)
│   ├── origen
│   ├── destino
│   ├── camino []
│   ├── coste
│   └── encontrada
│
├── UI State
│   ├── current_tab (0-3)
│   ├── selected_node
│   ├── click_origen
│   └── show_labels
│
├── Cámara
│   ├── cell_size
│   └── map_offset
│
└── Componentes UI
    ├── inp_nombre_ciudad (TextInput)
    ├── btn_guardar (Button)
    └── log_lines []
```

## Ciclo de Vida de una Búsqueda

```
1. Usuario hace click (origen)
   └─ click_origen = nodo

2. Usuario hace click (destino)
   └─ _calcular_ruta(origen, destino)
      └─ dijkstra(grafo, origen, destino)
         ├─ Inicializar distancias
         ├─ Procesar nodos con heap
         ├─ Reconstruir camino
         └─ Retorna ResultadoRuta
      └─ self.ruta = resultado
      └─ _log("Ruta encontrada...")

3. draw() dibuja:
   └─ Aristas normales
   └─ Aristas de ruta (con glow)
   └─ Nodos
   └─ Labels en ruta
```

## Tabla de Complejidades

| Operación | Complejidad | Notas |
|-----------|------------|-------|
| Dijkstra | O((V+E)logV) | Con heap binario |
| Dibujo mapa | O(V+E) | Una vez por frame |
| Guardar ciudad | O(V+E) | Serialización JSON |
| Cargar ciudad | O(V+E) | Deserialización JSON |
| Buscar nodo por pantalla | O(1) | Cálculo directo |
| Aplicar tráfico | O(E) | Búsqueda en aristas |

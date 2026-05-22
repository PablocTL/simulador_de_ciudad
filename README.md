# SIMULADOR DE CIUDAD – GRAFOS

Aplicación interactiva de visualización y búsqueda de rutas en una ciudad representada como grafo.

## Estructura del Proyecto

```
.
├── main.py                 # Aplicación principal y UI
├── algorithm.py            # Algoritmo de Dijkstra
├── models.py              # Modelos de datos (Grafo, Nodo, Arista)
├── config.py              # Configuración y constantes
├── city_generator.py      # Generador de ciudades y persistencia
├── drawing_utils.py       # Utilidades de dibujo
├── ui_components.py       # Componentes de interfaz
└── README.md              # Este archivo
```

## Componentes

### 1. **config.py**
- Paleta de colores
- Constantes de la ciudad (GRID_SIZE, FILAS)
- Colores de nodos y aristas

### 2. **models.py**
Contiene las estructuras de datos fundamentales:
- `Nodo`: Representa una intersección, base o empresa
- `Arista`: Representa una calle con peso y tráfico
- `Grafo`: Estructura de adyacencia
- `ResultadoRuta`: Resultado de la búsqueda

### 3. **algorithm.py**
- `dijkstra()`: Implementación del algoritmo de Dijkstra
  - Encuentra el camino más corto entre dos nodos
  - Considera el tráfico (peso efectivo)

### 4. **city_generator.py**
- `crear_ciudad_20x20()`: Genera grilla 20×20 con pesos
- `cargar_ciudad_prueba()`: Carga bases, empresas y tráfico
- `guardar_ciudad()`: Persiste ciudad en JSON
- `cargar_ciudad_json()`: Carga ciudad desde archivo
- `listar_ciudades()`: Lista ciudades guardadas

### 5. **drawing_utils.py**
Funciones de dibujo:
- `draw_text()`: Dibuja texto
- `glow_line()`: Línea con efecto glow
- `glow_circle()`: Círculo con efecto glow
- `draw_button()`: Botón
- `draw_panel()`: Panel

### 6. **ui_components.py**
Componentes reutilizables:
- `TextInput`: Campo de entrada de texto
- `Button`: Botón interactivo

### 7. **main.py**
Aplicación principal:
- `App`: Clase que maneja toda la interfaz
- Loop principal de eventos, actualización y dibujo

## Uso

### Instalación
```bash
pip install pygame
```

### Ejecución
```bash
python main.py
```

## Controles

| Tecla | Acción |
|-------|--------|
| 1-4 | Cambiar pestaña |
| ESPACIO | Mostrar/ocultar etiquetas |
| Flechas ← → | Mover mapa izquierda/derecha |
| Flechas ↑ ↓ | Mover mapa arriba/abajo |
| W/S | Mover mapa vertical |
| ↑/↓ | Zoom in/out |
| R | Limpiar ruta |
| ESC | Salir |

## Interacción

### Búsqueda de Rutas
1. **Primer click izquierdo**: Selecciona origen (se marca en amarillo)
2. **Segundo click izquierdo**: Selecciona destino y calcula ruta
3. La ruta se muestra en cian con efecto glow

### Interfaz
- **Tab 1 (INFO)**: Controles y datos del grafo
- **Tab 2 (NODOS)**: Listado de nodos especiales
- **Tab 3 (CIUDADES)**: Guardar/cargar ciudades
- **Tab 4 (LOG)**: Registro de eventos

## Características

✓ Algoritmo de Dijkstra optimizado con heap  
✓ Visualización en tiempo real del grafo  
✓ Persistencia de ciudades en JSON  
✓ Sistema de tráfico dinámico  
✓ Interfaz con pestañas  
✓ Efectos glow neon  
✓ Zoom y pan del mapa  

## Estructura de Datos - Ejemplo JSON

```json
{
  "nodos": [
    {
      "nombre": "A1",
      "tipo": "base",
      "x": 0,
      "y": 0
    }
  ],
  "aristas": [
    {
      "origen": "A1",
      "destino": "A2",
      "peso_base": 1.0,
      "trafico": 1.0
    }
  ]
}
```

## Complejidad

- **Dijkstra**: O((V + E) log V) con heap
- **Dibujo**: O(V + E) por frame
- **Persistencia**: O(V + E) al guardar/cargar

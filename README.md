# Proyecto 4 — Árbol de Expansión Mínima  
## Algoritmos de Kruskal (directo e inverso) y Prim

En este proyecto se implementan los algoritmos clásicos para el cálculo del **Árbol de Expansión Mínima (Minimum Spanning Tree, MST)**:

- **Kruskal directo**
- **Kruskal inverso (reverse-delete)**
- **Prim**

La implementación se realiza **utilizando la biblioteca de grafos desarrollada en el Proyecto 1**, la cual **no es modificada**.  
En su lugar, se extiende la clase `Grafo` para incorporar pesos y los algoritmos de MST.

---

## Objetivo

Implementar y comparar distintos algoritmos de MST sobre grafos generados a partir de diferentes modelos clásicos, verificando:

- Correctitud de los algoritmos
- Consistencia entre métodos
- Comportamiento en grafos pequeños y grandes
- Diferencias en modelos que no garantizan conectividad

---

## Estructura del proyecto

```text
Proyecto-4/
│
├── lib/
│   └── Biblioteca-grafos/        # Proyecto 1 (submódulo, SIN modificaciones)
│
├── src/
│   └── grafo_mst.py              # Extensión de Grafo con pesos + MST
│
├── scripts/
│   ├── generar_grafos.py         # Generación de grafos ponderados
│   ├── generar_mst.py            # Cálculo de MST (KruskalD, KruskalI, Prim)
│   └── gephi_batch_export.py     # Exportación automática de imágenes (Gephi)
│
├── outputs/
│   ├── gv/
│   │   ├── generados/            # Grafos originales (.gv)
│   │   └── mst/                  # Árboles MST calculados (.gv)
│   │
│   ├── img/
│   │   ├── generados/            # Visualizaciones de grafos originales (.png)
│   │   └── mst/                  # Visualizaciones de MST (.png)
│   │
│   └── mst_valores/              # Valores numéricos del MST (.txt)
│
├── tests/
│
└── README.md
``` 

##Modelos de grafos utilizados

Se generan grafos a partir de seis modelos clásicos, implementados en el Proyecto 1:

    Malla

    Erdős–Rényi

    Gilbert

    Geográfico

    Barabási–Albert

    Dorogovtsev–Mendes

Para cada modelo se generan dos tamaños:

    *_pocos : grafo pequeño

    *_muchos: grafo grande

Total de grafos generados:

    6 modelos × 2 tamaños = 12 grafos base 


## Grafos calculados

Para cada grafo base se calculan:

    Árbol de expansión mínima con Kruskal directo

    Árbol de expansión mínima con Kruskal inverso

    Árbol de expansión mínima con Prim

Total de grafos calculados:

    12 grafos base × 3 algoritmos = 36 grafos MST

## Implementación
Extensión de la clase Grafo

La clase GrafoMST (en src/grafo_mst.py) extiende la clase Grafo del Proyecto 1 y añade:

    Manejo de pesos de aristas

    Métodos:

        KruskalD(self)

        KruskalI(self)

        Prim(self)

De esta forma, el Proyecto 1 permanece completamente intacto. 

## Archivos .txt de valores del MST

En la carpeta:

    outputs/mst_valores/


se generan archivos .txt que contienen el valor total del MST, por ejemplo:

    malla_pocos KruskalD
    TOTAL_MST = 1142.0


Estos archivos sirven para:

    Evidencia numérica del resultado del algoritmo

    Comparación entre métodos

    Capturas de pantalla solicitadas en el entregable 

## Visualización (Gephi)

Todos los grafos se visualizan automáticamente usando Gephi 0.10.x mediante un script en Jython.

Pipeline aplicado

Para cada grafo:

    Inicialización aleatoria de posiciones

    ForceAtlas2 sin prevenir overlap

    Ajuste de tamaño de nodos:

        Grafos generados: tamaño proporcional al grado

        Grafos MST: tamaño fijo

    ForceAtlas2 con prevención de overlap

    Activación de labels:

        Grafos generados: pesos en aristas

        Grafos MST: nodos y pesos

    Exportación a PNG 


##  Ejecución
1) Generar grafos ponderados
    python scripts/generar_grafos.py

2) Calcular MST
    python scripts/generar_mst.py

3) Exportar imágenes con Gephi

En el Jython shell de Gephi:

    execfile(r"K:\scripts\gephi_batch_export.py")

## Autor

    Daniel Vázquez
    Maestría en Ciencias de la Computación
    Instituto Politécnico Nacional (CIC-IPN)

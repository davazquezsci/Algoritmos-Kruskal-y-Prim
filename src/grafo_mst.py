from __future__ import annotations
import sys
from pathlib import Path
import heapq

# ============================================================
# Localizar Proyecto 1 (Biblioteca de grafos)
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
P1_SRC = ROOT / "lib" / "Biblioteca-grafos" / "src"
sys.path.insert(0, str(P1_SRC))

from grafo import Grafo


# ============================================================
# Union-Find (Disjoint Set Union)
# ============================================================

class DSU:
    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


# ============================================================
# GrafoMST (extiende Grafo del Proyecto 1)
# ============================================================

class GrafoMST(Grafo):
    """
    Extensión de Grafo (Proyecto 1) para manejar pesos
    y calcular Árboles de Expansión Mínima.
    """

    def __init__(self, dirigido: bool = False):
        super().__init__(dirigido=dirigido)
        self._peso = {}   # (u, v) -> w  (normalizado)

    # ------------------ Pesos ------------------

    def _key(self, u, v):
        if self.dirigido:
            return (u, v)
        return (u, v) if u <= v else (v, u)

    def add_arista_peso(self, u, v, w: float) -> bool:
        ok = super().add_arista(u, v)
        if ok:
            self._peso[self._key(u, v)] = float(w)
        return ok

    def peso_arista(self, u, v) -> float:
        return self._peso[self._key(u, v)]

    def aristas_con_peso(self):
        return [
            (u, v, self._peso[self._key(u, v)])
            for (u, v) in self._aristas_key
        ]

    # ------------------ Exportación DOT ------------------

    def to_graphviz_ponderado(self, path: str):
        sep = "->" if self.dirigido else "--"
        header = "digraph G {" if self.dirigido else "graph G {"

        lines = [header]

        for n in self.nodos():
            if n.x is not None and n.y is not None:
                lines.append(f'"{n.id}" [pos="{n.x},{n.y}!"];')
            else:
                lines.append(f'"{n.id}";')

        for u, v, w in self.aristas_con_peso():
            lines.append(f'"{u}" {sep} "{v}" [label="{int(w)}"];')

        lines.append("}")

        Path(path).write_text("\n".join(lines), encoding="utf-8")

    # =====================================================
    # KRUSKAL DIRECTO
    # =====================================================

    def KruskalD(self):
        if self.dirigido:
            raise ValueError("Kruskal requiere grafo no dirigido")

        T = GrafoMST(False)
        for n in self.nodos():
            T.add_nodo(n.id, x=n.x, y=n.y)

        dsu = DSU([n.id for n in]()

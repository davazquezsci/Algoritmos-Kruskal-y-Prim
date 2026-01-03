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
    y calcular Árboles de Expansión Mínima (MST).
    """

    def __init__(self, dirigido: bool = False):
        super().__init__(dirigido=dirigido)
        self._peso = {}   # (u, v) -> w (normalizado)

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
        return [(u, v, self._peso[self._key(u, v)]) for (u, v) in self._aristas_key]

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
            wlab = int(w) if abs(w - int(w)) < 1e-9 else w
            lines.append(f'"{u}" {sep} "{v}" [label="{wlab}"];')

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

        dsu = DSU([n.id for n in self.nodos()])
        total = 0.0

        for u, v, w in sorted(self.aristas_con_peso(), key=lambda e: e[2]):
            if dsu.union(u, v):
                T.add_arista_peso(u, v, w)
                total += w
                if T.numero_aristas() == T.numero_nodos() - 1:
                    break

        return T, total

    # =====================================================
    # KRUSKAL INVERSO (Reverse Delete)
    # =====================================================

    def KruskalI(self):
        if self.dirigido:
            raise ValueError("Kruskal requiere grafo no dirigido")

        # Copia completa
        H = GrafoMST(False)
        for n in self.nodos():
            H.add_nodo(n.id, x=n.x, y=n.y)
        for u, v, w in self.aristas_con_peso():
            H.add_arista_peso(u, v, w)

        def conectado(g: "GrafoMST") -> bool:
            nodos = [n.id for n in g.nodos()]
            if not nodos:
                return True
            visit = {nodos[0]}
            stack = [nodos[0]]

            while stack:
                u = stack.pop()
                for nb in g.vecinos(u):
                    if nb.id not in visit:
                        visit.add(nb.id)
                        stack.append(nb.id)

            return len(visit) == len(nodos)

        # eliminar aristas más pesadas si no desconectan
        for u, v, w in sorted(H.aristas_con_peso(), key=lambda e: e[2], reverse=True):
            tmp = GrafoMST(False)
            for n in H.nodos():
                tmp.add_nodo(n.id, x=n.x, y=n.y)

            for a, b, ww in H.aristas_con_peso():
                if (a == u and b == v) or (a == v and b == u):
                    continue
                tmp.add_arista_peso(a, b, ww)

            if conectado(tmp):
                H = tmp

            if H.numero_aristas() == H.numero_nodos() - 1:
                break

        total = sum(w for _, _, w in H.aristas_con_peso())
        return H, total

    # =====================================================
    # PRIM
    # =====================================================

    def Prim(self, start=None):
        if self.dirigido:
            raise ValueError("Prim requiere grafo no dirigido")

        nodos = [n.id for n in self.nodos()]
        if not nodos:
            return GrafoMST(False), 0.0

        if start is None:
            start = nodos[0]
        if start not in self._nodos:
            raise KeyError(f"El nodo fuente {start} no existe")

        T = GrafoMST(False)
        for n in self.nodos():
            T.add_nodo(n.id, x=n.x, y=n.y)

        visit = {start}
        heap = []
        total = 0.0

        def push(u):
            for nb in self.vecinos(u):
                v = nb.id
                if v not in visit:
                    heapq.heappush(heap, (self.peso_arista(u, v), u, v))

        push(start)

        while heap and len(visit) < len(nodos):
            w, u, v = heapq.heappop(heap)
            if v in visit:
                continue
            visit.add(v)
            T.add_arista_peso(u, v, w)
            total += w
            push(v)

        return T, total

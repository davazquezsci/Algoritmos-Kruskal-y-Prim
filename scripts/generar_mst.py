from __future__ import annotations
import sys
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(ROOT / "src"))
from grafo_mst import GrafoMST

P1_SRC = ROOT / "lib" / "Biblioteca-grafos" / "src"
sys.path.insert(0, str(P1_SRC))
import modelos

OUT_GV_MST = ROOT / "outputs" / "gv" / "mst"
OUT_TXT    = ROOT / "outputs" / "mst_valores"
OUT_GV_MST.mkdir(parents=True, exist_ok=True)
OUT_TXT.mkdir(parents=True, exist_ok=True)

def convertir_y_ponderar(g_base, seed: int, wmin: int = 1, wmax: int = 99) -> GrafoMST:
    rng = random.Random(seed)
    g = GrafoMST(False)
    for n in g_base.nodos():
        g.add_nodo(n.id, x=n.x, y=n.y)
    for (u, v) in g_base._aristas_key:
        g.add_arista_peso(u, v, rng.randint(wmin, wmax))
    return g

def guardar_valor(path: Path, titulo: str, total: float):
    path.write_text(f"{titulo}\nTOTAL_MST = {total}\n", encoding="utf-8")

def casos():
    return [
        ("malla_pocos",  lambda: modelos.grafoMalla(6, 6, dirigido=False),               101),
        ("malla_muchos", lambda: modelos.grafoMalla(22, 22, dirigido=False),             102),

        ("erdos_pocos",  lambda: modelos.grafoErdosRenyi(30, 60, False, seed=1),         201),
        ("erdos_muchos", lambda: modelos.grafoErdosRenyi(500, 2000, False, seed=2),      202),

        ("gilbert_pocos",lambda: modelos.grafoGilbert(30, 0.15, False, seed=1),          301),
        ("gilbert_muchos",lambda: modelos.grafoGilbert(500, 0.02, False, seed=2),        302),

        ("geo_pocos",    lambda: modelos.grafoGeografico(30, 0.25, False, seed=1),       401),
        ("geo_muchos",   lambda: modelos.grafoGeografico(500, 0.08, False, seed=2),      402),

        ("ba_pocos",     lambda: modelos.grafoBarabasiAlbert(30, 3, False, seed=1),      501),
        ("ba_muchos",    lambda: modelos.grafoBarabasiAlbert(500, 3, False, seed=2),     502),

        ("dm_pocos",     lambda: modelos.grafoDorogovtsevMendes(30, False, seed=1),      601),
        ("dm_muchos",    lambda: modelos.grafoDorogovtsevMendes(500, False, seed=2),     602),
    ]

def main():
    for nombre, builder, seed in casos():
        base = builder()
        g = convertir_y_ponderar(base, seed=seed, wmin=1, wmax=99)

        kd, tkd = g.KruskalD()
        ki, tki = g.KruskalI()
        pr, tpr = g.Prim()

        kd_gv = OUT_GV_MST / f"{nombre}_kruskalD.gv"
        ki_gv = OUT_GV_MST / f"{nombre}_kruskalI.gv"
        pr_gv = OUT_GV_MST / f"{nombre}_prim.gv"

        kd.to_graphviz_ponderado(str(kd_gv))
        ki.to_graphviz_ponderado(str(ki_gv))
        pr.to_graphviz_ponderado(str(pr_gv))

        guardar_valor(OUT_TXT / f"{nombre}_kruskalD.txt", f"{nombre} KruskalD", tkd)
        guardar_valor(OUT_TXT / f"{nombre}_kruskalI.txt", f"{nombre} KruskalI", tki)
        guardar_valor(OUT_TXT / f"{nombre}_prim.txt",     f"{nombre} Prim",     tpr)

        # sanity check
        ok = (abs(tkd - tki) < 1e-9) and (abs(tkd - tpr) < 1e-9)
        print("[OK]" if ok else "[WARN]", nombre, "KD=", tkd, "KI=", tki, "PR=", tpr)

if __name__ == "__main__":
    main()

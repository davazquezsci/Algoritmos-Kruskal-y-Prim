# -*- coding: utf-8 -*-
# Gephi Scripting Plugin (Jython 2.5)
# Batch: importar .gv, layouts + appearance ranking, exportar PNG
# PROYECTO 4:
#   - inputs: outputs/gv/generados/*.gv  y  outputs/gv/mst/*.gv
#   - outputs: outputs/img/generados/*.png  y  outputs/img/mst/*.png
# Labels (forzados en el grafo):
#   - Node labels: ID del nodo
#   - Edge labels: peso (edge.getWeight())
# Preview:
#   - Generados: edge labels ON, node labels OFF
#   - MST: node labels ON, edge labels ON
# Node size:
#   - Generados: Ranking Degree size 5..40
#   - MST: Size fijo 10

print("=== START gephi_batch_export (Proyecto 4) ===")

import os
from java.io import File
from org.openide.util import Lookup

from org.gephi.project.api import ProjectController
from org.gephi.io.importer.api import ImportController
from org.gephi.io.processor.plugin import DefaultProcessor
from org.gephi.graph.api import GraphController

# Layouts
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2
from org.gephi.layout.plugin.forceAtlas2 import ForceAtlas2Builder

from java.util import Random as JRandom

# Preview + Export
from org.gephi.preview.api import PreviewController
from org.gephi.io.exporter.api import ExportController

# Font/Color
from java.awt import Color, Font


# ---- AJUSTA ESTO A TU RUTA CORTA (alias) ----
# Ejemplo:
# ROOT = r"P:\Algoritmos-Kruskal-y-Prim"
#ROOT = r"C:\Users\dangv\OneDrive - Instituto Politecnico Nacional\Ciencias de la Computacion\MCC\Diseño de algoritmos\Proyectos\Proyecto 4\Algoritmos-Kruskal-y-Prim"
ROOT = r"K:\\"



GV_GENERADOS = File(ROOT, "outputs\\gv\\generados")
GV_MST       = File(ROOT, "outputs\\gv\\mst")

IMG_GENERADOS = File(ROOT, "outputs\\img\\generados")
IMG_MST       = File(ROOT, "outputs\\img\\mst")

print("ROOT =", ROOT)
print("GV_GENERADOS =", GV_GENERADOS.getAbsolutePath(), "exists?", GV_GENERADOS.exists(), "isDir?", GV_GENERADOS.isDirectory())
print("GV_MST       =", GV_MST.getAbsolutePath(),       "exists?", GV_MST.exists(),       "isDir?", GV_MST.isDirectory())
print("IMG_GENERADOS =", IMG_GENERADOS.getAbsolutePath(), "exists?", IMG_GENERADOS.exists(), "isDir?", IMG_GENERADOS.isDirectory())
print("IMG_MST       =", IMG_MST.getAbsolutePath(),       "exists?", IMG_MST.exists(),       "isDir?", IMG_MST.isDirectory())

FA2_ITERS_1 = 400
FA2_ITERS_2 = 400


def ensure_dir(path_or_file):
    if isinstance(path_or_file, File):
        if not path_or_file.exists():
            path_or_file.mkdirs()
    else:
        if not os.path.exists(path_or_file):
            os.makedirs(path_or_file)


def is_tree_like(name):
    name = name.lower()
    # en P4, todo lo que venga de mst es un árbol
    return ("_kruskal" in name) or ("_prim" in name) or ("_mst" in name)


def randomize_positions(workspace, seed=1337, scale=1000.0):
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()
    rng = JRandom(seed)

    graph.writeLock()
    try:
        it = graph.getNodes().iterator()
        while it.hasNext():
            n = it.next()
            x = (rng.nextDouble() - 0.5) * scale
            y = (rng.nextDouble() - 0.5) * scale
            n.setX(float(x))
            n.setY(float(y))
    finally:
        graph.writeUnlock()


def run_forceatlas2(workspace, iters, prevent_overlap):
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)

    fa2 = ForceAtlas2(ForceAtlas2Builder())
    fa2.setGraphModel(graphModel)

    fa2.setScalingRatio(2.0)
    fa2.setGravity(1.0)
    fa2.setStrongGravityMode(False)
    fa2.setLinLogMode(False)

    fa2.setAdjustSizes(True if prevent_overlap else False)

    fa2.initAlgo()
    for i in range(iters):
        fa2.goAlgo()
    fa2.endAlgo()


def apply_degree_size_ranking(workspace, min_size, max_size):
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    degrees = {}
    deg_min = None
    deg_max = None

    it = graph.getNodes().iterator()
    while it.hasNext():
        n = it.next()
        d = n.getInDegree() + n.getOutDegree()
        degrees[n.getId()] = d
        if deg_min is None or d < deg_min:
            deg_min = d
        if deg_max is None or d > deg_max:
            deg_max = d

    denom = float(deg_max - deg_min) if (deg_max is not None and deg_min is not None and deg_max != deg_min) else 1.0
    span = float(max_size - min_size)

    graph.writeLock()
    try:
        it2 = graph.getNodes().iterator()
        while it2.hasNext():
            n = it2.next()
            d = degrees.get(n.getId(), 0)
            t = float(d - deg_min) / denom
            size = float(min_size + t * span)
            n.setSize(size)
    finally:
        graph.writeUnlock()


def force_labels(workspace, want_node_labels, want_edge_labels):
    """
    Garantiza que existan labels reales en el grafo:
    - Nodos: label = id (para que Preview los muestre)
    - Aristas: label = peso (edge.getWeight()) con 2 decimales
    """
    graphModel = Lookup.getDefault().lookup(GraphController).getGraphModel(workspace)
    graph = graphModel.getGraphVisible()

    graph.writeLock()
    try:
        if want_node_labels:
            itn = graph.getNodes().iterator()
            while itn.hasNext():
                n = itn.next()
                if n.getLabel() is None or len(n.getLabel()) == 0:
                    n.setLabel(str(n.getId()))

        if want_edge_labels:
            ite = graph.getEdges().iterator()
            while ite.hasNext():
                e = ite.next()
                w = e.getWeight()
                e.setLabel("%.2f" % float(w))
    finally:
        graph.writeUnlock()


def configure_preview(workspace, tree_mode, show_node_labels, show_edge_labels):
    previewController = Lookup.getDefault().lookup(PreviewController)
    previewModel = previewController.getModel(workspace)
    props = previewModel.getProperties()

    # Estilo de aristas
    props.putValue("edgeCurved", (not tree_mode))
    props.putValue("edgeThickness", 0.3 if not tree_mode else 0.9)

    # Node labels
    props.putValue("showNodeLabels", True if show_node_labels else False)
    props.putValue("nodeLabelFont", Font("Serif", Font.PLAIN, 20))
    props.putValue("nodeLabelColor", Color(255, 255, 255))
    props.putValue("nodeLabelOutlineSize", 1.0)
    props.putValue("nodeLabelOutlineColor", Color(0, 0, 0))
    props.putValue("nodeLabelBox", True)
    props.putValue("nodeLabelBoxOpacity", 0.0)

    # Edge labels (pesos)
    props.putValue("showEdgeLabels", True if show_edge_labels else False)
    props.putValue("edgeLabelFont", Font("Serif", Font.ITALIC, 14))
    props.putValue("edgeLabelColor", Color(0, 0, 0))
    props.putValue("edgeLabelOutlineSize", 0.0)

    previewController.refreshPreview(workspace)


def export_png(workspace, out_file):
    exportController = Lookup.getDefault().lookup(ExportController)
    pngExporter = exportController.getExporter("png")
    if isinstance(out_file, File):
        exportController.exportFile(out_file, pngExporter)
    else:
        exportController.exportFile(File(out_file), pngExporter)


def process_flat_dir(gv_dir, img_dir, category_name):
    pc = Lookup.getDefault().lookup(ProjectController)
    importController = Lookup.getDefault().lookup(ImportController)

    if not gv_dir.exists():
        print("No existe:", gv_dir.getAbsolutePath())
        return

    ensure_dir(img_dir)

    gv_files = [f for f in gv_dir.listFiles()
                if f.isFile() and f.getName().lower().endswith(".gv")]
    gv_files.sort(key=lambda f: f.getName().lower())

    for gv_file in gv_files:
        name = gv_file.getName()[:-3]  # sin .gv
        out_png = File(img_dir, name + ".png")

        print("[%s] Importando:" % category_name, gv_file.getAbsolutePath())

        pc.newProject()
        workspace = pc.getCurrentWorkspace()

        container = importController.importFile(gv_file)
        importController.process(container, DefaultProcessor(), workspace)

        tree_mode = is_tree_like(name)

        # 1) Random positions
        randomize_positions(workspace, seed=1337, scale=1000.0)

        # 2) FA2 sin overlap
        run_forceatlas2(workspace, FA2_ITERS_1, prevent_overlap=False)

        # 3) Tamaño por categoría
        if category_name == "generados":
            apply_degree_size_ranking(workspace, 5.0, 40.0)
        else:
            apply_degree_size_ranking(workspace, 10.0, 10.0)

        # 4) FA2 con overlap
        run_forceatlas2(workspace, FA2_ITERS_2, prevent_overlap=True)

        # Preview + labels forzados:
        if category_name == "generados":
            # Solo pesos
            force_labels(workspace, want_node_labels=False, want_edge_labels=True)
            configure_preview(workspace, tree_mode, show_node_labels=False, show_edge_labels=True)
        else:
            # MST: nodos + pesos
            force_labels(workspace, want_node_labels=True, want_edge_labels=True)
            configure_preview(workspace, tree_mode, show_node_labels=True, show_edge_labels=True)

        export_png(workspace, out_png)
        print("[%s] Exportado:" % category_name, out_png.getAbsolutePath())


def main():
    process_flat_dir(GV_GENERADOS, IMG_GENERADOS, "generados")
    process_flat_dir(GV_MST,       IMG_MST,       "mst")
    print("DONE.")


try:
    main()
    print("=== END gephi_batch_export (Proyecto 4) ===")
except Exception:
    import traceback
    err = traceback.format_exc()
    print(err)
    ensure_dir(File(ROOT, "scripts"))
    f = open(os.path.join(ROOT, "scripts", "gephi_batch_error.txt"), "w")
    f.write(err)
    f.close()
    print("ERROR guardado en", os.path.join(ROOT, "scripts", "gephi_batch_error.txt"))
    print("=== END gephi_batch_export (Proyecto 4) ===")

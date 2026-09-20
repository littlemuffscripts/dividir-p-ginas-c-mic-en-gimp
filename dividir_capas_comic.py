#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import gi

gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
from gi.repository import Gimp, GimpUi, Gio, GLib, GObject


PROC_NAME = "plug-in-dividir-capas-comic"


def _dejar_una_capa(image, indice):
    """Elimina de una copia de la imagen todas las capas raíz salvo una."""
    layers = list(image.get_layers())
    keep = layers[indice]
    for layer in layers:
        if layer != keep:
            image.remove_layer(layer)


def _guardar_png(image, ruta):
    archivo = Gio.File.new_for_path(ruta)
    if not Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image, archivo, None):
        raise RuntimeError(f"No se pudo exportar: {ruta}")


def dividir_run(procedure, run_mode, image, drawables, config, run_data):
    if run_mode == Gimp.RunMode.INTERACTIVE:
        GimpUi.init("dividir_capas_comic")
        dialog = GimpUi.ProcedureDialog.new(
            procedure, config, "Dividir capas de cómic"
        )
        dialog.fill(["output-folder"])
        if not dialog.run():
            dialog.destroy()
            return procedure.new_return_values(Gimp.PDBStatusType.CANCEL, None)
        dialog.destroy()

    output_folder = config.get_property("output-folder")

    if output_folder is None or output_folder.get_path() is None:
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error("Debes elegir una carpeta de salida."),
        )

    salida = output_folder.get_path()
    os.makedirs(salida, exist_ok=True)

    layers = list(image.get_layers())
    if not layers:
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error("La imagen no contiene capas."),
        )

    width = image.get_width()
    height = image.get_height()
    left_width = width // 2
    right_width = width - left_width

    if left_width < 1 or right_width < 1:
        return procedure.new_return_values(
            Gimp.PDBStatusType.CALLING_ERROR,
            GLib.Error("La imagen es demasiado estrecha para dividirla."),
        )

    # get_layers() devuelve la pila en el orden mostrado por GIMP.
    indices = list(range(len(layers)))

    total_paginas = len(indices) * 2
    numero = 1
    Gimp.progress_init("Dividiendo las capas del cómic…")

    try:
        for indice in indices:
            izquierda = image.duplicate()
            _dejar_una_capa(izquierda, indice)

            derecha = izquierda.duplicate()

            if not izquierda.crop(left_width, height, 0, 0):
                raise RuntimeError("No se pudo recortar la página izquierda.")
            if not derecha.crop(right_width, height, left_width, 0):
                raise RuntimeError("No se pudo recortar la página derecha.")

            _guardar_png(izquierda, os.path.join(salida, f"{numero:04d}.png"))
            numero += 1
            Gimp.progress_update((numero - 1) / total_paginas)

            _guardar_png(derecha, os.path.join(salida, f"{numero:04d}.png"))
            numero += 1
            Gimp.progress_update((numero - 1) / total_paginas)

            izquierda.delete()
            derecha.delete()

    except Exception as exc:
        return procedure.new_return_values(
            Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error(str(exc))
        )

    Gimp.progress_update(1.0)
    Gimp.message(
        f"Proceso terminado: {total_paginas} páginas guardadas en:\n{salida}"
    )
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


class DividirCapasComic(Gimp.PlugIn):
    def do_query_procedures(self):
        return [PROC_NAME]

    def do_create_procedure(self, name):
        if name != PROC_NAME:
            return None

        procedure = Gimp.ImageProcedure.new(
            self, name, Gimp.PDBProcType.PLUGIN, dividir_run, None
        )
        procedure.set_sensitivity_mask(
            Gimp.ProcedureSensitivityMask.DRAWABLE
            | Gimp.ProcedureSensitivityMask.NO_DRAWABLES
        )
        procedure.set_menu_label("Dividir capas de cómic…")
        # Las rutas internas de menú no se traducen; GIMP mostrará "Filtros".
        procedure.add_menu_path("<Image>/Filters")
        procedure.set_documentation(
            "Divide cada capa verticalmente y exporta las páginas en PNG",
            "Procesa cada capa raíz como una doble página. Exporta primero la "
            "mitad izquierda y después la derecha, con numeración correlativa.",
            None,
        )
        procedure.set_attribution("Juanlo García", "Juanlo García", "2026")

        procedure.add_file_argument(
            "output-folder",
            "Carpeta de salida",
            "Carpeta donde se guardarán las páginas PNG",
            Gimp.FileChooserAction.SELECT_FOLDER,
            False,
            None,
            GObject.ParamFlags.READWRITE,
        )
        return procedure


Gimp.main(DividirCapasComic.__gtype__, sys.argv)

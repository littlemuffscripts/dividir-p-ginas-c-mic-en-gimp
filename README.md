# Dividir capas de cómic — GIMP 3

Este complemento convierte cada capa raíz de una imagen de GIMP en dos páginas
PNG. El orden dentro de cada doble página es **izquierda y después derecha**.

## Instalación en macOS

1. En GIMP, abre **GIMP → Ajustes → Carpetas → Complementos** y localiza la
   carpeta personal de complementos.
2. Copia dentro de ella la carpeta completa `dividir_capas_comic`. La carpeta y
   el archivo Python deben conservar exactamente estos nombres:

   ```text
   dividir_capas_comic/
   └── dividir_capas_comic.py
   ```

3. Abre Terminal, escribe `chmod +x ` —con un espacio al final—, arrastra
   `dividir_capas_comic.py` sobre la ventana de Terminal y pulsa Intro.
4. Cierra GIMP completamente y vuelve a abrirlo.

La ruta habitual de GIMP 3 en macOS es:

```text
~/Library/Application Support/GIMP/3.0/plug-ins/
```

Conviene comprobarla en los ajustes porque puede variar según la instalación.

## Uso

1. Abre el archivo XCF que contiene una doble página en cada capa.
2. Comprueba el orden de la pila de capas.
3. Ejecuta **Filtros → Dividir capas de cómic…**.
4. Elige una carpeta vacía para la salida.
5. Pulsa **Aceptar**.

El complemento procesará primero la capa superior. Cada doble página se
exportará en el orden izquierda y después derecha.

El resultado será:

```text
0001.png  ← mitad izquierda de la primera capa
0002.png  ← mitad derecha de la primera capa
0003.png  ← mitad izquierda de la segunda capa
0004.png  ← mitad derecha de la segunda capa
…
```

## Consideraciones

- El XCF original no se modifica: el complemento trabaja con copias temporales.
- Las capas se procesan de arriba hacia abajo, según aparecen en GIMP.
- Si el ancho es impar, la página derecha tendrá un píxel más que la izquierda.
- Procesa las capas raíz. Un grupo de capas se trata como una sola doble página.
- Las páginas se exportan en PNG para no añadir pérdida de calidad.
- Utiliza una carpeta vacía: los archivos con los mismos nombres se
  sobrescribirán.

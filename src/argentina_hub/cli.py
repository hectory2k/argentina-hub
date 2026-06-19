"""
cli.py — Puntos de entrada CLI para argentina-hub.

Uso:
  argentina-hub resumen
  argentina-hub cargar <dataset> [--provincia XX]
"""

import argparse

from .core import ArgentinaHub


def main():
    parser = argparse.ArgumentParser(prog="argentina-hub")
    subparsers = parser.add_subparsers(dest="comando")

    # Comando: resumen
    subparsers.add_parser("resumen", help="Mostrar catálogo de datasets")

    # Comando: cargar
    cargar_parser = subparsers.add_parser("cargar", help="Cargar un dataset")
    cargar_parser.add_argument("dataset", help="Nombre del dataset")
    cargar_parser.add_argument("--provincia", help="Filtrar por código de provincia")

    args = parser.parse_args()
    hub = ArgentinaHub()

    if args.comando == "resumen":
        for nombre, info in hub.resumen().items():
            print(f"{nombre}: {info['registros']} registros, {len(info['columnas'])} columnas")

    elif args.comando == "cargar":
        filtros = {}
        if args.provincia:
            filtros["codigo_provincia"] = args.provincia
        df = hub.cargar(args.dataset, **filtros)
        print(df)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script de descarga de datos climáticos ERA5-Land desde Copernicus CDS
Descripción: Descarga temperatura del aire a 2m para Bogotá, enero 2020
"""

import os
import sys
from pathlib import Path

def main():
    # Verificar dependencias
    try:
        import cdsapi
    except ImportError:
        print("❌ ERROR: cdsapi no está instalado")
        print("\nInstala con:")
        print("  pip install cdsapi")
        sys.exit(1)
    
    # Crear directorio de datos
    data_dir = Path("./data_heavy")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Directorio creado/verificado: {data_dir}")
    
    # Verificar credenciales de CDS
    cds_config = Path.home() / ".cdsapirc"
    if not cds_config.exists():
        print("\n⚠️  ADVERTENCIA: No se encontró ~/.cdsapirc")
        print("\nDebes registrarte en https://cds.climate.copernicus.eu")
        print("Luego copia tus credenciales en ~/.cdsapirc con formato:")
        print("""
url: https://cds.climate.copernicus.eu/api/v2
key: <UID>:<API-KEY>
        """)
        sys.exit(1)
    
    print("✓ Credenciales de CDS encontradas")
    
    # Inicializar cliente
    try:
        client = cdsapi.Client()
        print("✓ Cliente CDS inicializado")
    except Exception as e:
        print(f"❌ Error al inicializar cliente: {e}")
        sys.exit(1)
    
    # Parámetros de descarga
    dataset = "reanalysis-era5-land"
    target = data_dir / "era5_land_bogota_2020_01.nc"
    
    request = {
        "variable": ["2m_temperature"],
        "year": ["2020"],
        "month": ["01"],
        "day": [str(d).zfill(2) for d in range(1, 32)],  # 01-31
        "time": [f"{h:02d}:00" for h in range(24)],      # 00:00-23:00
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [5.2, -74.6, 4.2, -73.6]  # [N, W, S, E] para Bogotá
    }
    
    print("\n📋 Parámetros de descarga:")
    print(f"  Dataset: {dataset}")
    print(f"  Variable: {request['variable'][0]}")
    print(f"  Período: {request['year'][0]}-{request['month'][0]}")
    print(f"  Área: {request['area']} (Bogotá)")
    print(f"  Archivo destino: {target}")
    
    # Descargar
    print("\n⏳ Descargando datos... (esto puede tomar varios minutos)")
    try:
        client.retrieve(dataset, request, str(target))
        print(f"\n✓ Descarga completada: {target}")
        
        # Verificar archivo
        if target.exists():
            size_mb = target.stat().st_size / (1024**2)
            print(f"  Tamaño: {size_mb:.2f} MB")
        
    except Exception as e:
        print(f"\n❌ Error en la descarga: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
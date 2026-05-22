#!/usr/bin/env python3
"""
Script de procesamiento del cubo NetCDF ERA5-Land - VERSIÓN CORREGIDA
Descripción: Lee, transforma, remuestrea y calcula máximos mensuales
Maneja correctamente diferentes nombramientos de dimensiones temporales
"""

import sys
import pandas as pd
from pathlib import Path


def encontrar_dim_temporal(da):
    """Detecta automáticamente cuál es la dimensión temporal"""
    candidatos = ["time", "valid_time", "forecast_time"]
    for dim in candidatos:
        if dim in da.dims:
            return dim
    
    # Si no encuentra nombre estándar, asume que la primera dimensión es tiempo
    # (esto ocurre a menudo con archivos GRIB)
    if len(da.dims) > 0:
        print(f"⚠️  Advertencia: No se encontró dimensión temporal estándar")
        print(f"   Dimensiones detectadas: {da.dims}")
        print(f"   Asumiendo que '{da.dims[0]}' es la dimensión temporal")
        return da.dims[0]
    
    return None


def main():
    # Verificar dependencias
    try:
        import numpy as np
        import xarray as xr
        import rioxarray
        import matplotlib.pyplot as plt
    except ImportError as e:
        print(f"❌ ERROR: Falta la librería {e.name}")
        print("\nInstala todas las dependencias con:")
        print("  pip install numpy pandas xarray rioxarray matplotlib netCDF4 dask cfgrib")
        sys.exit(1)

    print("✓ Todas las librerías importadas correctamente\n")

    # RUTAS
    project_root = Path(__file__).resolve().parent.parent
    data_dir = project_root / "data_heavy"
    ncfile = data_dir / "era5_land_bogota_2020_01.nc"
    outfile = data_dir / "mi_zona_procesada.nc"
    plot_file = data_dir / "temperatura_maxima_enero_2020.png"

    # Verificar archivo de entrada
    if not ncfile.exists():
        print(f"❌ ERROR: No se encuentra {ncfile}")
        print(f"\nEjecuta primero: python descarga_datos.py")
        sys.exit(1)

    print(f"📂 Leyendo archivo: {ncfile}\n")

    # ====================
    # 1. LECTURA PEREZOSA
    # ====================
    try:
        # Intentar con engine automático primero
        ds = xr.open_dataset(ncfile, chunks="auto")
        print("✓ Lectura perezosa completada (chunks='auto')")
    except Exception as e:
        print(f"⚠️  Advertencia en lectura automática: {e}")
        print("   Intentando con engine='netcdf4'...")
        try:
            ds = xr.open_dataset(ncfile, chunks="auto", engine="netcdf4")
            print("✓ Lectura con engine='netcdf4' completada")
        except Exception as e2:
            print(f"❌ Error al leer archivo: {e2}")
            sys.exit(1)

    # ====================
    # 2. NORMALIZAR NOMBRES
    # ====================
    rename_dict = {}

    if "valid_time" in ds.coords or "valid_time" in ds.dims:
        rename_dict["valid_time"] = "time"
    elif "forecast_time" in ds.coords or "forecast_time" in ds.dims:
        rename_dict["forecast_time"] = "time"

    if "lon" in ds.coords or "lon" in ds.dims:
        rename_dict["lon"] = "longitude"
    if "lat" in ds.coords or "lat" in ds.dims:
        rename_dict["lat"] = "latitude"

    if rename_dict:
        ds = ds.rename(rename_dict)
        print(f"✓ Coordenadas/dimensiones renombradas: {rename_dict}\n")

    # Auditoría
    print("=== AUDITORÍA DIMENSIONAL ===")
    print(f"Dimensiones: {dict(ds.dims)}")
    print(f"Variables: {list(ds.data_vars)}")
    print(f"Coordenadas: {list(ds.coords)}")

    print("\n=== METADATOS GLOBALES ===")
    if ds.attrs:
        for key, value in ds.attrs.items():
            if len(str(value)) < 100:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: {str(value)[:97]}...")
    else:
        print("  (Sin metadatos globales visibles)")

    # ====================
    # 3. SELECCIÓN DE VARIABLE
    # ====================
    if len(ds.data_vars) == 0:
        print("❌ ERROR: El dataset no contiene variables de datos")
        sys.exit(1)

    var_name = list(ds.data_vars)[0]
    da = ds[var_name]

    print(f"\n=== VARIABLE PRINCIPAL ===")
    print(f"Nombre: {var_name}")
    print(f"Shape: {da.shape}")
    print(f"Dtype: {da.dtype}")
    print(f"Dims: {da.dims}")

    # Detectar dimensión temporal
    time_dim = encontrar_dim_temporal(da)
    
    if time_dim is None:
        print("❌ ERROR: No se pudo identificar la dimensión temporal")
        sys.exit(1)

    try:
        print(f"Rango temporal: {da[time_dim].values[0]} a {da[time_dim].values[-1]}")
    except Exception as e:
        print(f"⚠️  No se pudo mostrar rango temporal: {e}")

    # ====================
    # 4. ASIGNAR CRS
    # ====================
    if "longitude" in da.coords and "latitude" in da.coords:
        try:
            da = da.rio.set_spatial_dims(
                x_dim="longitude",
                y_dim="latitude",
                inplace=False
            )
            da = da.rio.write_crs("EPSG:4326", inplace=False)
            print(f"\n✓ CRS asignado: {da.rio.crs}")
        except Exception as e:
            print(f"⚠️  Advertencia al asignar CRS: {e}")
    else:
        print("⚠️  No se encontraron coordenadas 'longitude' y 'latitude'; se omite asignación CRS")

    # ====================
    # 5. TRANSFORMACIÓN DE UNIDADES
    # ====================
    print("\n=== TRANSFORMACIÓN: Kelvin → Celsius ===")
    da_c = da - 273.15
    da_c.attrs["units"] = "°C"
    da_c.attrs["long_name"] = "Temperatura del aire a 2 m en Celsius"

    try:
        temp_min_c = float(da_c.min().compute())
        temp_max_c = float(da_c.max().compute())
        print(f"Rango de temperatura: [{temp_min_c:.2f}, {temp_max_c:.2f}] °C")
    except Exception as e:
        print(f"⚠️  No se pudo calcular el rango térmico: {e}")

    # ====================
    # 6. REMUESTREO TEMPORAL
    # ====================
    print("\n=== REMUESTREO TEMPORAL ===")
    print(f"Datos horarios originales: {len(da_c[time_dim])} instantes")

    try:
        da_daily = da_c.resample({time_dim: "1D"}).mean()
        print(f"✓ Remuestreo diario completado: {len(da_daily['time'])} días")
        print(f"  Primeras fechas: {da_daily['time'].values[:3]}")
    except Exception as e:
        print(f"❌ Error en remuestreo: {e}")
        print(f"   Intentando renombrar '{time_dim}' a 'time'...")
        try:
            da_c = da_c.rename({time_dim: "time"})
            time_dim = "time"
            da_daily = da_c.resample(time="1D").mean()
            print(f"✓ Remuestreo diario completado: {len(da_daily['time'])} días")
            print(f"  Primeras fechas: {da_daily['time'].values[:3]}")
        except Exception as e2:
            print(f"❌ Error en remuestreo: {e2}")
            sys.exit(1)

    # ====================
    # 7. MÁXIMO MENSUAL
    # ====================
    print("\n=== CÁLCULO DE MÁXIMOS MENSUALES ===")
    da_monthly_max = da_daily.resample(time="1MS").max()
    da_monthly_max.name = "t2m_max_mensual_c"

    print(f"Máximos mensuales calculados: {len(da_monthly_max.time)} mes(es)")
    try:
        temp_max_mensual = float(da_monthly_max.max().compute())
        print(f"Temperatura máxima mensual registrada: {temp_max_mensual:.2f} °C")
    except Exception as e:
        print(f"⚠️  No se pudo calcular el máximo mensual global: {e}")

    # ====================
    # 8. FECHA DE OCURRENCIA DEL MÁXIMO
    # ====================
    print("\n=== FECHA DE OCURRENCIA DEL MÁXIMO ===")
    
    # Enfoque sin .map() - usar loops explícitos y numpy
    print("Calculando fechas de máximo por píxel...")
    
    da_fecha_max_list = []
    
    for time_label, grupo in da_daily.resample(time="1MS"):
        """
        Para cada mes (grupo):
        1. Encontrar el índice del máximo en dimensión time
        2. Convertir ese índice a la fecha correspondiente
        3. Crear DataArray con las fechas para ese mes
        """
        
        # Shape del grupo: (time, latitude, longitude)
        valores = grupo.values
        tiempos = grupo["time"].values
        
        # Encontrar argmax en la dimensión temporal (axis=0)
        # Resultado: array (latitude, longitude)
        idx_max = np.argmax(valores, axis=0)
        
        # Para cada píxel, obtener la fecha correspondiente
        # idx_max[i,j] contiene el índice en la dimensión time
        fechas = np.empty_like(idx_max, dtype='datetime64[ns]')
        
        for i in range(idx_max.shape[0]):
            for j in range(idx_max.shape[1]):
                if np.isnan(valores[0, i, j]):
                    # Si el píxel tiene NaN, marcar la fecha como NaT
                    fechas[i, j] = np.datetime64('NaT')
                else:
                    fechas[i, j] = tiempos[idx_max[i, j]]
        
        # Crear DataArray con las fechas
        fecha_da = xr.DataArray(
            fechas,
            coords={
                "latitude": grupo.latitude,
                "longitude": grupo.longitude
            },
            dims=["latitude", "longitude"]
        )
        
        da_fecha_max_list.append(fecha_da)
    
    # Concatenar todos los meses
    da_fecha_max = xr.concat(da_fecha_max_list, dim="time")
    
    # Reasignar coordenada de tiempo al resultado
    da_fecha_max = da_fecha_max.assign_coords(
        time=da_monthly_max.time
    )
    da_fecha_max.name = "fecha_max"
    
    print("✓ Fechas de máximo calculadas")

    try:
        # Extraer fecha de ejemplo (píxel central si es posible)
        ejemplo_lat = da_fecha_max.sizes.get("latitude", 0) // 2
        ejemplo_lon = da_fecha_max.sizes.get("longitude", 0) // 2
        
        if ejemplo_lat > 0 and ejemplo_lon > 0:
            fecha_ejemplo = da_fecha_max.isel(
                time=0,
                latitude=ejemplo_lat,
                longitude=ejemplo_lon
            ).values
            print(f"  Fecha ejemplo (píxel central, mes 0): {pd.Timestamp(fecha_ejemplo).strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"⚠️  No se pudo extraer fecha de ejemplo: {e}")

    # ====================
    # 9. VISUALIZACIÓN
    # ====================
    print("\n=== VISUALIZACIÓN ===")
    try:
        fig, ax = plt.subplots(figsize=(10, 8))
        da_monthly_max.isel(time=0).plot(ax=ax, cmap="inferno", add_colorbar=True)
        ax.set_title("Temperatura máxima mensual - enero 2020 (°C)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Longitud")
        ax.set_ylabel("Latitud")

        plt.tight_layout()
        plt.savefig(plot_file, dpi=150, bbox_inches="tight")
        print(f"✓ Gráfica guardada: {plot_file}")
        plt.close()

    except Exception as e:
        print(f"⚠️  No se pudo guardar la gráfica: {e}")

    # ====================
    # 10. EXPORTACIÓN
    # ====================
    print("\n=== EXPORTACIÓN DEL RESULTADO ===")

    ds_out = xr.Dataset({
        "t2m_max_mensual_c": da_monthly_max,
        "fecha_max": da_fecha_max
    })

    ds_out.attrs["title"] = "Temperatura máxima mensual ERA5-Land - Bogotá"
    ds_out.attrs["source"] = "Copernicus Climate Change Service (CDS)"
    ds_out.attrs["region"] = "Bogotá, Colombia"
    ds_out.attrs["area_bounds"] = "[5.2°N, 74.6°W, 4.2°N, 73.6°W]"
    ds_out.attrs["processing"] = "xarray + rioxarray"

    try:
        ds_out.to_netcdf(outfile)
        size_mb = outfile.stat().st_size / (1024**2)
        print(f"✓ Archivo exportado: {outfile}")
        print(f"  Tamaño: {size_mb:.4f} MB")
        print(f"  Variables: {list(ds_out.data_vars)}")
        print(f"  Dimensiones: {dict(ds_out.dims)}")
    except Exception as e:
        print(f"❌ Error al exportar: {e}")
        sys.exit(1)

    # ====================
    # RESUMEN FINAL
    # ====================
    print("\n" + "=" * 60)
    print("✓ PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"\nArchivo de entrada:  {ncfile}")
    print(f"Archivo de salida:   {outfile}")
    print(f"Gráfica:             {plot_file}")
    print(f"\nPasos realizados:")
    print(f"  1. Lectura perezosa del cubo horario")
    print(f"  2. Detección automática de dimensión temporal: '{time_dim}'")
    print(f"  3. Transformación: K → °C")
    print(f"  4. Remuestreo: horario → diario")
    print(f"  5. Cálculo de máximos mensuales")
    print(f"  6. Identificación de fechas de máximo")
    print(f"  7. Exportación a NetCDF")


if __name__ == "__main__":
    main()
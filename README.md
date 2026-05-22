# Tarea – Cubos Multidimensionales

Este repositorio contiene el desarrollo de la tarea sobre cubos multidimensionales aplicada al procesamiento de datos climáticos en formato NetCDF.

El trabajo se centró en la descarga, lectura, transformación y análisis de un cubo climático ERA5-Land para un área de estudio sobre Bogotá, utilizando Python y bibliotecas orientadas al manejo de datos multidimensionales.

## Integrantes

- Valentina Ramírez
- Jesús Flores
- Santiago Gallego
- Viviana Peña

## Objetivo

Construir un flujo de trabajo reproducible para:

- descargar datos climáticos desde Copernicus CDS,
- leer un cubo NetCDF en forma perezosa,
- normalizar dimensiones y coordenadas,
- transformar unidades de temperatura,
- remuestrear la serie temporal,
- calcular máximos mensuales por píxel,
- identificar la fecha de ocurrencia del máximo,
- exportar un producto derivado en formato NetCDF.

## Estructura del proyecto

```text
20_cubos_multidimensionales/
├── data_heavy/
│   ├── era5_land_bogota_2020_01.nc
│   ├── mi_zona_procesada.nc
│   └── temperatura_maxima_enero_2020.png
├── notebooks/
├── scripts/
│   ├── descarga_cds.py
│   └── procesar_cubo.py
├── respuestas.qmd
├── respuestas.html
├── respuestas.pdf
├── README.md
└── .gitignore
```

## Dataset utilizado

- Fuente: Copernicus Climate Data Store
- Producto: ERA5-Land
- Variable: `2m_temperature`
- Periodo: enero de 2020
- Cobertura espacial: recorte sobre Bogotá

## Tecnologías y librerías

El flujo fue desarrollado en Python con las siguientes librerías principales:

- `cdsapi`
- `xarray`
- `rioxarray`
- `numpy`
- `pandas`
- `matplotlib`
- `netCDF4`
- `dask`

### Instalación sugerida

```bash
pip install cdsapi xarray rioxarray numpy pandas matplotlib netCDF4 dask
```

## Requisitos previos

Antes de ejecutar los scripts se requiere:

- tener una cuenta activa en Copernicus CDS,
- haber configurado el archivo de credenciales `~/.cdsapirc`,
- haber aceptado los términos del dataset en la plataforma de Copernicus,
- tener creada la carpeta `data_heavy/`.

## Flujo de trabajo

El procesamiento siguió las siguientes etapas:

1. Descarga automatizada del archivo NetCDF desde Copernicus CDS.
2. Lectura perezosa del cubo con `xarray`.
3. Auditoría de dimensiones, coordenadas y metadatos.
4. Normalización de nombres temporales y espaciales.
5. Conversión de Kelvin a Celsius.
6. Remuestreo temporal de horario a diario.
7. Cálculo del máximo mensual por píxel.
8. Cálculo de la fecha de ocurrencia del máximo.
9. Generación de visualizaciones de verificación.
10. Exportación del producto final a un nuevo archivo NetCDF.

## Archivos principales

### `scripts/descarga_cds.py`

Realiza la descarga del archivo climático desde Copernicus CDS y lo guarda en `data_heavy/`.

### `scripts/procesar_cubo.py`

Implementa el procesamiento del cubo NetCDF, incluyendo transformación de unidades, remuestreo temporal, cálculo de máximos y exportación final.

### `respuestas.qmd`

Documento fuente del informe en Quarto.

### `respuestas.html` / `respuestas.pdf`

Salidas renderizadas del informe.

## Resultados esperados

Al ejecutar correctamente el flujo, se generan:

- `data_heavy/era5_land_bogota_2020_01.nc`: archivo descargado desde Copernicus CDS.
- `data_heavy/mi_zona_procesada.nc`: producto NetCDF derivado con las variables `t2m_max_mensual_c` y `fecha_max`.
- `data_heavy/temperatura_maxima_enero_2020.png`: figura de verificación espacial.

## Ejecución

### 1. Descargar datos

```bash
python scripts/descarga_cds.py
```

### 2. Procesar cubo

```bash
python scripts/procesar_cubo.py
```

### 3. Renderizar informe

```bash
quarto render respuestas.qmd
```

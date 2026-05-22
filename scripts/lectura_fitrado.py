import matplotlib.pyplot as plt

# ============================================================
# Selección avanzada en cubo 5D (ERA5) con xarray
# - Selección por dimensiones (level, number, time)
# - Selección espacial (bounding box Bogotá)
# - Extracción de variable
# - Reducción a slice 2D + Visualización
# ============================================================

# -------------------------------------------------------------------------
# Selección 1: Subconjunto por dimensiones (label-based)
# -------------------------------------------------------------------------
# Selecciona:
# - miembro de ensamble 0
# - primeros dos niveles de presión
# - primer instante temporal
sel_dim = ds.sel(
    number=0,
    level=ds.level[:2],
    time=ds.time[0]
)

print(sel_dim)


# -------------------------------------------------------------------------
# Selección 2: Recorte espacial (Bogotá - WGS84)
# -------------------------------------------------------------------------
# Nota:
# - longitude = eje X
# - latitude  = eje Y
# - slice respeta orden de coordenadas

sel_bogota = ds.sel(
    longitude=slice(-74.25, -73.90),
    latitude=slice(4.85, 4.45)
)

print(sel_bogota)


# -------------------------------------------------------------------------
# Extracción de variable
# -------------------------------------------------------------------------
# 't' corresponde a temperatura (K)
t_bogota = sel_bogota["t"]

print(t_bogota)

# -------------------------------------------------------------------------
# Slice 2D (reducción dimensional)
# -------------------------------------------------------------------------
# Selecciona:
# - nivel más bajo (aprox. superficie)
# - ensamble 0
# - tiempo 0

capa_2d = t_bogota.isel(
    level=-1,
    number=0,
    time=0
)

print(capa_2d)

# Visualización de la matriz de datos
# El objeto se materializa (RAM) al usar .values
print(capa_2d.values)

# Verificación de las dimensiones restantes
print(capa_2d.dims)

# Verificación de los valores de las coordenadas
print(capa_2d.coords)

# Extracción de los valores de latitud o longitud asociados
eje_x = capa_2d.longitude.values
eje_y = capa_2d.latitude.values
print(eje_x)
print(eje_y)

# Verificación y extracción robusta
for dim in capa_2d.dims:
    print(f"Valores en la dimensión {dim}: {capa_2d[dim].values}")

# -------------------------------------------------------------------------
# Plot
# -------------------------------------------------------------------------



if capa_2d.size > 1:
    # Imprimir como mapa: requiere mínimo matriz de 2 x 2
    # El objeto se materializa (RAM) al usar .plot()
    capa_2d.plot(cmap="coolwarm")
else:
    print("⚠️ Solo hay un pixel, no se puede hacer plot espacial")
    # Esto ya no es un mapa, es un escalar
    plt.imshow(capa_2d.values.reshape(1,1), cmap="coolwarm")
    plt.colorbar(label="Temperatura (K)")

plt.title("Temperatura ERA5 - Bogotá (Superficie)")
plt.show()
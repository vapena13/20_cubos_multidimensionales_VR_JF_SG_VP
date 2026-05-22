import cdsapi

client = cdsapi.Client()

dataset = "reanalysis-era5-pressure-levels"
request = {
    "product_type": ["reanalysis"],
    "variable": ["geopotential"],
    "year": ["2024"],
    "month": ["03"],
    "day": ["01"],
    "time": ["13:00"],
    "pressure_level": ["1000"],
    "data_format": "grib",
}
target = "prueba_cds.grib"

client.retrieve(dataset, request, target)
print("Listo, funcionó")
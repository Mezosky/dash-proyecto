from typing import List

from geopandas import GeoDataFrame


def filtrar_region(gdf: GeoDataFrame, filtro_region: List[str]):
    if filtro_region == "Ninguna" or filtro_region is None or filtro_region == []:
        return gdf

    gdf = gdf[gdf["region"].isin(filtro_region)]
    return gdf

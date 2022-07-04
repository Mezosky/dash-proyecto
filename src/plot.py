from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.express as px


def get_map(geo_df_in, color: str, e2_elccion: str):

    fig_args: Dict[str, Any] = {
        "hover_name": "comuna",
        "hover_data": ["region"],
    }

    if color != "Ninguno":
        fig_args["color"] = color

    if color == "proporcion":
        fig_args["range_color"] = (0, 1)

    if e2_elccion is not None:
        fig_args["facet_col"] = "Fuente"
        fig_args["facet_col_wrap"] = 2

    # copia del geodf
    geo_df = geo_df_in.copy()
    geo_df = geo_df.dropna()
    geo_df = geo_df.dropna(subset=["geometry"])
    geo_df.index = geo_df.loc[:, "comuna"]

    # generar figura
    fig = px.choropleth(
        geo_df,
        geojson=geo_df.geometry,
        locations=geo_df.index,
        # color=color,
        projection="mercator",
        **fig_args,
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=1000)

    return fig


def get_diff_map(geo_df_in, color: str):

    # copia del geodf
    geo_df = geo_df_in.copy()
    geo_df = geo_df.dropna()
    geo_df = geo_df.dropna(subset=["geometry"])
    geo_df.index = geo_df.loc[:, "comuna"]

    fig_args: Dict[str, Any] = {}

    if color != "proporcion":
        fig_args["color"] = "diferencia_votos"
    else:
        fig_args["range_color"] = (-0.5, 0.5)
        fig_args["color"] = "diferencia_proporciones"

    # generar figura
    fig = px.choropleth(
        geo_df,
        geojson=geo_df.geometry,
        locations=geo_df.index,
        projection="mercator",
        color_continuous_scale=px.colors.diverging.RdBu,
        color_continuous_midpoint=0,
        **fig_args,
    )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=1000)

    return fig


def get_proyecciones_fig(df_cluster, pca, features: List[str]):

    df_cluster_ = df_cluster.copy()

    # Calcular loadings
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    # Formatear columnas como porcentajes
    for c in df_cluster_.select_dtypes(include=[np.float]):
        if c not in ["x", "y"]:
            if df_cluster_.loc[:, c].max() <= 1 and df_cluster_.loc[:, c].min() >= -1:
                df_cluster_[c] = (df_cluster_[c] * 100).round(1).astype(str) + "%"

    # Generar Labels
    var_ratio = pca.explained_variance_ratio_ * 100
    labels = {"x": f"PC 1 ({var_ratio[0]:.1f}%)", "y": f"PC 2 ({var_ratio[1]:.1f}%)"}

    hovers = features[:]

    for c in [
        "Indice Ruralidad",
        "Apruebo (Plebiscito)",
        "Rechazo (Plebiscito)",
        "Votos Totales Presidenciales",
    ]:
        if c not in hovers:
            hovers.append(c)

    # Graficar Proyecciones
    fig = px.scatter(
        df_cluster_,
        x="x",
        y="y",
        hover_name="comuna",
        color="Cluster",
        hover_data=hovers,
        height=600,
        labels=labels,
    ).update_traces(
        marker=dict(size=9, line=dict(width=1.2, color="DarkSlateGrey")),
        selector=dict(mode="markers"),
    )

    # Agregar loadings
    for i, feature in enumerate(features):
        fig.add_shape(type="line", x0=0, y0=0, x1=loadings[i, 0], y1=loadings[i, 1])
        fig.add_annotation(
            x=loadings[i, 0],
            y=loadings[i, 1],
            ax=0,
            ay=0,
            xanchor="center",
            yanchor="bottom",
            text=feature,
        )

    return fig


def get_clusters_fig(df_clusters: pd.DataFrame, gdf, features: List[str]):

    gdf_ = gdf.copy()

    # Merge proyecciones/clusters con mapas
    gdf_cluster = gdf_.loc[:, ["comuna_id", "geometry"]].merge(
        df_clusters, on="comuna_id"
    )
    gdf_cluster.index = gdf_cluster.loc[:, "comuna"]

    # Formatear columnas como porcentajes
    for c in gdf_cluster.select_dtypes(include=[np.float]):
        if c not in ["x", "y"]:
            if gdf_cluster.loc[:, c].max() <= 1 and gdf_cluster.loc[:, c].min() >= -1:
                gdf_cluster[c] = (gdf_cluster[c] * 100).round(1).astype(str) + "%"

    hovers = features[:]

    for c in [
        "Indice Ruralidad",
        "Apruebo (Plebiscito)",
        "Rechazo (Plebiscito)",
        "Votos Totales Presidenciales",
    ]:
        if c not in hovers:
            hovers.append(c)

    gdf_cluster = gdf_cluster.sort_values("Cluster")


    # generar figura
    fig_mapa = (
        px.choropleth(
            gdf_cluster,
            geojson=gdf_cluster.geometry,
            locations=gdf_cluster.index,
            color="Cluster",
            hover_name="comuna",
            hover_data=hovers,
        )
        .update_geos(fitbounds="locations", visible=False)
        .update_layout(height=1000)
    )

    return fig_mapa


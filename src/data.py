from typing import List

import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MaxAbsScaler


def get_df(df_: pd.DataFrame, opciones: List[str]):

    df = df_.copy()

    if opciones != []:
        df = df[df["opcion"].isin(opciones)]

    # if e1_opciones is None:
    df = (
        df.groupby(["comuna", "comuna_id"])
        .agg({"votos_totales": "sum", "proporcion": "sum"})
        .reset_index()
    )

    return df


def get_summary_df(df1_agg: pd.DataFrame, df2_agg: pd.DataFrame) -> pd.DataFrame:

    df1_agg = df1_agg.rename(
        columns={"votos_totales": "votos_totales_1", "proporcion": "proporción_1"}
    ).drop(columns=["Fuente"])

    if len(df2_agg) > 0:
        df2_agg = df2_agg.rename(
            columns={"votos_totales": "votos_totales_2", "proporcion": "proporción_2"}
        ).drop(columns=["Fuente"])

        df_diffs = pd.merge(
            df1_agg,
            df2_agg.loc[:, ["comuna_id", "votos_totales_2", "proporción_2"]],
            on="comuna_id",
        )
        df_diffs["diferencia_votos"] = (
            df_diffs["votos_totales_2"] - df_diffs["votos_totales_1"]
        )
        df_diffs["diferencia_proporciones"] = (
            df_diffs["proporción_2"] - df_diffs["proporción_1"]
        )

    else:
        df_diffs = df1_agg

    return df_diffs


def get_proj_clusters_df(
    df_cluster: pd.DataFrame, n_clusters: int, features: List[str]
):

    # ColumnTransformer para los pipelines

    cols_to_scale = (
        ["Votos Totales Presidenciales"]
        if "Votos Totales Presidenciales" in features
        else []
    )

    ct = ColumnTransformer(
        [
            (
                "minmax",
                MaxAbsScaler(),
                # features
                cols_to_scale,
            )
        ],
        remainder="passthrough",
    )

    # -----------------------------------------------------
    # Pipe PCA
    pca = PCA(n_components=2)

    pipe_pca = Pipeline([("Preprocesamiento", ct), ("Cluster", pca)])
    componentes = pipe_pca.fit_transform(df_cluster.loc[:, features])

    # Agregar x e y para proyectar
    df_cluster["x"] = componentes[:, 0]
    df_cluster["y"] = componentes[:, 1]

    # -----------------------------------------------------
    # Pipeline para el Cluster
    pipe_cluster = Pipeline(
        [
            ("Preprocesamiento", ct),
            (
                "Cluster",
                AgglomerativeClustering(n_clusters=n_clusters, linkage="ward"),
            ),
        ]
    )

    clusters = pipe_cluster.fit_predict(df_cluster.loc[:, features])

    # Agregar Clusters
    df_cluster["Cluster"] = clusters
    df_cluster = df_cluster.sort_values("Cluster")
    df_cluster["Cluster"] = df_cluster["Cluster"].astype(str)

    return df_cluster, pca

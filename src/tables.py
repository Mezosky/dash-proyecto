from typing import List

import pandas as pd


def get_cluster_summary_table(
    df_cluster: pd.DataFrame, features: List[str]
) -> pd.DataFrame:

    # # Groupby que describe el cluster:
    df_cluster_only_features = df_cluster.loc[:, features + ["Cluster"]]

    promedio_features_x_cluster = df_cluster_only_features.groupby("Cluster").mean()

    indice_ruralidad_x_cluster = (
        df_cluster.loc[:, ["Cluster", "Indice Ruralidad"]].groupby("Cluster").mean()
        * 100
    ).round(2).astype(str) + "%"

    porcentaje_apruebo_plebiscito = (
        df_cluster.loc[:, ["Cluster", "Apruebo (Plebiscito)"]].groupby("Cluster").mean()
        * 100
    ).round(2).astype(str) + "%"

    porcentaje_rechazo_plebiscito = (
        df_cluster.loc[:, ["Cluster", "Rechazo (Plebiscito)"]].groupby("Cluster").mean()
        * 100
    ).round(2).astype(str) + "%"

    # groupby_std = (
    #     gdf_cluster.groupby("Cluster")
    #     .std()
    # )

    # Rankings en el caso que sea necesario :/
    # rank = (
    #     groupby_mean.rank(axis=1, ascending=False, method="first")
    #     .astype(int)
    #     .astype(str)
    # )
    # rank = " (" + rank + ")"

    # Obtener cantidad de votos en ese cluster
    num_votos_x_cluster = (
        df_cluster.groupby("Cluster").sum().loc[:, "Votos Totales Presidenciales"]
    )

    # Obtener la proporción de gente que votó dentro de ese cluster.
    porcentaje_votos_x_cluster = (
        (
            df_cluster.groupby("Cluster").sum().loc[:, "Votos Totales Presidenciales"]
            / df_cluster["Votos Totales Presidenciales"].sum()
        )
        * 100
    ).round(2).astype(str) + "%"

    # con std
    # grouped_clusters_df = (
    #     (groupby_mean * 100).round(2).astype(str)
    #     + "% ±"
    #     + (groupby_std * 100).round(1).astype(str)
    # )

    # Diseñar clusters
    summary_clusters_df = (promedio_features_x_cluster * 100).round(2).astype(str) + "%"
    summary_clusters_df["Num. Votos Cluster (Presidenciales)"] = num_votos_x_cluster
    summary_clusters_df["% Votos Cluster (Presidenciales)"] = porcentaje_votos_x_cluster
    summary_clusters_df["Índice Ruralidad"] = indice_ruralidad_x_cluster
    summary_clusters_df["% Apruebo (Plebiscito)"] = porcentaje_apruebo_plebiscito
    summary_clusters_df["% Rechazo (Plebiscito)"] = porcentaje_rechazo_plebiscito

    summary_clusters_df = summary_clusters_df.reset_index()

    grouped_clusters_columns = [
        {"name": i, "id": i} for i in summary_clusters_df.columns
    ]
    grouped_clusters_data = summary_clusters_df.to_dict("records")

    return grouped_clusters_columns, grouped_clusters_data


def get_cluster_datatable(df_cluster):
    df_cluster_datatable = pd.DataFrame(df_cluster.drop(columns=["x", "y"]))

    cluster_columns = [{"name": i, "id": i} for i in df_cluster_datatable.columns]
    cluster_data = df_cluster_datatable.to_dict("records")

    return cluster_columns, cluster_data

def get_cluster_recommendation(
    df_cluster: pd.DataFrame) -> pd.DataFrame:

    # # Groupby que describe el cluster:
    col_interes = ['comuna',
                   'Posibles Izquierda (+ Boric)',
                   'Posibles Derecha (+ Kast)',
                   'Franco Parisi Fernandez',
                   'Votos Totales Presidenciales',
                   'Proporcion Presonas (Plebiscito) - 18 a 19 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 20-24 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 25-29 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 30-34 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 35-39 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 40-44 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 45-49 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 50-54 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 55-59 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 60-64 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 65-69 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 70-74 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 75-79 - sufragó',
                   'Proporcion Presonas (Plebiscito) - 80 o + - sufragó',
                   'Indice Ruralidad',  
                   'Apruebo (Plebiscito)',
                   'Rechazo (Plebiscito)',
                   'Sufragó (Plebiscito)',
                   'Diff Posibles Boric - Apruebo',
                   'Cluster']

    recom_cluster_df  = df_cluster.loc[:, col_interes]

    recom_cluster_df = recom_cluster_df.sort_values(by=['Diff Posibles Boric - Apruebo',
                                                        'Posibles Izquierda (+ Boric)'], 
                                                        ascending=[True, False])

    for col_i in col_interes:
        if col_i not in ['comuna','Votos Totales Presidenciales', 'Sufragó (Plebiscito)', 'Cluster']:
            recom_cluster_df[col_i] = (
                recom_cluster_df.loc[:, [col_i]]*100
                ).round(2).astype(str) + "%"

    recom_cluster_df_1 = recom_cluster_df[recom_cluster_df["Cluster"]=='3']
    recom_cluster_df_2 = recom_cluster_df[recom_cluster_df["Cluster"]=='0']

    recom_clusters_columns_1 = [
        {"name": i, "id": i} for i in recom_cluster_df_1.columns
    ]
    recom_clusters_data_1 = recom_cluster_df_1.to_dict("records")

    recom_clusters_columns_2 = [
        {"name": i, "id": i} for i in recom_cluster_df_2.columns
    ]
    recom_clusters_data_2 = recom_cluster_df_2.to_dict("records")

    return (
            recom_clusters_columns_1, recom_clusters_data_1, 
            recom_clusters_columns_2, recom_clusters_data_2
            )


def proportion_score(df_cluster, perc_boric, perc_yasna, perc_parisi, perc_artes, per_meo, perc_kast, perc_sichel):
    
    df_proportion = df_cluster.copy()
    df_proportion = df_proportion.set_index(["comuna"])

    cols_prod = ["Eduardo Artes Brichetti",
                 "Gabriel Boric Font",
                 "Jose Antonio Kast Rist",
                 "Franco Parisi Fernandez",
                 "Marco Enriquez-Ominami Gumucio",
                 "Sebastian Sichel Ramirez",
                 "Yasna Provoste Campillay"]
                
    return (df_proportion[cols_prod] * [perc_boric, perc_yasna, perc_parisi, perc_artes, per_meo, perc_kast, perc_sichel]).sum(axis=0)




    
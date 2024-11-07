import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns



def tests_normalidad(df, columna_grupo, columna_metrica):
    print("Resultados del test de bondad de ajuste Shapiro-Wilk:")
    for grupo in df[columna_grupo].unique():
        grupo_df = df[df[columna_grupo] == grupo]
        if grupo_df[[columna_metrica]].shape[0] > 5000:
            grupo_df = grupo_df.sample(5000)
        print(f"El p-valor para el grupo '{grupo}' es {round(stats.shapiro(grupo_df[columna_metrica])[1],3)}")

    print("\n\nResultados del test de bondad de ajuste Kolmogorov-Smirnoff:")
    for grupo in df[columna_grupo].unique():
        grupo_df = df[df[columna_grupo] == grupo]
        media = np.mean(grupo_df[columna_metrica])
        desv_tip = np.std(grupo_df[columna_metrica], axis=0)
        print(f"El p-valor para el grupo '{grupo}' es {round(stats.kstest(grupo_df[columna_metrica],'norm', args=(media, desv_tip))[1],3)}")


def generate_groups_df_list(df,group_column,metric_column, sample_size=None):
    if isinstance(sample_size,int):
        return [df.loc[df[group_column]==grupo,metric_column].sample(sample_size) for grupo in df[group_column].unique()]
    return [df.loc[df[group_column]==grupo,metric_column] for grupo in df[group_column].unique()]



def evaluar_tamanio_muestras(df, columna_grupo, columna_metrica):

    print("El reparto de tamaños muestrales por grupo del conjunto es el siguiente:")
    display(df.groupby(columna_grupo)[[columna_metrica]].count())

    # comprobar condicion de que todos los grupos tienen mismo tamaño muestral
    tamanio_muestral_grupos = df.groupby(columna_grupo)[columna_metrica].count()
    muestras_igual_tamanio = all(tamanio_muestral_grupos == tamanio_muestral_grupos.min())

    # si no, genero y devuelvo df con remuestro
    if not muestras_igual_tamanio:
        print(f"""\n\nLas muestras no son del mismo tamaño, es necesario aplicar remuestreo para igualarlas.
Devolviendo grupos con remuestreo para equilibrar al tamaño muestral mínimo de {tamanio_muestral_grupos.min()}.""")
        print("\n\n························································································")
        
        # generar df remuestreo 
        df_remuestro_total = pd.DataFrame()

        for grupo in df[columna_grupo].unique():
            df_grupo_remuestreo = df.loc[df[columna_grupo]==grupo,[columna_grupo,columna_metrica]].sample(tamanio_muestral_grupos.min())
            df_remuestro_total = pd.concat([df_remuestro_total,df_grupo_remuestreo])

        # mostrar nuevo reparto
        print("El nuevo conjunto de datos con remuestreo por grupos es el siguiente:")
        display(df_remuestro_total.groupby(columna_grupo)[[columna_metrica]].count())
        return df_remuestro_total
    
    # si tamaños iguales, no hay cambio
    print("Tamaño muestral uniforme. Devolviendo lista de muestras por grupo.")
    return df


def test_no_parametrico(df,columna_grupo,columna_metrica,dependiente=False, proporcion=False):
    groups_df_list = generate_groups_df_list(df,columna_grupo,columna_metrica)
    tests = {
        len(groups_df_list) == 2: lambda group_dfs: stats.mannwhitneyu(*group_dfs),
        len(groups_df_list) == 2 & dependiente: lambda group_dfs: stats.wilcoxon(*group_dfs),
        len(groups_df_list) > 2: lambda group_dfs: stats.kruskal(*group_dfs),
        proporcion: lambda group_dfs: stats.zscore(*group_dfs,ddof=1)
    }

    return [test(groups_df_list) for condition,test in tests.items() if condition][0]




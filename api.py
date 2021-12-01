import os
import json
import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

# Definir o caminho da pasta em que o projeto se encontra
root_folder_path = os.path.abspath(os.getcwd())

class API_PKMON(Resource):
    def __init__(self):
        dataset_link = 'https://gist.githubusercontent.com/armgilles/194bcff35001e7eb53a2a8b441e8b2c6/raw/92200bc0a673d5ce2110aaad4544ed6c4010f687/pokemon.csv'
        self.dtset_pkmn = pd.read_csv(dataset_link)
        self.dtset_pkmn.loc[:, 'Type 2'].fillna('', inplace=True)
          
    
    def get(self, types):
        list_types = types.split('_')
        find_types = pd.Series([False] * len(self.dtset_pkmn))
        for type in list_types:
            aux_bool_types = self.dtset_pkmn['Type 1'] == type
            find_types = aux_bool_types | find_types
        self.group_data_by_types(find_types)
        self.dtset_filt = self.dataset_filtered(find_types)
        self.create_chart()

        return self.dtset_pkmn.loc[find_types].to_json()

    def group_data_by_types(self, find_types):
        df_by_type = self.dtset_pkmn.loc[find_types].groupby(['Type 1', 'Type 2']).agg({'Generation': 'max', 'Total':'count', 'Legendary': 'sum'})
        df_by_type.to_csv(root_folder_path + '/Agrupamento_por_Tipo.csv', sep=';', encoding='utf-8-sig')
        with open(root_folder_path + '/Agrupamento_por_Tipo.txt', 'w') as outfile:
            json.dump(df_by_type.to_json(), outfile)
    

    def dataset_filtered(self, find_types):
        columns_filt = ['Name', 'Type 1', 'Type 2', 'Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        dtset_filt = self.dtset_pkmn.loc[find_types, columns_filt]
        dtset_filt['Type'] = ''
        func = lambda x: x['Type 1'] if x['Type 2'] == '' else x['Type 1'] + '/' + x['Type 2']
        dtset_filt.loc[:, 'Type'] = dtset_filt.apply(func, axis=1)
        
        return dtset_filt


    def create_chart(self):
        # Create the Boxplot
        sns.set_theme()
        fig_dims = (30, 7)
        fig = plt.subplots(figsize=fig_dims)
        fig1 = sns.boxplot(data=self.dtset_filt, x='Type', y='Total', palette='pastel').get_figure()
        plt.title('Distribuição de Status x Tipo')
        plt.ylabel('Status')
        plt.xlabel('Tipos')
        fig1.savefig(root_folder_path + '/Boxplot_Status_x_Tipos.png')

        # Create the Barplot
        fig_dims = (20, 10)
        fig, axis = plt.subplots(2, 4, figsize=fig_dims)
        x_axis = ['Total', 'HP', 'Attack', 'Defense', 'Sp. Atk', 'Sp. Def', 'Speed']
        i = 0
        j = 0
        # Randomize the types to compare in chart
        unique_types = self.dtset_filt.Type.unique()
        type1 = random.choice(unique_types)
        type1_pos = np.where(unique_types == type1)[0][0]
        type2 = random.choice(np.delete(unique_types, type1_pos))
        for item in x_axis:
            fig2 = sns.barplot(ax=axis[i, j], data=self.dtset_filt.loc[(self.dtset_filt.Type == type1) | (self.dtset_filt.Type == type2)], y=item, x='Type',palette='pastel').get_figure()
            if j == 3:
                i += 1
                j = -1
            j += 1
        fig2.savefig(root_folder_path + '/Barplot_Status_x_Tipos.png')
        

api.add_resource(API_PKMON, '/types/<string:types>')

if __name__ == '__main__':
    app.run(debug=True)

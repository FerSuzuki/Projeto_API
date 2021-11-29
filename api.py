import os
import json
import pandas as pd
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

    def get(self, types):
        list_types = types.split('_')
        find_types = pd.Series([False] * len(self.dtset_pkmn))
        for type in list_types:
            aux_bool_types = self.dtset_pkmn['Type 1'] == type
            find_types = aux_bool_types | find_types
            
        return self.dtset_pkmn.loc[find_types].to_json()

    def group_data_by_types(self):
        df_by_type = self.dtset_pkmn.groupby(['Type 1', 'Type 2']).agg({'Generation': 'count', 'Legendary': 'sum'})
        df_by_type.to_csv(root_folder_path + '/Agrupamento_por_Tipo.csv')
        with open(root_folder_path + '/Agrupamento_por_Tipo.txt', 'w') as outfile:
            json.dump(df_by_type.to_json(), outfile)

api.add_resource(API_PKMON, '/types/<string:types>')

if __name__ == '__main__':
    app.run(debug=True)

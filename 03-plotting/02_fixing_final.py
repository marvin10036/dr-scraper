import pandas as pd


# Final: Get the last .csv and fix the name of the columns
df = pd.read_csv("./Input/08_join_instituicao.csv")
df = df.rename(columns={'emec_vagas': 'emec_conceito_institucional',
                        'emec_data_inicio': 'emec_conceito_institucional_ead'})
df.to_csv("../Final.csv", index=False, encoding="utf-8-sig")

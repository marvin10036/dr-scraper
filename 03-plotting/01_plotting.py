import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr

# Load CSV
df = pd.read_csv("03-plotting/Input/08_join_instituicao.csv")

# Define o estilo dos gráficos
sns.set(style="whitegrid")

# --- Gráfico 1: Top 15 Especialidades Médicas ---
plt.figure(figsize=(12, 8))
specialties = df['especialidade'].value_counts().nlargest(15).sort_values(ascending=True)
sns.barplot(x=specialties.values, y=specialties.index, palette='viridis')
plt.title('Top 15 Especialidades Médicas', fontsize=16)
plt.xlabel('Número de Médicos', fontsize=12)
plt.ylabel('Especialidade', fontsize=12)
plt.tight_layout()
plt.savefig('03-plotting/Output/specialties.png')

# --- Gráfico 2: Top 15 Universidades ---
plt.figure(figsize=(12, 8))
institutions = df['instituicao'].value_counts().nlargest(15).sort_values(ascending=True)
sns.barplot(x=institutions.values, y=institutions.index, palette='plasma')
plt.title('Top 15 Universidades que Mais Formaram Médicos', fontsize=16)
plt.xlabel('Número de Médicos', fontsize=12)
plt.ylabel('Universidade', fontsize=12)
plt.tight_layout()
plt.savefig('03-plotting/Output/universities.png')

# --- Gráfico 3: Inscrições de Médicos ao Longo do Tempo ---
# Converte a coluna 'data_inscricao' para o formato de data, tratando erros
df['data_inscricao'] = pd.to_datetime(df['data_inscricao'], format='%d/%m/%Y', errors='coerce')

# Remove linhas onde a conversão da data falhou
df.dropna(subset=['data_inscricao'], inplace=True)

df['ano_inscricao'] = df['data_inscricao'].dt.year
registrations_per_year = df['ano_inscricao'].value_counts().sort_index()

plt.figure(figsize=(12, 6))
sns.lineplot(x=registrations_per_year.index, y=registrations_per_year.values, marker='o', color='royalblue')
plt.title('Inscrições de Médicos ao Longo do Tempo', fontsize=16)
plt.xlabel('Ano de Inscrição', fontsize=12)
plt.ylabel('Número de Médicos', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.savefig('03-plotting/Output/registrations_over_time.png')

# Define o estilo e a paleta de cores dos gráficos
sns.set_style("whitegrid")
sns.set_palette("muted")

# --- Gráfico 4: Distribuição das Notas dos Médicos ('nota') ---
plt.figure(figsize=(10, 6))
sns.histplot(df['nota'], kde=True, bins=10, color='skyblue')
plt.title('Distribuição das Notas dos Médicos', fontsize=16)
plt.xlabel('Nota (nota)', fontsize=12)
plt.ylabel('Número de Médicos', fontsize=12)
plt.tight_layout()
plt.savefig('03-plotting/Output/ratings_distribution.png')

# --- Gráfico 5: Relação entre Número de Opiniões e Nota ---
plt.figure(figsize=(10, 6))
# Filtra outliers extremos em 'opinioes' para melhor visualização
opinions_filtered = df[df['opinioes'] < df['opinioes'].quantile(0.99)]
sns.scatterplot(data=opinions_filtered, x='opinioes', y='nota', alpha=0.6, color='coral')
plt.title('Relação entre Número de Opiniões e Nota', fontsize=16)
plt.xlabel('Número de Opiniões (opinioes)', fontsize=12)
plt.ylabel('Nota (nota)', fontsize=12)
plt.tight_layout()
plt.savefig('03-plotting/Output/opinions_vs_rating.png')

# --- Gráfico 6: Origem dos Médicos por Tipo de Universidade ('emec_modalidade') ---
plt.figure(figsize=(10, 8))
# Preenche valores NaN como 'Não informado' para incluí-los no gráfico
modalidade_counts = df['emec_modalidade'].fillna('Não informado').value_counts()
plt.pie(modalidade_counts, labels=modalidade_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
plt.title('Origem dos Médicos por Tipo de Universidade (emec_modalidade)', fontsize=16)
plt.ylabel('') # Oculta o rótulo do eixo y
plt.tight_layout()
plt.savefig('03-plotting/Output/university_type_distribution.png')

# --- Gráfico 7: Top 10 Cidades com Mais Médicos ---
# Extrai as cidades da coluna 'endereco'
df['city_from_address'] = df['endereco'].str.split(' - ').str[-1].str.replace(r'/[A-Z]{2}$', '', regex=True)

plt.figure(figsize=(12, 8))
# Exclui o nome do estado 'SC' se ele foi extraído por engano
city_counts = df[df['city_from_address'] != 'SC']['city_from_address'].value_counts().nlargest(10).sort_values(ascending=True)
sns.barplot(x=city_counts.values, y=city_counts.index, palette='crest')
plt.title('Top 10 Cidades com Mais Médicos (extraído do Endereço)', fontsize=16)
plt.xlabel('Número de Médicos', fontsize=12)
plt.ylabel('Cidade', fontsize=12)
plt.tight_layout()
plt.savefig('03-plotting/Output/doctors_by_city.png')

# --- Gráfico 8: Distribuição da Situação Cadastral ('situacao') ---
plt.figure(figsize=(10, 8))
status_counts = df['situacao'].value_counts()
plt.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("Set2"))
plt.title('Distribuição da Situação Cadastral dos Médicos', fontsize=16)
plt.ylabel('')
plt.tight_layout()
plt.savefig('03-plotting/Output/registration_status_distribution.png')

# --- Gráfico 9: Distribuição do Tipo de Inscrição ('tipo_inscricao') ---
plt.figure(figsize=(10, 8))
inscricao_counts = df['tipo_inscricao'].value_counts()
plt.pie(inscricao_counts, labels=inscricao_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('Distribuição do Tipo de Inscrição', fontsize=16)
plt.ylabel('')
plt.tight_layout()
plt.savefig('03-plotting/Output/registration_type_distribution.png')

# --- Corrected Plot: Average Rating by Specialty ---

plt.figure(figsize=(12, 8))

# Get the top 15 specialties to keep the chart clean
top_specialties = df['especialidade'].value_counts().nlargest(15).index

# Filter the DataFrame for only the top specialties, then group and get the mean
avg_rating_specialty = df[df['especialidade'].isin(top_specialties)].groupby('especialidade')['nota'].mean().sort_values()

# Create the bar plot
sns.barplot(
    x=avg_rating_specialty.values,
    y=avg_rating_specialty.index,
    palette='viridis_r' # Using a reversed palette
)

plt.title('Nota Média Real por Especialidade Médica (Top 15)', fontsize=16)
plt.xlabel('Nota Média (de 0 a 5)', fontsize=12)
plt.ylabel('Especialidade', fontsize=12)

# The key change is NOT setting the x-axis limit, letting it default from 0.
# plt.xlim(4.9, 5.0) # <-- This was the misleading line, now removed.

plt.tight_layout()
plt.savefig('03-plotting/Output/average_rating_by_specialty.png')
plt.show()

# --- Gráfico 11: Mapa de Calor de Correlação ---
# Limpa e converte a coluna 'emec_indices' para numérico
df['emec_indices'] = pd.to_numeric(df['emec_indices'], errors='coerce')
numeric_df = df[['nota', 'opinioes', 'emec_indices']].copy()

# Calcula a matriz de correlação
correlation_matrix = numeric_df.corr()

plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Mapa de Calor de Correlação entre Atributos Numéricos', fontsize=16)
plt.tight_layout()
plt.savefig('03-plotting/Output/correlation_heatmap.png')

# --- Análise de Correlação: Nota do Médico vs. Nota da Instituição ---

# 1. Limpeza dos Dados
df['emec_indices_numeric'] = pd.to_numeric(df['emec_indices'], errors='coerce')
analysis_df = df[['nota', 'emec_indices_numeric']].dropna()

# 2. Cálculo da Correlação
corr, _ = pearsonr(analysis_df['emec_indices_numeric'], analysis_df['nota'])

# 3. Criação do Gráfico
plt.figure(figsize=(10, 7))
sns.regplot(
    data=analysis_df,
    x='emec_indices_numeric',
    y='nota',
    scatter_kws={'alpha': 0.5},
    line_kws={'color': 'red'}
)

# 4. Customização do Gráfico
plt.title(f'Nota do Médico vs. Nota da Instituição de Ensino\nCoeficiente de Correlação: {corr:.2f}', fontsize=16)
plt.xlabel('Nota da Instituição (Índice EMEC)', fontsize=12)
plt.ylabel('Nota do Médico', fontsize=12)
plt.xticks([1, 2, 3, 4, 5])
plt.tight_layout()

# Salva o gráfico como uma imagem (opcional)
plt.savefig('03-plotting/Output/correlacao_nota_medico_instituicao.png')

# 5. EXIBE o Gráfico na tela
plt.show()

# --- Data Preparation ---
# 1. Convert EMEC indices to a numeric format
df['emec_indices_numeric'] = pd.to_numeric(df['emec_indices'], errors='coerce')

# 2. Get the top 15 institutions by count
top_institutions = df['instituicao'].value_counts().nlargest(15)

# 3. Create a new DataFrame for plotting
plot_df = top_institutions.reset_index()
plot_df.columns = ['instituicao', 'numero_de_medicos']

# 4. Map the numeric grade to each institution
grade_map = df.groupby('instituicao')['emec_indices_numeric'].first()
plot_df['nota_emec'] = plot_df['instituicao'].map(grade_map)

# 5. Create the legend label - THIS IS THE KEY CHANGE
# Fill missing grades (NaN) with 0, convert to integer, then to string
plot_df['legenda_nota'] = plot_df['nota_emec'].fillna(0).astype(int).astype(str)
# Replace '0' with the 'Ungraded' label for clarity
plot_df['legenda_nota'] = plot_df['legenda_nota'].replace('0', 'Nota Não Disponível')

# Sort for a cleaner plot
plot_df = plot_df.sort_values('numero_de_medicos', ascending=False)


# --- Plot Creation ---
plt.figure(figsize=(14, 10))
sns.set_style("whitegrid")

# Use the new 'legenda_nota' column for the hue
# We can also define a custom color palette
custom_palette = {'5': '#2a7886', '4': '#22a884', '3': '#7aa351', 'Nota Não Disponível': '#c455cc'}

barplot = sns.barplot(
    x='numero_de_medicos',
    y='instituicao',
    data=plot_df,
    hue='legenda_nota',
    palette=custom_palette,
    hue_order=['5', '4', '3', 'Nota Não Disponível'], # Control legend order
    dodge=False
)

# --- Customization ---
plt.title('Top 15 Universidades por Número de Médicos e Nota da Instituição (EMEC)', fontsize=18, pad=20)
plt.xlabel('Número de Médicos Formados', fontsize=14)
plt.ylabel('Instituição de Ensino', fontsize=14)

# Update legend
leg = plt.legend(title='Nota da Instituição (EMEC)', fontsize=12, title_fontsize=14)
leg.get_frame().set_edgecolor('black')

plt.tight_layout()
plt.savefig('03-plotting/Output/universidades_por_nota.png')
plt.show()

# --- Find the Top 10 Doctors ---
# Sort by 'nota' (descending) and then by 'opinioes' (descending)
top_10_doctors = df.sort_values(by=['nota', 'opinioes'], ascending=[False, False]).head(10)


# --- Create the Visualization ---
plt.figure(figsize=(12, 8))
sns.set_style("whitegrid")

# Create a bar plot
ax = sns.barplot(
    x='opinioes',
    y='nome',
    data=top_10_doctors,
    palette='viridis'
)

# --- Customize the Plot ---
plt.title('Top 10 Médicos por Número de Opiniões (com Nota 5.0)', fontsize=16)
plt.xlabel('Número de Opiniões', fontsize=12)
plt.ylabel('Nome do Médico', fontsize=12)

# Add the number of opinions as a label on each bar
ax.bar_label(ax.containers[0], padding=3)

plt.tight_layout()
plt.savefig('03-plotting/Output/top_10_doctors_by_opinions.png')
plt.show()
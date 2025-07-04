# dr-scraper
Trabalho da matéria de Tópicos Especiais em Gerência de Dados

## Integrantes
- Guilherme Focassio dos Santos (21202329)
- Julia Fernanda Werlang (21202333)
- Marcus Vinicius Ribeiro Silveira (21201474)

## Rodando os scripts na ordem do fluxo

- Para reproduzir os passos realizados em ordem, você precisa antes exluir (ou salvar em outro local) todos os Outputs já gerados:
    - `01-Scraping/Output/*`
    - `02-Filtering/Output/*`
    - `03-plotting/Output/*`

1. Navegue para a raíz do projeto e crie um ambiente virtual e instale as dependências nele:

    ```
    python3 -m venv venvlibs
    ```

    ```
    source venvlibs/bin/activate
    ```

    ```
    pip install -r requirements.txt
    ```

2. Entre na primeira etapa e rode o scraper do doctoralia:

    ```
    cd 01-Scraping
    ```

    ```
    python3 doctoralia_scraper.py
    ```

    O resultado ficará salvo na pasta Output dessa etapa. Os outros scrapers foram incorporados ao código das etapas posteriores.
    O output dessa etapa já foi movido (manualmente, previamete) para a pasta input da etapa posterior. Então prosseguimos para lá agora.

    ```
    cd ../02-Filtering
    ```

3. Na segunda etapa você pode rodar os scripts pela sequência numérica. É aqui onde filtragens no .csv e "joins" entre os sites ocorrem:

    ```
    python3 01_filter_csv.py
    ```

    Esse vai gerar na pasta `Output` interna os .csv: `01_doctoralia_no_duplicates.csv`, `02_doctoralia-no-duplicates-indexed.csv`, `03_accepted.csv` e `03_rejected.csv`.

    ```
    python3 02_doctoralia_join_CFM.py
    ```

    Esse vai gerar na pasta `Output` interna os .csv: `04_accepted_indexed.csv`, `05_CRM_UF_key_column_added.csv` e `06_joined.csv`

    ```
    python3 03_e_mec_join.py
    ```

    Esse vai gerar na pasta `Output` interna os .csv: `07_ordered_CFM_join.csv`, `07_rejected.csv` e `08_join_instituicao.csv`.

    Apenas o `08_join_instituicao.csv` vai ser usado como input na próxima etapa. A explicação do que cada output gerado é está explicada em comentários dentro do código.

    Novamente, o output dessa etapa já foi movido manualmente por nós para o input da próxima. Prosseguimos para a etapa final:

    ```
    cd ../03-plotting
    ```

4. Na última etapa vamos gerar os gráficos e fazer um pequeno fix no nome de duas colunas do .csv de input:

    ```
    python3 01_plotting.py
    ```

    Vai salvar todos os outputs de gráfico na pasta `Output` interna a etapa.

    ```
    python3 02_fixing_final.py
    ```
    Vai corrigir dois nomes de coluna incorretos e mandar o .csv final para
    a raíz do projeto (`Final.csv`).

## Outputs mais importantes

Os Outputs que consideramos ser importantes na avaliação são:

- Os gráficos gerados em `03-plotting/Output/*`
- O .csv final com todos os joins na raíz do projeto: `Final.csv`


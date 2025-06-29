import pandas as pd
import re
import os


def output_to_csv(file_name: str, data: list):
    df = pd.DataFrame(data)
    # If the file already exists
    if os.path.exists(file_name):
        # Append only mode
        df.to_csv(file_name, mode='a', header=False, index=False, encoding="utf-8-sig")
    else:
        # Create the file and headers
        df.to_csv(file_name, index=False, encoding="utf-8-sig")


def extract_uf(line: str):
    UFs = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
           "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
           "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

    pattern = r'\b(' + '|'.join(UFs) + r')\b'
    pattern_matched = re.search(pattern, line)
    if pattern_matched:
        return pattern_matched.group()
    else:
        return None


def extract_CRM_number(line: str):
    pattern = r"[0-9]+\.[0-9]*|[0-9]+"
    pattern_matched = re.search(pattern, line)
    if pattern_matched:
        # Only the first ocurrence
        return pattern_matched.group(0)
    else:
        return None


# First: Read the Input and remove duplicate rows
df = pd.read_csv("./Input/doctoralia_scraping_result.csv")
df_no_duplicates = df.drop_duplicates()
df_no_duplicates.to_csv("./Output/01_doctoralia_no_duplicates.csv", index=False)

# Second: Load the new .csv and create an index columnn for later usage
df = pd.read_csv("./Output/01_doctoralia_no_duplicates.csv")

df['index'] = df.index
df = df[['index'] + [col for col in df.columns if col != 'index']]
df.to_csv("./Output/02_doctoralia-no-duplicates-indexed.csv", index=False)

# Third: Load the new .csv and filter structured CRM only registries
df = pd.read_csv("./Output/02_doctoralia-no-duplicates-indexed.csv")

# Creating a dictionary struct like:
# { 0: {'index': 0, 'Name': 'Alice', ...}, 1: {'index': 1, 'Name': 'Bob', ...}, ...}
index_dict = df.to_dict(orient="index")

for index, line in enumerate(df["registro"]):
    current_line_dict = index_dict.get(index)

    # If it's not a number (NaN), aka line's empty
    if pd.isna(line):
        # Send to reject.csv
        output_to_csv("./Output/03_rejected.csv", [current_line_dict])
    # If there isn't a CRM string on the line
    elif "CRM" not in line:
        output_to_csv("./Output/03_rejected.csv", [current_line_dict])
    else:
        current_CRM = extract_CRM_number(line)
        current_uf = extract_uf(line)
        # Treating this case as unstructured data
        if current_uf is None:
            output_to_csv("./Output/03_rejected.csv", [current_line_dict])
        else:
            output_to_csv("./Output/03_accepted.csv", [current_line_dict])

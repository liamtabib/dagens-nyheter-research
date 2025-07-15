from pathlib import Path
import pandas as pd
import os
import csv
import shutil
import time


def to_zip(data: pd.DataFrame, filename: str, archive_name: str, **csv_opts) -> None:
    data.to_csv(filename, compression=dict(method='zip', archive_name=archive_name), **csv_opts)


def combine_csv(path_to_csvs_dir, output_filename):
    path_object = Path(path_to_csvs_dir)
    csv_files = list(path_object.rglob('*.csv'))  # Get all CSV files in the directory

    if not csv_files:
        print("No CSV files found.")
        return

    combined_data = []

    for csv_file in csv_files:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                combined_data.append(row)

    if combined_data:
        output_path = os.path.join(path_to_csvs_dir, output_filename)
        with open(output_path, 'w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerows(combined_data)

        print(f"CSV files combined and saved to {output_filename}.")
    else:
        print("No data to combine.")




def combine_csv_pd(path_to_csvs_dir):
    path_object = Path(path_to_csvs_dir)
    csv_files = list(path_object.rglob('*.csv'))  # Get all CSV files in the directory

    if not csv_files:
        print("No CSV files found.")
        return

    combined_data = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        combined_data.append(df)

    if combined_data:
        combined_df = pd.concat(combined_data, ignore_index=True)

        return combined_df



if __name__ == '__main__':
    start_time = time.time()
    #df = combine_csv('csvs','con.csv')
    df = combine_csv_pd('csv_batches')
    if df.empty:

        print("No data to combine.")

    else:
        westac_hub_dir_path='westac_hub_files'

        if os.path.exists(westac_hub_dir_path):
            shutil.rmtree(westac_hub_dir_path)
        os.makedirs(westac_hub_dir_path)

        to_zip(data=df,filename=f'{westac_hub_dir_path}/documents.zip',archive_name='documents.csv',sep='\t',index=False)
        print(f"CSV files combined and saved to {westac_hub_dir_path}/documents.zip.")
    end_time = time.time()
    execution_time_seconds = end_time - start_time
    execution_time_hours = execution_time_seconds / 3600  # 3600 seconds in an hour
    script_name = "combine_inputs_csvs_dn.py"
    print(f"Script '{script_name}' executed in {execution_time_hours:.2f} hours.")



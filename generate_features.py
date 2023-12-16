from pathlib import Path
from argparse import ArgumentParser

import cv2
import pandas as pd
from tqdm import tqdm

import preprocessing
from preprocessing import get_features


def parse_arguments():
    parser = ArgumentParser(description="Generate a CSV file with features and targets")
    parser.add_argument("data_folder", help="Path to data folder")
    return parser.parse_args()


def generate_path_df(data_folder: Path) -> pd.DataFrame:
    data = {"path": [], "label": []}
    for folder in data_folder.iterdir():
        if folder.is_dir():
            for file in folder.iterdir():
                if file.is_file():
                    data["path"].append(file)
                    data["label"].append(folder.name)
    df = pd.DataFrame(data)
    return df


def main():
    args = parse_arguments()
    data_folder = Path(args.data_folder)
    df_path = generate_path_df(data_folder)

    df = pd.DataFrame()

    tqdm.pandas()

    df[["1", "2", "3", "4", "5"]] = df_path["path"].progress_apply(
        lambda path: pd.Series(get_features(cv2.imread(str(path))))
    )
    df["target"] = df_path["label"]

    df.dropna(inplace=True)
    print(df["target"].value_counts())

    output_path = data_folder / "features.csv"
    df.to_csv(output_path, index=False)
    print(f"Features saved to {output_path}")


if __name__ == "__main__":
    main()

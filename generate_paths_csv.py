from pathlib import Path
import argparse

import pandas as pd


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate {data_folder}/paths.csv")
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


if __name__ == "__main__":
    args = parse_arguments()
    data_folder = Path(args.data_folder)
    df = generate_path_df(data_folder)
    output_path = data_folder / "paths.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved to {output_path}")

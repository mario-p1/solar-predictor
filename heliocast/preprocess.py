from pathlib import Path
from typing import Annotated

import pandas as pd
import typer

from heliocast.data import drop_incomplete_tail, read_sarah3
from heliocast.features import build_tree_features

INPUT_DIR = Path("/opt/ml/processing/input")
OUTPUT_DIR = Path("/opt/ml/processing/output")


def main(
    input_dir: Annotated[Path, typer.Option()] = INPUT_DIR,
    output_dir: Annotated[Path, typer.Option()] = OUTPUT_DIR,
):
    csvs = sorted(input_dir.rglob("sarah3.csv"))
    print(f"Found {len(csvs)} files in {input_dir}")

    df = read_sarah3(None, csvs=csvs, read_fn=pd.read_csv)

    features_df = build_tree_features(drop_incomplete_tail(df))

    # Drop all NaNs
    features_df = features_df.dropna()

    features_df.to_csv(output_dir / "tree_features.csv")
    print(f"Wrote {len(features_df)} rows to {output_dir}")


if __name__ == "__main__":
    typer.run(main)

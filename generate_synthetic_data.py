import pandas as pd
import numpy as np

def synthetic_data(count:int,seed:int):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "time": pd.date_range("2023-01-01", "2023-12-31", periods=count) + pd.to_timedelta(rng.random(count) * 5.0, unit="m"),
            "id": rng.integers(0, 10, size=count),
            "value_alpha": rng.random(size=count) * 100,
            "value_beta": np.abs(rng.random(size=count) * 100),
            "class_gamma": rng.choice(list("abcdefg"), size=count),
        }
    )
    return df

def main():
    df = synthetic_data(1_000_000, 451)
    df.to_parquet("synthetic_data.parquet")

if __name__ == "__main__":
    main()

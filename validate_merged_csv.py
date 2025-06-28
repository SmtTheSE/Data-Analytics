import pandas as pd
import sys

CSV_PATH = 'data/master_merged.csv'

CRITICAL_COLUMNS = ['transaction_id', 'user_id', 'Merchant_id']  # adjust as needed


def main():
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Failed to load CSV: {e}")
        sys.exit(1)

    print(f" Loaded {len(df)} rows, {len(df.columns)} columns.")

    # 1. Check for missing values in critical columns
    for col in CRITICAL_COLUMNS:
        if col not in df.columns:
            print(f" Critical column missing: {col}")
        else:
            missing = df[col].isna().sum()
            if missing > 0:
                print(f" {missing} missing values in critical column '{col}'")
            else:
                print(f" No missing values in '{col}'")

    # 2. Check for duplicate rows on keys
    if all(col in df.columns for col in CRITICAL_COLUMNS):
        dups = df.duplicated(subset=CRITICAL_COLUMNS).sum()
        if dups > 0:
            print(f" {dups} duplicate rows found on {CRITICAL_COLUMNS}")
        else:
            print(f"No duplicate rows on {CRITICAL_COLUMNS}")

    # 3. Check for all-null or constant columns
    for col in df.columns:
        if df[col].isnull().all():
            print(f"  Column '{col}' is all nulls.")
        elif df[col].nunique(dropna=True) == 1:
            print(f" Column '{col}' is constant: {df[col].iloc[0]}")

    # 4. Check for correct data types
    for col in CRITICAL_COLUMNS:
        if col in df.columns:
            if df[col].dtype == object and df[col].str.strip().eq('').any():
                print(f"⚠️  Empty strings in column '{col}'")

    # 5. Sanity check: row count > 0
    if len(df) == 0:
        print(" CSV has zero rows!")
    else:
        print(" CSV has data rows.")

    # 6. Print sample for manual inspection
    print("\nSample data:")
    print(df.head(5).to_string())


if __name__ == "__main__":
    main()
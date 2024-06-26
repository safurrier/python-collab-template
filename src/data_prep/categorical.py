"""
Data preparation methods for categorical variables.
"""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any


def lowercase_string(string: str) -> str:
    """Returns a lowercased string

    Args:
        string: String to lowercase

    Returns:
        String in lowercase
    """
    return string.lower()


def lowercase_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Lowercases a column in a dataframe

    Args:
        df: DataFrame to lowercase
        col: Column in DataFrame to lowercase

    Returns:
        A DataFrame with column lowercased
    """
    df[col] = df[col].apply(lowercase_string)
    return df


def extract_title(
    df: pd.DataFrame,
    col: str,
    replace_dict: Optional[Dict[str, Any]] = None,
    title_col: str = "title",
) -> pd.DataFrame:
    """Extracts titles into a new title column

    Args:
        df: DataFrame to extract titles from
        col: Column in DataFrame to extract titles from
        replace_dict (Optional): Optional dictionary to map titles
        title_col: Name of new column containing extracted titles

    Returns:
        A DataFrame with an additional column of extracted titles
    """
    df[title_col] = df[col].str.extract(r" ([A-Za-z]+)\.", expand=False)

    if replace_dict:
        df[title_col] = np.where(
            df[title_col].isin(replace_dict.keys()),
            df[title_col].map(replace_dict),
            df[title_col],
        )

    return df

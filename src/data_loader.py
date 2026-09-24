from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "Bakery sales.csv"

# Encabezados del CSV de Kaggle ya normalizados.
REQUIRED_COLUMNS = [
    "date", "time", "ticket_number", "article", "quantity", "unit_price",
]


class DatasetError(Exception):
    """Error controlado al leer o validar el dataset."""


def _to_number(series: pd.Series) -> pd.Series:
    """"1.234,50 €" -> 1234.5. Si no hay coma, el punto ya es el decimal."""
    cleaned = (
        series.astype("string")
        .str.replace("€", "", regex=False)
        .str.replace(" ", "", regex=False)  # espacio no separable
        .str.replace(r"\s+", "", regex=True)
    )
    with_comma = cleaned.str.contains(",", na=False)
    cleaned = cleaned.mask(
        with_comma,
        cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_sales(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Limpia el dataset crudo y devuelve (datos, estadísticas de limpieza)."""
    df = raw.copy()

    df = df.drop(columns=[c for c in df.columns if str(c).startswith("Unnamed")])
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise DatasetError(
            "Al dataset le faltan columnas obligatorias: " + ", ".join(missing)
        )

    rows_read = len(df)

    # Lo que no se puede convertir queda como NaT/NaN y se descarta abajo.
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["time"] = df["time"].astype("string").str.strip()
    df["hour"] = pd.to_datetime(df["time"], format="%H:%M", errors="coerce").dt.hour
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = _to_number(df["unit_price"])
    df["article"] = df["article"].astype("string").str.strip()
    df["ticket_number"] = pd.to_numeric(df["ticket_number"], errors="coerce")

    valid = (
        df["date"].notna()
        & df["hour"].notna()
        & df["quantity"].notna()
        & df["unit_price"].notna()
        & df["article"].notna()
        & (df["article"].str.len() > 0)
        & (df["article"] != ".")  # marcador de ticket sin producto real
    )
    df = df.loc[valid].copy()

    # Las cantidades negativas son devoluciones: se conservan (ingreso neto).
    df["quantity"] = df["quantity"].astype("float64")
    df["unit_price"] = df["unit_price"].astype("float64")
    df["revenue"] = df["quantity"] * df["unit_price"]

    df["hour"] = df["hour"].astype("int8")
    df["ticket_number"] = df["ticket_number"].astype("int64")
    df = df[
        ["date", "time", "hour", "ticket_number", "article", "quantity",
         "unit_price", "revenue"]
    ]
    df = df.sort_values(["date", "time"]).reset_index(drop=True)

    stats = {
        "rows_read": rows_read,
        "rows_kept": len(df),
        "rows_dropped": rows_read - len(df),
    }
    return df, stats


@st.cache_data(show_spinner="Cargando histórico de ventas...")
def load_sales(path: str = str(DATA_PATH)) -> tuple[pd.DataFrame, dict]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise DatasetError(
            f"No se encontró el dataset en '{csv_path}'. "
            "Descarga 'French Bakery Daily Sales' de Kaggle y colócalo en data/."
        )
    try:
        raw = pd.read_csv(csv_path)
    except UnicodeDecodeError:
        raw = pd.read_csv(csv_path, encoding="latin-1")
    except pd.errors.EmptyDataError as exc:
        raise DatasetError("El archivo del dataset está vacío.") from exc
    except pd.errors.ParserError as exc:
        raise DatasetError(f"No se pudo interpretar el CSV: {exc}") from exc

    df, stats = clean_sales(raw)
    if df.empty:
        raise DatasetError("El dataset no contiene registros válidos tras la limpieza.")
    return df, stats

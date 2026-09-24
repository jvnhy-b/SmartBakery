import pandas as pd

ALL_PRODUCTS = "Todos"
CURRENCY = "EUR"


def filter_sales(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    article: str = ALL_PRODUCTS,
) -> pd.DataFrame:
    mask = df["date"].between(pd.Timestamp(start), pd.Timestamp(end))
    if article and article != ALL_PRODUCTS:
        mask &= df["article"] == article
    return df.loc[mask]


def product_options(df: pd.DataFrame) -> list[str]:
    return [ALL_PRODUCTS, *sorted(df["article"].dropna().unique())]


def revenue_by_day(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("date", as_index=False)
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .sort_values("date")
    )


def revenue_by_product(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("article", as_index=False)
        .agg(revenue=("revenue", "sum"), units=("quantity", "sum"))
        .sort_values("revenue", ascending=False)
    )


def top_products(df: pd.DataFrame, metric: str = "revenue", limit: int = 10) -> pd.DataFrame:
    """``metric``: "revenue" o "units"."""
    return revenue_by_product(df).nlargest(limit, metric).reset_index(drop=True)


def sales_by_hour(df: pd.DataFrame) -> pd.DataFrame:
    hourly = df.groupby("hour", as_index=False).agg(
        revenue=("revenue", "sum"),
        units=("quantity", "sum"),
        tickets=("ticket_number", "nunique"),
    )
    # Incluye las horas sin ventas para cubrir el día completo.
    full_day = pd.DataFrame({"hour": range(24)})
    return full_day.merge(hourly, on="hour", how="left").fillna(0)


def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_units": 0.0,
            "total_tickets": 0,
            "best_selling_product": None,
            "highest_revenue_product": None,
            "best_sales_day": None,
            "best_sales_day_revenue": 0.0,
        }

    by_product = revenue_by_product(df)
    by_day = revenue_by_day(df)
    best_day = by_day.loc[by_day["revenue"].idxmax()]

    return {
        "total_revenue": float(df["revenue"].sum()),
        "total_units": float(df["quantity"].sum()),
        "total_tickets": int(df["ticket_number"].nunique()),
        "best_selling_product": str(by_product.nlargest(1, "units")["article"].iloc[0]),
        "highest_revenue_product": str(by_product["article"].iloc[0]),
        "best_sales_day": best_day["date"].date().isoformat(),
        "best_sales_day_revenue": float(best_day["revenue"]),
    }


def build_metrics_payload(
    df: pd.DataFrame,
    start: pd.Timestamp,
    end: pd.Timestamp,
    product: str = ALL_PRODUCTS,
    top_n: int = 10,
) -> dict:
    """JSON que se envía a la API de IA: sólo métricas ya agregadas."""
    kpis = compute_kpis(df)
    daily = revenue_by_day(df)

    return {
        "currency": CURRENCY,
        "period": {
            "start": pd.Timestamp(start).date().isoformat(),
            "end": pd.Timestamp(end).date().isoformat(),
            "product_filter": product,
        },
        "metrics": {
            "total_revenue": round(kpis["total_revenue"], 2),
            "total_units": round(kpis["total_units"], 2),
            "total_tickets": kpis["total_tickets"],
            "best_selling_product": kpis["best_selling_product"] or "",
            "highest_revenue_product": kpis["highest_revenue_product"] or "",
            "best_sales_day": kpis["best_sales_day"] or "",
        },
        "top_products": [
            {
                "article": row.article,
                "revenue": round(float(row.revenue), 2),
                "units": round(float(row.units), 2),
            }
            for row in top_products(df, "revenue", top_n).itertuples()
        ],
        "daily_performance": [
            {
                "date": row.date.date().isoformat(),
                "revenue": round(float(row.revenue), 2),
                "units": round(float(row.units), 2),
            }
            for row in daily.itertuples()
        ],
        "hourly_performance": [
            {"hour": int(row.hour), "revenue": round(float(row.revenue), 2)}
            for row in sales_by_hour(df).itertuples()
        ],
    }


def previous_period(start, end) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Periodo inmediatamente anterior, de la misma duración."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    previous_end = start - pd.Timedelta(days=1)
    return previous_end - (end - start), previous_end


def percent_change(current: float, previous: float) -> float | None:
    """None si no hay base de comparación."""
    if not previous:
        return None
    return (current - previous) / abs(previous) * 100.0


def peak_hour(df: pd.DataFrame) -> int | None:
    if df.empty:
        return None
    hourly = sales_by_hour(df)
    return int(hourly.loc[hourly["revenue"].idxmax(), "hour"])

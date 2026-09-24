import pandas as pd
import streamlit as st

from src.ai import render_ai_panel
from src.analytics import (
    ALL_PRODUCTS,
    build_metrics_payload,
    compute_kpis,
    filter_sales,
    peak_hour,
    percent_change,
    previous_period,
    product_options,
    revenue_by_day,
    sales_by_hour,
    top_products,
)
from src.data_loader import DatasetError, load_sales
from src.ui import (
    KPI_HEIGHT,
    filter_pill,
    format_eur,
    format_units,
    kpi_card,
    page_header,
)

CHART_HEIGHT = 330
CHARTS_HEIGHT = 430
BLOCK_GAP = 14  # separación de 1rem entre bloques de Streamlit

# El panel de IA iguala el alto de las tarjetas más las gráficas.
AI_PANEL_HEIGHT = KPI_HEIGHT + BLOCK_GAP + CHARTS_HEIGHT
PREVIEW_ROWS = 100

try:
    sales, _ = load_sales()
except DatasetError as error:
    st.error(str(error), icon=":material/database_off:")
    st.stop()

min_date = sales["date"].min().date()
max_date = sales["date"].max().date()

title_col, filter_col = st.columns([4, 1], vertical_alignment="center")

with title_col:
    page_header(
        "Analítica de ventas",
        "Explora el comportamiento histórico de las ventas de SmartBakery.",
    )

with filter_col:
    with st.container(horizontal_alignment="right"):
        with st.popover("Filtros", icon=":material/tune:", width="stretch"):
            st.markdown("**Filtros del periodo**")
            date_range = st.date_input(
                "Rango de fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                format="DD/MM/YYYY",
                key="analytics_date_range",
            )
            product = st.selectbox(
                "Producto", product_options(sales), key="analytics_product"
            )
            st.caption(
                f"Histórico disponible: {min_date:%d/%m/%Y} – {max_date:%d/%m/%Y}."
            )

if not isinstance(date_range, tuple) or len(date_range) != 2:
    st.info("Selecciona la fecha final del rango para ver los resultados.")
    st.stop()

start_date, end_date = date_range
filtered = filter_sales(sales, start_date, end_date, product)

if filtered.empty:
    st.warning(
        "No hay ventas registradas con los filtros seleccionados.",
        icon=":material/search_off:",
    )
    st.stop()

kpis = compute_kpis(filtered)
daily = revenue_by_day(filtered)

previous = filter_sales(sales, *previous_period(start_date, end_date), product)
previous_kpis = compute_kpis(previous)
revenue_change = percent_change(kpis["total_revenue"], previous_kpis["total_revenue"])
units_change = percent_change(kpis["total_units"], previous_kpis["total_units"])

# Sólo se resaltan los filtros que el usuario cambió.
filter_pill(
    [
        (
            f"{start_date:%d/%m/%Y} – {end_date:%d/%m/%Y}",
            (start_date, end_date) != (min_date, max_date),
        ),
        (
            product if product != ALL_PRODUCTS else "Todos los productos",
            product != ALL_PRODUCTS,
        ),
        (f"{len(daily)} días con ventas", False),
        (f"{kpis['total_tickets']:,} tickets".replace(",", "."), False),
    ]
)

board_col, ai_col = st.columns([2, 1], gap="medium")

with board_col:
    revenue_card, units_card, product_card, day_card = st.columns(4)

    with revenue_card:
        kpi_card(
            "Ingresos",
            format_eur(kpis["total_revenue"]),
            tone=0,
            delta=revenue_change,
            delta_context="vs anterior",
            help="Suma de cantidad × precio unitario. La variación compara "
            "contra el periodo anterior de la misma duración.",
        )

    with units_card:
        kpi_card(
            "Unidades vendidas",
            format_units(kpis["total_units"]),
            tone=1,
            delta=units_change,
            delta_context="vs anterior",
            help="Suma de unidades; las devoluciones restan.",
        )

    with product_card:
        kpi_card(
            "Producto más vendido",
            kpis["best_selling_product"],
            tone=3,
            note="Por unidades",
            help="Producto con más unidades vendidas en el periodo.",
        )

    with day_card:
        kpi_card(
            "Mejor día",
            pd.Timestamp(kpis["best_sales_day"]).strftime("%d/%m/%Y"),
            tone=4,
            note=f"Ingresos: {format_eur(kpis['best_sales_day_revenue'])}",
            help="Fecha con mayor ingreso total del periodo.",
        )

    daily_tab, products_tab, hours_tab, detail_tab = st.tabs(
        [
            ":material/show_chart: Ingresos por día",
            ":material/leaderboard: Productos",
            ":material/schedule: Ventas por hora",
            ":material/table_rows: Detalle",
        ],
        height=CHARTS_HEIGHT,
    )

    with daily_tab:
        st.caption(
            f"Promedio de {format_eur(daily['revenue'].mean())} por día con ventas."
        )
        st.line_chart(
            daily,
            x="date",
            y="revenue",
            x_label="Fecha",
            y_label="Ingresos (€)",
            height=CHART_HEIGHT,
        )

    with products_tab:
        metric_label = st.segmented_control(
            "Métrica",
            ["Ingresos", "Unidades"],
            default="Ingresos",
            key="top_products_metric",
            label_visibility="collapsed",
        )
        metric = "units" if metric_label == "Unidades" else "revenue"
        best = top_products(filtered, metric).sort_values(metric)
        st.caption(
            "Top 10 de productos por ingresos totales (€)."
            if metric == "revenue"
            else "Top 10 de productos por unidades vendidas."
        )
        st.bar_chart(
            best,
            x="article",
            y=metric,
            horizontal=True,
            sort=False,
            x_label="Ingresos (€)" if metric == "revenue" else "Unidades",
            y_label="Producto",
            height=CHART_HEIGHT,
        )

    with hours_tab:
        busiest = peak_hour(filtered)
        st.caption(f"La hora de mayor ingreso del periodo es las {busiest}:00.")
        st.bar_chart(
            sales_by_hour(filtered),
            x="hour",
            y="revenue",
            x_label="Hora del día",
            y_label="Ingresos (€)",
            height=CHART_HEIGHT,
        )

    with detail_tab:
        st.caption(
            f"Primeros {min(PREVIEW_ROWS, len(filtered)):,} de "
            f"{len(filtered):,} registros filtrados.".replace(",", ".")
        )
        st.dataframe(
            filtered.head(PREVIEW_ROWS),
            hide_index=True,
            height=CHART_HEIGHT,
            column_config={
                "date": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
                "time": st.column_config.TextColumn("Hora"),
                "hour": None,
                "ticket_number": st.column_config.NumberColumn("Ticket", format="%d"),
                "article": st.column_config.TextColumn("Producto"),
                "quantity": st.column_config.NumberColumn("Unidades", format="%.0f"),
                "unit_price": st.column_config.NumberColumn(
                    "Precio unitario", format="euro"
                ),
                "revenue": st.column_config.NumberColumn("Ingreso", format="euro"),
            },
        )

with ai_col:
    render_ai_panel(
        build_metrics_payload(filtered, start_date, end_date, product),
        height=AI_PANEL_HEIGHT,
    )

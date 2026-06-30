import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Análisis de Acciones IA", page_icon="📈", layout="wide")

st.title("📈 Analizador Inteligente de Acciones")
st.markdown("Selecciona una acción del desplegable o escribe el ticker para obtener un análisis completo con gráficos en tiempo real.")

# ---------------------------------------------------------
# SELECTOR DE ACCIONES (Desplegable + Escritura manual)
# ---------------------------------------------------------
acciones_conocidas = {
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Tesla (TSLA)": "TSLA",
    "Amazon (AMZN)": "AMZN",
    "Google (GOOGL)": "GOOGL",
    "Nvidia (NVDA)": "NVDA",
    "Meta / Facebook (META)": "META",
    "Netflix (NFLX)": "NFLX",
    "Berkshire Hathaway (BRK-B)": "BRK-B",
    "Coca-Cola (KO)": "KO",
    "Escribir otro ticker manualmente": "OTRO"
}

opcion_seleccionada = st.selectbox("Selecciona una empresa o elige escribir manualmente:", list(acciones_conocidas.keys()))

if opcion_seleccionada == "Escribir otro ticker manualmente":
    ticker = st.text_input("Introduce el Ticker exacto (ej. KO, MCD, UBER):", "AAPL").upper()
else:
    ticker = acciones_conocidas[opcion_seleccionada]

if st.button("Analizar", type="primary"):
    if not ticker:
        st.warning("Por favor, introduce o selecciona un ticker válido.")
    else:
        with st.spinner(f"Analizando {ticker} y descargando gráficos..."):
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1y")
                
                if not info or hist.empty:
                    st.error("No se encontraron datos para este ticker. Intenta con otro.")
                else:
                    # Variables básicas
                    precio_actual = hist['Close'].iloc[-1]
                    nombre = info.get('shortName', ticker)
                    market_cap = info.get('marketCap', 0) or 0
                    sector = info.get('sector', 'N/A')
                    
                    st.header(f"Análisis para: {nombre}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Precio Actual", f"${precio_actual:.2f}")
                    col2.metric("Capitalización de Mercado", f"${market_cap/1e9:.2f}B" if market_cap > 0 else "N/A")
                    col3.metric("Sector", sector)
                    
                    # ---------------------------------------------------------
                    # RESUMEN Y ANÁLISIS DE LA ACCIÓN (Widgets arreglados)
                    # ---------------------------------------------------------
                    st.subheader("📄 Resumen y Análisis del Símbolo")
                    
                    # 1. Widget de Resumen (Symbol Overview)
                    overview_html = f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ margin: 0; padding: 0; overflow: hidden; }}
                            .tv-container {{ height: 400px; width: 100%; }}
                        </style>
                    </head>
                    <body>
                        <div class="tradingview-widget-container tv-container">
                            <div class="tradingview-widget-container__widget"></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js" async>
                            {{
                                "symbols": [[
                                    "{ticker}|1D"
                                ]],
                                "chartOnly": false,
                                "width": "100%",
                                "height": "100%",
                                "locale": "es",
                                "colorTheme": "light",
                                "autosize": true,
                                "showVolume": true,
                                "showMA": true,
                                "hideDateRanges": false,
                                "hideMarketStatus": false,
                                "hideSymbolLogo": false,
                                "scalePosition": "right",
                                "scaleMode": "Normal",
                                "fontFamily": "Trebuchet MS, sans-serif",
                                "fontSize": "10",
                                "noTimeScale": false,
                                "valuesTracking": "1",
                                "changeMode": "price-and-percent",
                                "chartType": "area",
                                "lineWidth": 2,
                                "lineType": 0,
                                "dateRanges": [
                                    "1d|1",
                                    "1m|30",
                                    "3m|60",
                                    "12m|1D",
                                    "60m|1W",
                                    "all|1M"
                                ]
                            }}
                            </script>
                        </div>
                    </body>
                    </html>
                    """
                    st.components.v1.html(overview_html, height=420)
                    
                    # Texto de respaldo (Descripción de Yahoo Finance)
                    with st.expander("Leer descripción textual de la empresa"):
                        st.write(info.get('longBusinessSummary', 'No hay resumen disponible.'))

                    # 2. Widget de Análisis Técnico (Compra/Venta automático)
                    st.markdown("#### 🔍 Análisis Técnico Automático (Señales de TradingView)")
                    analysis_html = f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ margin: 0; padding: 0; overflow: hidden; }}
                            .tv-container {{ height: 400px; width: 100%; }}
                        </style>
                    </head>
                    <body>
                        <div class="tradingview-widget-container tv-container">
                            <div class="tradingview-widget-container__widget"></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
                            {{
                                "interval": "1D",
                                "width": "100%",
                                "height": "100%",
                                "isTransparent": false,
                                "symbol": "{ticker}",
                                "showIntervalTabs": true,
                                "locale": "es",
                                "colorTheme": "light"
                            }}
                            </script>
                        </div>
                    </body>
                    </html>
                    """
                    st.components.v1.html(analysis_html, height=420)

                    # ---------------------------------------------------------
                    # PUNTOS FUERTES Y DÉBILES
                    # ---------------------------------------------------------
                    st.subheader("💪 Puntos Fuertes y ⚠️ Puntos Débiles")
                    col_fortalezas, col_debilidades = st.columns(2)
                    
                    fortalezas = []
                    debilidades = []
                    
                    profit_margins = info.get('profitMargins') or 0
                    if profit_margins > 0.15:
                        fortalezas.append(f"Alto margen de beneficio ({profit_margins*100:.1f}%)")
                    elif profit_margins < 0:
                        debilidades.append(f"La empresa opera en pérdidas (Margen: {profit_margins*100:.1f}%)")
                    
                    revenue_growth = info.get('revenueGrowth') or 0
                    if revenue_growth > 0.1:
                        fortalezas.append(f"Fuerte crecimiento de ingresos ({revenue_growth*100:.1f}%)")
                    elif revenue_growth < 0:
                        debilidades.append(f"Caída de ingresos ({revenue_growth*100:.1f}%)")
                    
                    debt_to_equity = info.get('debtToEquity') or 0
                    if 0 < debt_to_equity < 100:
                        fortalezas.append(f"Bajo nivel de deuda (Deuda/Capital: {debt_to_equity})")
                    elif debt_to_equity > 200:
                        debilidades.append(f"Alta deuda apalancada (Deuda/Capital: {debt_to_equity})")
                    
                    current_ratio = info.get('currentRatio') or 0
                    if current_ratio > 1.5:
                        fortalezas.append(f"Excelente liquidez (Ratio corriente: {current_ratio})")
                    elif 0 < current_ratio < 1:
                        debilidades.append(f"Posibles problemas de liquidez a corto plazo (Ratio: {current_ratio})")

                    with col_fortalezas:
                        st.success("**Fortalezas:**")
                        for f in fortalezas:
                            st.write(f"✅ {f}")
                        if not fortalezas: st.write("No se detectaron fortalezas destacables.")

                    with col_debilidades:
                        st.error("**Debilidades:**")
                        for d in debilidades:
                            st.write(f"❌ {d}")
                        if not debilidades: st.write("No se detectaron debilidades críticas.")

                    # ---------------------------------------------------------
                    # PREVISIÓN Y PRECIOS OBJETIVO
                    # ---------------------------------------------------------
                    st.subheader("🎯 Previsión de Crecimiento y Precios Objetivo")
                    target_low = info.get('targetLowPrice') or precio_actual
                    target_mean = info.get('targetMeanPrice') or precio_actual
                    target_high = info.get('targetHighPrice') or precio_actual
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Precio Objetivo Bajo", f"${target_low:.2f}")
                    c2.metric("Precio Objetivo Medio", f"${target_mean:.2f}")
                    c3.metric("Precio Objetivo Alto", f"${target_high:.2f}")
                    potencial = ((target_mean - precio_actual) / precio_actual) * 100
                    c4.metric("Potencial (Media)", f"{potencial:.1f}%", delta_color="inverse" if potencial < 0 else "normal")

                    # ---------------------------------------------------------
                    # INDICADORES TÉCNICOS Y PUNTOS DE ENTRADA/SALIDA
                    # ---------------------------------------------------------
                    st.subheader("📊 Indicadores Técnicos y Puntos de Entrada/Salida")
                    
                    hist['SMA50'] = hist['Close'].rolling(window=50).mean()
                    hist['SMA200'] = hist['Close'].rolling(window=200).mean()
                    
                    sma50 = hist['SMA50'].iloc[-1] if not pd.isna(hist['SMA50'].iloc[-1]) else precio_actual
                    sma200 = hist['SMA200'].iloc[-1] if not pd.isna(hist['SMA200'].iloc[-1]) else precio_actual
                    
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_actual = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
                    
                    precio_entrada_ideal = sma50 * 0.98  
                    precio_salida_ideal = target_high    
                    precio_stop_loss = sma200            
                    
                    col_ent, col_sal, col_ind = st.columns(3)
                    with col_ent:
                        st.info("**Puntos de Entrada (Compras)**")
                        st.write(f"🔹 Precio de entrada técnica ideal: **${precio_entrada_ideal:.2f}** (Cerca del soporte SMA50)")
                        st.write(f"🔹 Punto de entrada por sobreventa (RSI < 30): Esperar a que el precio caiga a zonas de pánico.")
                    
                    with col_sal:
                        st.warning("**Puntos de Salida (Take Profit / Stop Loss)**")
                        st.write(f"🔸 Take Profit (Objetivo alcista): **${precio_salida_ideal:.2f}**")
                        st.write(f"🔸 Stop Loss (Soporte técnico crítico): **${precio_stop_loss:.2f}** (SMA200, si cae por debajo, vender)")
                    
                    with col_ind:
                        st.info("**Indicadores Clave**")
                        st.write(f"📈 RSI (14): **{rsi_actual:.1f}**")
                        st.write(f"📈 SMA 50: **${sma50:.2f}**")
                        st.write(f"📈 SMA 200: **${sma200:.2f}**")

                    # ---------------------------------------------------------
                    # GRÁFICO GIGANTE DE TRADINGVIEW (Cuadro arreglado a 1000px)
                    # ---------------------------------------------------------
                    st.subheader("📈 Gráfico Técnico Avanzado (Tiempo Real)")
                    st.markdown("*(Puedes hacer zoom, cambiar a velas japonesas, y ver diferentes temporalidades usando la barra superior del gráfico)*")
                    
                    chart_html = f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ margin: 0; padding: 0; overflow: hidden; }}
                            .tv-container {{ height: 1000px; width: 100%; }}
                        </style>
                    </head>
                    <body>
                        <div class="tradingview-widget-container tv-container">
                            <div class="tradingview-widget-container__widget"></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                            {{
                                "autosize": true,
                                "symbol": "{ticker}",
                                "interval": "D",
                                "timezone": "Etc/UTC",
                                "theme": "light",
                                "style": "1",
                                "locale": "es",
                                "toolbar_bg": "#f1f3f6",
                                "enable_publishing": false,
                                "allow_symbol_change": true,
                                "studies": [
                                    "STD;SMA",
                                    "STD;RSI",
                                    "STD;MACD"
                                ]
                            }}
                            </script>
                        </div>
                    </body>
                    </html>
                    """
                    # El contenedor de Streamlit ahora tiene 1000px de alto, sin scroll
                    st.components.v1.html(chart_html, height=1000)
                    
                    # ---------------------------------------------------------
                    # RECOMENDACIÓN FINAL
                    # ---------------------------------------------------------
                    st.subheader("🤖 Veredicto Final: ¿Es buena compra?")
                    
                    score = 0
                    if precio_actual < sma50: score += 1
                    if precio_actual > sma200: score += 1
                    if rsi_actual < 40: score += 1
                    if potencial > 15: score += 2
                    if len(fortalezas) > len(debilidades): score += 1
                    
                    if score >= 4:
                        st.success("🟢 **COMPRAR / BUENA OPCIÓN**: La acción muestra fortaleza fundamental y un potencial de crecimiento alto. Los técnicos sugieren que no está sobrevalorada.")
                    elif score >= 2:
                        st.warning("🟡 **ESPERAR**: La acción tiene señales mixtas. Ya sea porque está cara técnicamente (sobrecompra) o su crecimiento fundamental es moderado. Mejor buscar un mejor punto de entrada.")
                    else:
                        st.error("🔴 **NI MIRARLA**: La acción está sobrevalorada, en tendencia bajista o tiene graves problemas fundamentales (alta deuda/pérdidas). Evítala por ahora.")

            except Exception as e:
                st.error(f"Ocurrió un error inesperado al procesar los datos. Intenta con otro ticker. (Detalle: {e})")

import streamlit as st
import yfinance as yf
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Análisis de Acciones IA", page_icon="📈", layout="wide")

# Inicializar estado para pantalla completa
if "fullscreen_chart" not in st.session_state:
    st.session_state.fullscreen_chart = False

# ---------------------------------------------------------
# LÓGICA DE PANTALLA COMPLETA (Solo muestra el gráfico gigante)
# ---------------------------------------------------------
if st.session_state.fullscreen_chart:
    if st.button("⬅️ Volver al Análisis Completo"):
        st.session_state.fullscreen_chart = False
        st.rerun()
    
    st.subheader("Gráfico en Pantalla Completa")
    ticker_tv = st.session_state.get("ticker_tv", "AAPL")
    chart_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ margin: 0; padding: 0; overflow: hidden; }}
            .tv-container {{ height: 1500px; width: 100%; }}
        </style>
    </head>
    <body>
        <div class="tradingview-widget-container tv-container">
            <div class="tradingview-widget-container__widget"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
            {{
                "autosize": true,
                "symbol": "{ticker_tv}",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "light",
                "style": "1",
                "locale": "es",
                "toolbar_bg": "#f1f3f6",
                "enable_publishing": false,
                "allow_symbol_change": true,
                "studies": ["STD;SMA", "STD;RSI", "STD;MACD"]
            }}
            </script>
        </div>
    </body>
    </html>
    """
    st.components.v1.html(chart_html, height=1500)
    st.stop() # Detiene la ejecución del resto de la app

# ---------------------------------------------------------
# DICCIONARIO DE ACCIONES (Incluye Fibras de México)
# Se usa formato: "Nombre": ("Ticker_Yahoo", "Ticker_TradingView")
# ---------------------------------------------------------
acciones_conocidas = {
    "Apple (AAPL)": ("AAPL", "AAPL"),
    "Microsoft (MSFT)": ("MSFT", "MSFT"),
    "Tesla (TSLA)": ("TSLA", "TSLA"),
    "Amazon (AMZN)": ("AMZN", "AMZN"),
    "Google (GOOGL)": ("GOOGL", "GOOGL"),
    "Nvidia (NVDA)": ("NVDA", "NVDA"),
    "Coca-Cola (KO)": ("KO", "KO"),
    "Fibra Uno (México)": ("FUNO11.MX", "BMV:FUNO11"),
    "Fibra Danhos (México)": ("DANHOS13.MX", "BMV:DANHOS13"),
    "Fibra Macquarie (México)": ("FIBRAMQ.MX", "BMV:FIBRAMQ"),
    "Fibra Hotel (México)": ("FHO14.MX", "BMV:FHO14"),
    "América Móvil (México)": ("AMXL.MX", "BMV:AMXL"),
    "Walmart de México": ("WALMEX.MX", "BMV:WALMEX"),
    "Escribir ticker manualmente": ("OTRO", "OTRO")
}

st.title("📈 Analizador Inteligente de Acciones")
st.markdown("Selecciona una empresa o escribe el ticker. (Para acciones mexicanas manualmente, usa el formato BMV:TICKER para que el gráfico cargue).")

opcion_seleccionada = st.selectbox("Selecciona una empresa:", list(acciones_conocidas.keys()))

if opcion_seleccionada == "Escribir ticker manualmente":
    ticker_input = st.text_input("Introduce el Ticker (ej. AAPL, o para México: BMV:FUNO11):", "AAPL")
    ticker_yf = ticker_input.replace("BMV:", "") + (".MX" if "BMV:" in ticker_input and ".MX" not in ticker_input else "")
    ticker_tv = ticker_input
else:
    ticker_yf, ticker_tv = acciones_conocidas[opcion_seleccionada]

if st.button("Analizar", type="primary"):
    if not ticker_yf:
        st.warning("Por favor, introduce un ticker válido.")
    else:
        with st.spinner(f"Analizando {ticker_yf}..."):
            try:
                stock = yf.Ticker(ticker_yf)
                info = stock.info
                hist = stock.history(period="1y")
                
                if not info or hist.empty:
                    st.error(f"No se encontraron datos para {ticker_yf}. Intenta con otro.")
                else:
                    # Variables básicas
                    precio_actual = hist['Close'].iloc[-1]
                    nombre = info.get('shortName', ticker_yf)
                    market_cap = info.get('marketCap', 0) or 0
                    sector = info.get('sector', 'N/A')
                    
                    st.header(f"Análisis para: {nombre}")
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Precio Actual", f"${precio_actual:.2f}")
                    col2.metric("Capitalización", f"${market_cap/1e9:.2f}B" if market_cap > 0 else "N/A")
                    col3.metric("Sector", sector)
                    
                    # ---------------------------------------------------------
                    # DESCRIPCIÓN DE LA EMPRESA (Directo de Yahoo, siempre visible)
                    # ---------------------------------------------------------
                    st.subheader("📄 Descripción del Negocio")
                    descripcion = info.get('longBusinessSummary')
                    if descripcion:
                        st.write(descripcion)
                    else:
                        st.warning("No hay descripción textual disponible para este ticker en Yahoo Finance.")
                    
                    # ---------------------------------------------------------
                    # PUNTOS FUERTES Y DÉBILES
                    # ---------------------------------------------------------
                    st.subheader("💪 Puntos Fuertes y ⚠️ Puntos Débiles")
                    col_fortalezas, col_debilidades = st.columns(2)
                    
                    fortalezas = []
                    debilidades = []
                    
                    profit_margins = info.get('profitMargins') or 0
                    if profit_margins > 0.15: fortalezas.append(f"Alto margen de beneficio ({profit_margins*100:.1f}%)")
                    elif profit_margins < 0: debilidades.append(f"La empresa opera en pérdidas (Margen: {profit_margins*100:.1f}%)")
                    
                    revenue_growth = info.get('revenueGrowth') or 0
                    if revenue_growth > 0.1: fortalezas.append(f"Fuerte crecimiento de ingresos ({revenue_growth*100:.1f}%)")
                    elif revenue_growth < 0: debilidades.append(f"Caída de ingresos ({revenue_growth*100:.1f}%)")
                    
                    debt_to_equity = info.get('debtToEquity') or 0
                    if 0 < debt_to_equity < 100: fortalezas.append(f"Bajo nivel de deuda (Deuda/Capital: {debt_to_equity})")
                    elif debt_to_equity > 200: debilidades.append(f"Alta deuda apalancada (Deuda/Capital: {debt_to_equity})")
                    
                    current_ratio = info.get('currentRatio') or 0
                    if current_ratio > 1.5: fortalezas.append(f"Excelente liquidez (Ratio: {current_ratio})")
                    elif 0 < current_ratio < 1: debilidades.append(f"Problemas de liquidez (Ratio: {current_ratio})")

                    with col_fortalezas:
                        st.success("**Fortalezas:**")
                        for f in fortalezas: st.write(f"✅ {f}")
                        if not fortalezas: st.write("No se detectaron fortalezas destacables.")
                    with col_debilidades:
                        st.error("**Debilidades:**")
                        for d in debilidades: st.write(f"❌ {d}")
                        if not debilidades: st.write("No se detectaron debilidades críticas.")

                    # ---------------------------------------------------------
                    # PREVISIÓN Y PRECIOS OBJETIVO
                    # ---------------------------------------------------------
                    st.subheader("🎯 Previsión y Precios Objetivo")
                    target_low = info.get('targetLowPrice') or precio_actual
                    target_mean = info.get('targetMeanPrice') or precio_actual
                    target_high = info.get('targetHighPrice') or precio_actual
                    
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Objetivo Bajo", f"${target_low:.2f}")
                    c2.metric("Objetivo Medio", f"${target_mean:.2f}")
                    c3.metric("Objetivo Alto", f"${target_high:.2f}")
                    potencial = ((target_mean - precio_actual) / precio_actual) * 100
                    c4.metric("Potencial (Media)", f"{potencial:.1f}%", delta_color="inverse" if potencial < 0 else "normal")

                    # ---------------------------------------------------------
                    # INDICADORES TÉCNICOS
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
                        st.info("**Puntos de Entrada**")
                        st.write(f"🔹 Entrada técnica ideal: **${precio_entrada_ideal:.2f}**")
                        st.write(f"🔹 Entrada por sobreventa (RSI < 30)")
                    with col_sal:
                        st.warning("**Puntos de Salida**")
                        st.write(f"🔸 Take Profit: **${precio_salida_ideal:.2f}**")
                        st.write(f"🔸 Stop Loss: **${precio_stop_loss:.2f}**")
                    with col_ind:
                        st.info("**Indicadores Clave**")
                        st.write(f"📈 RSI (14): **{rsi_actual:.1f}**")
                        st.write(f"📈 SMA 50: **${sma50:.2f}**")
                        st.write(f"📈 SMA 200: **${sma200:.2f}**")

                    # ---------------------------------------------------------
                    # GRÁFICO DE TRADINGVIEW (Con control de altura y pantalla completa)
                    # ---------------------------------------------------------
                    st.subheader("📈 Gráfico Técnico Avanzado")
                    
                    # Guardar ticker de TradingView en sesión para pantalla completa
                    st.session_state.ticker_tv = ticker_tv
                    
                    col_btn, col_slider = st.columns([1, 3])
                    with col_btn:
                        if st.button("🖥️ Ver en Pantalla Completa"):
                            st.session_state.fullscreen_chart = True
                            st.rerun()
                    with col_slider:
                        altura_grafico = st.slider("Ajustar altura del gráfico (px)", min_value=400, max_value=1500, value=800, step=100)
                    
                    chart_html = f"""
                    <!DOCTYPE html>
                    <html lang="es">
                    <head>
                        <meta charset="UTF-8">
                        <style>
                            body {{ margin: 0; padding: 0; overflow: hidden; }}
                            .tv-container {{ height: {altura_grafico}px; width: 100%; }}
                        </style>
                    </head>
                    <body>
                        <div class="tradingview-widget-container tv-container">
                            <div class="tradingview-widget-container__widget"></div>
                            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js" async>
                            {{
                                "autosize": true,
                                "symbol": "{ticker_tv}",
                                "interval": "D",
                                "timezone": "Etc/UTC",
                                "theme": "light",
                                "style": "1",
                                "locale": "es",
                                "toolbar_bg": "#f1f3f6",
                                "enable_publishing": false,
                                "allow_symbol_change": true,
                                "studies": ["STD;SMA", "STD;RSI", "STD;MACD"]
                            }}
                            </script>
                        </div>
                    </body>
                    </html>
                    """
                    st.components.v1.html(chart_html, height=altura_grafico + 20)
                    
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
                        st.success("🟢 **COMPRAR / BUENA OPCIÓN**: Fortaleza fundamental y alto potencial de crecimiento.")
                    elif score >= 2:
                        st.warning("🟡 **ESPERAR**: Señales mixtas. Mejor buscar un mejor punto de entrada.")
                    else:
                        st.error("🔴 **NI MIRARLA**: Sobrevalorada, tendencia bajista o problemas fundamentales.")

            except Exception as e:
                st.error(f"Ocurrió un error. (Detalle: {e})")

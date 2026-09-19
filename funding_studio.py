import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FFMpegWriter

# --- 1. CONFIGURATION FOR 1-MINUTE RUNTIME ---
frames_total = 300         # Extended timeline to hit exactly 60 seconds
fps_rate = 5               # 5 Frames Per Second = 60 Seconds total runtime
tenors = np.array([0.33, 1.0, 3.0, 7.0]) # 8H, 1D, 3D, 7D Term Horizons
venues = ['Binance', 'Bybit', 'OKX', 'dYdX']

print("📈 Initializing professional 1-minute historical regime simulator...")

# --- 2. GENERATING HIGH-FIDELITY PRICE ACTION & REALISTIC COINTEGRATED RATES ---
np.random.seed(88)

# Simulating a realistic multi-regime institutional tape (incorporating cyclical drift and mean reversion)
btc_prices = []
current_price = 84000.0  # Grounding price action around known recent velocity levels
for f in range(frames_total):
    if f < 100:
        # Regime I: Aggressive institutional accumulation trend (Frames 0-100)
        current_price += np.random.normal(120, 180) + 40
    elif f >= 100 and f < 180:
        # Regime II: Distribution phase with heavy whale selling (Frames 100-180)
        current_price += np.random.normal(-50, 310)
    elif f >= 180 and f < 250:
        # Regime III: Long Squeeze & Forced Liquidation Cascade (Frames 180-250)
        current_price += np.random.normal(-450, 450) - 150
    else:
        # Regime IV: Market Capitulation Bottom & Volatility Compression (Frames 250-300)
        current_price += np.random.normal(60, 140)
    btc_prices.append(current_price)

# Constructing high-fidelity candles (Open, High, Low, Close) from the ticker array
candles = []
for i in range(frames_total):
    close_p = btc_prices[i]
    open_p = btc_prices[i-1] if i > 0 else close_p - 110
    high_p = max(open_p, close_p) + np.abs(np.random.normal(140, 45))
    low_p = min(open_p, close_p) - np.abs(np.random.normal(140, 45))
    candles.append((open_p, high_p, low_p, close_p))

# --- 3. CANVAS LAYOUT SETUP (DEEP BLACK / ANTI-FLASH MODE) ---
plt.style.use('dark_background')
fig = plt.figure(figsize=(15, 11), dpi=120)
fig.patch.set_facecolor('#020406')

# Allocate layouts: Top 65% for 3D topology radar, bottom 35% for the candlestick tape
gs = gridspec.GridSpec(2, 1, height_ratios=[1.3, 0.7], hspace=0.28)
ax_3d = fig.add_subplot(gs[0], projection='3d')
ax_2d = fig.add_subplot(gs[1])

ax_3d.set_facecolor('#05080b')
ax_2d.set_facecolor('#05080b')

# Add subtle slate paneling so the background feels premium rather than flat grey
for axis in [ax_2d.xaxis, ax_2d.yaxis]:
    axis.label.set_color('#b5c0d1')
    axis.set_tick_params(colors='#b5c0d1', labelsize=8)

for spine in ax_2d.spines.values():
    spine.set_color('#18212b')

# 3D pane styling: darker, more cinematic black/charcoal surfaces
ax_3d.xaxis.pane.set_facecolor((0.03, 0.05, 0.08, 1.0))
ax_3d.yaxis.pane.set_facecolor((0.03, 0.05, 0.08, 1.0))
ax_3d.zaxis.pane.set_facecolor((0.03, 0.05, 0.08, 1.0))
ax_3d.xaxis.pane.set_edgecolor('#1a2330')
ax_3d.yaxis.pane.set_edgecolor('#1a2330')
ax_3d.zaxis.pane.set_edgecolor('#1a2330')

# --- 4. EXECUTING SEQUENTIAL VIDEO COMPILATION ---
writer = FFMpegWriter(fps=fps_rate, metadata=dict(title='Term Structure Analytics', artist='QuantDesk'))

print("🎬 Recording stream frames directly into MP4 container format...")

with writer.saving(fig, "historical_funding_arbitrage.mp4", dpi=120):
    for f in range(frames_total):
        ax_3d.clear()
        ax_2d.clear()
        
        # Segment and classify the active macroeconomic regimes dynamically
        if f < 100:
            regime_text = "MACRO ACCUMULATION PHASE (High Contango Surcharges)"
            regime_color = "#00ff66" # Institutional Green
            macro_skew = 0.16 * (f / 100.0) + 0.02
        elif f >= 100 and f < 180:
            regime_text = "VOLATILITY DISTRIBUTION PHASE (Curve Mean Reversion)"
            regime_color = "#ffcc00" # Warning Yellow
            macro_skew = 0.18 + np.sin(f * 0.15) * 0.04
        elif f >= 180 and f < 250:
            regime_text = "LIQUIDATION MELTDOWN (Deep Backwardation Inversion)"
            regime_color = "#ff3333" # Risk Crimson
            macro_skew = -0.12 * ((f - 180) / 70.0) + 0.10
        else:
            regime_text = "CAPITULATION FLOOR (Consolidation & Re-Accumulation)"
            regime_color = "#00ccff" # Cyan Stabilization
            macro_skew = -0.02 + np.random.normal(0, 0.005)

        fig.suptitle(f"BITCOIN FUNDING RATE TERM STRUCTURE RADAR\nRegime Monitor: {regime_text}", 
                     color=regime_color, fontsize=13, fontweight='bold', y=0.96)

        # --- A. GENERATING THE 3D KINETIC TOPOLOGY SURFACE ---
        X_tenors = np.linspace(0.33, 7.0, 40)
        Y_venues = np.arange(len(venues))
        X_mesh, Y_mesh = np.meshgrid(X_tenors, Y_venues)
        
        Z_surface = np.zeros_like(X_mesh)
        for v_idx, venue in enumerate(venues):
            # Formulating baseline structural curve behavior
            base = macro_skew * np.exp(-0.4 * X_tenors)
            # Embedding localized exchange constraints (simulating real order-book supply/demand friction)
            exchange_friction = 0.02 * np.sin(f * 0.12 + v_idx) if f < 180 else -0.025 * np.cos(f * 0.2 + v_idx)
            Z_surface[v_idx, :] = base + exchange_friction

        # Render custom mathematical mesh grids
        surf = ax_3d.plot_surface(X_mesh, Y_mesh, Z_surface * 100, cmap='bwr', 
                                  alpha=0.55, edgecolor='#161b22', linewidth=0.5)
        
        # Plot precise mathematical telemetry markers per venue
        for v_idx, venue in enumerate(venues):
            actual_yields = macro_skew * np.exp(-0.4 * tenors) + (0.02 * np.sin(f * 0.12 + v_idx) if f < 180 else -0.025 * np.cos(f * 0.2 + v_idx))
            
            # Label node states based on calculated statistical anomalies
            node_colors = []
            for yld in actual_yields * 100:
                if yld > 12: node_colors.append('#00ff66')   # Short Arbitrage Condition
                elif yld < -4: node_colors.append('#ff3333') # Long Premium Arbitrage Condition
                else: node_colors.append('#ffffff')          # Stable State
                
            ax_3d.scatter(tenors, [v_idx]*len(tenors), actual_yields * 100, c=node_colors, s=40, edgecolors='#000000', zorder=12)

        # Formatting axis properties inside the 3D projection room
        ax_3d.set_xlabel('Tenor Structure (Days Horizon)', color='#848e9c', labelpad=9)
        ax_3d.set_ylabel('Trading Venues', color='#848e9c', labelpad=12)
        ax_3d.set_zlabel('Annualized Funding APR (%)', color='#848e9c', labelpad=6)
        ax_3d.set_yticks(range(len(venues)))
        ax_3d.set_yticklabels(venues, color='#848e9c', fontsize=9)
        ax_3d.set_zlim(-15, 20)
        ax_3d.grid(True, color='#1a2330', alpha=0.7, linewidth=0.5)
        
        # Controlled slow pan: Rotates precisely 1.2 degrees per frame to achieve professional cinematic effect
        ax_3d.view_init(elev=26, azim=-55 + (f * 1.2))

        # --- B. DRAWING THE TRADINGVIEW-STYLE CANDLESTICK ENGINE ---
        # Fixed 40-candle trailing historical lookback window for optimal professional visual density
        window_len = 40
        window_start = max(0, f - window_len)
        active_range = range(window_start, f + 1)
        
        for idx in active_range:
            o, h, l, c = candles[idx]
            # Precise TradingView colors: Hex codes for deep emerald green and matching crimson red
            candle_color = '#02c076' if c >= o else '#e44243'
            
            # Plot center-line wick structures
            ax_2d.vlines(idx, l, h, color=candle_color, linewidth=1.2)
            # Plot thick primary asset candle bodies
            ax_2d.vlines(idx, min(o, c), max(o, c), color=candle_color, linewidth=5.5)
        
        # Style configurations for the 2D charting console
        ax_2d.set_xlim(window_start - 1, window_start + window_len + 2)
        ax_2d.set_ylabel('BTC Spot Index Price ($)', color='#b5c0d1')
        ax_2d.yaxis.tick_right()
        ax_2d.yaxis.set_label_position("right")
        ax_2d.grid(True, color='#1b2430', linestyle='--', linewidth=0.6, alpha=0.85)
        ax_2d.set_xticklabels([]) 
        
        # Live HUD text readout printing current telemetry parameters on-screen
        ax_2d.text(0.015, 0.82, f"BTC Index: ${btc_prices[f]:,.2f}\nCurve Vector: {'STEEP CONTANGO' if macro_skew > 0.05 else 'INVERTED BACKWARDATION' if macro_skew < -0.02 else 'FLAT FLUIDITY'}", 
                   transform=ax_2d.transAxes, color='#ffffff', fontsize=9, 
                   fontfamily='monospace', bbox=dict(facecolor='#0d1117', alpha=0.9, edgecolor='#21262d'))

        # Commit compiled frame coordinates to file stream
        writer.grab_frame()
        
        if (f + 1) % 25 == 0:
            print(f"🎬 Progress Telemetry Matrix: Frame {f + 1}/300 rendered successfully.")

print("✨ Done! High-fidelity video generated. Check file: 'historical_funding_arbitrage.mp4'")

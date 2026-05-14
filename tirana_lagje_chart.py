import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Data ──────────────────────────────────────────────────────────────────────
districts = [
    "1. VERI",
    "2. LINDJE",
    "3. LINDJE JUG",
    "4. QENDËR",
    "5. PERËNDIM",
    "6. JUG PERËNDIM",
    "7. JUG",
    "8. JUG LINDJE",
]

percentages = [17.2, 16.8, 14.3, 15.5, 13.1, 11.8, 10.6, 10.7]

colors = [
    "#5B9BD5",   # 1. VERI        – steel blue
    "#70B244",   # 2. LINDJE      – green
    "#F4C144",   # 3. LINDJE JUG  – amber/yellow
    "#E05A4E",   # 4. QENDËR      – coral red
    "#F0872D",   # 5. PERËNDIM    – orange
    "#3BAAA0",   # 6. JUG PERËNDIM – teal
    "#7B62B5",   # 7. JUG         – purple
    "#E884A8",   # 8. JUG LINDJE  – pink
]

# Sub-districts listed in the image
sub_districts = [
    "Bërxullë · Kashar · Yzberisht",
    "Dajt · Paskuqan · Shën Koll",
    "Liqeni Artificial · Selitë · Kombinat",
    "Sheshi Skënderbej · Blloku · Pazari i Ri",
    "Kashar · Vaqarr · Mezez",
    "Laprakë · Don Bosko · Ali Demi",
    "Komuna e Parisit · Myslym Shyri · Kodra e Diellit",
    "Farkë · Qesarak · Petrelë",
]

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8), facecolor="#F5F0E8")
fig.suptitle("TIRANA – 8 LAGJE", fontsize=26, fontweight="bold",
             x=0.72, y=0.95, ha="center", va="top")

# Left: pie chart
ax_pie = fig.add_axes([0.02, 0.05, 0.55, 0.88])   # [left, bottom, width, height]
ax_pie.set_facecolor("#F5F0E8")

wedges, texts, autotexts = ax_pie.pie(
    percentages,
    colors=colors,
    startangle=90,                    # start at the top, matching the image
    counterclock=False,               # clockwise, matching the image
    autopct="%1.1f%%",
    pctdistance=0.78,
    wedgeprops=dict(linewidth=2.5, edgecolor="white"),
)

for at in autotexts:
    at.set_fontsize(10)
    at.set_fontweight("bold")
    at.set_color("white")

ax_pie.set_aspect("equal")

# ── Right panel: legend ───────────────────────────────────────────────────────
ax_leg = fig.add_axes([0.58, 0.05, 0.40, 0.80])
ax_leg.set_facecolor("#F5F0E8")
ax_leg.axis("off")

row_h   = 0.115          # vertical spacing between rows
start_y = 0.92           # y of first row (axes fraction, top-down)

for i, (name, pct, color, sub) in enumerate(
        zip(districts, percentages, colors, sub_districts)):

    y = start_y - i * row_h

    # Colour square
    sq = mpatches.FancyBboxPatch(
        (0.0, y - 0.030), 0.072, 0.060,
        boxstyle="square,pad=0",
        facecolor=color, edgecolor="white", linewidth=1.5,
        transform=ax_leg.transAxes, clip_on=False,
    )
    ax_leg.add_patch(sq)

    # District name
    ax_leg.text(0.095, y + 0.010, name,
                transform=ax_leg.transAxes,
                fontsize=11, fontweight="bold", va="center",
                color="#1A1A1A")

    # Percentage (right-aligned)
    ax_leg.text(0.98, y + 0.010, f"{pct}%",
                transform=ax_leg.transAxes,
                fontsize=11, fontweight="bold", va="center",
                ha="right", color="#1A1A1A")

    # Sub-district names (smaller, grey)
    ax_leg.text(0.095, y - 0.028, sub,
                transform=ax_leg.transAxes,
                fontsize=7.5, va="center", color="#555555",
                style="italic")

# Thin separator line under the title area
ax_leg.axhline(y=1.00, xmin=0, xmax=1, color="#CCCCCC", linewidth=0.8)

plt.savefig("tirana_lagje_chart.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Chart saved as tirana_lagje_chart.png")
plt.show()

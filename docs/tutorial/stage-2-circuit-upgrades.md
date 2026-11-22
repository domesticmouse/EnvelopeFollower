# Stage 2: Sketch Extraction & Quantitative Circuit Critique

Start from [Hagiwo's original post](https://note.com/solder_state/n/n110e9ba066b3?hl=en) and the hand-drawn reference schematic, [`EnvelopeFollower.webp`](https://github.com/domesticmouse/EnvelopeFollower/blob/main/EnvelopeFollower.webp):

![Hagiwo's Original Envelope Follower Sketch](../images/EnvelopeFollower.webp)

Download the raw image into your project directory and verify that you fetched a real WebP image rather than an HTML wrapper page before asking your agent to inspect it:

```bash
curl -LO https://raw.githubusercontent.com/domesticmouse/EnvelopeFollower/main/EnvelopeFollower.webp
file EnvelopeFollower.webp
```

Rather than jumping straight from a raw sketch to a PCB in a single prompt, Stage 2 splits into two focused engineering steps: **faithful baseline transcription** (`EnvelopeFollower.md`) followed by **quantitative analog critique** (`EnvelopeFollowerImprovements.md`). Deciding which fixes and modular features to adopt then happens interactively one improvement at a time in [Stage 3](stage-3-bom-and-dfm.md).

---

## Step 2.1: Multi-Scale Extraction into Immutable `EnvelopeFollower.md`

### AI Agent Prompt

> *"Please review `EnvelopeFollower.webp`. I'd like to extract a Markdown description of the circuit that can be used to build a circuit, and save it to `EnvelopeFollower.md`. Afterwards, update `@[README.md]` and git commit."*

### Extraction Guardrails Observed in Trace 02

1. **Multi-Scale Visual Cropping (Pillow, Not `sips --cropOffset`)**:
   A single downscaled view of a hand-drawn schematic can blur diode bars and capacitor polarity markings. Have the agent crop full-resolution quadrants and tight macro crops around diodes (`D1`–`D3`) and the LED network (`LED1`) into `/tmp/` using `PIL.Image.crop((left, top, right, bottom))`—avoiding macOS `sips --cropOffset`, which behaves inconsistently relative to expected top-left origins.
2. **KCL Cross-Validation & Immutability**:
   Cross-check every visual diode/polarity read with Kirchhoff's Current Law (for instance, confirming `C4` on the `-12V` rail puts `+` on `GND` (`0 V`) and `-` on `-12V`, and tracing both `V_pre > 0` and `V_pre < 0` through `D1`/`D2`). Keep the extracted baseline `EnvelopeFollower.md` **immutable**—transcribe what the sketch shows in Sections 1–5 (`R1`–`R23`, `RV1`–`RV4`, `C1`–`C4`, `D1`–`D3`, `LED1`, `U1`–`U2`, `J1`–`J3`, `J_PWR`), and keep optional Eurorack build advice cleanly separated in Section 6.
3. **Python BOM ↔ Netlist Pin-Completeness Assertion**:
   Verify every component and pin directly on the Markdown tables before moving to critique. Always use a **single-quoted heredoc** (`python3 - <<'EOF'`) instead of `python3 -c "..."` in `zsh`, because embedded Markdown backticks inside double quotes execute as shell commands:

```bash
python3 - <<'EOF'
import re
from pathlib import Path

text = Path("EnvelopeFollower.md").read_text(encoding="utf-8")
bom_sec = text.split("## 3. Complete Bill of Materials")[1].split("## 4. Pin Conventions")[0]
net_sec = text.split("## 5. Complete Pin-Level Netlist")[1].split("## 6. Practical Build")[0]

bom_refs = set(re.findall(r"^\|\s*`([A-Z0-9_]+)`\s*\|", bom_sec, re.M))
net_rows = re.findall(r"^\|\s*(\d+)\s*\|\s*`([^`]+)`[^|]*\|\s*(.+?)\s*\|$", net_sec, re.M)
assert len(bom_refs) == 41, f"Expected 41 BOM components, got {len(bom_refs)}"
assert len(net_rows) == 30, f"Expected 30 nets, got {len(net_rows)}"
print(f"Verified {len(bom_refs)} BOM parts across {len(net_rows)} nets.")
EOF
```

### Extracted Baseline Topology (`6` Op-Amps, `41` Components, `30` Nets)

1. **Power Entry (`J_PWR`, `C3`, `C4`)**: Bipolar $\pm 12\text{ V}$ entry bypassed by $4.7\,\mu\text{F}$ electrolytics (`C3` `+` on `+12V`; `C4` `+` on `GND`, `-` on `-12V`).
2. **AC-Coupled Variable-Gain Preamp (`U1A`)**: `J1` (`IN`) feeds `C1` ($4.7\,\mu\text{F}$) and `R1` ($1\text{ M}\Omega$) into inverting amplifier `U1A` (`R2 = 10 kΩ`, feedback rheostat `RV1 = 100 kΩ`, $0\times$ to $-10\times$ gain).
3. **Precision Full-Wave Rectifier (`U1B`, `U1C`, `D1`, `D2`)**: `U1B` half-wave stage (`R3 = R4 = 10 kΩ`, `D1`/`D2` `1N4148`), summed by `U1C` (`R5 = 10 kΩ` vs. `R6 + R7 = 20 kΩ` feedforward, `R8 = 22 kΩ` feedback for $+1.1\times |V_{\text{pre}}|$).
4. **Attack / Release Peak Detector (`D3`, `RV2`, `C2`, `R9`, `R10`, `RV3`)**: Passive `1N4148` `D3` charges `C2` ($1\,\mu\text{F}$) through `RV2` (`50 kΩ`), feeding `NET_ENV_SENSE` through `R9` ($1\text{ k}\Omega$) and discharging through `R10` ($10\text{ k}\Omega$) + `RV3` (`1 MΩ`).
5. **Offset Summer, `OUT` & `INV_OUT` (`U1D`, `U2A`, `RV4`)**: Non-inverting `U1D` (`+`) with $\pm 12\text{ V}$ bias divider (`R11 = R12 = 10 kΩ`, `RV4 = 100 kΩ`, `R13`–`R15 = 10 kΩ`) on `U1D` (`-`), driving `J2` (`OUT`) via `R16` ($1\text{ k}\Omega$) and unity inverter `U2A` (`R17 = R18 = 10 kΩ`) driving `J3` (`INV_OUT`) via `R19` ($1\text{ k}\Omega$).
6. **Pre-Biased LED Driver (`U2B`)**: Unity follower fed through `R20` ($10\text{ k}\Omega$), driving `LED1` through `R21` ($22\text{ k}\Omega$) against a $-2.79\text{ V}$ cathode bias divider (`R22 = 10 kΩ` to `GND`, `R23 = 33 kΩ` to `-12V`).

---

## Step 2.2: Quantitative Critique & Tiered Upgrade Architecture (`EnvelopeFollowerImprovements.md`)

### AI Agent Prompt

> *"Please review `EnvelopeFollower.md`. Are there improvements that could be made to the circuit? Record the suggested improvements and explanations to `EnvelopeFollowerImprovements.md`. Update `@[README.md]` and git commit."*

### What Makes a Critique Actionable (Distilled from Trace 03)

1. **Re-Verify Tricky Schematic Areas Independently**: Before prescribing fixes, re-inspect zoomed diode/polarity crops of `EnvelopeFollower.webp` so critique math never inherits an extraction typo.
2. **Triage into Tiers + Explicit Op-Amp Budget Options**:
   Structure `EnvelopeFollowerImprovements.md` into **Tier 1 (Critical Electrical/Ergonomic Fixes)**, **Tier 2 (Precision, Noise & Protection Refinements)**, **Tier 3 (Optional Eurorack "Mod Cons")**, plus an explicit **Architecture Comparison** contrasting **Option A** (`1× TL074H + 1× TL072H`, `6` op-amps, minimal drop-in fixes) against **Option B** (`2× TL074H`, `8/8` sections, single IC SKU with an active skew limiter).
3. **Back Stability Claims with Python Bode/Nyquist Sweeps**:
   When proposing an active feedback skew limiter around a capacitive load (`U_DRV` + `D_atk`/`D_rel` + `C2` + unity buffer `U_BUF`), do not guess the compensation capacitor (`C_comp`) value. In Trace 03, running a Python loop-gain phase-margin sweep across `RV2`/`RV3` (`100 Ω` to `1 MΩ`) caught that a naive `C_comp = 100 pF` drops into a complex-zero notch with just **`12.2°` phase margin** (prone to ringing/oscillation), whereas **`R_fb = 10 kΩ` and `C_comp = 2.2 nF` (`C0G/NP0`)** pushes unity crossover safely past the notch for **`~90.3°` phase margin** across the entire `100 Ω–1 MΩ` and `470 nF–4.87 µF` operating space.
4. **Lint Markdown, Links, Math & Mermaid**: Run a quick Python check over `EnvelopeFollowerImprovements.md` to confirm zero broken relative links, balanced KaTeX/MathJax `$`/`$$` delimiters (never letting bare currency `$` prices open math spans), and properly quoted Mermaid node labels.

### Tier 1 Critical Fixes (`1.1`–`1.5`)

| # | Stage / RefDes | Flaw in Hagiwo Baseline | Recommended Redesign (`Option B: 2× TL074H`) | Quantitative Impact |
| :- | :--- | :--- | :--- | :--- |
| **1.1** | Detector (`RV2`, `C2`, `R9`, `R10`, `RV3`) | `ATK` and `Release` form a resistive voltage divider: slow `ATK` (`50 kΩ`) + fast `REL` (`11 kΩ`) collapses peak voltage to **`16.4%` (`-15.7 dB`)** and shrinks $\tau_{\text{atk}}$ to `9.02 ms`; `R9` causes a **`9.0%`** release-dependent gain shift. | Remove `R9` and adopt an **active 2-op-amp Skew Limiter (`U_DRV` + `U_BUF`)** with opposite-facing diodes inside the loop. | **`100%` independent** `ATK` & `REL`; **`0 dB`** divider collapse. |
| **1.2** | Peak Detector (`D3`, `RV2`, `C2`) | Passive `D3` adds a **`~0.65 V` deadzone** (`1.35–1.75 V` lost at `OUT`) and `-4.5 mV/°C` drift; `ATK = 0 Ω` slams `U1C` directly into `C2`. | Active loop eliminates `D3` drop (`< 5 mV`), stabilized by **`R_fb = 10 kΩ` + `C_comp = 2.2 nF` C0G** and series minimum resistors (`1 kΩ` / `1 kΩ`). | **`~90.3°` phase margin** (`100 Ω–1 MΩ`), zero deadzone, linear-safe driver current. |
| **1.3** | Offset & Output (`R11`–`R15`, `RV4`, `U1D`) | `RV4` (`100 kΩ`) Thévenin resistance shifts gain **`+12.1%`** (`2.25×`–`2.52×`), compresses **`72.5%`** of offset into the outer `25%` of travel, inverts knob sense (`CW = negative`), and couples raw rail noise. | Re-architect as a **virtual-ground inverting unity summer (`U2B` $\rightarrow$ `INV_OUT`) + unity inverter (`U2C` $\rightarrow$ `OUT`)** with `RV4 = 10 kΩ B` and local rail RC filters. | **`0.00%` gain shift**, **`49.6%`** linear travel at `75%`, `CW = +OUT`. |
| **1.4** | Input & Preamp (`J1`, `C1`, `R1`, `R2`, `RV1`, `U1A`, `R8`) | $Z_{\text{in}} = 9.90\,\text{k}\Omega$ (`9.1%` loss); `R1` sits on the wrong side of `C1`; `24.75×` max gain clips `OUT` at **`9.8%`** `GAIN` rotation on `10 Vpp` Eurorack signals while `LED1` keeps rising. | `1 MΩ` jack bleed, `470 nF` film `C7`, `100 kΩ A` input attenuator ($Z_{\text{in}} = 90.9\,\text{k}\Omega$), `×2.00` non-inverting Eurorack preamp (`U1A`), and exact `1.000×` FWR (`R13 + R14 = 20 kΩ`). | Full `100%` `GAIN` sweep on `10 Vpp` audio, `3.72 Hz` HPF, true LED tracking. |
| **1.5** | LED Driver (`R20`–`R23`, `U2B`, `LED1`) | `-2.79 V` pre-bias leaks `23–33 µA` idle glow on red/green LEDs while limiting `5 V` drive to `0.16–0.20 mA`. | **Active $V$-to-$I$ driver (`U2D`)** with `LED1` in feedback over `R_sense = 2.2 kΩ` (or post-offset 2-pin anti-parallel Red/Green bi-color LED). | **`0.00 mA` idle**, `2.3 mA @ 5 V` linear drive independent of LED $V_f$. |

### Tier 2 Refinements & Tier 3 Eurorack Candidates (`2.1`–`3.4`)

- **Tier 2 (`2.1`–`2.5`)**: Upgrade to **`TL074H`** (eliminating legacy `TL074` phase reversal, adding `~2.5 Vpp` headroom, `1 mV` $V_{os}$, `~1 pA` $I_b$; **never** use BJT-input op-amps like `NE5532` on `C2`); match rectifier resistors (`10 kΩ ±0.1%`) with `BAT54S` HWR diodes while keeping **low-leakage silicon (`1N4148W`)** on the hold cap; add a switchable **`SMOOTH`** `2f` ripple filter (`50 Hz` sine droops `59.7%` per half-cycle at `11 ms` release); harden Eurorack power/I/O (`J_PWR` shrouded `2×5` header, series `B5819W` Schottkys, `10 Ω` + `47 µF` RC filters, `4× 100 nF` local bypasses, `J1.TN → GND`, `1 kΩ` output protection); and standardize on **Audio/Log (`A`)** pots for `GAIN`/`ATK`/`REL`, **Linear (`B`) center-detent** for `OFFSET`, plus a `FAST / SLOW` capacitor switch.
- **Tier 3 (`3.1`–`3.4`)**: Candidate modular extensions to weigh against 6 HP panel space and the `2× TL074H` budget—normaled **`SLEW IN`** jack (`3.1`), Schmitt-trigger **`GATE OUT`** (`3.2`), **`PRE OUT` / `AC/DC` / `CLIP` LED** (`3.3`), or an `LM13700` OTA CV-controlled core (`3.4`).

---

## Step 2.3: Streamlining Protections & Optional Features into Interactive Q&A

In earlier drafts of this workflow, users ran a separate one-shot *"add Eurorack protections"* prompt at the end of Stage 2 before firing another one-shot prompt to produce four disconnected Markdown files. Instead, both **Tier 2 Eurorack protections (`2.4`)** and **Tier 3 feature candidates (`3.1`–`3.4`)** are now decided **collaboratively inside [Stage 3](stage-3-bom-and-dfm.md)**—locking every electrical value, component package, and test point straight into a single **`DesignSpec.md`**.

!!! tip "Exploring Optional Feature Branches from `EnvelopeFollowerImprovements.md`"
    Want to see how Antigravity expands on an individual Tier 3 candidate when you explore a custom branch—such as turning Tier 3.3's **`AC / DC` coupling switch** into a precision CV rectifier and LFO frequency doubler? Read **[Optional Direction: AC/DC Input Coupling Mode](optional-dc-coupled-mode.md)**.

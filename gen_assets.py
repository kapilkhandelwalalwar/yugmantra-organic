#!/usr/bin/env python3
"""Generates the SVG art for Yugmantra Organic: jars, marks, seals, editorial plates."""
import os, textwrap

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "img")
os.makedirs(OUT, exist_ok=True)

def w(name, svg):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(textwrap.dedent(svg).strip() + "\n")
    print("wrote", name)

# ----------------------------------------------------------------------------
# JAR — parametric
# ----------------------------------------------------------------------------
def jar(uid, label_top, label_mid, label_sub, size_txt,
        ghee_a, ghee_b, ghee_c, lid_a, lid_b, tall=False, wide=False):
    """Glass jar with molten ghee, foil lid, letterpress label."""
    H = 700
    if tall:   body_top, body_bot, halfw = 196, 648, 168
    elif wide: body_top, body_bot, halfw = 250, 636, 196
    else:      body_top, body_bot, halfw = 236, 640, 172
    cx = 260
    L, R = cx - halfw, cx + halfw
    neck_hw = int(halfw * 0.60)
    nL, nR = cx - neck_hw, cx + neck_hw
    lid_hw = neck_hw + 14
    lid_top = 74
    lid_bot = 150
    shoulder = body_top + 8

    # ghee surface a little below the shoulder
    gh_top = body_top + 30
    lab_top = body_top + (150 if tall else 116)
    lab_h   = 232 if tall else 214
    lab_w   = int(halfw * 1.52)

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 {H}" width="520" height="{H}" role="img" aria-label="{label_mid} jar">
      <defs>
        <linearGradient id="gh{uid}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0"   stop-color="{ghee_a}"/>
          <stop offset=".34" stop-color="{ghee_b}"/>
          <stop offset=".72" stop-color="{ghee_c}"/>
          <stop offset="1"   stop-color="{ghee_a}"/>
        </linearGradient>
        <linearGradient id="ld{uid}" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0"    stop-color="{lid_a}"/>
          <stop offset=".16"  stop-color="{lid_b}"/>
          <stop offset=".40"  stop-color="#FFF0C4"/>
          <stop offset=".58"  stop-color="{lid_b}"/>
          <stop offset=".82"  stop-color="{lid_a}"/>
          <stop offset="1"    stop-color="#6E4A12"/>
        </linearGradient>
        <linearGradient id="gl{uid}" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0"   stop-color="#ffffff" stop-opacity=".62"/>
          <stop offset=".14" stop-color="#ffffff" stop-opacity=".06"/>
          <stop offset=".70" stop-color="#ffffff" stop-opacity="0"/>
          <stop offset=".90" stop-color="#ffffff" stop-opacity=".30"/>
          <stop offset="1"   stop-color="#7a5a22" stop-opacity=".22"/>
        </linearGradient>
        <linearGradient id="lb{uid}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#FDFAF2"/>
          <stop offset="1" stop-color="#F0E7D4"/>
        </linearGradient>
        <radialGradient id="sh{uid}" cx=".5" cy=".5" r=".5">
          <stop offset="0"   stop-color="#6b4a17" stop-opacity=".38"/>
          <stop offset="1"   stop-color="#6b4a17" stop-opacity="0"/>
        </radialGradient>
        <filter id="gr{uid}" x="-20%" y="-20%" width="140%" height="140%">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" result="n"/>
          <feColorMatrix in="n" type="saturate" values="0" result="d"/>
          <feComposite in="d" in2="SourceGraphic" operator="in" result="c"/>
          <feBlend in="SourceGraphic" in2="c" mode="multiply"/>
        </filter>
        <clipPath id="cp{uid}">
          <path d="M{nL} {lid_bot-4}
                   L{nL} {body_top-26}
                   Q{nL} {shoulder} {L+14} {body_top+16}
                   Q{L} {body_top+26} {L} {body_top+52}
                   L{L} {body_bot-30}
                   Q{L} {body_bot} {L+30} {body_bot}
                   L{R-30} {body_bot}
                   Q{R} {body_bot} {R} {body_bot-30}
                   L{R} {body_top+52}
                   Q{R} {body_top+26} {R-14} {body_top+16}
                   Q{nR} {shoulder} {nR} {body_top-26}
                   L{nR} {lid_bot-4} Z"/>
        </clipPath>
      </defs>

      <!-- cast shadow -->
      <ellipse cx="{cx}" cy="{body_bot+22}" rx="{halfw+34}" ry="26" fill="url(#sh{uid})"/>

      <!-- glass body -->
      <path d="M{nL} {lid_bot-4}
               L{nL} {body_top-26}
               Q{nL} {shoulder} {L+14} {body_top+16}
               Q{L} {body_top+26} {L} {body_top+52}
               L{L} {body_bot-30}
               Q{L} {body_bot} {L+30} {body_bot}
               L{R-30} {body_bot}
               Q{R} {body_bot} {R} {body_bot-30}
               L{R} {body_top+52}
               Q{R} {body_top+26} {R-14} {body_top+16}
               Q{nR} {shoulder} {nR} {body_top-26}
               L{nR} {lid_bot-4} Z"
            fill="#F6F1E4" fill-opacity=".55"/>

      <!-- ghee fill -->
      <g clip-path="url(#cp{uid})">
        <rect x="{L-6}" y="{gh_top}" width="{halfw*2+12}" height="{body_bot-gh_top+8}" fill="url(#gh{uid})"/>
        <rect x="{L-6}" y="{gh_top}" width="{halfw*2+12}" height="{body_bot-gh_top+8}" fill="url(#gh{uid})" filter="url(#gr{uid})" opacity=".55"/>
        <!-- meniscus -->
        <ellipse cx="{cx}" cy="{gh_top+2}" rx="{halfw-6}" ry="15" fill="#FFF1C6" opacity=".55"/>
        <ellipse cx="{cx}" cy="{gh_top+7}" rx="{halfw-18}" ry="9" fill="#FFFAE4" opacity=".38"/>
        <!-- grain flecks -->
        <g opacity=".30" fill="#FFF6DA">
          <circle cx="{cx-72}" cy="{gh_top+92}" r="4.5"/><circle cx="{cx+58}" cy="{gh_top+146}" r="6"/>
          <circle cx="{cx-24}" cy="{gh_top+210}" r="3.6"/><circle cx="{cx+96}" cy="{gh_top+238}" r="4.2"/>
          <circle cx="{cx-104}" cy="{gh_top+186}" r="3.2"/><circle cx="{cx+14}" cy="{gh_top+64}" r="3.4"/>
          <circle cx="{cx-52}" cy="{gh_top+272}" r="5"/><circle cx="{cx+74}" cy="{gh_top+46}" r="3"/>
        </g>
        <!-- inner light -->
        <ellipse cx="{cx-halfw*0.42}" cy="{gh_top+130}" rx="46" ry="118" fill="#FFF3CE" opacity=".22"/>
      </g>

      <!-- glass sheen over everything -->
      <path d="M{nL} {lid_bot-4}
               L{nL} {body_top-26}
               Q{nL} {shoulder} {L+14} {body_top+16}
               Q{L} {body_top+26} {L} {body_top+52}
               L{L} {body_bot-30}
               Q{L} {body_bot} {L+30} {body_bot}
               L{R-30} {body_bot}
               Q{R} {body_bot} {R} {body_bot-30}
               L{R} {body_top+52}
               Q{R} {body_top+26} {R-14} {body_top+16}
               Q{nR} {shoulder} {nR} {body_top-26}
               L{nR} {lid_bot-4} Z"
            fill="url(#gl{uid})"/>
      <!-- specular streak -->
      <rect x="{L+22}" y="{body_top+64}" width="13" height="{body_bot-body_top-150}" rx="7" fill="#fff" opacity=".40"/>
      <rect x="{R-40}" y="{body_top+96}" width="7" height="{body_bot-body_top-210}" rx="4" fill="#fff" opacity=".22"/>

      <!-- neck ring -->
      <rect x="{nL-3}" y="{lid_bot-6}" width="{neck_hw*2+6}" height="11" rx="5" fill="#E4DAC4" opacity=".85"/>

      <!-- lid -->
      <rect x="{cx-lid_hw}" y="{lid_top}" width="{lid_hw*2}" height="{lid_bot-lid_top}" rx="9" fill="url(#ld{uid})"/>
      <rect x="{cx-lid_hw}" y="{lid_top}" width="{lid_hw*2}" height="9" rx="4.5" fill="#FFF3CF" opacity=".55"/>
      <rect x="{cx-lid_hw}" y="{lid_bot-13}" width="{lid_hw*2}" height="13" rx="6" fill="#7A5316" opacity=".45"/>
      <g opacity=".26" fill="#3A2708">
        {''.join(f'<rect x="{cx-lid_hw+8+i*13}" y="{lid_top+13}" width="2.4" height="{lid_bot-lid_top-30}" rx="1.2"/>' for i in range(int(lid_hw*2/13)-1))}
      </g>
      <ellipse cx="{cx}" cy="{lid_top+3}" rx="{lid_hw}" ry="10" fill="#FFE9B0"/>
      <ellipse cx="{cx}" cy="{lid_top+2}" rx="{lid_hw-16}" ry="6" fill="#C9982F" opacity=".45"/>

      <!-- label -->
      <g>
        <rect x="{cx-lab_w//2}" y="{lab_top}" width="{lab_w}" height="{lab_h}" rx="4" fill="url(#lb{uid})"/>
        <rect x="{cx-lab_w//2}" y="{lab_top}" width="{lab_w}" height="{lab_h}" rx="4" fill="none" stroke="#C9B893" stroke-width="1"/>
        <rect x="{cx-lab_w//2+11}" y="{lab_top+11}" width="{lab_w-22}" height="{lab_h-22}" rx="2" fill="none" stroke="#C08A2E" stroke-width="1" opacity=".55"/>
        <!-- monogram -->
        <g transform="translate({cx},{lab_top+50})">
          <circle r="21" fill="none" stroke="#C08A2E" stroke-width="1.1" opacity=".8"/>
          <text x="0" y="8" text-anchor="middle" font-family="Georgia,serif" font-size="24" fill="#8A5F1B">Y</text>
        </g>
        <text x="{cx}" y="{lab_top+96}" text-anchor="middle" font-family="Inter,Helvetica,sans-serif"
              font-size="8" letter-spacing="3.4" fill="#9A8F7F">{label_top}</text>
        <text x="{cx}" y="{lab_top+128}" text-anchor="middle" font-family="Georgia,serif"
              font-size="25" fill="#1C1815">{label_mid}</text>
        <line x1="{cx-34}" y1="{lab_top+146}" x2="{cx+34}" y2="{lab_top+146}" stroke="#C08A2E" stroke-width="1"/>
        <text x="{cx}" y="{lab_top+170}" text-anchor="middle" font-family="Inter,Helvetica,sans-serif"
              font-size="8" letter-spacing="2.6" fill="#6B6154">{label_sub}</text>
        <text x="{cx}" y="{lab_top+lab_h-20}" text-anchor="middle" font-family="Inter,Helvetica,sans-serif"
              font-size="9" letter-spacing="2.2" fill="#8A5F1B">{size_txt}</text>
      </g>
    </svg>
    """

w("jar-gir.svg", jar("a", "BILONA · HAND CHURNED", "Gir A2", "GRASS-FED DESI COW GHEE", "500 ML",
                     "#E3A32B", "#F7C752", "#FFE08A", "#B4831F", "#EFC15A"))
w("jar-sahiwal.svg", jar("b", "BILONA · HAND CHURNED", "Sahiwal A2", "GRASS-FED DESI COW GHEE", "500 ML",
                         "#DE9A24", "#F2BE45", "#FFDA7E", "#A87A1B", "#E7B84E"))
w("jar-sahiwal-1l.svg", jar("c", "BILONA · HAND CHURNED", "Sahiwal A2", "GRASS-FED DESI COW GHEE", "1 LITRE",
                            "#DE9A24", "#F2BE45", "#FFDA7E", "#A87A1B", "#E7B84E", tall=True))
w("jar-buffalo.svg", jar("d", "SLOW SIMMERED", "Desi Buffalo", "PURE BUFFALO MILK GHEE", "1 LITRE",
                         "#EFE2C4", "#FBF3DE", "#FFFBF0", "#9E9382", "#D9D0BC", tall=True))
w("jar-honey.svg", jar("e", "RAW · UNPASTEURISED", "Ashwagandha", "INFUSED RAW FOREST HONEY", "325 G",
                       "#A8621B", "#D08A2A", "#EDB24F", "#8A5312", "#C99036", wide=True))

# ----------------------------------------------------------------------------
# WORDMARK / MONOGRAM
# ----------------------------------------------------------------------------
w("mark.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 60" width="60" height="60" role="img" aria-label="Yugmantra monogram">
  <defs>
    <linearGradient id="mg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#8A5F1B"/><stop offset=".5" stop-color="#E8B84B"/><stop offset="1" stop-color="#B4831F"/>
    </linearGradient>
  </defs>
  <circle cx="30" cy="30" r="28.4" fill="none" stroke="url(#mg)" stroke-width="1.2"/>
  <circle cx="30" cy="30" r="24" fill="none" stroke="url(#mg)" stroke-width=".6" opacity=".5"/>
  <!-- stylised Y as a sprout / churn -->
  <path d="M30 41.5 V29.5" stroke="#1C1815" stroke-width="1.9" stroke-linecap="round"/>
  <path d="M30 29.6 C30 23.4 25.4 20.6 20.6 19.4 C20.8 25.4 24.4 29.2 30 29.6 Z" fill="#1C1815"/>
  <path d="M30 29.6 C30 23.4 34.6 20.6 39.4 19.4 C39.2 25.4 35.6 29.2 30 29.6 Z" fill="url(#mg)"/>
  <circle cx="30" cy="44.6" r="1.7" fill="url(#mg)"/>
</svg>
""")

# ----------------------------------------------------------------------------
# ROTATING SEAL
# ----------------------------------------------------------------------------
w("seal.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200" role="img" aria-label="Small batch seal">
  <defs>
    <path id="cir" d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/>
    <linearGradient id="sg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#8A5F1B"/><stop offset=".5" stop-color="#E8B84B"/><stop offset="1" stop-color="#B4831F"/>
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="93" fill="none" stroke="url(#sg)" stroke-width="1"/>
  <circle cx="100" cy="100" r="58" fill="none" stroke="url(#sg)" stroke-width=".8" opacity=".55"/>
  <text font-family="Inter,Helvetica,sans-serif" font-size="11" letter-spacing="3.1" fill="#8A5F1B">
    <textPath href="#cir" startOffset="1%">SMALL BATCHES · ALWAR · SINCE 2019 · </textPath>
  </text>
  <g transform="translate(100,100)">
    <path d="M0 22 V2" stroke="#1C1815" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M0 2 C0 -9 -8 -14 -16 -16 C-15.6 -6 -10 -1 0 2 Z" fill="#1C1815"/>
    <path d="M0 2 C0 -9 8 -14 16 -16 C15.6 -6 10 -1 0 2 Z" fill="url(#sg)"/>
  </g>
</svg>
""")

# ----------------------------------------------------------------------------
# EDITORIAL PLATES
# ----------------------------------------------------------------------------
w("plate-cow.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="800" height="1000" role="img" aria-label="Grazing desi cow at dawn">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F6E2B4"/><stop offset=".45" stop-color="#F0D89F"/><stop offset="1" stop-color="#E5C88C"/>
    </linearGradient>
    <linearGradient id="fld" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#C9B37E"/><stop offset="1" stop-color="#9E8B58"/>
    </linearGradient>
    <radialGradient id="sun" cx=".5" cy=".5" r=".5">
      <stop offset="0" stop-color="#FFF3C8"/><stop offset=".55" stop-color="#FFDD8E" stop-opacity=".8"/><stop offset="1" stop-color="#FFD37A" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="800" height="1000" fill="url(#sky)"/>
  <circle cx="560" cy="300" r="210" fill="url(#sun)"/>
  <circle cx="560" cy="300" r="72" fill="#FFF0BE" opacity=".95"/>
  <!-- distant treeline -->
  <g fill="#B6A171" opacity=".55">
    <ellipse cx="90" cy="620" rx="70" ry="34"/><ellipse cx="200" cy="628" rx="54" ry="26"/>
    <ellipse cx="700" cy="624" rx="66" ry="30"/><ellipse cx="600" cy="632" rx="46" ry="22"/>
    <ellipse cx="380" cy="630" rx="50" ry="24"/>
  </g>
  <rect y="640" width="800" height="360" fill="url(#fld)"/>
  <!-- grass strokes -->
  <g stroke="#8A7746" stroke-width="2" opacity=".45" stroke-linecap="round">
    <path d="M40 1000 q10 -60 2 -104"/><path d="M120 1000 q-12 -70 4 -120"/><path d="M690 1000 q14 -66 0 -110"/>
    <path d="M760 1000 q-10 -80 6 -126"/><path d="M300 1000 q8 -50 0 -84"/><path d="M470 1000 q-8 -56 2 -92"/>
  </g>
  <!-- cow silhouette: Gir — shoulder hump, dewlap, drooping ears, lyre horns -->
  <g fill="#2C2419" transform="translate(150,392) scale(1.12)">
    <!-- barrel -->
    <ellipse cx="140" cy="150" rx="92" ry="53"/>
    <rect x="48" y="128" width="184" height="62" rx="26"/>
    <!-- shoulder hump -->
    <ellipse cx="198" cy="108" rx="31" ry="27"/>
    <!-- rump -->
    <ellipse cx="66" cy="132" rx="30" ry="30"/>
    <!-- neck -->
    <path d="M188 112 L258 100 L272 152 L196 176 Z"/>
    <!-- head + muzzle -->
    <path d="M252 104 C276 96 296 102 304 116
             C312 130 322 138 330 144 C334 148 332 156 324 158
             C310 160 292 156 280 148 C266 138 254 126 250 116 Z"/>
    <!-- dewlap -->
    <path d="M262 148 C258 168 246 186 230 194 C220 198 210 192 208 182
             C220 176 236 164 246 146 Z"/>
    <!-- ears -->
    <path d="M258 106 C240 108 226 118 222 130 C236 130 252 122 260 112 Z"/>
    <path d="M268 100 C282 98 294 104 298 114 C286 112 274 108 266 104 Z"/>
    <!-- lyre horns -->
    <path d="M266 96 C270 78 264 64 250 58" stroke="#2C2419" stroke-width="7.5" stroke-linecap="round" fill="none"/>
    <path d="M282 100 C293 86 294 70 284 60" stroke="#2C2419" stroke-width="7.5" stroke-linecap="round" fill="none"/>
    <!-- legs -->
    <rect x="196" y="176" width="15" height="86" rx="6"/>
    <rect x="216" y="172" width="15" height="90" rx="6"/>
    <rect x="62"  y="176" width="15" height="86" rx="6"/>
    <rect x="86"  y="172" width="15" height="90" rx="6"/>
    <!-- hocks -->
    <ellipse cx="70" cy="182" rx="13" ry="16"/>
    <ellipse cx="94" cy="180" rx="13" ry="16"/>
    <!-- udder -->
    <ellipse cx="150" cy="192" rx="26" ry="14"/>
    <!-- tail -->
    <path d="M46 126 C32 158 32 200 40 228" stroke="#2C2419" stroke-width="5.5" stroke-linecap="round" fill="none"/>
    <ellipse cx="41" cy="238" rx="7" ry="13"/>
    <!-- eye -->
    <circle cx="282" cy="124" r="4.2" fill="#F0D89F"/>
  </g>

  <!-- calf -->
  <g fill="#3A3021" opacity=".62" transform="translate(486,558) scale(.52)">
    <ellipse cx="140" cy="150" rx="88" ry="50"/>
    <rect x="52" y="130" width="176" height="58" rx="25"/>
    <ellipse cx="192" cy="116" rx="26" ry="22"/>
    <ellipse cx="68" cy="134" rx="28" ry="28"/>
    <path d="M186 118 L254 106 L268 154 L194 176 Z"/>
    <path d="M250 110 C274 102 294 108 302 122
             C310 136 320 144 328 150 C332 154 330 162 322 164
             C308 166 290 162 278 154 C264 144 252 132 248 122 Z"/>
    <path d="M256 112 C238 114 224 124 220 136 C234 136 250 128 258 118 Z"/>
    <rect x="196" y="176" width="14" height="86" rx="6"/>
    <rect x="214" y="172" width="14" height="90" rx="6"/>
    <rect x="64"  y="176" width="14" height="86" rx="6"/>
    <rect x="88"  y="172" width="14" height="90" rx="6"/>
    <path d="M48 128 C34 158 34 198 42 224" stroke="#3A3021" stroke-width="6" stroke-linecap="round" fill="none"/>
  </g>

  <!-- birds -->
  <g stroke="#3A3021" stroke-width="2.4" fill="none" opacity=".5" stroke-linecap="round">
    <path d="M110 210 q14-12 28 0 q14-12 28 0"/><path d="M180 150 q10-9 20 0 q10-9 20 0"/>
  </g>
</svg>
""")

w("plate-bilona.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="800" height="1000" role="img" aria-label="Clay pot and wooden churn">
  <defs>
    <linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#EFE4CE"/><stop offset="1" stop-color="#DBCBAA"/>
    </linearGradient>
    <linearGradient id="clay" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7C3A26"/><stop offset=".3" stop-color="#A0503A"/>
      <stop offset=".62" stop-color="#C0705A"/><stop offset="1" stop-color="#7A3824"/>
    </linearGradient>
    <linearGradient id="wood" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#6B4E2C"/><stop offset=".4" stop-color="#9C7645"/>
      <stop offset=".7" stop-color="#B08A55"/><stop offset="1" stop-color="#6B4E2C"/>
    </linearGradient>
    <radialGradient id="glow2" cx=".5" cy=".38" r=".55">
      <stop offset="0" stop-color="#FFF0C8" stop-opacity=".9"/><stop offset="1" stop-color="#FFF0C8" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="800" height="1000" fill="url(#bg2)"/>
  <circle cx="400" cy="420" r="330" fill="url(#glow2)"/>
  <!-- floor line -->
  <rect y="792" width="800" height="208" fill="#C6B18A"/>
  <ellipse cx="400" cy="792" rx="300" ry="34" fill="#B29B72" opacity=".6"/>
  <!-- pot -->
  <path d="M400 792 c-118 0-186-66-186-150 0-78 46-128 60-156 h252 c14 28 60 78 60 156 0 84-68 150-186 150z" fill="url(#clay)"/>
  <ellipse cx="400" cy="486" rx="126" ry="26" fill="#5E2A1B"/>
  <ellipse cx="400" cy="484" rx="112" ry="20" fill="#F7EEDA"/>
  <!-- rim highlight -->
  <path d="M274 486 a126 26 0 0 1 252 0" fill="none" stroke="#D08C74" stroke-width="4" opacity=".6"/>
  <!-- decorative bands -->
  <g stroke="#EBD9B8" stroke-width="3" opacity=".38" fill="none">
    <path d="M228 596 q172 40 344 0"/><path d="M222 650 q178 44 356 0"/>
  </g>
  <!-- churn -->
  <rect x="388" y="120" width="24" height="380" rx="12" fill="url(#wood)"/>
  <rect x="330" y="112" width="140" height="20" rx="10" fill="url(#wood)"/>
  <g fill="url(#wood)">
    <path d="M400 508 l-56 -34 a66 66 0 0 1 112 0 z"/>
    <rect x="342" y="466" width="116" height="14" rx="7"/>
  </g>
  <!-- rope -->
  <path d="M340 210 q60 42 120 0 q-60 42 -120 0" fill="none" stroke="#C9B187" stroke-width="7" stroke-linecap="round"/>
  <path d="M340 250 q60 42 120 0 q-60 42 -120 0" fill="none" stroke="#C9B187" stroke-width="7" stroke-linecap="round"/>
  <!-- butter flecks -->
  <g fill="#FFF6DC" opacity=".85">
    <circle cx="362" cy="482" r="9"/><circle cx="432" cy="478" r="12"/><circle cx="400" cy="490" r="7"/>
    <circle cx="466" cy="486" r="6"/><circle cx="336" cy="488" r="5"/>
  </g>
</svg>
""")

w("plate-pour.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="800" height="1000" role="img" aria-label="Golden ghee pouring from a spoon">
  <defs>
    <linearGradient id="bg3" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2A2219"/><stop offset="1" stop-color="#151009"/>
    </linearGradient>
    <linearGradient id="pour" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#C08A2E"/><stop offset=".35" stop-color="#FFE49B"/>
      <stop offset=".6" stop-color="#F3C860"/><stop offset="1" stop-color="#A8701C"/>
    </linearGradient>
    <linearGradient id="pour2" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#B4831F"/><stop offset=".4" stop-color="#FFE9AE"/><stop offset="1" stop-color="#9B6716"/>
    </linearGradient>
    <radialGradient id="lit" cx=".5" cy=".42" r=".55">
      <stop offset="0" stop-color="#FFD98A" stop-opacity=".5"/><stop offset="1" stop-color="#FFD98A" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="800" height="1000" fill="url(#bg3)"/>
  <ellipse cx="400" cy="440" rx="360" ry="380" fill="url(#lit)"/>
  <!-- spoon -->
  <g transform="translate(400,250) rotate(-16)">
    <ellipse cx="0" cy="0" rx="96" ry="56" fill="#D8CBB4"/>
    <ellipse cx="0" cy="-5" rx="82" ry="44" fill="#F3E9D4"/>
    <ellipse cx="-14" cy="2" rx="62" ry="30" fill="#F0C24E"/>
    <rect x="86" y="-13" width="250" height="26" rx="13" fill="#D8CBB4"/>
    <rect x="86" y="-13" width="250" height="9" rx="5" fill="#F6EFDF"/>
  </g>
  <!-- stream -->
  <path d="M378 292 c-6 90 -14 150 -6 226 c6 58 -2 106 -20 152" stroke="url(#pour2)" stroke-width="21" fill="none" stroke-linecap="round"/>
  <path d="M378 292 c-6 90 -14 150 -6 226 c6 58 -2 106 -20 152" stroke="#FFF3CD" stroke-width="6" fill="none" stroke-linecap="round" opacity=".55"/>
  <!-- pool -->
  <ellipse cx="352" cy="690" rx="188" ry="58" fill="#B4831F"/>
  <ellipse cx="352" cy="682" rx="176" ry="50" fill="#E8B84B"/>
  <ellipse cx="352" cy="676" rx="150" ry="38" fill="#FFD980"/>
  <ellipse cx="316" cy="666" rx="66" ry="18" fill="#FFF0C0" opacity=".7"/>
  <!-- ripples -->
  <g fill="none" stroke="#FFF3CD" stroke-width="2" opacity=".4">
    <ellipse cx="352" cy="682" rx="120" ry="30"/><ellipse cx="352" cy="686" rx="164" ry="44"/>
  </g>
  <!-- droplets -->
  <g fill="#FFE49B" opacity=".9">
    <circle cx="452" cy="600" r="8"/><circle cx="478" cy="654" r="5"/><circle cx="240" cy="620" r="6"/>
  </g>
</svg>
""")

w("plate-kitchen.svg", """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000" width="800" height="1000" role="img" aria-label="Jars on a shelf">
  <defs>
    <linearGradient id="bg4" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F2E9D6"/><stop offset="1" stop-color="#E0D2B6"/>
    </linearGradient>
    <linearGradient id="shelf" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#A9865A"/><stop offset="1" stop-color="#7C5C33"/>
    </linearGradient>
    <linearGradient id="sh2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#B08A55"/><stop offset="1" stop-color="#7C5C33"/>
    </linearGradient>
    <linearGradient id="jg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#DFA02B"/><stop offset=".45" stop-color="#F8CE63"/><stop offset="1" stop-color="#C98C22"/>
    </linearGradient>
  </defs>
  <rect width="800" height="1000" fill="url(#bg4)"/>
  <!-- wall texture lines -->
  <g stroke="#D6C6A6" stroke-width="1.4" opacity=".5">
    <path d="M0 120 H800"/><path d="M0 620 H800"/>
  </g>
  <!-- shelves -->
  <rect y="470" width="800" height="22" fill="url(#sh2)"/>
  <rect y="880" width="800" height="22" fill="url(#sh2)"/>
  <rect y="470" width="800" height="6" fill="#C8A472" opacity=".7"/>
  <rect y="880" width="800" height="6" fill="#C8A472" opacity=".7"/>
  <!-- jar helper shapes: row 1 -->
  <g>
    <g transform="translate(150,470)">
      <path d="M-62 0 v-190 q0-22 20-30 v-24 h84 v24 q20 8 20 30 V0 Z" fill="url(#jg)"/>
      <rect x="-46" y="-244" width="92" height="26" rx="6" fill="#B4831F"/>
      <rect x="-44" y="-150" width="88" height="82" rx="3" fill="#F7EFDD"/>
      <line x1="-28" y1="-118" x2="28" y2="-118" stroke="#C08A2E" stroke-width="1.6"/>
      <rect x="-54" y="-176" width="8" height="120" rx="4" fill="#fff" opacity=".35"/>
    </g>
    <g transform="translate(330,470)">
      <path d="M-52 0 v-160 q0-20 18-27 v-20 h68 v20 q18 7 18 27 V0 Z" fill="url(#jg)" opacity=".92"/>
      <rect x="-40" y="-212" width="80" height="24" rx="6" fill="#B4831F"/>
      <rect x="-36" y="-132" width="72" height="66" rx="3" fill="#F7EFDD"/>
      <rect x="-45" y="-150" width="7" height="96" rx="3.5" fill="#fff" opacity=".32"/>
    </g>
    <g transform="translate(530,470)">
      <path d="M-70 0 v-152 q0-24 22-32 v-22 h96 v22 q22 8 22 32 V0 Z" fill="#EFE2C4"/>
      <rect x="-52" y="-212" width="104" height="26" rx="6" fill="#B8AE9A"/>
      <rect x="-48" y="-128" width="96" height="72" rx="3" fill="#FDFAF2"/>
      <rect x="-62" y="-142" width="8" height="90" rx="4" fill="#fff" opacity=".5"/>
    </g>
    <g transform="translate(690,470)">
      <path d="M-46 0 v-120 q0-18 16-24 v-18 h60 v18 q16 6 16 24 V0 Z" fill="#C98C22" opacity=".8"/>
      <rect x="-34" y="-172" width="68" height="22" rx="5" fill="#8A5F1B"/>
    </g>
  </g>
  <!-- row 2 -->
  <g>
    <g transform="translate(210,880)">
      <path d="M-58 0 v-150 q0-22 20-30 v-22 h76 v22 q20 8 20 30 V0 Z" fill="url(#jg)" opacity=".95"/>
      <rect x="-42" y="-224" width="84" height="24" rx="6" fill="#B4831F"/>
      <rect x="-40" y="-128" width="80" height="70" rx="3" fill="#F7EFDD"/>
      <rect x="-50" y="-142" width="8" height="92" rx="4" fill="#fff" opacity=".35"/>
    </g>
    <g transform="translate(410,880)">
      <path d="M-74 0 v-186 q0-26 24-34 v-24 h100 v24 q24 8 24 34 V0 Z" fill="url(#jg)"/>
      <rect x="-56" y="-256" width="112" height="28" rx="7" fill="#B4831F"/>
      <rect x="-52" y="-158" width="104" height="90" rx="3" fill="#F7EFDD"/>
      <line x1="-30" y1="-120" x2="30" y2="-120" stroke="#C08A2E" stroke-width="1.8"/>
      <rect x="-66" y="-180" width="9" height="120" rx="4.5" fill="#fff" opacity=".38"/>
    </g>
    <g transform="translate(610,880)">
      <path d="M-50 0 v-128 q0-20 18-26 v-20 h64 v20 q18 6 18 26 V0 Z" fill="#EFE2C4"/>
      <rect x="-38" y="-190" width="76" height="24" rx="6" fill="#B8AE9A"/>
      <rect x="-44" y="-118" width="9" height="76" rx="4.5" fill="#fff" opacity=".5"/>
    </g>
  </g>
</svg>
""")

print("done")

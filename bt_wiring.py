#!/usr/bin/env python3
"""Рисует подробную схему соединений Bluetooth-дисплея: bt_wiring.svg.

Каждый провод помечен номером в кружке; расшифровка — таблицей на странице.
Сверху — вариант с платой расширения (макетная плата не нужна), снизу — вариант
на макетной плате.
"""

import pathlib

BASE = pathlib.Path(__file__).resolve().parent
W, H = 1000, 940

CSS = """
  .bg{fill:#0b1220}
  .box{fill:#111827;stroke:#334155;stroke-width:2}
  .box2{fill:#0f172a;stroke:#334155;stroke-width:1.6}
  .lbl{fill:#e2e8f0;font-size:15px;font-weight:600}
  .h{fill:#f8fafc;font-size:18px;font-weight:700}
  .sub{fill:#94a3b8;font-size:12.5px}
  .pin{fill:#cbd5e1;font-size:11px;font-family:ui-monospace,Consolas,monospace}
  .num{fill:#0b1220;font-size:12px;font-weight:700}
  .wp{stroke:#ef4444;stroke-width:3.6;fill:none;stroke-linecap:round}
  .wn{stroke:#94a3b8;stroke-width:3.6;fill:none;stroke-linecap:round}
  .wd{stroke:#38bdf8;stroke-width:3;fill:none;stroke-linecap:round}
  .wbt{stroke:#a78bfa;stroke-width:3;fill:none;stroke-linecap:round;stroke-dasharray:4 6}
  .hole{fill:#1e293b}
  .rail{stroke:#ef4444;stroke-width:2;fill:none}
  .railn{stroke:#3b82f6;stroke-width:2;fill:none}
  .gutter{fill:#0b1220;stroke:#1e293b;stroke-width:1}
"""


def t(x, y, s, cls="sub", anchor="start", size=None):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    z = f' font-size="{size}"' if size else ""
    return f'<text x="{x}" y="{y}" class="{cls}"{a}{z}>{s}</text>'


def box(x, y, w, h, r=10, cls="box"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" class="{cls}"/>'


def badge(x, y, n):
    return f'<circle cx="{x}" cy="{y}" r="11" fill="#38bdf8"/>' + t(x, y + 4, str(n), "num", "middle")


def wire(pts, cls="wd"):
    return f'<path d="M{" L".join(f"{x},{y}" for x, y in pts)}" class="{cls}"/>'


def panel_a():
    s = [t(24, 40, "Вариант 1 (основной) — с платой-переходником и зарядкой", "h"),
         t(24, 62, "Зарядка стоит в разрыве между отсеком и платой: аккумулятор → плата зарядки → кабель PH2.0 → гнездо переходника.", "sub")]

    # ESP-модуль
    s += [box(390, 92, 210, 46, 8, "box2"),
          t(495, 112, "ESP32-C3 SuperMini", "lbl", "middle"),
          t(495, 128, "ножки припаяны заранее", "sub", "middle")]
    for i in range(9):
        x = 406 + i * 23
        s.append(f'<line x1="{x}" y1="138" x2="{x}" y2="176" stroke="#94a3b8" stroke-width="2.4"/>')
    s.append(t(495, 190, "вставляется ножками в гнёзда переходника", "pin", "middle"))

    # переходник
    s += [box(330, 200, 350, 300),
          t(505, 224, "Плата расширения (переходник)", "lbl", "middle"),
          t(505, 243, "разводка GPIO, гнёзда для модуля и гнездо PH2.0", "sub", "middle")]

    # гнездо PH2.0 (слева на плате)
    s += [box(342, 300, 42, 54, 6, "box2"),
          t(363, 320, "PH", "middle", "pin"), t(363, 336, "2.0", "pin", "middle"),
          t(440, 318, "гнездо: сюда щёлкает", "sub"), t(440, 336, "штекер кабеля зарядки", "sub")]

    # штырьки разводки
    for i, n in enumerate(["3V3", "GND", "GPIO8", "GPIO9"]):
        y = 262 + i * 34
        s += [box(560, y, 100, 26, 5, "box2"), t(610, y + 17, n, "pin", "middle")]

    s += [t(505, 448, "зарядки внутри переходника нет — он только разводит контакты,", "sub", "middle"),
          t(505, 466, "поэтому плата зарядки стоит отдельно, в разрыве питания", "sub", "middle"),
          t(505, 490, "питание модуля идёт через гнездо PH2.0, по дорожкам платы", "pin", "middle")]

    # аккумулятор
    s += [box(30, 100, 240, 118),
          t(150, 128, "Аккумулятор 18650", "lbl", "middle"),
          t(150, 148, "3,7 В, 2000 мА·ч в отсеке", "sub", "middle"),
          box(48, 162, 204, 42, 6, "box2"),
          t(150, 180, "на проводах — разъём PH2.0,", "pin", "middle"),
          t(150, 197, "его срезаем: концы идут в B+ и B−", "pin", "middle")]

    # плата зарядки
    s += [box(30, 300, 240, 150),
          t(150, 328, "Плата зарядки TP4056", "lbl", "middle"),
          t(150, 348, "вход B+ / B− — от аккумулятора", "sub", "middle"),
          t(150, 366, "выход OUT+ / OUT− — на плату", "sub", "middle"),
          box(48, 382, 204, 40, 6, "box2"),
          t(150, 400, "USB-C ← зарядка от телефона", "pin", "middle"),
          t(150, 419, "заряд идёт прямо через устройство", "sub", "middle")]

    # провода 1 и 2: отсек → плата зарядки
    s += [wire([(120, 218), (120, 300)], "wp"), wire([(180, 218), (180, 300)], "wn"),
          badge(120, 259, 1), badge(180, 259, 2),
          t(196, 259, "1 — красный: плюс → B+", "sub"), t(196, 278, "2 — чёрный: минус → B−", "sub")]

    # кабель 3: зарядка → гнездо переходника
    s += [wire([(270, 330), (340, 330)], "wd"),
          badge(305, 330, 3),
          t(30, 530, "3 — кабель PH2.0 (30 см): один конец паяется к выходу OUT+/OUT−, второй щёлкает в гнездо переходника.", "sub"),
          t(30, 548, "Паять за всю сборку — 4 точки: два провода отсека и два провода кабеля. Без пайки: концы вставить", "sub"),
          t(30, 566, "в отверстия платы и зафиксировать термоклеем или изолентой.", "sub")]

    # дисплей
    s += [box(730, 200, 240, 250),
          t(850, 226, "Дисплей OLED 0,96″", "lbl", "middle"),
          t(850, 245, "128×64, I2C", "sub", "middle"),
          box(742, 264, 104, 116, 6, "box2"),
          t(794, 288, "VCC", "pin", "middle"), t(794, 316, "GND", "pin", "middle"),
          t(794, 344, "SDA", "pin", "middle"), t(794, 372, "SCL", "pin", "middle"),
          t(850, 412, "ножки дисплея уже распаяны", "sub", "middle"),
          t(850, 430, "продавцом — подключаются как есть", "sub", "middle")]

    for i, (n, y) in enumerate([("4", 282), ("5", 310), ("6", 338), ("7", 366)]):
        ty = 275 + i * 34
        s += [wire([(738, y), (700, y), (700, ty), (662, ty)], "wd"), badge(700, y, n)]

    # телефон
    s += [box(730, 480, 240, 90),
          t(850, 506, "Телефон или ноутбук", "lbl", "middle"),
          t(850, 526, "пишет текст на дисплей", "sub", "middle"),
          t(850, 548, "Bluetooth (BLE), 5–10 м", "pin", "middle")]
    s += [wire([(770, 480), (770, 460), (700, 460), (700, 430)], "wbt"),
          badge(735, 460, 8)]
    return "".join(s)


def panel_b():
    s = [t(24, 660, "Вариант 2 — без переходника, на макетной плате", "h"),
         t(24, 682, "Макетная плата здесь заменяет переходник: плата и все провода вставляются в её отверстия и держатся жёстко.", "sub")]

    bx, by, bw, bh = 40, 720, 570, 190
    s += [box(bx, by, bw, bh, 8, "box2")]
    s += [f'<path d="M{bx + 20},{by + 24} L{bx + bw - 20},{by + 24}" class="rail"/>',
          t(bx + 24, by + 18, "+ красная шина питания", "pin"),
          f'<path d="M{bx + 20},{by + bh - 22} L{bx + bw - 20},{by + bh - 22}" class="railn"/>',
          t(bx + 24, by + bh - 8, "− синяя шина питания", "pin")]

    cols, rows = 28, 8
    for c in range(cols):
        x = bx + 46 + c * 18
        for r in range(rows):
            y = by + 48 + r * 13 + (11 if r >= rows // 2 else 0)
            s.append(f'<circle cx="{x}" cy="{y}" r="2.4" class="hole"/>')
    s += [f'<rect x="{bx + 40}" y="{by + 84}" width="{cols * 18}" height="14" class="gutter"/>']

    s += [box(bx + 70, by + 66, 130, 48, 6, "box"),
          t(bx + 135, by + 88, "ESP32-C3", "lbl", "middle"),
          t(bx + 135, by + 105, "ножки в отверстия", "sub", "middle")]
    s += [box(bx + 250, by + 66, 130, 48, 6, "box"),
          t(bx + 315, by + 88, "OLED 0,96″", "lbl", "middle"),
          t(bx + 315, by + 105, "4 провода", "sub", "middle")]

    for i, (n, y) in enumerate([("3", 72), ("4", 84), ("5", 96), ("6", 108)]):
        s += [wire([(bx + 200, by + y), (bx + 250, by + y)], "wd"), badge(bx + 225, by + y, n)]

    s += [wire([(bx + 135, by + 114), (bx + 135, by + 120), (bx + 100, by + 120), (bx + 100, by + 24)], "wp"),
          t(bx + 150, by + 140, "1 и 2: питание модуля — плюс на красную шину, минус на синюю", "sub")]

    s += [box(630, 720, 340, 190),
          t(800, 746, "Питание в этом варианте", "lbl", "middle"),
          t(648, 772, "отсек с аккумулятором → винтовая колодка →", "sub"),
          t(648, 790, "плата зарядки TP4056 → провода на шины платы", "sub"),
          t(648, 818, "Площадки TP4056 рассчитаны на пайку: провода", "sub"),
          t(648, 836, "держатся трением, а надёжнее — пропаять 4 точки.", "sub"),
          t(648, 864, "Провода «мама-мама» резать не нужно: 10 см хватает.", "sub"),
          t(648, 882, "Этот вариант дороже на 175 ₽ (сама плата).", "sub")]
    return "".join(s)


SVG = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
    f'font-family="system-ui, -apple-system, \'Segoe UI\', Roboto, sans-serif" '
    f'role="img" aria-label="Подробная схема соединений Bluetooth-дисплея: аккумулятор, переходник, ESP32-C3, OLED и Bluetooth; и вариант на макетной плате">\n'
    f'  <defs><style>{CSS}</style></defs>\n'
    f'  <rect x="0" y="0" width="{W}" height="{H}" class="bg"/>\n'
    f'{panel_a()}\n{panel_b()}\n</svg>\n'
)

if __name__ == "__main__":
    (BASE / "bt_wiring.svg").write_text(SVG, encoding="utf-8")
    print("bt_wiring.svg записан:", len(SVG), "байт")

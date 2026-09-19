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
    s = [t(24, 40, "Вариант 1 — с платой расширения (макетная плата не нужна)", "h"),
         t(24, 62, "Пайка один раз: две планки ножек к самому ESP32. Дальше всё вставляется: разъём в гнездо, провода на штырьки.", "sub")]

    # ESP-модуль над переходником
    s += [box(370, 92, 220, 46, 8, "box2"),
          t(480, 112, "ESP32-C3 SuperMini", "lbl", "middle"),
          t(480, 128, "ножки припаяны заранее", "sub", "middle")]
    for i in range(9):
        x = 386 + i * 25
        s.append(f'<line x1="{x}" y1="138" x2="{x}" y2="158" stroke="#94a3b8" stroke-width="2.4"/>')
    s.append(t(480, 174, "вставляется ножками в гнёзда переходника", "pin", "middle"))

    # переходник
    s += [box(300, 186, 380, 250),
          t(490, 212, "Плата расширения (переходник) для ESP32-C3", "lbl", "middle"),
          t(490, 231, "внутри: разводка GPIO, гнездо аккумулятора, питание на плату", "sub", "middle")]

    # гнездо PH2.0 внутри переходника
    s += [box(312, 258, 40, 52, 6, "box2"),
          t(332, 276, "PH", "pin", "middle"), t(332, 291, "2.0", "pin", "middle"),
          t(332, 330, "гнездо", "sub", "middle"), t(332, 346, "аккумулятора", "sub", "middle")]

    # штырьки GPIO внутри переходника (вертикальный столбик справа)
    names = [("3V3", "питание дисплея"), ("GND", "общий минус"), ("GPIO8", "данные SDA"),
             ("GPIO9", "такт SCL"), ("5V", "питание платы")]
    for i, (n, d) in enumerate(names):
        y = 256 + i * 34
        s += [box(560, y, 96, 24, 5, "box2"), t(608, y + 16, n, "pin", "middle"),
              t(608, y + 32, d, "sub", "middle", 10.5)]

    s += [t(390, 470, "питание ESP идёт внутри переходника", "sub"),
          t(390, 488, "отдельные провода от аккумулятора к ESP не нужны", "sub")]

    # аккумулятор в отсеке
    s += [box(30, 200, 210, 150),
          t(135, 228, "Аккумулятор 18650", "lbl", "middle"),
          t(135, 248, "3,7 В, 2000 мА·ч лежит", "sub", "middle"),
          t(135, 265, "в батарейном отсеке", "sub", "middle"),
          box(52, 285, 166, 46, 6, "box2"),
          t(135, 303, "на проводах отсека —", "pin", "middle"),
          t(135, 320, "белый разъём (2 контакта)", "pin", "middle")]

    # провода 1 и 2: отсек → гнездо
    s += [wire([(238, 300), (270, 300), (270, 276), (310, 276)], "wp"),
          wire([(238, 318), (282, 318), (282, 296), (310, 296)], "wn"),
          badge(254, 300, 1), badge(254, 318, 2),
          t(150, 372, "1 — красный: + отсека", "sub"), t(150, 390, "2 — чёрный: − отсека", "sub"),
          t(150, 412, "разъём щёлкает в гнездо — паять не надо", "sub")]

    # пояснение про питание переносим ниже блока переходника

    # дисплей
    s += [box(720, 186, 250, 250),
          t(845, 214, "Дисплей OLED 0,96″", "lbl", "middle"),
          t(845, 233, "128×64, I2C", "sub", "middle"),
          box(730, 250, 104, 116, 6, "box2"),
          t(782, 274, "VCC", "pin", "middle"), t(782, 302, "GND", "pin", "middle"),
          t(782, 330, "SDA", "pin", "middle"), t(782, 358, "SCL", "pin", "middle"),
          t(845, 400, "ножки у дисплея уже распаяны", "sub", "middle"),
          t(845, 420, "продавцом — вставляются как есть", "sub", "middle")]

    # провода 3-6: дисплей → штырьки
    pins = [(268, "3", "VCC → 3V3"), (296, "4", "GND → GND"),
            (324, "5", "SDA → GPIO8"), (352, "6", "SCL → GPIO9")]
    for i, (y, n, _) in enumerate(pins):
        ty = 268 + i * 34
        s += [wire([(728, y), (694, y), (694, ty + 12), (656, ty + 12)], "wd"),
              badge(690, y, n)]

    # телефон
    s += [box(720, 480, 250, 96),
          t(845, 508, "Телефон или ноутбук", "lbl", "middle"),
          t(845, 528, "пишет текст на дисплей", "sub", "middle"),
          t(845, 552, "Bluetooth (BLE), 5–10 м", "pin", "middle")]
    s += [wire([(760, 480), (760, 452), (700, 452), (700, 400)], "wbt"),
          badge(730, 452, 7),
          t(730, 470, "7 — только текст; прошивка заливается по USB", "sub")]

    # как заряжать
    s += [box(30, 452, 330, 154),
          t(195, 480, "Как заряжать аккумулятор", "lbl", "middle"),
          t(46, 506, "1) Вынуть ячейку из отсека и зарядить в обычной", "sub"),
          t(46, 524, "зарядке для 18650 — паять вообще нечего.", "sub"),
          t(46, 552, "2) Либо поставить модуль TP4056: у него площадки", "sub"),
          t(46, 570, "под пайку B+ / B−, к ним идут провода отсека.", "sub"),
          t(46, 592, "Это единственное место, где пайка реально уместна.", "sub")]
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

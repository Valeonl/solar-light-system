#!/usr/bin/env python3
"""Собирает страницу проекта «Bluetooth-дисплей на аккумуляторе» (bt-display.html).

Читает bt_items.json (товары с Ozon, доставка ≤7 дней) и пишет bt-display.html.
Картинки товаров лежат в img/. Прошивка и скрипт отправки — в files/bt_display/.

    python bt_display.py
"""

from __future__ import annotations

import json
import pathlib

BASE = pathlib.Path(__file__).parent
D = json.loads((BASE / "bt_items.json").read_text(encoding="utf-8"))
V1 = D["variant1"]          # TTGO T-Display + батарея
V2 = D["variant2"]          # ESP32-C3 + OLED + 18650
PRICE_DATE = D["date"]

# ---------------------------------------------------------------- расчёты
ESP_MA = 90.0          # ESP32 + дисплей, средний ток при работе
CELL_MAH = 2000        # ёмкость аккумулятора, мА·ч
HOURS = CELL_MAH / ESP_MA * 0.8     # 80% полезной ёмкости
V1_TOTAL = sum(i["price"] for i in V1)
V1_BASE = sum(i["price"] for i in V1 if "запасн" not in i.get("role", ""))
V2_TOTAL = sum(i["price"] for i in V2)


def money(n: int) -> str:
    return f"{n:,}".replace(",", "\u00a0")


def card(i: dict) -> str:
    img = i.get("img_local") or ""
    return f"""
      <article class="card">
        <div class="card-img"><img src="{img}" alt=""></div>
        <div class="card-body">
          <span class="role">{i.get('role','')}</span>
          <h3>{i['title']}</h3>
          <p class="specs">{i.get('specs','')}</p>
          <p class="note">{i.get('note','')}</p>
          <div class="row"><span class="price">{money(i['price'])} ₽</span>
            <span class="days">доставка {i['days']} дн.</span></div>
          <a class="btn" href="{i['url']}" target="_blank" rel="noopener">Открыть на Ozon</a>
        </div>
      </article>"""


def rows(items: list[dict]) -> str:
    return "\n".join(
        f"<tr><td>{i['role']}</td><td>{i['title'][:64]}</td><td class='num'>{money(i['price'])} ₽</td>"
        f"<td class='num'>{i['days']} дн.</td></tr>" for i in items)


HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bluetooth-дисплей на аккумуляторе своими руками — без пайки</title>
<style>
  :root{{--bg:#0b1220;--panel:#111827;--panel2:#0f172a;--line:#1f2937;--line2:#334155;
    --fg:#e5e7eb;--muted:#94a3b8;--accent:#38bdf8;--good:#22c55e;--bad:#ef4444;--radius:14px}}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}}
  a{{color:var(--accent)}}
  .wrap{{max-width:1080px;margin:0 auto;padding:32px 20px 80px}}
  .back{{display:inline-block;margin-bottom:18px;color:var(--muted);text-decoration:none;font-size:14px}}
  h1{{font-size:clamp(24px,3.6vw,36px);line-height:1.18;margin:0 0 12px}}
  .lead{{color:var(--muted);font-size:17.5px;max-width:72ch}}
  h2{{font-size:clamp(19px,2.4vw,25px);margin:52px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--line)}}
  h3{{font-size:17px;margin:0 0 6px;line-height:1.3}}
  .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:24px 0}}
  .kpi{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px}}
  .kpi b{{display:block;font-size:23px;color:var(--accent);line-height:1.2}}
  .kpi span{{color:var(--muted);font-size:13.5px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin:20px 0}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}}
  .card-img{{background:#fff;aspect-ratio:1/1;display:flex;align-items:center;justify-content:center}}
  .card-img img{{width:100%;height:100%;object-fit:contain}}
  .card-body{{padding:14px;display:flex;flex-direction:column;gap:6px;flex:1}}
  .role{{display:inline-block;background:var(--panel2);border:1px solid var(--line2);color:var(--muted);
    font-size:12px;padding:2px 8px;border-radius:999px;align-self:flex-start}}
  .specs{{font-size:14px;margin:0}} .note{{color:var(--muted);font-size:13px;margin:0}}
  .row{{display:flex;justify-content:space-between;align-items:baseline;margin-top:auto;gap:8px}}
  .price{{font-size:20px;font-weight:700}} .days{{color:var(--muted);font-size:13px;text-align:right}}
  .btn{{display:block;text-align:center;background:var(--accent);color:#062033;font-weight:600;
    text-decoration:none;padding:9px 12px;border-radius:10px;margin-top:10px}}
  table{{width:100%;border-collapse:collapse;margin:18px 0;font-size:14.5px}}
  th,td{{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}}
  th{{background:var(--panel2);color:var(--muted);font-weight:600}}
  td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
  tr.total td{{background:var(--panel);font-weight:700}}
  .good{{color:var(--good)}} .bad{{color:var(--bad)}}
  .box{{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
    border-radius:10px;padding:14px 16px;margin:18px 0}}
  .warn{{border-left-color:var(--bad)}} .ok{{border-left-color:var(--good)}}
  ol.steps{{counter-reset:s;list-style:none;padding:0}}
  ol.steps li{{counter-increment:s;position:relative;padding:12px 16px 12px 54px;margin:10px 0;
    background:var(--panel);border:1px solid var(--line);border-radius:12px}}
  ol.steps li::before{{content:counter(s);position:absolute;left:15px;top:12px;width:26px;height:26px;border-radius:50%;
    background:var(--accent);color:#062033;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:14px}}
  figure{{margin:22px 0}} figure svg{{width:100%;height:auto;border:1px solid var(--line);border-radius:var(--radius)}}
  figcaption{{color:var(--muted);font-size:13.5px;margin-top:8px}}
  code{{background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:13.5px}}
  pre{{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;font-size:13.5px}}
  footer{{margin-top:60px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13.5px}}
  @media (max-width:600px){{.wrap{{padding:22px 14px 60px}}table{{font-size:13px}}}}
</style>
</head>
<body>
<div class="wrap">

<a class="back" href="index.html">← На главную проекта (солнечная панель, аккумулятор, лампа)</a><br>
<a class="back" href="budget.html">Бюджетный свет до 1000 ₽ (садовые светильники) →</a>

<h1>Bluetooth-дисплей на аккумуляторе: устройство, которому я смогу писать сам</h1>
<p class="lead">Маленький экран с аккумулятором, который показывает всё, что ему пришлют по
Bluetooth. Никакой пайки: либо одна плата со встроенным экраном, либо микроконтроллер и экран,
соединённые четырьмя шлейфами. Дальше я или телефон пишем на него текст — и он появляется на экране.</p>

<div class="kpis">
  <div class="kpi"><b>{money(V1_BASE)} ₽</b><span>вариант «одна плата»: ESP32 с экраном + аккумулятор</span></div>
  <div class="kpi"><b>{money(V2_TOTAL)} ₽</b><span>вариант «из модулей»: ESP32-C3 + OLED + аккумулятор</span></div>
  <div class="kpi"><b>≈{HOURS:.0f} ч</b><span>работа от одного заряда ({CELL_MAH:.0f} мА·ч, ток ≈{ESP_MA:.0f} мА)</span></div>
  <div class="kpi"><b>0</b><span>паяных соединений в обоих вариантах</span></div>
</div>

<h2>Что это вообще такое</h2>
<ol>
  <li><b>ESP32</b> — микроконтроллер за 300–500 ₽, у которого на борту Wi-Fi, Bluetooth и память
      под программу. Именно он умеет принимать текст по воздуху.</li>
  <li><b>Экран</b> — либо встроенный в плату (вариант «одна плата»), либо отдельный OLED 0,96″,
      который соединяется с платой четырьмя шлейфами.</li>
  <li><b>Аккумулятор</b> — литиевый на 3,7 В с платой защиты и разъёмом; заряжается от USB.</li>
  <li><b>Прошивка</b> — программа, которую надо один раз залить в плату по USB (файлы ниже уже готовы).
      Она поднимает Bluetooth-сервис и выводит принятый текст на экран.</li>
</ol>
<div class="box ok">
  <b>Как я буду на него писать.</b> Прошивка поднимает стандартный BLE-сервис «UART». Я отправляю
  строку скриптом <code>send_text.py</code> (он лежит в файлах ниже) — устройство принимает её и
  показывает. С телефона то же самое делает любой BLE-терминал, например «nRF Connect».
</div>

<h2>Два варианта сборки</h2>
<table>
  <tr><th>Вариант</th><th>Что покупаешь</th><th>Итого</th><th>Сборка</th><th>Особенности</th></tr>
  <tr>
    <td><b>Одна плата</b><br><span class="good">рекомендую</span></td>
    <td>TTGO T-Display (ESP32 + цветной экран 1,14″) и аккумулятор Li-Po 2000 мА·ч с разъёмом</td>
    <td class="num">{money(V1_BASE)} ₽<br><span class="note">с переходником {money(V1_TOTAL)} ₽</span></td>
    <td>подключить аккумулятор в разъём</td>
    <td>ничего соединять не надо, экран цветной, есть зарядка от USB-C; разъём батареи и платы
        должен совпасть (JST 1.25 — проверяй при заказе)</td>
  </tr>
  <tr>
    <td><b>Из модулей</b></td>
    <td>ESP32-C3, OLED 0,96″, аккумулятор 18650 с холдером, плата зарядки, шлейфы</td>
    <td class="num">{money(V2_TOTAL)} ₽</td>
    <td>4 шлейфа на экран + 2 провода питания</td>
    <td>все детали приезжают быстрее и есть в наличии, но проводов больше; экран монохромный</td>
  </tr>
</table>

<h3>Вариант 1: одна плата со встроенным экраном — {money(V1_BASE)} ₽</h3>
<div class="grid">
{"".join(card(i) for i in V1)}
</div>
<table>
  <tr><th>Роль</th><th>Деталь</th><th>Цена</th><th>Доставка</th></tr>
  {rows(V1)}
  <tr class="total"><td colspan="2">Итого</td><td class="num">{money(V1_TOTAL)} ₽</td><td></td></tr>
  <tr><td colspan="4" class="note" style="color:#94a3b8">Из них {money(V1_TOTAL - V1_BASE)} ₽ — запасной переходник: нужен только если разъём аккумулятора не совпадёт с разъёмом платы. Без него набор стоит {money(V1_BASE)} ₽.</td></tr>
</table>

<h3>Вариант 2: из модулей — {money(V2_TOTAL)} ₽</h3>
<div class="grid">
{"".join(card(i) for i in V2)}
</div>
<table>
  <tr><th>Роль</th><th>Деталь</th><th>Цена</th><th>Доставка</th></tr>
  {rows(V2)}
  <tr class="total"><td colspan="2">Итого</td><td class="num">{money(V2_TOTAL)} ₽</td><td></td></tr>
</table>

<h2>Схема подключения (для варианта 2)</h2>
<figure>
  {{SVG_SCHEMA}}
  <figcaption>Питание: аккумулятор → плата зарядки → вход 5 В платы. Экран: четыре провода,
  VCC и GND на 3,3 В и землю, SDA на GPIO8, SCL на GPIO9.</figcaption>
</figure>
<p>В варианте 1 схема не нужна вовсе: аккумулятор вставляется в разъём на плате, экран уже распаян
производителем. Это и главный аргумент в его пользу.</p>

<h2>Расчёт автономности</h2>
<table>
  <tr><th>Что</th><th>Значение</th><th>Пояснение</th></tr>
  <tr><td>Ток устройства</td><td class="num">{ESP_MA:.0f} мА</td>
      <td>ESP32 с включённым Bluetooth и работающим экраном</td></tr>
  <tr><td>Ёмкость аккумулятора</td><td class="num">{CELL_MAH:.0f} мА·ч</td>
      <td>типичный Li-Po 2000 мА·ч или элемент 18650</td></tr>
  <tr><td>Время работы</td><td class="num">≈{HOURS:.0f} ч</td>
      <td>{CELL_MAH:.0f} ÷ {ESP_MA:.0f} с поправкой на 80% полезной ёмкости</td></tr>
  <tr class="total"><td>Вывод</td><td colspan="2">сутки с небольшим на одном заряде; если нужна неделя —
      либо яркость экрана вниз и режим сна между сообщениями, либо аккумулятор побольше (я допишу
      прошивку под сон, когда железо будет на руках)</td></tr>
</table>

<h2>Сборка и запуск — по шагам</h2>
<ol class="steps">
  <li><b>Закажи детали</b> из выбранного варианта. Все позиции — с доставкой до 7 дней.</li>
  <li><b>Соедини питание.</b> Вариант 1: аккумулятор в разъём на плате. Вариант 2: аккумулятор
      в холдер → провода холдера → вход платы зарядки → выход платы зарядки на пин 5V платы ESP32.
      Плюс с плюсом, минус с минусом — здесь полярность важнее всего.</li>
  <li><b>Подключи экран</b> (только вариант 2): VCC → 3V3, GND → GND, SDA → GPIO8, SCL → GPIO9.
      Если экран не завёлся — поменяй SDA и SCL местами: у разных плат они переставлены.</li>
  <li><b>Подключи плату к компьютеру по USB</b> и залей прошивку — файл <code>t_display_firmware.ino</code>
      (вариант 1) или <code>c3_oled_firmware.ino</code> (вариант 2). В Arduino IDE нужно доустановить
      библиотеки: TFT_eSPI и NimBLE-Arduino для первого варианта, Adafruit SSD1306 и NimBLE-Arduino
      для второго. Инструкция — в комментариях внутри файла.</li>
  <li><b>Проверь, что устройство видно по Bluetooth:</b> оно поднимется как <code>Hermes-Display</code>.</li>
  <li><b>Отправь первый текст</b> с компьютера:
      <code>python send_text.py "Привет, дисплей!"</code> — на экране появится строка.
      С телефона — любым BLE-терминалом, тот же текст в характеристику RX.</li>
</ol>
<div class="box">
  <b>Файлы для этого устройства</b> (лежат в репозитории рядом со страницей):<br>
  <a href="files/bt_display/t_display_firmware.ino">t_display_firmware.ino</a> — прошивка для варианта 1<br>
  <a href="files/bt_display/c3_oled_firmware.ino">c3_oled_firmware.ino</a> — прошивка для варианта 2<br>
  <a href="files/bt_display/send_text.py">send_text.py</a> — скрипт отправки текста (Python, библиотека bleak)
</div>

<h2>Честно о рисках</h2>
<ul>
  <li><b>Первая прошивка требует компьютера с USB.</b> Без этого шага устройство не заработает —
      готового «купил и пишет» здесь нет, и это цена дешевизны.</li>
  <li><b>Код написан, но на живом железе ещё не проверен.</b> Скажи, когда детали приедут, — я
      подключу плату по USB, залью прошивку, поправлю то, что не сойдётся, и покажу, как пишу на экран.</li>
  <li><b>Разъёмы батарей различаются.</b> У платы T-Display разъём JST 1.25 мм, у многих аккумуляторов —
      PH 2.0. Это самая частая заминка: проверяй тип разъёма при заказе, иначе понадобится переходник.</li>
  <li><b>Bluetooth только в упор.</b> BLE держит связь на 5–10 м в комнате; для дальности нужна
      другая антенна и другой бюджет.</li>
  <li><b>Яркость и ток.</b> Подсветка экрана — основная нагрузка: если нужна неделя автономности,
      яркость снижаем, а между сообщениями плату усыпляем.</li>
</ul>

<footer>
  Цены и наличие — Ozon, {PRICE_DATE}, фильтр «доставка до 7 дней». Фотографии товаров принадлежат
  продавцам на Ozon и приведены со ссылками на страницы товаров. Прошивки и скрипт написаны под эти
  платы; проверка на живом модуле — после покупки, вместе с владельцем.
</footer>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    svg = (BASE / "bt_schematic.svg").read_text(encoding="utf-8")
    out = HTML.replace("{SVG_SCHEMA}", svg)
    (BASE / "bt-display.html").write_text(out, encoding="utf-8")
    print(f"bt-display.html записан: {len(out):,} байт | вариант 1: {money(V1_TOTAL)} ₽ | "
          f"вариант 2: {money(V2_TOTAL)} ₽ | автономность ≈{HOURS:.0f} ч")

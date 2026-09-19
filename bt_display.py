#!/usr/bin/env python3
"""Собирает страницу «Bluetooth-дисплей на аккумуляторе» (bt-display.html).

Читает bt_items.json: одна проверенная сборка (все товары с отзывами) плюс пояснение,
почему не берём «одну плату со встроенным экраном». Прошивки — в files/bt_display/.
"""

from __future__ import annotations

import json
import pathlib

BASE = pathlib.Path(__file__).parent
D = json.loads((BASE / "bt_items.json").read_text(encoding="utf-8"))
BUILD = D["build"]
OPT = {i["key"]: i for i in D.get("optional", [])}
WHY = D["why_no_board"]
PRICE_DATE = D["date"]

ESP_MA = 90.0
CELL_MAH = 2000
HOURS = CELL_MAH / ESP_MA * 0.8
TOTAL = sum(i["price"] * i["qty"] for i in BUILD)


def money(n: int) -> str:
    return f"{n:,}".replace(",", "\u00a0")


def rating_html(i: dict) -> str:
    r, n = i.get("rating"), i.get("reviews")
    if not r or not n:
        return '<div class="rating">отзывов пока нет</div>'
    if n % 10 == 1 and n % 100 != 11:
        word = "отзыв"
    elif 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14:
        word = "отзыва"
    else:
        word = "отзывов"
    return f'<div class="rating">★{r:.1f} · {money(n)} {word}</div>'


def term(d) -> str:
    return "завтра" if d == 1 else f"{d} дн."


def card(i: dict) -> str:
    img = i.get("img_local") or ""
    qty = f' × {i["qty"]}' if i["qty"] > 1 else ""
    price = money(i["price"]) + (f' × {i["qty"]}' if i["qty"] > 1 else "")
    return (
        '\n      <article class="card">\n'
        f'        <div class="card-img"><img src="{img}" alt=""></div>\n'
        f'        {rating_html(i)}\n'
        '        <div class="card-body">\n'
        f'          <span class="role">{i["role"]}{qty}</span>\n'
        f'          <h3>{i["title"]}</h3>\n'
        f'          <p class="specs">{i.get("specs","")}</p>\n'
        f'          <p class="note">{i.get("how","")}</p>\n'
        f'          <div class="row"><span class="price">{price} ₽</span>'
        f'<span class="days">доставка {term(i["days"])}</span></div>\n'
        f'          <a class="btn" href="{i["url"]}" target="_blank" rel="noopener">Открыть на Ozon</a>\n'
        '        </div>\n      </article>')


rows = "\n".join(
    f"<tr><td>{i['role']}</td><td>{i['title'][:56]}</td>"
    f"<td class='num'>{money(i['price'])} ₽</td><td class='num'>{i['qty']} шт</td>"
    f"<td class='num'>{money(i['price'] * i['qty'])} ₽</td>"
    f"<td class='num'>{term(i['days'])}</td>"
    f"<td class='num'>★{i['rating']:.1f} · {money(i['reviews'])}</td></tr>" for i in BUILD)

cards = "\n".join(card(i) for i in BUILD)

CSS = """
  :root{--bg:#0b1220;--panel:#111827;--panel2:#0f172a;--line:#1f2937;--line2:#334155;
    --fg:#e5e7eb;--muted:#94a3b8;--accent:#38bdf8;--good:#22c55e;--bad:#ef4444;--radius:14px}
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}
  a{color:var(--accent)}
  .wrap{max-width:1080px;margin:0 auto;padding:32px 20px 80px}
  .back{display:inline-block;margin-bottom:18px;color:var(--muted);text-decoration:none;font-size:14px}
  h1{font-size:clamp(24px,3.6vw,36px);line-height:1.18;margin:0 0 12px}
  .lead{color:var(--muted);font-size:17.5px;max-width:72ch}
  h2{font-size:clamp(19px,2.4vw,25px);margin:52px 0 16px;padding-bottom:8px;border-bottom:1px solid var(--line)}
  h3{font-size:17px;margin:0 0 6px;line-height:1.3}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:24px 0}
  .kpi{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px}
  .kpi b{display:block;font-size:23px;color:var(--accent);line-height:1.2}
  .kpi span{color:var(--muted);font-size:13.5px}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;margin:20px 0}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}
  .card-img{background:#fff;aspect-ratio:1/1;display:flex;align-items:center;justify-content:center}
  .card-img img{width:100%;height:100%;object-fit:contain}
  .rating{background:var(--panel2);color:#fbbf24;font-size:13px;padding:6px 12px;
    border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
  .card-body{padding:14px;display:flex;flex-direction:column;gap:6px;flex:1}
  .role{display:inline-block;background:var(--panel2);border:1px solid var(--line2);color:var(--muted);
    font-size:12px;padding:2px 8px;border-radius:999px;align-self:flex-start}
  .specs{font-size:14px;margin:0} .note{color:var(--muted);font-size:13px;margin:0}
  .row{display:flex;justify-content:space-between;align-items:baseline;margin-top:auto;gap:8px}
  .price{font-size:20px;font-weight:700} .days{color:var(--muted);font-size:13px;text-align:right}
  .btn{display:block;text-align:center;background:var(--accent);color:#062033;font-weight:600;
    text-decoration:none;padding:9px 12px;border-radius:10px;margin-top:10px}
  table{width:100%;border-collapse:collapse;margin:18px 0;font-size:14.5px}
  th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
  th{background:var(--panel2);color:var(--muted);font-weight:600}
  td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
  tr.total td{background:var(--panel);font-weight:700}
  .good{color:var(--good)} .bad{color:var(--bad)}
  .box{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
    border-radius:10px;padding:14px 16px;margin:18px 0}
  .warn{border-left-color:var(--bad)} .ok{border-left-color:var(--good)}
  ol.steps{counter-reset:s;list-style:none;padding:0}
  ol.steps li{counter-increment:s;position:relative;padding:12px 16px 12px 54px;margin:10px 0;
    background:var(--panel);border:1px solid var(--line);border-radius:12px}
  ol.steps li::before{content:counter(s);position:absolute;left:15px;top:12px;width:26px;height:26px;border-radius:50%;
    background:var(--accent);color:#062033;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:14px}
  figure{margin:22px 0} figure svg{width:100%;height:auto;border:1px solid var(--line);border-radius:var(--radius)}
  figcaption{color:var(--muted);font-size:13.5px;margin-top:8px}
  code{background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:13.5px}
  footer{margin-top:60px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13.5px}
  @media (max-width:600px){.wrap{padding:22px 14px 60px} table{font-size:13px}}
"""


BODY = f"""
<a class="back" href="index.html">← На главную проекта (солнечная панель, аккумулятор, лампа)</a><br>
<a class="back" href="budget.html">Бюджетный свет до 1000 ₽ (садовые светильники) →</a>

<h1>Bluetooth-дисплей на аккумуляторе: устройство, которому я смогу писать сам</h1>
<p class="lead">Маленький экран с аккумулятором, который показывает всё, что ему пришлют по
Bluetooth. Собирается почти без пайки: у экрана ножки уже распаяны продавцом, сам модуль вставляется
в плату-переходник, аккумулятор — в её гнездо PH2.0, а провода дисплея садятся на штырьки разводки.
Паять за всю сборку 4 точки, плюс две планки ножек на самом микроконтроллере. Питание — один элемент
18650, заряжается через USB-C прямо в собранном устройстве: вынимать ничего не нужно. Дальше я или
телефон пишем на него текст — и он появляется на экране.</p>

<div class="kpis">
  <div class="kpi"><b>{money(TOTAL)} ₽</b><span>вся сборка: {len(BUILD)} позиций, у всех доставка «завтра»</span></div>
  <div class="kpi"><b>★4.9</b><span>у всех товаров есть отзывы (82–22 604 штуки)</span></div>
  <div class="kpi"><b>≈{HOURS:.0f} ч</b><span>работа от одного заряда ({CELL_MAH:.0f} мА·ч, ток ≈{ESP_MA:.0f} мА)</span></div>
  <div class="kpi"><b>1</b><span>пайка за всю сборку — две планки ножек на плате</span></div>
</div>

<h2>Почему нет «одной платы со встроенным экраном»</h2>
<div class="box warn">
  <b>Эту ловушку стоит знать.</b> Дешёвые предложения «TTGO T-Display ESP32 с дисплеем 1,14″»
  за {money(WHY['case_price'])} ₽ — это <b>не плата, а пластиковый корпус</b> под неё
  (в названии спрятано «ABS Shell»). Настоящая плата с экраном, у которой есть отзывы, стоит
  {money(WHY['real_board_price'])} ₽ — вчетверо дороже всей сборки ниже. А комплект ESP32-S3
  с дисплеем за 224 ₽ имеет оценку ★{WHY['s3_kit_rating']:.1f} по одному отзыву. Поэтому собираем
  из проверенных модулей.
</div>

<h2>Что покупать</h2>
<div class="grid">
{cards}
</div>

<h3>Смета</h3>
<table>
  <tr><th>Роль</th><th>Товар</th><th>Цена</th><th>Кол-во</th><th>Итого</th><th>Доставка</th><th>Отзывы</th></tr>
  {rows}
  <tr class="total"><td colspan="4">Всего</td><td class="num">{money(TOTAL)} ₽</td><td></td><td></td></tr>
</table>
<p><b>Опция, если хочется другой путь:</b> {{OPT_BRD_TITLE}} — {{OPT_BRD_PRICE}} ₽ (★{{OPT_BRD_RATING}}, {{OPT_BRD_REVIEWS}} отзывов) — {{OPT_BRD_NOTE}}.</p>
<p>Количества указаны явно: в наборе проводов 40 штук, а нужно 6 — одного набора хватит с запасом;
остальные позиции берутся по одной.</p>

<h2>Как это соединяется: провод за проводом</h2>
<table>
  <tr><th>№</th><th>Откуда</th><th>Куда</th><th>Чем</th></tr>
  <tr><td>—</td><td>Ножки микроконтроллера</td><td>гнёзда переходника</td>
      <td><b>пайка</b> двух планок: гребёнки идут в комплекте отдельно и не распаяны</td></tr>
  <tr><td>1</td><td>Плюс отсека (красный провод)</td><td>вход B+ платы зарядки</td>
      <td>разъём отсека срезается, конец провода идёт в отверстие B+ (пайка или трение)</td></tr>
  <tr><td>2</td><td>Минус отсека (чёрный провод)</td><td>вход B− платы зарядки</td>
      <td>то же самое</td></tr>
  <tr><td>3</td><td>Выход OUT+ / OUT− платы зарядки</td><td>гнездо PH2.0 переходника</td>
      <td>кабель PH2.0 30 см: один конец к выходу платы, второй щёлкает в гнездо</td></tr>
  <tr><td>4</td><td>VCC дисплея</td><td>3V3 переходника</td><td>провод «мама-мама»</td></tr>
  <tr><td>5</td><td>GND дисплея</td><td>GND переходника</td><td>провод «мама-мама»</td></tr>
  <tr><td>6</td><td>SDA дисплея</td><td>GPIO8 (данные)</td><td>провод «мама-мама»</td></tr>
  <tr><td>7</td><td>SCL дисплея</td><td>GPIO9 (такт)</td><td>провод «мама-мама»</td></tr>
  <tr><td>8</td><td>Телефон или ноутбук</td><td>устройство</td>
      <td>Bluetooth, только текст. Прошивка — кабелем USB в микроконтроллер</td></tr>
  <tr><td>—</td><td>Зарядка</td><td>USB-C на плате зарядки</td>
      <td>любой блок от телефона: аккумулятор заряжается прямо в собранном устройстве</td></tr>
</table>

<figure>
  {{SVG_WIRING}}
  <figcaption>Подробная схема: сверху — основной вариант с переходником и платой зарядки в разрыве
  питания, снизу — вариант без переходника на макетной плате. Номера проводов совпадают с таблицей.</figcaption>
</figure>

<div class="box">
  <b>Главный вопрос: как заряжать, если аккумулятор вставлен в плату.</b> Плата-переходник
  <b>не заряжает</b> — на ней только гнёзда и разводка, микросхемы зарядки нет. Поэтому плата
  зарядки ставится в разрыв: провода отсека идут на её вход B+/B−, а её выход OUT+/OUT− — кабелем
  PH2.0 в гнездо переходника. Получается: аккумулятор заряжается через USB-C платы зарядки,
  при этом питание идёт на переходник и дальше на ESP. Ничего вынимать не нужно.
</div>
<div class="box">
  <b>Про короткие провода отсека.</b> Резать их не страшно: к плате зарядки нужно всего 2–3 см,
  а длину до переходника даёт кабель PH2.0 на 30 см ({money(190)} ₽) — он и есть решение проблемы
  «провод короткий, неудобно». Всего паять 4 точки: два провода отсека и два провода кабеля.
  Если паять не хочется совсем — концы вставляются в отверстия платы и фиксируются термоклеем.
</div>
<div class="box">
  <b>Заряд показываем самим ESP32 — индикатор не нужен.</b> Да, плата сама умеет измерять
  аккумулятор: у ESP32-C3 есть АЦП, а в прошивке это уже реализовано. Нужен один провод
  и два резистора:<br><br>
  <code>Плюс аккумулятора ──[100 кОм]──┬── GPIO4</code><br>
  <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──[100 кОм]── GND</code><br><br>
  Делитель пополам: 4,2 В на банке превращаются в 2,1 В на выводе — АЦП такое держит
  спокойно. Вольты и примерный процент выводятся прямо в шапке экрана, рядом с состоянием
  Bluetooth. Спросить состояние можно и по Bluetooth — отправить слово <code>bat</code>.<br><br>
  Честно про точность: литий разряжается неравномерно, а под нагрузкой напряжение проседает,
  поэтому процент — «примерно», зато порог «пора на зарядку» видно надёжно. Если хочется
  точности до процента, нужен счётчик заряда, а не измерение напряжения — он заметно дороже
  и в эту сборку не входит.
</div>
<div class="box warn">
  <b>Про индикатор BCI-2.8S-RG (270 ₽, ★4.8 / 368 отзывов, доставка завтра) — он нам не подойдёт.</b>
  В его характеристиках диапазон измерения <b>4–34 В</b> и «от 2 до 8 элементов»: это индикатор
  для сборок из двух и более банок. Один 18650 (3,7–4,2 В) лежит ниже его нижней границы, и он
  просто не покажет заряд. Для нашей сборки подошёл бы индикатор на <b>1S</b> — например
  «Индикатор уровня заряда Li-Ion 1S…8S» за 239 ₽ (★4.9, 3 934 отзыва), но и он не нужен:
  то же самое уже делает ESP32 и показывает на экране.
</div>
<div class="box">
  <b>Нужна ли батарея на 5 вольт.</b> Нет. Надпись <code>5V</code> — это не «нужно ровно 5 В»,
  а вход стабилизатора: он принимает примерно от 3,4 до 6 В и делает из них 3,3 В для ESP и
  дисплея. Поэтому один 18650 (3,7–4,2 В) питает плату напрямую — это штатный батарейный режим,
  так собирают все автономные поделки на C3. Отдельная «батарея на 5 В» — это либо две банки
  последовательно (7,4 В, а не 5), либо плата с повышением напряжения: деталей больше, потерь
  больше, а универсальности не прибавляется.<br><br>
  Если под универсальностью имеется в виду «питать от чего угодно через USB» — проще возить с
  собой обычный повербанк и включать его в USB-C модуля: схема для этого меняется не нужно,
  USB-разъём на плате — это тот же вход питания. Единственная оговорка: этот разъём занят, пока
  устройство работает от повербанка, и его же нужно освобождать для прошивки.
</div>
<div class="box">
  <b>Распиновка: что написано на плате и что это значит.</b> На самой плате ESP32-C3 подписи
  короткие, поэтому вот соответствие:
  <table style="margin-top:8px">
    <tr><th>Надпись на плате</th><th>Что это</th><th>Куда идёт провод</th></tr>
    <tr><td><code>3.3</code></td><td>выход 3,3 В — питание дисплея (да, он там есть)</td>
        <td>VCC дисплея</td></tr>
    <tr><td><code>G</code></td><td>минус, общий провод</td><td>GND дисплея</td></tr>
    <tr><td><code>8</code></td><td>GPIO8 — данные</td><td>SDA дисплея</td></tr>
    <tr><td><code>9</code></td><td>GPIO9 — такт</td><td>SCL дисплея</td></tr>
    <tr><td><code>5V</code></td><td>вход питания платы</td><td>сюда приходит аккумулятор через плату зарядки</td></tr>
  </table>
  Дисплей питается именно от <code>3.3</code>, а не от <code>5V</code>: это 3,3-вольтовая деталь.
  Запас по току есть: стабилизатор на плате даёт до ~0,5 А, а дисплей берёт 10–30 мА
  (радио ESP добавляет до ~350 мА в пике, но вместе всё равно укладывается).
  Логика у обоих тоже 3,3 В, поэтому никаких согласователей уровней не нужно.
</div>
<div class="box">
  <b>Нужна ли макетная плата.</b> В основном варианте — <b>не нужна</b>: её работу делает
  плата-переходник (гнёзда для модуля, разводка GPIO и гнездо аккумулятора уже на ней).
  Макетная плата ({{OPT_BRD_PRICE}} ₽) нужна только если собирать без переходника — тогда в неё
  вставляются и плата, и дисплей, и все провода.
</div>

<h2>Три вопроса про соединения</h2>
<div class="box">
  <b>1. Провода отсека правда просто засовываются в винты?</b><br>
  Да. У колодки восемь независимых винтов: зачищаешь конец провода на 8–10 мм, вставляешь в
  отверстие, затягиваешь винт. Это самое крепкое соединение во всей сборке, паять не нужно.
  Полярность проверь дважды: перепутанный плюс портит плату зарядки.<br><br>
  <b>2. Провода «мама-мама» не будут болтаться?</b><br>
  На штырьках они держатся трением: сами не выпадут, но при рывке сойдут. Подрезать провода не
  нужно и вредно — подрезанный конец придётся переобжимать, то есть паять. Вместо подрезки в сборке
  есть <b>плата-переходник</b>: модуль вставляется в её гнёзда, дисплей садится на её штырьки
  проводами «мама-мама», а разъём аккумулятора — в её гнездо. Всё держится на плате, а не на
  весу проводов. Если собирать без переходника, ту же роль играет макетная плата.<br><br>
  <b>3. Значит, паять всё-таки придётся?</b><br>
  Да, ровно один раз: <b>две планки ножек к микроконтроллеру</b>. На фото товара видно, что гребёнка
  лежит рядом с платой отдельно — без неё провода физически некуда надеть. Это две планки, около
  5 минут любым паяльником. Всё остальное собирается без пайки. Вариант «вообще без пайки» бывает,
  но требует платы с уже распаянными ножками: с доставкой «завтра» и нормальными отзывами таких
  в наличии нет — они едут 3–7 дней.
</div>

<h2>Схема</h2>
<figure>
  {{SVG_SCHEMA}}
  <figcaption>Питание: отсек → клеммная колодка → плата зарядки → макетная плата. Экран: четыре провода «мама-мама».</figcaption>
</figure>

<h2>Расчёт автономности</h2>
<table>
  <tr><th>Что</th><th>Значение</th><th>Пояснение</th></tr>
  <tr><td>Ток устройства</td><td class="num">{ESP_MA:.0f} мА</td><td>ESP32 с включённым Bluetooth и работающим экраном</td></tr>
  <tr><td>Ёмкость аккумулятора</td><td class="num">{CELL_MAH:.0f} мА·ч</td><td>элемент 18650 на 2000 мА·ч</td></tr>
  <tr><td>Время работы</td><td class="num">≈{HOURS:.0f} ч</td><td>{CELL_MAH:.0f} ÷ {ESP_MA:.0f} с поправкой на 80% полезной ёмкости</td></tr>
</table>

<h2>Как залить прошивку</h2>
<p>По Bluetooth или Wi-Fi прошивка <b>не заливается</b> — у ESP32 так не бывает. Порядок такой:</p>
<ol class="steps">
  <li><b>Первая заливка — только по USB.</b> Плата подключается кабелем к компьютеру, в Arduino IDE
      ставится ядро esp32 и библиотеки (NimBLE-Arduino, Adafruit SSD1306, Adafruit GFX), выбирается
      плата «ESP32C3 Dev Module» и нажимается «Загрузить». Внутри файла прошивки это расписано по шагам.
      На Windows может понадобиться драйвер USB-COM (CH340) — обычная заминка первого запуска.</li>
  <li><b>Дальше можно по Wi-Fi.</b> Если добавить в прошивку режим OTA (обновление по воздуху),
      следующие версии будут заливаться по Wi-Fi без кабеля. Скажи — добавлю, когда плата будет на руках.</li>
  <li><b>Bluetooth — только для данных.</b> По нему устройство принимает текст для показа
      (сервис <code>Hermes-Display</code>), но не прошивку.</li>
</ol>

<h2>Порядок сборки</h2>
<ol class="steps">
  <li>Припаяй две планки ножек к микроконтроллеру — это единственная пайка за всю сборку.</li>
  <li>Вставь микроконтроллер и экран в макетную плату.</li>
  <li>Соедини экран с платой четырьмя проводами «мама-мама»: VCC → 3V3, GND → GND, SDA → GPIO8,
      SCL → GPIO9. Если экран молчит — поменяй местами SDA и SCL.</li>
  <li>Вставь аккумулятор в отсек. Провода отсека и провода от платы зарядки зажми в клеммной
      колодке винтами: плюс → B+, минус → B−. Полярность проверь дважды — перепутанная портит плату.</li>
  <li>Двумя проводами «мама-мама» подай выход платы зарядки (OUT+ и OUT−) на 5V и GND макетной платы.</li>
  <li>Подключи плату к компьютеру по USB и залей прошивку
      (<a href="files/bt_display/c3_oled_firmware.ino">c3_oled_firmware.ino</a>).</li>
  <li>Проверь, что устройство видно как <code>Hermes-Display</code>, и отправь первый текст:
      <code>python send_text.py "Привет, дисплей!"</code>
      (<a href="files/bt_display/send_text.py">send_text.py</a>).</li>
</ol>

<div class="box">
  <b>Файлы проекта:</b><br>
  <a href="files/bt_display/c3_oled_firmware.ino">c3_oled_firmware.ino</a> — прошивка под ESP32-C3 и OLED<br>
  <a href="files/bt_display/t_display_firmware.ino">t_display_firmware.ino</a> — вторая прошивка, если
  когда-нибудь появится плата со встроенным экраном<br>
  <a href="files/bt_display/send_text.py">send_text.py</a> — скрипт отправки текста (Python, bleak)
</div>

<h2>Честно о рисках</h2>
<ul>
  <li><b>Стоимость — {money(TOTAL)} ₽</b>, а не меньше: это цена правильных разъёмов и товаров
      с отзывами. Убрать клеммную колодку нельзя — без неё голые провода отсека соединять нечем.</li>
  <li><b>Одна пайка всё-таки есть</b> — две планки ножек микроконтроллера. Без них провода
      подключать некуда, а плат с уже распаянными ножками с доставкой «завтра» и отзывами
      в наличии не оказалось (они едут 3–7 дней).</li>
  <li><b>Слабое место сборки</b> — стык проводов отсека с платой зарядки: винтовая колодка держит
      крепко, но если хочется совсем надёжно, эти четыре точки стоит пропаять.</li>
  <li><b>Код написан, но на живом железе не проверен</b> — платы пока нет. Скажи, когда приедет, —
      зальём прошивку и поправим то, что не сойдётся.</li>
  <li><b>Первая прошивка требует компьютера</b> с USB и драйвером USB-COM.</li>
  <li><b>Bluetooth работает в упор</b> — 5–10 м в комнате.</li>
</ul>

<footer>
  Цены, наличие и отзывы — Ozon, {PRICE_DATE}, фильтр «доставка завтра». Товары без отзывов
  или с плохими оценками в список не включались. Фотографии принадлежат продавцам Ozon и приведены
  со ссылками на страницы товаров. Прошивки написаны под эти платы; проверка на живом модуле —
  после покупки.
</footer>
"""

HTML = ('<!DOCTYPE html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Bluetooth-дисплей на аккумуляторе своими руками — сборка почти без пайки</title>\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n<div class="wrap">\n' + BODY +
        '\n</div>\n</body>\n</html>\n')

if __name__ == "__main__":
    svg = (BASE / "bt_schematic.svg").read_text(encoding="utf-8")
    wiring = (BASE / "bt_wiring.svg").read_text(encoding="utf-8")
    out = (HTML.replace("{SVG_SCHEMA}", svg)
                 .replace("{SVG_WIRING}", wiring)
                 .replace("{OPT_BRD_TITLE}", OPT["brd"]["title"])
                 .replace("{OPT_BRD_PRICE}", str(OPT["brd"]["price"]))
                 .replace("{OPT_BRD_RATING}", str(OPT["brd"]["rating"]))
                 .replace("{OPT_BRD_REVIEWS}", f'{OPT["brd"]["reviews"]:,}'.replace(",", "\u00a0"))
                 .replace("{OPT_BRD_NOTE}", OPT["brd"]["note"]))
    (BASE / "bt-display.html").write_text(out, encoding="utf-8")
    print(f"bt-display.html записан: {len(out):,} байт | позиций {len(BUILD)} | итого {money(TOTAL)} ₽")

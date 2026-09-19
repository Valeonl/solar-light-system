#!/usr/bin/env python3
"""Собирает страницу проекта «солнечная панель + АКБ + лампа (без пайки)».

Читает items_final.json (товары с Ozon) и расчётные константы,
пишет index.html рядом со скриптом. Картинки товаров кладутся в img/.

    python build.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
import math
import pathlib

BASE = pathlib.Path(__file__).parent
ITEMS = json.loads((BASE / "items_final.json").read_text(encoding="utf-8"))

# ---------------------------------------------------------------- расчётные допущения
LAMP_W = 5.0                 # мощность лампы, Вт
DARK_AUTUMN_H = 12.0         # часов темноты в сентябре–октябре
DARK_WINTER_H = 17.0         # часов темноты в декабре
TRAKT_EFF = 0.70             # КПД тракта: PWM-контроллер, нагрев, угол, пыль
AGM_DOD = 0.50               # допустимая глубина разряда свинцового АКБ
BATTERY_AH = 7               # выбранная ёмкость, А·ч (реально доступная с доставкой ≤7 дней)
PANEL_W = 30                 # выбранная мощность панели, Вт
PRICE_DATE = dt.date.today().strftime("%d.%m.%Y")


def calc() -> dict:
    """Все числа страницы. Режим «по таймеру» — лампа горит 6 ч после заката,
    режим «всю ночь» — всю темноту. Считаем оба, потому что выбор режима и есть
    то, что делает бюджетную систему работоспособной."""
    e_timer = LAMP_W * 6                     # 6 часов после заката
    e_autumn = LAMP_W * DARK_AUTUMN_H        # вся осенняя ночь
    e_winter = LAMP_W * DARK_WINTER_H        # вся декабрьская ночь
    usable = 12 * BATTERY_AH * AGM_DOD

    rows_batt = []
    for ah in (7, 12, 18, 24):
        u = 12 * ah * AGM_DOD
        rows_batt.append({"ah": ah, "usable": u,
                          "timer": u / e_timer, "autumn": u / e_autumn, "winter": u / e_winter})

    # сколько панель реально соберёт за день: мощность × солнечные часы × КПД
    seasons = (("Июнь (5 ч солнца)", 5.0), ("Сентябрь–октябрь (2,5 ч)", 2.5), ("Декабрь (0,8 ч)", 0.8))
    panel_rows = []
    for label, sun_h in seasons:
        harvest = PANEL_W * sun_h * TRAKT_EFF
        panel_rows.append({"label": label, "harvest": harvest,
                           "hours_lamp": harvest / LAMP_W,
                           "covers_timer": harvest >= e_timer,
                           "covers_autumn": harvest >= e_autumn})

    need_autumn = e_timer / TRAKT_EFF
    fuse = math.ceil(PANEL_W / 12 * 1.5 / 5) * 5
    return {
        "e_timer": e_timer, "e_autumn": e_autumn, "e_winter": e_winter, "usable": usable,
        "autonomy_timer": usable / e_timer, "autonomy_autumn": usable / e_autumn,
        "autonomy_winter": usable / e_winter, "batt_rows": rows_batt, "panel_rows": panel_rows,
        "need_autumn": need_autumn, "fuse": fuse, "panel_a": PANEL_W / 12, "lamp_a": LAMP_W / 12,
        "harvest_autumn": PANEL_W * 2.5 * TRAKT_EFF, "harvest_winter": PANEL_W * 0.8 * TRAKT_EFF,
        "harvest_summer": PANEL_W * 5.0 * TRAKT_EFF,
    }


C = calc()
TOTAL = sum(i["price"] for i in ITEMS)


def rating_html(i: dict) -> str:
    """Строка отзывов под картинкой: «★4.9 · 286 отзывов»."""
    r, n = i.get("rating"), i.get("reviews")
    if not r or not n:
        return ""
    word = "отзыв" if n % 10 == 1 and n % 100 != 11 else ("отзыва" if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else "отзывов")
    return f'<div class="rating">★{r:.1f} · {n:,}'.replace(",", "\u00a0") + f' {word}</div>'


def money(n: int) -> str:
    """Русский формат: 3368 → «3 368»."""
    return f"{n:,}".replace(",", "\u00a0")


def item_card(i: dict) -> str:
    img = html.escape(i.get("img_local") or "")
    return f"""
      <article class="card">
        <div class="card-img"><img src="{img}" alt="{html.escape(i['title'][:80])}"></div>
        {rating_html(i)}
        <div class="card-body">
          <span class="role">{html.escape(i['role'])}</span>
          <h3>{html.escape(i['title'])}</h3>
          <p class="specs">{html.escape(i.get('specs', ''))}</p>
          <p class="note">{html.escape(i.get('note', ''))}</p>
          <div class="row">
            <span class="price">{money(i['price'])} ₽</span>
            <span class="days">доставка {i.get('delivery') or str(i.get('days')) + ' дн.'}</span>
          </div>
          <a class="btn" href="{html.escape(i['url'])}" target="_blank" rel="noopener">Открыть на Ozon</a>
        </div>
      </article>"""


def item_row(i: dict) -> str:
    return (f"<tr><td>{html.escape(i['role'])}</td><td>{html.escape(i['title'][:70])}</td>"
            f"<td class='num'>{money(i['price'])} ₽</td>"
            f"<td class='num'>{html.escape(str(i.get('delivery') or ''))}</td></tr>")


batt_rows = "\n".join(
    f"<tr><td class='num'>{r['ah']}</td><td class='num'>{r['usable']:.0f}</td>"
    f"<td class='num{' good' if r['timer'] >= 1 else ''}'>{r['timer']:.1f}</td>"
    f"<td class='num{' good' if r['autumn'] >= 1 else ' bad'}'>{r['autumn']:.1f}</td>"
    f"<td class='num'>{r['winter']:.1f}</td></tr>" for r in C["batt_rows"])

panel_rows = "\n".join(
    f"<tr><td>{r['label']}</td><td class='num'>{r['harvest']:.0f}</td>"
    f"<td class='num'>{r['hours_lamp']:.1f} ч</td>"
    f"<td class='num{' good' if r['covers_timer'] else ' bad'}'>"
    f"{'да' if r['covers_timer'] else 'нет'}</td>"
    f"<td class='num{' good' if r['covers_autumn'] else ' bad'}'>"
    f"{'да' if r['covers_autumn'] else 'нет'}</td></tr>" for r in C["panel_rows"])

cards = "\n".join(item_card(i) for i in ITEMS)
rows = "\n".join(item_row(i) for i in ITEMS)

HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Автономный свет на солнечной панели — сборка без пайки</title>
<style>
  :root{{
    --bg:#0b1220; --panel:#111827; --panel2:#0f172a; --line:#1f2937; --line2:#334155;
    --fg:#e5e7eb; --muted:#94a3b8; --accent:#f59e0b; --good:#22c55e; --bad:#ef4444;
    --radius:14px;
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--fg);
    font:16px/1.6 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif}}
  a{{color:var(--accent)}}
  .wrap{{max-width:1080px;margin:0 auto;padding:32px 20px 80px}}
  header.hero{{border-bottom:1px solid var(--line);padding-bottom:24px;margin-bottom:36px}}
  h1{{font-size:clamp(26px,4vw,40px);line-height:1.15;margin:0 0 12px}}
  .lead{{color:var(--muted);font-size:18px;max-width:70ch}}
  h2{{font-size:clamp(20px,2.6vw,26px);margin:56px 0 16px;padding-bottom:8px;
    border-bottom:1px solid var(--line)}}
  h3{{font-size:17px;margin:0 0 6px;line-height:1.3}}
  p{{margin:10px 0}}
  .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:24px 0}}
  .kpi{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:16px}}
  .kpi b{{display:block;font-size:24px;color:var(--accent);line-height:1.2}}
  .kpi span{{color:var(--muted);font-size:13.5px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px;margin:20px 0}}
  .card{{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    overflow:hidden;display:flex;flex-direction:column}}
  .card-img{{background:#fff;aspect-ratio:1/1;display:flex;align-items:center;justify-content:center}}
  .card-img img{{width:100%;height:100%;object-fit:contain}}
  .card-body{{padding:14px;display:flex;flex-direction:column;gap:6px;flex:1}}
  .role{{display:inline-block;background:var(--panel2);border:1px solid var(--line2);color:var(--muted);
    font-size:12px;padding:2px 8px;border-radius:999px;align-self:flex-start}}
  .specs{{color:var(--fg);font-size:14px;margin:0}}
  .note{{color:var(--muted);font-size:13px;margin:0}}
  .row{{display:flex;justify-content:space-between;align-items:baseline;margin-top:auto;gap:8px}}
  .price{{font-size:20px;font-weight:700}}
  .days{{color:var(--muted);font-size:13px;text-align:right}}
  .btn{{display:block;text-align:center;background:var(--accent);color:#111827;font-weight:600;
    text-decoration:none;padding:9px 12px;border-radius:10px;margin-top:10px}}
  .btn:hover{{filter:brightness(1.08)}}
  table{{width:100%;border-collapse:collapse;margin:18px 0;font-size:14.5px}}
  th,td{{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}}
  th{{background:var(--panel2);color:var(--muted);font-weight:600}}
  td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
  tr.total td{{background:var(--panel);font-weight:700;font-size:16px}}
  .good{{color:var(--good)}} .bad{{color:var(--bad)}}
  .box{{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
    border-radius:10px;padding:14px 16px;margin:18px 0}}
  .warn{{border-left-color:var(--bad)}}
  .ok{{border-left-color:var(--good)}}
  ol.steps{{counter-reset:s;list-style:none;padding:0}}
  ol.steps li{{counter-increment:s;position:relative;padding:14px 16px 14px 58px;margin:10px 0;
    background:var(--panel);border:1px solid var(--line);border-radius:12px}}
  ol.steps li::before{{content:counter(s);position:absolute;left:16px;top:14px;width:28px;height:28px;
    border-radius:50%;background:var(--accent);color:#111827;font-weight:700;display:flex;
    align-items:center;justify-content:center;font-size:14px}}
  figure{{margin:22px 0}}
  figure svg{{width:100%;height:auto;border:1px solid var(--line);border-radius:var(--radius)}}
  figcaption{{color:var(--muted);font-size:13.5px;margin-top:8px}}
  code{{background:var(--panel2);border:1px solid var(--line);border-radius:6px;padding:1px 6px;font-size:14px}}
  footer{{margin-top:64px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13.5px}}
  @media (max-width:600px){{ .wrap{{padding:22px 14px 60px}} table{{font-size:13px}} }}
</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <h1>Автономный свет: солнечная панель → аккумулятор → лампа</h1>
  <p class="lead">Днём панель заряжает аккумулятор, вечером лампа загорается сама — по фотореле.
  Никакой пайки: все соединения на винтовых клеммах и болтах. Цены и сроки доставки — Ozon,
  на {PRICE_DATE}.</p>
  <div class="kpis">
    <div class="kpi"><b>{money(TOTAL)} ₽</b><span>весь комплект по этому списку</span></div>
    <div class="kpi"><b>{LAMP_W:.0f} Вт</b><span>лампа; 6 часов после заката = {C['e_timer']:.0f} Вт·ч в сутки</span></div>
    <div class="kpi"><b>{C['autonomy_timer']:.1f} сут</b><span>автономия на АКБ {BATTERY_AH} А·ч в режиме 6 часов</span></div>
    <div class="kpi"><b>{PANEL_W} Вт</b><span>панель даёт {C['harvest_autumn']:.0f} Вт·ч в сутки в сентябре–октябре</span></div>
  </div>
</header>

<div class="box ok">
  <b>Есть бюджетный вариант.</b> Если задача — просто «свет включается сам при темноте»
  и бюджет до 1000 ₽, посмотрите <a href="budget.html"><b>готовые светильники на солнечной батарее
  от 132 ₽</b></a> — там та же функция без сборки и за меньшие деньги.
</div>

<div class="box">
  <b>Другие проекты на этом сайте:</b>
  <a href="budget.html">бюджетный свет до 1000 ₽</a> ·
  <a href="bt-display.html">Bluetooth-дисплей на аккумуляторе: экран, 18650 и зарядка (1 483 ₽, доставка завтра)</a>
</div>

<h2>Как это работает</h2>
<ol>
  <li><b>Солнечная панель</b> — 12 В, отдаёт ток, когда на неё падает свет.</li>
  <li><b>Контроллер заряда (PWM)</b> — держит напряжение в безопасных для аккумулятора пределах
      и не даёт энергии уходить обратно в панель ночью. В выбранном комплекте панели он уже есть,
      отдельно покупать не нужно.</li>
  <li><b>Аккумулятор 12 В</b> — накапливает заряд, вечером отдаёт его лампе.</li>
  <li><b>Фотореле 12 В</b> — датчик освещённости: стемнело — замкнуло цепь, рассвело — разомкнуло.</li>
  <li><b>Лампа 12 В</b> — светит всю ночь, не потребляя 220 В.</li>
</ol>
<p>Ключевая деталь для «горит, когда уходит солнце» — <b>фотореле</b> (или режим светоконтроля
в самом контроллере, если он его поддерживает). Фотореле ставится в разрыв плюсового провода
нагрузки и работает как автоматический выключатель по освещённости.</p>

<figure>
  {{SVG_SCHEMA}}
  <figcaption>Схема: панель и аккумулятор идут на контроллер, контроллер отдаёт нагрузку через фотореле на лампу.</figcaption>
</figure>

<h2>Расчёт мощностей</h2>
<p>Исходные данные: лампа <b>{LAMP_W:.0f} Вт</b>, темнота осенью <b>{DARK_AUTUMN_H:.0f} ч</b>,
зимой <b>{DARK_WINTER_H:.0f} ч</b>; КПД всего тракта (контроллер, нагрев, угол, пыль) <b>{TRAKT_EFF:.0%}</b>;
для свинцового АКБ берём разряд не глубже <b>{AGM_DOD:.0%}</b>.</p>

<h3>1. Сколько энергии съедает лампа</h3>
<table>
  <tr><th>Режим лампы</th><th>Сколько горит</th><th>Расход за сутки</th></tr>
  <tr><td><b>По таймеру</b> (рекомендуемый)</td><td class="num">6 ч после заката</td><td class="num">{C['e_timer']:.0f} Вт·ч</td></tr>
  <tr><td>Всю ночь, сентябрь–октябрь</td><td class="num">{DARK_AUTUMN_H:.0f} ч</td><td class="num">{C['e_autumn']:.0f} Вт·ч</td></tr>
  <tr><td>Всю ночь, декабрь</td><td class="num">{DARK_WINTER_H:.0f} ч</td><td class="num">{C['e_winter']:.0f} Вт·ч</td></tr>
</table>
<p>Режим задаётся на контроллере (у большинства ШИМ-моделей есть «светоконтроль» и таймер
2/4/6/8 часов). Именно этот выбор делает систему на 7-амперном аккумуляторе рабочей:
за 6 часов лампа съедает {C['e_timer']:.0f} Вт·ч, а не {C['e_autumn']:.0f}.</p>

<h3>2. Какая нужна ёмкость аккумулятора</h3>
<p>Полезная ёмкость = 12 В × А·ч × {AGM_DOD:.0%}. «Автономия» — на сколько суток хватит
заряженного аккумулятора без всякого солнца.</p>
<table>
  <tr><th>Ёмкость, А·ч</th><th>Полезно, Вт·ч</th><th>Автономия, режим 6 ч</th><th>Автономия, вся ночь осенью</th><th>Автономия в декабре</th></tr>
  {batt_rows}
</table>

<h3>3. Какая нужна панель</h3>
<p>Считаем честно: панель {PANEL_W} Вт × число «солнечных часов» × КПД тракта {TRAKT_EFF:.0%}.
Солнечные часы — это время, когда панель выдаёт близкую к паспортной мощность. Для
Санкт-Петербурга это примерно 5 ч в июне, 2,5 ч в сентябре–октябре и всего 0,8 ч в декабре.</p>
<table>
  <tr><th>Сезон</th><th>Соберёт за сутки</th><th>Хватит лампе на</th><th>Покрывает режим 6 ч</th><th>Покрывает всю ночь</th></tr>
  {panel_rows}
</table>
<p>Читается это так: с сентября по апрель панели <b>хватает</b> на режим «6 часов после заката»,
а всю ночь на 5-ваттной лампе она вытягивает только в светлое время года.</p>
<div class="box warn">
  <b>Честно про декабрь.</b> В декабре в Петербурге панель {PANEL_W} Вт соберёт всего
  около {C['harvest_winter']:.0f} Вт·ч в сутки — это {C['harvest_winter'] / LAMP_W:.1f} часа работы лампы.
  Остальное надо либо взять из аккумулятора (он начнёт постепенно разряжаться), либо дозаряжать
  аккумулятор от сети раз в неделю. С марта по октябрь такой системы хватает с запасом,
  летом аккумулятор будет заряжаться быстрее, чем разряжаться.
</div>

<h3>4. Токи и защита</h3>
<table>
  <tr><th>Участок</th><th>Ток</th><th>Защита</th></tr>
  <tr><td>Панель {PANEL_W} Вт → контроллер</td><td class="num">{C['panel_a']:.1f} А</td>
      <td>предохранитель {C['fuse']} А в плюсовом проводе у аккумулятора</td></tr>
  <tr><td>Лампа {LAMP_W:.0f} Вт</td><td class="num">{C['lamp_a']:.2f} А</td>
      <td>достаточно предохранителя 2 А</td></tr>
  <tr><td>Контроллер</td><td class="num">до 10 А</td><td>берём с запасом по току и напряжению 12/24 В</td></tr>
</table>

<h2>Список товаров</h2>
<p>Всё найдено на Ozon с фильтром <b>«доставка до 7 дней»</b> — то, что реально придёт на этой неделе.
Цены — на момент сборки страницы, они меняются каждый день.</p>
<div class="grid">
{cards}
</div>

<h3>Смета</h3>
<table>
  <tr><th>Роль</th><th>Товар</th><th>Цена</th><th>Доставка</th></tr>
  {rows}
  <tr class="total"><td colspan="2">Итого</td><td class="num">{money(TOTAL)} ₽</td><td></td></tr>
</table>

<h2>Сборка без пайки — по шагам</h2>
<ol class="steps">
  <li><b>Подготовь место.</b> Сухая полка или ящик рядом с окном/на балконе. Аккумулятор — не на
      морозе и не в сырости: свинцовому AGM комфортно при 10–25 °C, на холоде он теряет ёмкость.</li>
  <li><b>Разложи провода до подключения.</b> Панель и аккумулятор должны быть отключены —
      собираем «на сухую», проверяя, что провода дотягиваются до клемм.</li>
  <li><b>Аккумулятор → контроллер.</b> Сначала минус, потом плюс. Провод от АКБ зачисти на 8–10 мм,
      вставь в клемму <code>BAT</code> и затяни винт. Никакой пайки: винтовой зажим держит
      надёжнее, чем скрутка. К самому аккумулятору провод цепляется крокодилами из списка;
      если клеммы АКБ плоские (как у батарей для ИБП) — вместо крокодилов удобнее взять
      разъёмы «мама» 6,3 мм, комплект стоит около 97 ₽.</li>
  <li><b>В плюсовом проводе от аккумулятора поставь предохранитель {C['fuse']} А</b> — держатель
      с винтовыми зажимами или колодку с предохранителем. Это защита от короткого замыкания.</li>
  <li><b>Панель → контроллер.</b> Клеммы <code>PV+</code> и <code>PV−</code>. Панель на солнце
      сразу даёт напряжение, поэтому её подключают последней и обязательно с соблюдением полярности.</li>
  <li><b>Лампа → фотореле → контроллер.</b> Плюс с клеммы <code>LOAD+</code> идёт на вход фотореле,
      с выхода фотореле — на патрон лампы. Минус идёт напрямую с <code>LOAD−</code> на второй провод
      патрона. Все соединения — в клеммных колодках.</li>
  <li><b>Настрой режим контроллера.</b> Кнопками на контроллере выбери режим нагрузки:
      «светоконтроль» (включение по темноте) и таймер <b>6 часов</b>. Если оставить «всегда
      включено», лампа будет гореть и днём, а аккумулятор разрядится за одну ночь.
      Пара «светоконтроль + 6 ч» — это и есть «горит, когда уходит солнце».</li>
  <li><b>Проверь и включи.</b> Убедись, что нигде нет перепутанных полюсов. Контроллер включится
      и покажет напряжение аккумулятора. Прикрой фотореле рукой или накрой коробкой — лампа
      должна загореться через несколько секунд. Открыл — гаснет.</li>
  <li><b>Закрепи и спрячь от воды.</b> Панель — под углом к солнцу (в Петербурге лучше
      на юг и под углом ~45°), контроллер и аккумулятор — в сухом боксе, провода — в гофре
      или кабель-канале.</li>
  <li><b>Отключение — в обратном порядке:</b> сначала панель, потом нагрузка, в конце аккумулятор.
      Так контроллер и аккумулятор не пострадают.</li>
</ol>

<div class="box warn">
  <b>Три ошибки, которые убивают систему.</b>
  Первая — перепутать плюс и минус: контроллер выходит из строя сразу, проверяй дважды.
  Вторая — оставлять аккумулятор разряженным «в ноль»: свинцовый АКБ от глубокого разряда
  теряет ёмкость навсегда, поэтому разряжать его больше чем наполовину нельзя, а на зиму
  лучше дозаряжать от сети. Третья — ставить панель и контроллер под дождь: панель герметична,
  а вот электроника и клеммы — нет.
</div>

<h2>Эксплуатация</h2>
<table>
  <tr><th>Что</th><th>Как часто</th><th>Зачем</th></tr>
  <tr><td>Протереть панель</td><td>раз в 1–2 недели</td><td>пыль и снег срезают выработку на 20–40%</td></tr>
  <tr><td>Проверить напряжение АКБ</td><td>раз в месяц</td><td>ниже 11,8 В под нагрузкой — пора дозарядить</td></tr>
  <tr><td>Протянуть винты клемм</td><td>раз в сезон</td><td>винтовые соединения со временем ослабевают</td></tr>
  <tr><td>Дозарядить АКБ от сети</td><td>в декабре–январе</td><td>солнца физически не хватает, АКБ иначе засульфатируется</td></tr>
</table>

<h2>Что улучшить, когда захочешь больше</h2>
<ul>
  <li><b>Второй такой же аккумулятор</b> ({BATTERY_AH} А·ч) параллельно первому — тогда лампа
      сможет гореть всю ночь, а не 6 часов: ёмкость станет {BATTERY_AH * 2} А·ч, полезно
      {12 * BATTERY_AH * 2 * AGM_DOD:.0f} Вт·ч. Соединять однотипные АКБ: плюс к плюсу, минус к минусу,
      провода одинаковой длины.</li>
  <li><b>Вторая панель</b> ({PANEL_W}+{PANEL_W} Вт) — вдвое больше выработки, зимой заметнее всего.</li>
  <li><b>MPPT-контроллер вместо PWM</b> — те же панели дают на 10–30% больше энергии, но дороже.</li>
  <li><b>LiFePO4 вместо AGM</b> — можно разряжать до 90%, легче и живёт в разы дольше;
      дороже в 2–3 раза, но при ежедневной работе окупается.</li>
  <li><b>Контроллер с режимом «светоконтроль»</b> — тогда отдельное фотореле не нужно, но такие
      модели чаще приходят с долгой доставкой.</li>
</ul>

<footer>
  Цены и наличие — Ozon, {PRICE_DATE}, фильтр «доставка до 7 дней». Фотографии товаров принадлежат
  продавцам на Ozon и приведены здесь как иллюстрации к конкретным позициям со ссылками на страницы
  товаров. Расчёты сделаны для лампы {LAMP_W:.0f} Вт и Санкт-Петербурга; для другого города
  цифры по панели изменятся (нужно своё число солнечных часов).
</footer>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    svg = (BASE / "schematic.svg").read_text(encoding="utf-8")
    svg = svg.replace('<svg ', '<svg style="display:block" ', 1)
    out = HTML.replace("{SVG_SCHEMA}", svg)
    (BASE / "index.html").write_text(out, encoding="utf-8")
    print(f"index.html записан: {len(out):,} байт, товаров {len(ITEMS)}, итого {money(TOTAL)} ₽")

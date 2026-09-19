#!/usr/bin/env python3
"""Собирает страницу бюджетного варианта (budget.html): свет до 1000 ₽.

Читает budget_items.json — товары и детали с Ozon, проверенные фильтром
«доставка до 7 дней». Пишет budget.html рядом со скриптом.

    python budget.py
"""

from __future__ import annotations

import json
import pathlib

BASE = pathlib.Path(__file__).parent
D = json.loads((BASE / "budget_items.json").read_text(encoding="utf-8"))

READY = D["ready"]      # готовые светильники
DIY = D["diy"]          # детали самодельного мини-набора
PRICE_DATE = D["date"]


def money(n: int) -> str:
    return f"{n:,}".replace(",", "\u00a0")


# ---------------------------------------------------------------- расчёты
LAMP_NO = 3                                     # сколько садовых светильников
READY_TOTAL = READY[0]["price"] * LAMP_NO
DIY_TOTAL = sum(i["price"] for i in DIY)
DIY_NO_WIRES = DIY_TOTAL - next(i["price"] for i in DIY if i["key"] == "wires")

# мини-система: панель 1 Вт, 18650 2200 мА·ч, один светодиод
PANEL_W = 1.0
SUN_H = 2.5
EFF = 0.70
CELL_WH = 3.7 * 2.2                            # 18650 2200 мА·ч
LED_W = 0.25
LED_H = 6.0
harvest = PANEL_W * SUN_H * EFF
spend = LED_W * LED_H


def card(i: dict, badge: str = "") -> str:
    img = i.get("img_local") or ""
    return f"""
      <article class="card">
        <div class="card-img"><img src="{img}" alt=""></div>
        <div class="card-body">
          <span class="role">{badge or i.get('role','')}</span>
          <h3>{i['title']}</h3>
          <p class="specs">{i.get('specs','')}</p>
          <p class="note">{i.get('note','')}</p>
          <div class="row"><span class="price">{money(i['price'])} ₽</span>
            <span class="days">доставка {i['days']} дн.</span></div>
          <a class="btn" href="{i['url']}" target="_blank" rel="noopener">Открыть на Ozon</a>
        </div>
      </article>"""


cards_ready = "\n".join(card(r) for r in READY)
diy_rows = "\n".join(
    f"<tr><td>{i['role']}</td><td>{i['title'][:66]}</td><td class='num'>{money(i['price'])} ₽</td>"
    f"<td class='num'>{i['days']} дн.</td></tr>" for i in DIY)

variants = "\n".join(
    f"<tr><td class='num'>{n}</td><td class='num'>{money(READY[0]['price'] * n)} ₽</td>"
    f"<td>{'хватит на дорожку к дому' if n <= 3 else 'двор или дачный участок'}</td></tr>"
    for n in (1, 2, 3, 5, 7))

HTML = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Бюджетный автономный свет до 1000 ₽ — садовые светильники на солнечной батарее</title>
<style>
  :root{{--bg:#0b1220;--panel:#111827;--panel2:#0f172a;--line:#1f2937;--line2:#334155;
    --fg:#e5e7eb;--muted:#94a3b8;--accent:#22c55e;--good:#22c55e;--bad:#ef4444;--radius:14px}}
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
  .btn{{display:block;text-align:center;background:var(--accent);color:#06210f;font-weight:600;
    text-decoration:none;padding:9px 12px;border-radius:10px;margin-top:10px}}
  table{{width:100%;border-collapse:collapse;margin:18px 0;font-size:14.5px}}
  th,td{{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}}
  th{{background:var(--panel2);color:var(--muted);font-weight:600}}
  td.num{{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}}
  tr.total td{{background:var(--panel);font-weight:700}}
  .good{{color:var(--good)}} .bad{{color:var(--bad)}}
  .box{{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);
    border-radius:10px;padding:14px 16px;margin:18px 0}}
  .warn{{border-left-color:var(--bad)}}
  ol.steps{{counter-reset:s;list-style:none;padding:0}}
  ol.steps li{{counter-increment:s;position:relative;padding:12px 16px 12px 54px;margin:10px 0;
    background:var(--panel);border:1px solid var(--line);border-radius:12px}}
  ol.steps li::before{{content:counter(s);position:absolute;left:15px;top:12px;width:26px;height:26px;border-radius:50%;
    background:var(--accent);color:#06210f;font-weight:700;display:flex;align-items:center;justify-content:center;font-size:14px}}
  footer{{margin-top:60px;padding-top:20px;border-top:1px solid var(--line);color:var(--muted);font-size:13.5px}}
  @media (max-width:600px){{.wrap{{padding:22px 14px 60px}}table{{font-size:13px}}}}
</style>
</head>
<body>
<div class="wrap">

<a class="back" href="index.html">← Полный вариант (3 368 ₽, панель 30 Вт, аккумулятор 7 А·ч)</a>

<h1>Бюджетный вариант: свет, который включается сам — до 1000 ₽</h1>
<p class="lead">Те же условия: никакой пайки, доставка до 7 дней, лампа загорается при темноте.
Только вместо сборки из панели, контроллера и аккумулятора берём готовые светильники на
солнечной батарее: внутри у них уже есть всё то же самое — панель, аккумулятор, датчик темноты
и светодиод.</p>

<div class="kpis">
  <div class="kpi"><b>{money(READY_TOTAL)} ₽</b><span>{LAMP_NO} садовых светильника на солнечной батарее</span></div>
  <div class="kpi"><b>{money(READY[0]['price'])} ₽</b><span>цена одного светильника — дешевле любой сборки</span></div>
  <div class="kpi"><b>0 ₽</b><span>инструментов и проводов — ничего лишнего</span></div>
  <div class="kpi"><b>{money(DIY_TOTAL)} ₽</b><span>если собирать мини-набор своими руками — дороже</span></div>
</div>

<h2>Два пути — и почему я рекомендую первый</h2>
<table>
  <tr><th>Путь</th><th>Что покупаешь</th><th>Итого</th><th>Сборка</th><th>Минусы</th></tr>
  <tr>
    <td><b>Готовые светильники</b><br><span class="good">рекомендую</span></td>
    <td>{LAMP_NO} садовых светильника на солнечной батарее</td>
    <td class="num">{money(READY_TOTAL)} ₽</td>
    <td>воткнуть в землю</td>
    <td>один светодиод на штуку, свет декоративный, а не «чтобы читать»</td>
  </tr>
  <tr>
    <td><b>Мини-набор своими руками</b></td>
    <td>панель {PANEL_W:.0f} Вт, аккумулятор 18650, плата зарядки, датчик света, реле, светодиод, провода</td>
    <td class="num">{money(DIY_TOTAL)} ₽</td>
    <td>соединять по схеме, разбираться с реле</td>
    <td>дороже готового, требует аккуратности и понимания; часть деталей без проводов-перемычек не соединить</td>
  </tr>
</table>
<div class="box">
  <b>Главная мысль.</b> Готовый садовый светильник за {money(READY[0]['price'])} ₽ — это ровно то,
  что мы собирали в полном варианте, только в одном корпусе и в сто раз дешевле: панель,
  аккумулятор, датчик темноты и светодиод уже внутри, а производитель сделал миллион таких.
  Собирать это из отдельных деталей дороже и дольше. Самоделка имеет смысл только тогда,
  когда нужна своя мощность, свой размер или лампа внутри дома.
</div>

<h2>Путь 1: готовые светильники</h2>
<div class="grid">
{cards_ready}
</div>

<h3>Сколько взять, чтобы остаться в тысяче</h3>
<table>
  <tr><th>Штук</th><th>Итого</th><th>Куда хватит</th></tr>
  {variants}
</table>
<p>Каждый светильник работает автономно: днём панель заряжает встроенный аккумулятор,
с наступлением темноты светодиод включается сам, утром гаснет. Ни проводов, ни розетки,
ни настройки — только воткнуть в землю или прикрутить к стене.</p>

<h2>Путь 2: если хочется собрать самому — честная смета</h2>
<p>Считаю по тем же правилам: все позиции с доставкой до 7 дней, соединения — разъёмы и винтовые
клеммы, без паяльника.</p>
<table>
  <tr><th>Роль</th><th>Деталь</th><th>Цена</th><th>Доставка</th></tr>
  {diy_rows}
  <tr class="total"><td colspan="2">Итого</td><td class="num">{money(DIY_TOTAL)} ₽</td><td></td></tr>
</table>
<div class="box warn">
  <b>Что тут честно сказать.</b> Без проводов-перемычек набор стоит {money(DIY_NO_WIRES)} ₽ —
  в тысячу влезает. С ними — {money(DIY_TOTAL)} ₽, то есть <b>дороже трёх готовых светильников</b>
  ({money(READY_TOTAL)} ₽). Плюс есть два подводных камня, которых нет у готового изделия:
  модуль реле на 5 В от аккумулятора 3,7 В может не срабатывать (нужен либо 3-вольтовый,
  либо питание от двух элементов), а панель на 1 Вт даёт очень мало — зимой почти ничего.
  Если цель — «дешёвый свет, который включается сам», первый путь объективно лучше.
</div>

<h2>Расчёт мини-набора: сколько он реально может</h2>
<table>
  <tr><th>Что считаем</th><th>Формула</th><th>Результат</th></tr>
  <tr><td>Соберёт панель {PANEL_W:.0f} Вт за день</td>
      <td class="num">{PANEL_W:.0f} Вт × {SUN_H} ч × {EFF:.0%}</td><td class="num">{harvest:.1f} Вт·ч</td></tr>
  <tr><td>Запас в аккумуляторе 18650 (2200 мА·ч)</td>
      <td class="num">3,7 В × 2,2 А·ч</td><td class="num">{CELL_WH:.1f} Вт·ч</td></tr>
  <tr><td>Съест один светодиод за ночь</td>
      <td class="num">{LED_W} Вт × {LED_H:.0f} ч</td><td class="num">{spend:.1f} Вт·ч</td></tr>
  <tr class="total"><td>Вывод</td><td colspan="2" class="good">
      панели хватает на {harvest / spend:.1f} ночи работы одного светодиода — мини-набор
      работоспособен, но это свет «на один диод», а не освещение комнаты</td></tr>
</table>
<p>У готового садового светильника параметры того же порядка: маленькая панель, аккумулятор
на несколько сотен мА·ч и один светодиод. Разница только в том, что там это уже собрано,
герметично и стоит в разы дешевле.</p>

<h2>Что выбрать</h2>
<ol class="steps">
  <li><b>Нужен свет вокруг дома или на даче</b> — бери {LAMP_NO} садовых светильника
      ({money(READY_TOTAL)} ₽) или семь штук на тысячу: {money(READY[0]['price'] * 7)} ₽. Ноль работы руками.</li>
  <li><b>Нужно ярче, чем декоративный светодиод</b> — уличный светильник-прожектор с пультом
      и датчиком движения за 660 ₽: светит заметно сильнее, питается от своей панели.</li>
  <li><b>Нужна лампа внутри дома</b> — это уже полный вариант с аккумулятором на 7 А·ч
      и низковольтной лампой: 3 368 ₽, <a href="index.html">страница с расчётом и схемой</a>.</li>
  <li><b>Просто хочется спаять/собрать самому</b> — смета выше {money(DIY_TOTAL)} ₽, будет дороже
      готового и с подводными камнями. Но если интересно именно собрать — это рабочий путь.</li>
</ol>

<footer>
  Цены и наличие — Ozon, {PRICE_DATE}, фильтр «доставка до 7 дней». Фотографии товаров
  принадлежат продавцам на Ozon и приведены со ссылками на страницы товаров.
  Расчёт для мини-набора сделан для панели {PANEL_W:.0f} Вт и Санкт-Петербурга
  ({SUN_H} ч солнца в сутки осенью, КПД тракта {EFF:.0%}).
</footer>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    (BASE / "budget.html").write_text(HTML, encoding="utf-8")
    print(f"budget.html записан: {len(HTML):,} байт | готовых светильников {len(READY)} | "
          f"деталей DIY {len(DIY)} | итог DIY {money(DIY_TOTAL)} ₽ | {LAMP_NO} светильника = {money(READY_TOTAL)} ₽")

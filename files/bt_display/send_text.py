#!/usr/bin/env python3
"""Отправить текст на Bluetooth-дисплей (Hermes-Display).

Работает по BLE, поэтому подходит и для отправки с ноутбука, и с телефона
(на телефоне — любым BLE-терминалом, например «nRF Connect» или «Serial Bluetooth
Terminal» в режиме BLE).

    pip install bleak
    python send_text.py "Привет, дисплей!"
    python send_text.py --scan          # посмотреть, какие BLE-устройства рядом
    python send_text.py --name My-Disp "текст"

Скрипт соединяется, пишет строку в характеристику RX (Nordic UART Service),
печатает ответ устройства и отключается.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    print("нужен пакет bleak: pip install bleak")
    raise SystemExit(2)

SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
CHAR_RX_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"   # сюда пишем текст
CHAR_TX_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"   # ответы устройства
DEFAULT_NAME = "Hermes-Display"


async def scan() -> None:
    print("ищу BLE-устройства 8 секунд…")
    devices = await BleakScanner.discover(timeout=8.0)
    if not devices:
        print("ничего не найдено — включён ли Bluetooth на этом компьютере?")
        return
    for d in devices:
        print(f"  {d.name or '(без имени)':24s} {d.address}")


async def send(name: str, text: str) -> int:
    print(f"ищу «{name}»…")
    device = await BleakScanner.find_device_by_filter(
        lambda d, adv: (d.name or "") == name or name.lower() in (d.name or "").lower(),
        timeout=15.0,
    )
    if device is None:
        print("устройство не найдено. Проверь, что дисплей включён и не подключён к телефону.")
        return 3

    got: list[str] = []

    def on_notify(_sender, data: bytearray) -> None:
        got.append(data.decode("utf-8", "replace"))

    async with BleakClient(device) as client:
        print("подключено:", device.address)
        try:
            await client.start_notify(CHAR_TX_UUID, on_notify)
        except Exception:
            pass  # не все прошивки отдают ответы — это не ошибка
        await client.write_gatt_char(CHAR_RX_UUID, text.encode("utf-8"), response=False)
        print("отправлено:", text)
        await asyncio.sleep(1.0)

    if got:
        print("ответ устройства:", " | ".join(got))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Отправка текста на Bluetooth-дисплей")
    ap.add_argument("text", nargs="?", help="текст для отправки")
    ap.add_argument("--scan", action="store_true", help="найти BLE-устройства рядом")
    ap.add_argument("--name", default=DEFAULT_NAME, help=f"имя устройства (по умолчанию {DEFAULT_NAME})")
    a = ap.parse_args()

    if a.scan:
        asyncio.run(scan())
        return 0
    if not a.text:
        ap.print_help()
        return 1
    return asyncio.run(send(a.name, a.text))


if __name__ == "__main__":
    sys.exit(main())

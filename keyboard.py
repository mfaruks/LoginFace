import time
import uinput

# Tüm gerekli tuşları başlangıçta tanımlıyoruz (0-9 ve A-F dahil)
keys = [
    uinput.KEY_LEFTCTRL,
    uinput.KEY_LEFTSHIFT,
    uinput.KEY_ENTER,
    uinput.KEY_U,
]

# Rakamları ekle
for i in range(10):
    keys.append(getattr(uinput, f"KEY_{i}"))

# Hex harfleri ekle (A-F)
for c in "ABCDEF":
    keys.append(getattr(uinput, f"KEY_{c}"))

# Cihazı oluştur
device = uinput.Device(keys)

# Sanal klavyenin ayağa kalkması için kısa bir bekleme
time.sleep(0.2)


def write_unicode(char, interval=0.005):
    """Linux Ctrl+Shift+U yöntemiyle, araya küçük bir interval koyarak yazar."""
    code = ord(char)
    hex_code = format(code, "x")

    # 1. Adım: Ctrl + Shift + U tuş kombinasyonunu başlat
    device.emit(uinput.KEY_LEFTCTRL, 1)
    device.emit(uinput.KEY_LEFTSHIFT, 1)
    device.emit(uinput.KEY_U, 1)
    device.emit(uinput.KEY_U, 0)
    device.emit(uinput.KEY_LEFTSHIFT, 0)
    device.emit(uinput.KEY_LEFTCTRL, 0)

    if interval:
        time.sleep(interval)

    # 2. Adım: Hex kodunu oluşturan karakterleri gönder
    for h in hex_code:
        upper_h = h.upper()
        key_code = getattr(uinput, f"KEY_{upper_h}")
        device.emit(key_code, 1)
        device.emit(key_code, 0)
        if interval:
            time.sleep(interval)

    # 3. Adım: Enter ile karakteri onaylayıp ekrana bastır
    device.emit(uinput.KEY_ENTER, 1)
    device.emit(uinput.KEY_ENTER, 0)
    
    if interval:
        time.sleep(interval)


def type_text(text, interval=0.005):
    """Metnin tamamını güvenli bir aralıkla UTF-8 olarak yazar."""
    for char in text:
        write_unicode(char, interval)

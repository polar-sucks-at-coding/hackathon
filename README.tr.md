# SAÜ Connect

[English](README.md) | **Türkçe**

Sakarya Üniversitesi (SAÜ) öğrencileri için bir kampüs platformu. Ders notlarını paylaş, yardım iste, projeler için takım arkadaşı bul ve diğer öğrencilerin profillerine göz at; hepsi tek bir yerde.

Arayüz Türkçedir. Uygulama, küçük bir Flask arka ucu tarafından sunulan tek sayfalık bir web uygulamasıdır. Tüm veriler düz dosyalarda tutulduğu için kurulması gereken bir veritabanı yoktur.

## Özellikler

**Notlar**
- Ders notlarını başlık, açıklama ve isteğe bağlı dosya eki (PDF vb.) ile paylaşma
- Notları beğenme / beğeniyi geri çekme ve ekleri indirme
- "Haftanın en iyi notları" bölümü
- Yazarlar kendi notlarını silebilir (ekli dosya da silinir)

**İstekler ve topluluk**
- Yardım ya da bilgi isteği paylaşma ve başkalarının yorum yapabilmesi
- Öğrenci rehberine göz atma ve profillerini açma

**Takımlar**
- Bir proje veya yarışma için (örneğin Teknofest) açıklama, aranan yetenekler ve hedef takım büyüklüğü ile takım oluşturma
- Diğer öğrenciler mesajlarıyla katılma isteği gönderir; takım sahibi kabul eder ya da reddeder
- Üyeler takımdan ayrılabilir, sahipler üyeleri çıkarabilir veya takımı silebilir
- Takım içi sohbet

**Profiller**
- Fakülte, bölüm, kısa biyografi ve profil fotoğrafı ile kayıt olma
- Herkese açık profil sayfalarında öğrencinin notları, istekleri ve takımları ile toplam not ve beğeni sayısı görünür

**Diğer**
- Kullanıcılar içerikleri şikayet edebilir
- İstemci sunucudaki değişiklikleri düzenli olarak sorgular, böylece listeler elle yenilemeye gerek kalmadan güncel kalır
- Tailwind CSS ile hazırlanmış koyu temalı, neumorfik arayüz

## Teknolojiler

- **Arka uç:** Python 3, [Flask](https://flask.palletsprojects.com/), flask-cors
- **Ön uç:** tek bir `index.html` (saf JavaScript, CDN üzerinden Tailwind CSS, Font Awesome, Google Fonts)
- **Depolama:** `data/` klasöründeki düz metin ve JSON dosyaları

## Başlarken

**Gereksinimler:** Python 3.9 veya üzeri.

```bash
git clone https://github.com/polar-sucks-at-coding/hackathon.git
cd hackathon

pip install flask flask-cors

python networking/server.py
```

Ardından tarayıcında <http://localhost:5000> adresini aç. Kayıt sekmesinden bir hesap oluşturup giriş yapabilirsin.

Sunucu `0.0.0.0:5000` üzerinde dinler; yani aynı ağdaki diğer cihazlar `http://<ip-adresin>:5000` adresinden erişebilir. Ön uç Tailwind, Font Awesome ve Google Fonts dosyalarını CDN'lerden yüklediği için sayfa ilk açıldığında internet bağlantısı gerekir.

## Proje yapısı

```
.
├── index.html                  # Tüm ön uç (arayüz + istemci tarafı mantık)
├── logo.jpeg
├── user_files/
│   ├── user.py                 # Kullanıcı modeli (kullanıcı adı + şifre)
│   └── user_profile.py         # Profil modeli (fakülte, bölüm, biyografi, fotoğraf, not ID'leri)
├── notes/
│   └── note.py                 # Not modeli
├── networking/
│   ├── server.py               # Flask sunucusu ve tüm API işleyicileri
│   └── server_interaction.py   # Eski Python soket istemcisi (aşağıdaki notlara bakın)
└── data/                       # Çalışma sırasında oluşturulur ve güncellenir
    ├── accounts.txt            # kullanıcı_adı|şifre
    ├── user_profiles.txt       # her kullanıcının profil bilgileri ve not ID'leri
    ├── notes.txt               # her satırda bir not
    ├── likes.txt               # kullanıcı_adı|not_id çiftleri
    ├── next_id.txt             # sıradaki not ID'si
    ├── requests.json           # yardım istekleri ve yorumlar
    ├── teams.json              # takımlar, katılma istekleri, sohbet mesajları
    ├── reports.json            # kullanıcı şikayetleri
    └── uploads/                # yüklenen not ekleri
```

## API

Sunucu `/` adresinde `index.html` dosyasını sunar ve tek bir uç nokta sunar: `POST /api/command`. İstek gövdesi, bir `command` alanı ve o komuta ait parametreleri içeren JSON'dır. Her yanıtta `success` veya `error` değerinde bir `status` alanı bulunur.

```bash
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "LOGIN", "username": "ayse", "password": "secret"}'
```

| Alan | Komutlar |
| --- | --- |
| Hesaplar | `REGISTER`, `LOGIN`, `LOGOUT`, `UPDATE_PROFILE`, `GET_ALL_USERS`, `GET_USER_PROFILE` |
| Notlar | `CREATE_NOTE`, `GET_NOTE`, `GET_ALL_NOTES`, `DELETE_NOTE`, `LIKE_NOTE`, `DOWNLOAD_FILE` |
| İstekler | `CREATE_REQUEST`, `GET_ALL_REQUESTS`, `DELETE_REQUEST`, `ADD_COMMENT` |
| Takımlar | `CREATE_TEAM`, `GET_ALL_TEAMS`, `JOIN_TEAM`, `ACCEPT_JOIN_REQUEST`, `REJECT_JOIN_REQUEST`, `LEAVE_TEAM`, `KICK_MEMBER`, `DELETE_TEAM`, `ADD_TEAM_MESSAGE` |
| Moderasyon | `CREATE_REPORT` |
| Senkronizasyon | `CHECK_UPDATES` (verinin son değiştiği zaman damgasını döndürür; istemci bunu düzenli olarak sorgular) |

Dosya yükleme ve indirme işlemleri, JSON içinde base64 olarak taşınır.

## Bilinen sınırlamalar

Bu proje bir hackathon çalışması olarak başladı ve henüz canlıya almaya hazır değil.

- **Şifreler düz metin olarak saklanıyor** (`data/accounts.txt`). Oturum ya da token yok; API, her istekle gönderilen `username` değerine güveniyor.
- **Depolama düz dosyalardır** ve her değişiklikte yeniden yazılır. Demo için yeterli, çok sayıda eşzamanlı kullanıcı için uygun değil.
- Değerler dikey çizgiyle (`|`) ayrılarak saklandığı için başlık veya not metnindeki bir `|` karakteri o satırı bozar.
- `data/` klasörü şu anda örnek veriler ve yüklenmiş dosyalar içeriyor. Gerçek bir dağıtımdan önce temizle.
- `networking/server_interaction.py`, artık HTTP sunucusuyla uyuşmayan, soket tabanlı eski bir istemcidir ve web uygulaması tarafından kullanılmaz.

## Sonraki adımlar için fikirler

- Şifreleri hash'leyip gerçek bir kimlik doğrulama eklemek (oturum veya JWT)
- Depolamayı SQLite veya PostgreSQL'e taşımak
- `requirements.txt` ve `__pycache__/` ile çalışma zamanı verileri için `.gitignore` eklemek
- Notlar için fakülte, bölüm veya derse göre arama ve filtreleme eklemek

## Lisans

Henüz bir lisans dosyası eklenmedi. Başkalarının kodu kullanmasını istiyorsan bir tane ekle.
## Geliştirici Ekip

- **Melih Ekinci**
- **Mehmet Yusuf Yöndem**

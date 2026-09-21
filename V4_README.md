# Fox Shorts Bot V4 — özgün çizgi film denemesi 🦊

V4 motoru `scripts/render_v4.py` dosyasına ChatGPT tarafından **doğrudan GitHub'a yüklendi**. Kullanıcının dosya yüklemesi veya bilgisayarına program kurması gerekmez. V3 dosyaları korunur.

## Tarayıcıda test videosu üret
1. [Actions → Render Fox Short V4 (Review Only)](https://github.com/averelliq/fox-shorts-bot/actions/workflows/render-v4.yml) sayfasını aç.
2. Gerekirse **Run workflow → Run workflow** seç. V4 kaynak kodu/senaryosu güncellenince de otomatik test çalışır.
3. Çalışma yeşile dönünce sayfanın altındaki **fox-short-v4-review** çıktı paketini indir. ZIP içinden `short.mp4` ile `metadata.json` çıkar.
4. İzleyerek karakter, akış, sesin İngilizcesi ve finali kontrol et. Otomatik testler sanatsal kaliteyi veya doğal oyunculuğu kanıtlamaz.

## Özellikler ve sınırlar

Özgün ve referans görselin karakterlerini kopyalamayan, kalın konturlu SVG tabanlı tilki; sabit zümrüt kostüm; telefon, patron ve ev sahibi sahneleri; yakın/uzak kadrajlar; kısa altyazı parçaları; basit özgün efektler ve görünür kapı kapanışı. Bu **profesyonel kare kare elle çizilmiş animasyon değil**, CPU üzerinde üretilen stilize SVG çizgi film prototipidir. Kaynak dosyanın lokal ön izlemeden farkı, kodun okunabilir ve GitHub'da çalıştırılabilir bir V4 uyarlaması olmasıdır.

İngilizce konuşma `edge-tts` üzerinden dış çevrimiçi servise bağlıdır; erişim, ücret veya ticari kullanım koşulları garanti edilmez. Servis başarısız olursa üretim hata verir; gizlice robotik sese dönmez. `FOX_OFFLINE_TEST=1` yalnızca çevrimdışı teknik denemeler içindir ve yayın sesi değildir. Standart GitHub işleyicilerinin kullanım/depolama sınırları bulunur. **YouTube'a otomatik yükleme bulunmaz.** Hiçbir hesap şifresini veya OAuth anahtarını herkese açık depoya koyma.

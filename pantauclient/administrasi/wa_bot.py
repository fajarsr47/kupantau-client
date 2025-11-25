import os
import time
import subprocess
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from akademik.models import PresensiSekolah, Kelas

# --- FUNGSI 1: GENERATE EXCEL (TIDAK BERUBAH) ---
def generate_laporan_excel(kelas_id, tanggal):
    try:
        kelas = Kelas.objects.get(id=kelas_id)
        presensi_list = PresensiSekolah.objects.filter(
            siswa__kelas_id=kelas_id,
            tanggal=tanggal
        ).select_related('siswa').order_by('siswa__nama')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"Presensi {kelas.nama_kelas}"

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill("solid", fgColor="4F46E5")
        border_style = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        headers = ["No", "NISN", "Nama Siswa", "Status", "Waktu Input"]
        ws.append(headers)

        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

        stats = {'H': 0, 'I': 0, 'S': 0, 'A': 0, 'T': 0}

        for idx, p in enumerate(presensi_list, 1):
            waktu = p.waktu.strftime("%H:%M") if p.waktu else "-"
            status_ket = p.get_status_display()
            if p.status in stats: stats[p.status] += 1
            
            row_data = [idx, p.siswa.nisn, p.siswa.nama, status_ket, waktu]
            ws.append(row_data)
            
            for col_idx in range(1, 6):
                ws.cell(row=idx+1, column=col_idx).border = border_style

        ws.append([])
        ws.append(["Ringkasan Kehadiran:"])
        ws.append([f"Hadir: {stats['H']}"])
        ws.append([f"Izin: {stats['I']}"])
        ws.append([f"Sakit: {stats['S']}"])
        ws.append([f"Alpha: {stats['A']}"])

        nama_file = f"Laporan_{kelas.nama_kelas.replace(' ', '_')}_{tanggal}.xlsx"
        full_path = os.path.join(settings.BASE_DIR, 'media', 'temp_reports')
        os.makedirs(full_path, exist_ok=True)
        
        file_path = os.path.join(full_path, nama_file)
        wb.save(file_path)
        
        # Kembalikan path absolute agar PowerShell bisa membacanya
        return os.path.abspath(file_path), stats, kelas.nama_grup_wa, kelas.nama_kelas

    except Exception as e:
        print(f"Error Excel: {e}")
        return None, None, None, None

# --- FUNGSI HELPER: COPY FILE (POWERSHELL) ---
def copy_file_to_clipboard(filepath):
    print(f"📋 Menyalin file ke clipboard: {filepath}")
    # Perintah PowerShell untuk set file object ke clipboard
    cmd = f'Set-Clipboard -Path "{filepath}"'
    subprocess.run(["powershell", "-Command", cmd], shell=True)

# --- FUNGSI 2: KIRIM WA (METODE PASTE) ---
def kirim_laporan_wa_otomatis(file_path, nama_grup, caption):
    print("⚙️  Menyiapkan Browser Selenium (Metode Paste)...")
    
    bot_profile_path = os.path.join(settings.BASE_DIR, "session_wa_bot")
    options = Options()
    options.add_argument(f"user-data-dir={bot_profile_path}")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://web.whatsapp.com")
        
        wait = WebDriverWait(driver, 120) # Tunggu agak lama untuk login
        
        # 1. Login Check
        print("⏳ Menunggu Login WA Web...")
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[@id="side"]')))
        print("✅ Login Terdeteksi.")

        # 2. Cari Grup (Sesuai kode user yang berhasil)
        print(f"🔎 Mencari grup: {nama_grup}")
        try:
            search_box = wait.until(EC.element_to_be_clickable((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')))
            search_box.clear()
            search_box.click()
            time.sleep(0.5)
            
            search_box.send_keys(nama_grup)
            time.sleep(2) # Tunggu hasil search muncul
            search_box.send_keys(Keys.ENTER)
        except Exception as e:
            print(f"❌ Gagal mencari grup: {e}")
            return False

        # 3. Tunggu Chat Terbuka
        print("   -> Menunggu chat terbuka...")
        # Mencari kolom ketik pesan (data-tab=10)
        chat_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
        time.sleep(1)

        # 4. Copy File & Paste (CTRL + V)
        if os.path.exists(file_path):
            copy_file_to_clipboard(file_path)
            time.sleep(1) # Tunggu clipboard system update
            
            print("📋 Menempelkan file (CTRL+V)...")
            chat_box.send_keys(Keys.CONTROL, 'v')
        else:
            print(f"❌ File tidak ditemukan: {file_path}")
            return False

        # 5. Tunggu Preview File Muncul
        print("   -> Menunggu preview file...")
        # Tunggu sampai muncul dialog caption (biasanya ada gambar/preview file)
        # Kita bisa tunggu elemen yang spesifik untuk preview media
        time.sleep(3) 
        
        # 6. Ketik Caption
        if caption:
            print("   -> Mengetik caption...")
            action = webdriver.ActionChains(driver)
            for line in caption.split('\n'):
                action.send_keys(line)
                action.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT)
            action.perform()
            time.sleep(1)

        # 7. Kirim (ENTER)
        print("🚀 Mengirim...")
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
        
        print(f"✅ Laporan BERHASIL terkirim ke {nama_grup}")
        time.sleep(5) # Tunggu proses upload selesai sebelum browser ditutup
        
        return True

    except Exception as e:
        print(f"❌ Error Selenium: {e}")
        return False
    finally:
        if driver:
            print("🏁 Menutup browser...")
            driver.quit()
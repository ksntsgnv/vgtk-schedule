import requests
from bs4 import BeautifulSoup
import os
import re
import uuid
from datetime import datetime

# --- НАСТРОЙКИ ---
MY_SUBJECTS = {
    "Тестирование": ["ВР-41"],
    "Инструменты": ["ВР-41"],
    "Информатика": ["ПКО-11", "ПСР-11", "ПКМ-12", "ПСМ-13", "ПСМ-113", "ПЭС-15", "ПОО-16", "ПТС-17", "ПМЭ-18", "ПМР-19"],
    "Комп.графика": ["ВР-31"],
}
CURATOR_HOUR_GROUP = "ПСР-11"

TELEGRAM_BOT_TOKEN = "9133871343:AAGTRsWdEHasEPbpD4W5kn_jJtJt7Dj3gQA"
TELEGRAM_CHAT_ID = "1542128677"

urls = {"Завтра": "https://www.vgtk.by/schedule/lessons/day-tomorrow.php"}
MONTHS = {"января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
          "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"}

all_lessons = []
seen_lessons = set()

print("⏳ Загружаю расписание...")

for day_name, url in urls.items():
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    
    date_tag = soup.find(string=lambda t: t and "на" in t and "года" in t)
    current_date_str = date_tag.strip() if date_tag else day_name

    date_match = re.search(r'(\d{1,2})\s+([а-я]+)\s+(\d{4})', current_date_str)
    if date_match:
        day = date_match.group(1).zfill(2)
        month = MONTHS.get(date_match.group(2).lower(), "01")
        year = date_match.group(3)
        event_date = f"{year}{month}{day}"
    else:
        event_date = "20261027"

    rows = soup.find_all('tr')
    day_data = []
    header_row = None
    lesson_time_map = {}
    
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if not cells: continue
        
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        if "Группы/ Звонки" in cell_texts or "Группы/  Звонки" in cell_texts:
            header_row = cells
            continue
            
        if header_row is not None and len(cells) > 2:
            lesson_num = cells[0].get_text(strip=True)
            if not lesson_num or not lesson_num[0].isdigit(): continue
            
            time = cells[1].get_text(strip=True)
            if "Обед" in time: continue
            
            lesson_num_clean = lesson_num.replace('.', '').strip()
            lesson_time_map[lesson_num_clean] = time

            for i in range(2, len(cells) - 1, 2):
                subject = cells[i].get_text(strip=True)
                room = cells[i+1].get_text(strip=True)
                group_name = header_row[i].get_text(strip=True) if i < len(header_row) else "Неизвестно"
                rowspan = int(cells[i].get('rowspan', 1))
                
                if subject and subject != "Обед":
                    day_data.append({
                        "lesson_num": lesson_num,
                        "lesson_num_clean": lesson_num_clean,
                        "time": time,
                        "group": group_name,
                        "subject": subject,
                        "room": room,
                        "rowspan": rowspan
                    })
    
    processed_indices = set()
    for idx, lesson in enumerate(day_data):
        if idx in processed_indices: continue
        lesson_key = f"{lesson['lesson_num_clean']}|{lesson['group']}|{lesson['subject']}"
        if lesson_key in seen_lessons: continue
        
        is_my_subject = any(subj.lower() in lesson['subject'].lower() and (not groups or lesson['group'] in groups) for subj, groups in MY_SUBJECTS.items())
        is_curator = "Час куратора" in lesson['subject'] and lesson['group'] == CURATOR_HOUR_GROUP
        
        if is_my_subject or is_curator:
            duration = lesson['rowspan']
            display_time = lesson['time']
            
            if duration == 2:
                current_num = int(lesson['lesson_num_clean'])
                next_num = str(current_num + 1)
                
                if next_num in lesson_time_map:
                    next_time = lesson_time_map[next_num]
                    end_time = next_time.split('–')[1].strip() if '–' in next_time else next_time.split('-')[1].strip()
                    start_time = lesson['time'].split('–')[0].strip() if '–' in lesson['time'] else lesson['time'].split('-')[0].strip()
                    display_time = f"{start_time} - {end_time}"
            
            seen_lessons.add(lesson_key)
            processed_indices.add(idx)
            all_lessons.append({
                "time": display_time,
                "lesson_num": lesson['lesson_num'],
                "group": lesson['group'],
                "subject": lesson['subject'],
                "room": lesson['room'],
                "duration": duration
            })

all_lessons.sort(key=lambda x: int(x["lesson_num"].replace('.', '').strip()))

# --- ГЕНЕРАЦИЯ .ics ---
ics_lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//VGTK Schedule//RU",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-CALNAME:Расписание ВГТК"
]

dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

for lesson in all_lessons:
    time_str = lesson['time'].replace('–', '-')
    
    if ' - ' in time_str:
        parts = time_str.split(' - ')
    elif '-' in time_str:
        parts = time_str.split('-')
    else:
        parts = [time_str, time_str]
    
    start_raw = parts[0].strip()
    end_raw = parts[1].strip() if len(parts) > 1 else start_raw
    
    def format_time(t):
        t = t.replace('.', '')
        if len(t) == 4:
            return t + "00"
        elif len(t) == 3:
            return "0" + t + "00"
        return t + "00"
    
    start_time_ics = format_time(start_raw)
    end_time_ics = format_time(end_raw)
    
    uid = str(uuid.uuid4()) + "@vgtk-schedule"
    description = f"Пара №{lesson['lesson_num']}\\nГруппа: {lesson['group']}"
    
    ics_lines.extend([
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{dtstamp}",
        f"DTSTART:{event_date}T{start_time_ics}",
        f"DTEND:{event_date}T{end_time_ics}",
        f"SUMMARY:{lesson['subject']} ({lesson['group']})",
        f"LOCATION:каб. {lesson['room']}",
        f"DESCRIPTION:{description}",
        "END:VEVENT"
    ])

ics_lines.append("END:VCALENDAR")

# Сохраняем файл в домашнюю папку PythonAnywhere
HOME = os.path.expanduser('~')
ics_file_path = os.path.join(HOME, "Расписание_на_завтра.ics")

with open(ics_file_path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write("\r\n".join(ics_lines))

print(f"✅ Файл создан: {ics_file_path}")
print(f"📅 Найдено пар: {len(all_lessons)}")

# --- ОТПРАВКА В TELEGRAM ---
print("📤 Отправляю файл в Telegram...")
tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"

with open(ics_file_path, "rb") as f:
    files = {"document": ("Расписание_на_завтра.ics", f, "text/calendar")}
    data = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "caption": f"📅 Ваше расписание на завтра ({current_date_str})\nНайдено пар: {len(all_lessons)}"
    }
    
    response = requests.post(tg_url, files=files, data=data)
    
    if response.status_code == 200:
        print("🎉 УСПЕШНО! Файл отправлен в Telegram.")
    else:
        print(f"❌ Ошибка: {response.text}")

print("✅ Готово!")

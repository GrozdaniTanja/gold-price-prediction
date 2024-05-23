import os
import csv
from datetime import datetime


def process_gold_data(GOLD_DATA_DIR, PROCESSED_GOLD_DIR):
    os.makedirs(PROCESSED_GOLD_DIR, exist_ok=True)

    for filename in os.listdir(GOLD_DATA_DIR):
        if filename.endswith('-gold-price-data.csv'):
            file_path = os.path.join(GOLD_DATA_DIR, filename)
            currency = filename.split('-')[0]
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                csv_filename = f"{currency}-processed-gold-price-data.csv"
                csv_file_path = os.path.join(PROCESSED_GOLD_DIR, csv_filename)

                file_exists = os.path.exists(csv_file_path)

                with open(csv_file_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['timestamp', 'price', 'prev_close_price',
                                  'open_price', 'low_price', 'high_price', 'ch', 'chp']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    if not file_exists:
                        writer.writeheader()

                    for record in reader:
                        timestamp = datetime.fromisoformat(
                            record['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

                        new_record = {
                            'timestamp': timestamp,
                            'price': record.get('price'),
                            'prev_close_price': record.get('prev_close_price'),
                            'open_price': record.get('open_price'),
                            'low_price': record.get('low_price'),
                            'high_price': record.get('high_price'),
                            'ch': record.get('ch'),
                            'chp': record.get('chp')
                        }
                        writer.writerow(new_record)


if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(ROOT_DIR, '..', '..', 'data')
    RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
    GOLD_DATA_DIR = RAW_DATA_DIR
    PROCESSED_GOLD_DIR = os.path.join(DATA_DIR, "processed")
    process_gold_data(GOLD_DATA_DIR, PROCESSED_GOLD_DIR)

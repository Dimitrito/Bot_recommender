import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Smartphone, Base

engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def parse_bool(value):
    return value.strip().lower() in ['yes', 'true', '1']


with open('data.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        phone = Smartphone(
            brand_name=row['brand_name'],
            model=row['model'],
            price=float(row['price']) if row['price'] else None,
            avg_rating=float(row['avg_rating']) if row['avg_rating'] else None,
            is_5g=parse_bool(row['5G_or_not']),

            processor_brand=row['processor_brand'],
            num_cores=int(row['num_cores']) if row['num_cores'] else None,
            processor_speed=float(row['processor_speed']) if row['processor_speed'] else None,

            battery_capacity=int(row['battery_capacity']) if row['battery_capacity'] else None,
            fast_charging_available=parse_bool(row['fast_charging_available']),
            fast_charging=float(row['fast_charging']) if row['fast_charging'] else None,

            ram_capacity=int(row['ram_capacity']) if row['ram_capacity'] else None,
            internal_memory=int(row['internal_memory']) if row['internal_memory'] else None,

            screen_size=float(row['screen_size']) if row['screen_size'] else None,
            refresh_rate=int(row['refresh_rate']) if row['refresh_rate'] else None,
            num_rear_cameras=int(row['num_rear_cameras']) if row['num_rear_cameras'] else None,

            os=row['os'],

            primary_camera_rear=int(row['primary_camera_rear']) if row['primary_camera_rear'] else None,
            primary_camera_front=int(row['primary_camera_front']) if row['primary_camera_front'] else None,

            extended_memory_available=parse_bool(row['extended_memory_available']),

            resolution_height=int(row['resolution_height']) if row['resolution_height'] else None,
            resolution_width=int(row['resolution_width']) if row['resolution_width'] else None
        )
        session.add(phone)

session.commit()
print("📥 Импорт завершён успешно.")

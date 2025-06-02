from sqlalchemy import create_engine, func, Integer
from sqlalchemy.orm import sessionmaker
from models import Base, Smartphone

engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def to_dict(sended):
    obj = sended[0]
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}


def get_average_values(session):
    avg_values = session.query(
        func.avg(Smartphone.price).label('price'),
        func.avg(Smartphone.avg_rating).label('avg_rating'),
        func.avg(Smartphone.num_cores).label('num_cores'),
        func.avg(Smartphone.processor_speed).label('processor_speed'),
        func.avg(Smartphone.battery_capacity).label('battery_capacity'),
        func.avg(Smartphone.fast_charging).label('fast_charging'),
        func.avg(Smartphone.ram_capacity).label('ram_capacity'),
        func.avg(Smartphone.internal_memory).label('internal_memory'),
        func.avg(Smartphone.screen_size).label('screen_size'),
        func.avg(Smartphone.refresh_rate).label('refresh_rate'),
        func.avg(Smartphone.num_rear_cameras).label('num_rear_cameras'),
        func.avg(Smartphone.primary_camera_rear).label('primary_camera_rear'),
        func.avg(Smartphone.primary_camera_front).label('primary_camera_front'),
        func.avg(Smartphone.resolution_height).label('resolution_height'),
        func.avg(Smartphone.resolution_width).label('resolution_width')
    ).one()

    most_common = session.query(
        Smartphone.brand_name,
        func.count(Smartphone.brand_name).label('count')
    ).group_by(Smartphone.brand_name).order_by(func.count(Smartphone.brand_name).desc()).first()

    most_common_os = session.query(
        Smartphone.os,
        func.count(Smartphone.os).label('count')
    ).group_by(Smartphone.os).order_by(func.count(Smartphone.os).desc()).first()

    most_common_processor = session.query(
        Smartphone.processor_brand,
        func.count(Smartphone.processor_brand).label('count')
    ).group_by(Smartphone.processor_brand).order_by(func.count(Smartphone.processor_brand).desc()).first()

    binary_stats = session.query(
        func.avg(func.cast(Smartphone.is_5g, Integer)).label('is_5g'),
        func.avg(func.cast(Smartphone.fast_charging_available, Integer)).label('fast_charging_available'),
        func.avg(func.cast(Smartphone.extended_memory_available, Integer)).label('extended_memory_available')
    ).one()

    return {
        'price': avg_values.price or 30000,
        'avg_rating': avg_values.avg_rating or 7.0,
        'num_cores': round(avg_values.num_cores) if avg_values.num_cores else 6,
        'processor_speed': avg_values.processor_speed or 2.5,
        'battery_capacity': round(avg_values.battery_capacity) if avg_values.battery_capacity else 4000,
        'fast_charging': avg_values.fast_charging or 18.0,
        'ram_capacity': round(avg_values.ram_capacity) if avg_values.ram_capacity else 6,
        'internal_memory': round(avg_values.internal_memory) if avg_values.internal_memory else 128,
        'screen_size': avg_values.screen_size or 6.5,
        'refresh_rate': round(avg_values.refresh_rate) if avg_values.refresh_rate else 90,
        'num_rear_cameras': round(avg_values.num_rear_cameras) if avg_values.num_rear_cameras else 3,
        'primary_camera_rear': round(avg_values.primary_camera_rear) if avg_values.primary_camera_rear else 48,
        'primary_camera_front': round(avg_values.primary_camera_front) if avg_values.primary_camera_front else 16,
        'resolution_height': round(avg_values.resolution_height) if avg_values.resolution_height else 2400,
        'resolution_width': round(avg_values.resolution_width) if avg_values.resolution_width else 1080,

        'brand_name': most_common[0] if most_common else 'unknown',
        'processor_brand': most_common_processor[0] if most_common_processor else 'unknown',
        'os': most_common_os[0] if most_common_os else 'unknown',

        'is_5g': binary_stats.is_5g > 0.5 if binary_stats.is_5g is not None else False,
        'fast_charging_available': binary_stats.fast_charging_available > 0.5 if binary_stats.fast_charging_available is not None else False,
        'extended_memory_available': binary_stats.extended_memory_available > 0.5 if binary_stats.extended_memory_available is not None else False
    }

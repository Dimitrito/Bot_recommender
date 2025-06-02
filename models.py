from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Smartphone(Base):
    __tablename__ = "smartphones"

    id = Column(Integer, primary_key=True, autoincrement=True)

    brand_name = Column(String)
    model = Column(String)
    price = Column(Float)
    avg_rating = Column(Float)
    is_5g = Column(Boolean)

    processor_brand = Column(String)
    num_cores = Column(Integer)
    processor_speed = Column(Float)

    battery_capacity = Column(Integer)
    fast_charging_available = Column(Boolean)
    fast_charging = Column(Float)

    ram_capacity = Column(Integer)
    internal_memory = Column(Integer)

    screen_size = Column(Float)
    refresh_rate = Column(Integer)
    num_rear_cameras = Column(Integer)

    os = Column(String)

    primary_camera_rear = Column(Integer)
    primary_camera_front = Column(Integer)

    extended_memory_available = Column(Boolean)

    resolution_height = Column(Integer)
    resolution_width = Column(Integer)

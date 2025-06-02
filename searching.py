from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.metrics.pairwise import cosine_similarity
from db import get_average_values
from models import Smartphone
import pandas as pd


def prepare_embeddings(session):
    smartphones = session.query(Smartphone).all()

    data = pd.DataFrame([{
        'price': phone.price,
        'avg_rating': phone.avg_rating,
        'num_cores': phone.num_cores,
        'processor_speed': phone.processor_speed,
        'battery_capacity': phone.battery_capacity,
        'fast_charging': phone.fast_charging,
        'ram_capacity': phone.ram_capacity,
        'internal_memory': phone.internal_memory,
        'screen_size': phone.screen_size,
        'refresh_rate': phone.refresh_rate,
        'num_rear_cameras': phone.num_rear_cameras,
        'primary_camera_rear': phone.primary_camera_rear,
        'primary_camera_front': phone.primary_camera_front,
        'resolution_height': phone.resolution_height,
        'resolution_width': phone.resolution_width,
        'brand_name': phone.brand_name,
        'processor_brand': phone.processor_brand,
        'os': phone.os,
        'is_5g': phone.is_5g,
        'fast_charging_available': phone.fast_charging_available,
        'extended_memory_available': phone.extended_memory_available,
        'id': phone.id
    } for phone in smartphones])

    numeric_features = [
        'price', 'avg_rating', 'num_cores', 'processor_speed',
        'battery_capacity', 'fast_charging', 'ram_capacity',
        'internal_memory', 'screen_size', 'refresh_rate',
        'num_rear_cameras', 'primary_camera_rear', 'primary_camera_front',
        'resolution_height', 'resolution_width'
    ]

    categorical_features = [
        'brand_name', 'processor_brand', 'os'
    ]

    binary_features = [
        'is_5g', 'fast_charging_available', 'extended_memory_available'
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features),
            ('binary', 'passthrough', binary_features)
        ]
    )

    features = preprocessor.fit_transform(data)

    return features, smartphones, preprocessor


class SmartphoneRecommender:
    def __init__(self, session):
        self.embeddings, self.smartphones, self.preprocessor = prepare_embeddings(session)
        self.smartphone_dict = {phone.id: phone for phone in self.smartphones}
        self.default_values = get_average_values(session)

    def find_similar(self, smartphone_id, top_n=1):
        idx = next(i for i, phone in enumerate(self.smartphones)
                   if phone.id == smartphone_id)

        similarities = cosine_similarity(
            self.embeddings[idx:idx + 1],
            self.embeddings
        )[0]

        similar_indices = similarities.argsort()[::-1][1:top_n + 1]

        return [
            (self.smartphones[i], similarities[i])
            for i in similar_indices
        ]

    def find_similar_to_features(self, features_dict, top_n=5):
        processed_features = self.default_values.copy()

        for key, value in features_dict.items():
            if key in processed_features:
                if key == 'os' and value.lower() in ('не задано', 'не вказано', 'unknown'):
                    processed_features[key] = self.default_values['os']
                else:
                    processed_features[key] = value

        input_data = pd.DataFrame([processed_features])

        try:
            features = self.preprocessor.transform(input_data)
            similarities = cosine_similarity(features, self.embeddings)[0]
            similar_indices = similarities.argsort()[::-1][:top_n]

            return [
                (self.smartphones[i], similarities[i])
                for i in similar_indices
            ]
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []

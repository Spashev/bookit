import random
import math
from django.core.files.storage import default_storage
from datetime import datetime, timedelta


def has_passed_30_minutes(target_time):
    current_time = datetime.now()
    time_difference = current_time - target_time
    return time_difference >= timedelta(minutes=30)


def has_passed_2_minutes(target_time):
    current_time = datetime.now()
    time_difference = current_time - target_time
    return time_difference >= timedelta(minutes=2)


def delete_file(file_path: str):
    try:
        full_path = default_storage.path(file_path)
        if default_storage.exists(file_path):
            default_storage.delete(file_path)

            directory = os.path.dirname(full_path)
            if not os.listdir(directory):
                os.rmdir(directory)

    except Exception as e:
        print(f"Error deleting file: {e}")


def generate_activation_code():
    digits = [i for i in range(0, 10)]

    random_str = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])

    return random_str

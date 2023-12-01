# 하드코딩된 마을 건물들의 데이터
data = {
    'town_center': {
        'class_name': 'TownCenter',
        'max_level': 1,
        'total_happiness': [500],
        'max_population': [20],
        'house_range': [3]
    },
    'house': {
        'class_name': 'House',
        'max_level': 4,
        'upgrade_price': [200, 400, 1200, 3000],
        'upgrade_time': [5, 10, 30, 60],
        'total_happiness': [100, 300, 800, 3000],
        'max_population': [5, 15, 30, 100]
    },
    'hospital': {
        'class_name': 'Hospital',
        'max_level': 4,
        'upgrade_price': [500, 600, 700, 800],
        'upgrade_time': [60, 90, 180, 240],
        'total_happiness': [50, 100, 200, 400],
        'house_range': [2, 3, 4, 5]
    },
    'school': {
        'class_name': 'School',
        'max_level': 2,
        'upgrade_price': [500, 1000],
        'upgrade_time': [90, 180],
        'total_happiness': [400, 800],
        'productivity_increase': [0.1, 0.2],
        'graduates_per_min': [10, 20],
    },
    'library': {
        'class_name': 'Library',
        'max_level': 2,
        'upgrade_price': [1200, 1600],
        'upgrade_time': [180, 240],
        'total_happiness': [600, 1000],
        'build_speed_increase': [0.1, 0.2]
    },
    'shop': {
        'class_name': 'Shop',
        'max_level': 4,
        'upgrade_price': [50, 100, 250, 1000],
        'upgrade_time': [10, 20, 40, 70],
        'total_happiness': [200, 400, 1000, 2400],
        'money_per_min': [40, 80, 120, 160],
    },
    'stadium': {
        'class_name': 'Stadium',
        'max_level': 1,
        'upgrade_price': [5000],
        'upgrade_time': [300],
        'total_happiness': [12000],
        'money_per_min': [200]
    },
    'park': {
        'class_name': 'Park',
        'max_level': 2,
        'upgrade_price': [2000, 3000],
        'upgrade_time': [30, 40],
        'total_happiness': [2000, 5000]
    },
    'weather_center': {
        'class_name': 'WeatherCenter',
        'max_level': 2,
        'upgrade_price': [3000, 4000],
        'upgrade_time': [150, 210],
        'total_happiness': [800, 1200],
        'repair_price_reduction': [0.05, 0.15],
    },
    'laboratory': {
        'class_name': 'Laboratory',
        'max_level': 1,
        'upgrade_price': [1750],
        'upgrade_time': [240],
        'total_happiness': [2000],
        'research_time': 30,
        'research_price': 1000,
    },
    'factory': {
        'class_name': 'Factory',
        'max_level': 1,
        'upgrade_price': [2000],
        'upgrade_time': [120],
        'total_happiness': [800],
        'manufacture_price': 100,
        'manufacture_count': 10,
        'manufacture_time': 30,
    },
    'art_center': {
        'class_name': 'ArtCenter',
        'max_level': 1,
        'upgrade_price': [10000],
        'upgrade_time': [300],
        'total_happiness': [10000]
    }
}

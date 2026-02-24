from typing import List, Tuple, Optional


class SimStopsDAO:
    @staticmethod
    def get_all() -> List[Tuple]:
        pass

    @staticmethod
    def get_by_id(stop_id: int) -> Optional[Tuple]:
        pass

    # В этом запросе надо использовать встроенные функции PostGIS для поиска
    @staticmethod
    def get_in_area(lat_min: float, lat_max: float,
                    lon_min: float, lon_max: float) -> List[Tuple]:
        pass

    # Аргументы функции надо дописать
    @staticmethod
    def create() -> Tuple:
        pass

    # Аргументы функции надо дописать
    @staticmethod
    def update() -> Optional[Tuple]:
        pass

    @staticmethod
    def delete() -> Optional[Tuple]:
        pass

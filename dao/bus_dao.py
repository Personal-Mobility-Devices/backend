from typing import List, Tuple, Optional
from database import get_db_connection
from schemas.busModels import BusUpdate
class BusDAO:
    @staticmethod
    def get_all() -> List[Tuple]:
        with get_db_connection() as conn:
            with conn.cursor() as curr:
                curr.execute("""
                SELECT
                    id,
                    name,
                    description
                FROM 
                    bus
                ORDER BY
                    id
                """)
                return curr.fetchall()

    @staticmethod
    def get_by_id(bus_id: int) -> Optional[Tuple]:
        with get_db_connection() as conn:
            with conn.cursor() as curr:
                curr.execute("""
                SELECT
                    id,
                    name,
                    description
                FROM 
                    bus
                WHERE
                    id = %s
                """, (bus_id,))
                return curr.fetchone()

    @staticmethod
    def create(
            name: str,
            description: Optional[str]
    ) -> Tuple:
        with get_db_connection() as conn:
            with conn.cursor() as curr:
                curr.execute("""
                INSERT INTO bus (name, description)
                VALUES (%s, %s)
                RETURNING 
                    id, 
                    name, 
                    description
                """, (name, description))
                conn.commit()
                return curr.fetchone()


    # Аргументы функции надо дописать
    @staticmethod
    def update(
            bus_id: int,
            bus_update: BusUpdate
    ) -> Optional[Tuple]:
        updates = []
        params = []

        if bus_update.name is not None:
            updates.append("name = %s")
            params.append(bus_update.name)

        if bus_update.description is not None:
            updates.append("description = %s")
            params.append(bus_update.description)

        if not updates:
            return BusDAO.get_by_id(bus_id)

        params.append(bus_id)

        query = f"""
            UPDATE bus
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING
                id,
                name,
                description
        """
        with get_db_connection() as conn:
            with conn.cursor() as curr:
                curr.execute(query, params)
                conn.commit()
                return curr.fetchone()

    @staticmethod
    def delete(bus_id: int) -> Optional[Tuple]:
        with get_db_connection() as conn:
            with conn.cursor() as curr:
                curr.execute(
                    "DELETE FROM bus WHERE id = %s RETURNING id",
                    (bus_id,)
                )
                conn.commit()
                return curr.fetchone()
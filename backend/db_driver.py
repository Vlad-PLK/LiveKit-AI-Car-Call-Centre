import sqlite3
from typing import Optional
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class Booking:
    Booking_Number: str
    DateIn: str
    DateOut: str
    NightsNumber : int
    Room: str
    Price: int

class DatabaseDriver:
    def __init__(self, db_path: str = "auto_db.sqlite"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create cars table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cars (
                    Booking_Number TEXT PRIMARY KEY,
                    DateIn TEXT NOT NULL,
                    DateOut TEXT NOT NULL,
                    NightsNumber INTEGER NOT NULL,
                    Room TEXT NOT NULL,
                    Price INTEGER NOT NULL
                )
            """)
            conn.commit()

    def create_booking(self, Booking_Number: str, DateIn: str, DateOut: str, NightsNumber: int, Room: str, Price: int) -> Booking:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO bookings (Booking_Number, DateIn, DateOut, NightsNumber, Room, Price) VALUES (?, ?, ?, ?)",
                (Booking_Number, DateIn, DateOut, NightsNumber, Room, Price)
            )
            conn.commit()
            return Booking(Booking_Number=Booking_Number, DateIn=DateIn, DateOut=DateOut, NightsNumber=NightsNumber, Room=Room, Price=Price)

    def get_booking_by_Booking_Number(self, Booking_Number: str) -> Optional[Booking]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bookings WHERE Booking_Number = ?", (Booking_Number,))
            row = cursor.fetchone()
            if not row:
                return None
            
            return Booking(
                Booking_Number=row[0],
                DateIn=row[1],
                DateOut=row[2],
                NightsNumber=row[3],
                Room=row[4],
                Price=row[5]
            )

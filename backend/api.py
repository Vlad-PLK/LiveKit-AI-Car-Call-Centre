from livekit.agents import llm
import enum
from typing import Annotated
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO)

DB = DatabaseDriver()

class BookingDetails(enum.Enum):
    Booking_Number = "Booking_Number"
    DateIn = "DateIn"
    DateOut = "DateOut"
    NightsNumber = "NightsNumber"
    Room = "Room"
    Price = "Price"
    

class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        
        self._booking_details = {
            BookingDetails.Booking_Number: "",
            BookingDetails.DateIn: "",
            BookingDetails.DateOut: "",
            BookingDetails.NightsNumber: "",
            BookingDetails.Room: "",
            BookingDetails.Price: ""
        }
    
    def get_booking_str(self):
        booking_str = ""
        for key, value in self._booking_details.items():
            booking_str += f"{key}: {value}\n"
            
        return booking_str
    
    @llm.ai_callable(description="lookup a booking by its Booking_Number")
    def lookup_booking(self, Booking_Number: Annotated[str, llm.TypeInfo(description="The Booking_Number of the booking to lookup")]):
        logger.info("lookup booking - Booking_Number: %s", Booking_Number)
        
        result = DB.get_booking_by_Booking_Number(Booking_Number)
        if result is None:
            return "Booking not found"
        
        self._booking_details = {
            BookingDetails.Booking_Number: result.Booking_Number,
            BookingDetails.DateIn: result.DateIn,
            BookingDetails.DateOut: result.DateOut,
            BookingDetails.NightsNumber: result.NightsNumber,
            BookingDetails.Room: result.Room,
            BookingDetails.Price: result.Price
        }
        
        return f"The booking details are: {self.get_booking_str()}"
    
    @llm.ai_callable(description="get the details of the current booking")
    def get_booking_details(self):
        logger.info("get booking details")
        return f"The booking details are: {self.get_booking_str()}"
    
    @llm.ai_callable(description="create a new booking")
    def create_booking(
        self, 
        Booking_Number: Annotated[str, llm.TypeInfo(description="The Booking_Number of the booking")],
        DateIn: Annotated[str, llm.TypeInfo(description="The DateIn of the booking ")],
        DateOut: Annotated[str, llm.TypeInfo(description="The DateOut of the booking ")],
        NightsNumber: Annotated[int, llm.TypeInfo(description="The number of nights of the booking ")],
        Room: Annotated[str, llm.TypeInfo(description="The Room of the booking")],
        Price: Annotated[int, llm.TypeInfo(description="The Price of the booking")]
    ):
        logger.info("create booking - Booking_Number: %s, Date In: %s, Date Out: %s, Number of Nights: %s, Room: %s, Price: %s", Booking_Number, DateIn, DateOut, NightsNumber, Room, Price)
        result = DB.create_booking(Booking_Number, DateIn, DateOut, NightsNumber, Room, Price)
        if result is None:
            return "Failed to create booking"
        
        self._booking_details = {
            BookingDetails.Booking_Number: result.Booking_Number,
            BookingDetails.DateIn: result.DateIn,
            BookingDetails.DateOut: result.DateOut,
            BookingDetails.NightsNumber: result.NightsNumber,
            BookingDetails.Room: result.Room,
            BookingDetails.Price: result.Price
        }
        
        return "booking created!"
    
    def has_booking(self):
        return self._booking_details[BookingDetails.Booking_Number] != ""
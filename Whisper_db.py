import motor.motor_asyncio  # MongoDB async client
import threading

# MongoDB connection
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017")  # Replace with your actual MongoDB URI
dbname = client["hasnainkk"]  # Replace with your actual database name

# Collection for whispers
collection = dbname.whisper
INSERTION_LOCK = threading.RLock()

class Whispers:
    @staticmethod
    async def add_whisper(WhisperId, WhisperData):
        with INSERTION_LOCK:
            whisper = {"WhisperId": WhisperId, "whisperData": WhisperData}
            await collection.insert_one(whisper)

    @staticmethod
    async def del_whisper(WhisperId):
        with INSERTION_LOCK:
            await collection.delete_one({"WhisperId": WhisperId})

    @staticmethod
    async def get_whisper(WhisperId):
        whisper = await collection.find_one({"WhisperId": WhisperId})
        if whisper:
            return whisper["whisperData"]
        return None
      

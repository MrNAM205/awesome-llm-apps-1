from src.harvester import harvest_all_chats
from src.harvester_status import status

def harvest_now():
    status.reset()
    harvest_all_chats()
    return True
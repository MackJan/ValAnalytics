from pypresence import Presence
import time
import nest_asyncio
from models import *

client_id = "1389311125681606666"
nest_asyncio.apply()

class DiscordRPC:
    def __init__(self):
        self.client_id = client_id
        self.presence = None
        self.connected = False
        self.connect()

    def connect(self):
        """Connect to Discord RPC"""
        if self.connected:
            return True

        try:
            self.presence = Presence(self.client_id)
            self.presence.connect()
            self.connected = True
            print("Successfully connected to Discord RPC")
            return True
        except Exception as e:
            print(f"Failed to connect to Discord: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from Discord RPC"""
        if self.connected and self.presence:
            try:
                self.presence.close()
                self.connected = False
                print("Disconnected from Discord RPC")
            except Exception as e:
                print(f"Error during disconnect: {e}")

    def set_presence(self, state=None, details=None, start=None, large_image=None, large_text=None, small_image=None, small_text=None):
        """Update Discord presence with given parameters"""
        if not self.connected:
            if not self.connect():
                print("Cannot update presence - not connected to Discord")
                return

        try:

            # Build presence data, only including non-None values
            presence_data = {
                "state": state,
                "details": details,
                "start": start,
                "large_image": large_image,
                "large_text": large_text,
                "small_image": small_image,
                "small_text": small_text
            }

            self.presence.update(**presence_data)
        except Exception as e:
            print(f"Failed to update Discord presence: {e}")

    def set_match_presence(self, match_data:CurrentMatch):
        """Set presence based on match data"""
        if not match_data or not match_data.match_id:
            return

        try:
            state = "Playing solo" if match_data.party_size == 1 else "Playing in a party"
            details = match_data.game_mode

            self.set_presence(
                state=state,
                details=details,
                start=int(time.time()),
                large_image=match_data.game_map.lower(),
                large_text=match_data.game_map,
                small_image=match_data.players[0].character.lower() if match_data.players else None,
                small_text=match_data.players[0].character if match_data.players else None
            )
        except Exception as e:
            print(f"Failed to set match presence: {e}")

"""In-memory session state for the GM application."""

from api.schemas.party import PartySchema


class SessionState:
    def __init__(self):
        self.parties: dict[str, PartySchema] = {}
        self.campaign_state = None
        self.campaign_history: list = []
        self.crises: list = []
        self.scenarios: dict = {}

    def reset(self):
        self.__init__()


session = SessionState()

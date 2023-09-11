import hashlib
from datetime import datetime, timezone, timedelta


class Match:
    def __init__(self, competition: str, teams: tuple, timestamp: int):
        self.competition = competition
        self.teams = teams

        self.summary = self.__generate_summary()
        self.start_time = datetime.fromtimestamp(timestamp, timezone.utc)
        self.end_time = self.start_time + timedelta(hours=1)
        self.id = self.__get_id_hash()

    def __str__(self) -> str:
        return f"{self.id} {self.competition} {self.teams[0]} {self.teams[1]} {self.start_time} {self.end_time}"

    def __get_id_hash(self) -> str:
        match_str = (
            str(self.competition) + str(self.teams) + self.start_time.isoformat()
        )
        hash = hashlib.sha256(match_str.encode())
        return hash.hexdigest()

    def __generate_summary(self) -> str:
        return f"{self.competition} - {self.teams[0]} vs {self.teams[1]}"

    def validate_match(self) -> bool:
        return self.competition and self.teams[0] and self.teams[1]

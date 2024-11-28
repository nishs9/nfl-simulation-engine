class Team:
    def __init__(self, name: str, stats: dict):
        self.name = name
        self.stats = {}

    def __str__(self):
        return f"Team object representing {self.name}"
    
    def get_name(self) -> str:
        return self.name
    
    def set_name(self, name: str) -> None:
        self.name = name
    
    def get_stats(self) -> dict:
        return self.stats
    
    def set_stats(self, stats: dict) -> None:
        self.stats = stats

    def get_stat(self, key: str) -> any:
        return self.stats[key]
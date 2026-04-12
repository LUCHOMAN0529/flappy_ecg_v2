import json
import os
import config as cfg
 
 
class ScoreManager:
    def __init__(self):
        self.high_score = 0
        self.last_score = None   # None = no hay partida previa aún
        self._load()
 
    def _load(self):
        if os.path.exists(cfg.HIGH_SCORE_FILE):
            try:
                with open(cfg.HIGH_SCORE_FILE, "r") as f:
                    data = json.load(f)
                self.high_score = data.get("high_score", 0)
                self.last_score = data.get("last_score", None)
            except Exception:
                self.high_score = 0
                self.last_score = None
 
    def save(self):
        try:
            with open(cfg.HIGH_SCORE_FILE, "w") as f:
                json.dump({"high_score": self.high_score,
                           "last_score": self.last_score}, f)
        except Exception as e:
            print(f"[ScoreManager] No se pudo guardar: {e}")
 
    def register_game(self, score: int):
        """Llama esto al terminar cada partida."""
        if score > self.high_score:
            self.high_score = score
        self.last_score = score
        self.save()
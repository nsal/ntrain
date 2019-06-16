from dataclasses import dataclass


@dataclass
class Ticket:
    origin: str
    destination: str
    date: int
    price: float

    def __str__(self):
        return f"From: {self.origin} to {self.destination} on {self.date} £{self.price}"
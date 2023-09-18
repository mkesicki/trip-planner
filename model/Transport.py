
from abc import abstractmethod

class Transport:

    def __init__(self, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, params : dict):

        self.fromCity = fromCity
        self.fromCountry = fromCountry
        self.toCity = toCity
        self.toCountry = toCountry
        self.roundTrip = roundTrip
        self.startDate = startDate
        self.endDate = endDate
        self.adults = adults
        self.params = params

    @abstractmethod
    def search(self):
        pass
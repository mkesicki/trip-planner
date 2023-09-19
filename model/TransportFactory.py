from model.Plane import Plane

class TransportFactory:

    def __init__(self):
        pass

    def createTransport(self, type : str, fromCity : str, fromCountry : str, toCity : str, toCountry : str, roundTrip : bool, startDate : str, endDate : str, adults : int, params : dict):

        if type.lower() == 'flight':

            return Plane(fromCity, fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, params)

        elif type.lower() == 'car':

            return None

            # return Car(fromCity, fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, params)

        elif type.lower() == 'train':

            return None

            # return Train(fromCity, fromCountry, toCity, toCountry, roundTrip, startDate, endDate, adults, params)

        else:

            raise Exception("Transport type not found")
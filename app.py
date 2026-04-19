from schemas import Reactor, reactor_run

def main():
    reactor = Reactor()
    counter = 0
    while True:
        reactor_run(reactor, 1.0)
        print(reactor.thermal_power_mw, reactor.reactivity_delta, reactor.xenon_level)
    #pętla programu 
    #połączenie z bazą danych
    #pobranie danych z bazy danych
    #inicjalizacja reaktora co 10sek nowy log
    #przy przekroczeniu progu reaktywności automatycznie dodanie control rods
    #powyżej jakiejś temperatury zwiększenie przepływu chłodziwa
    #Alarmujące wartości 
    #user input po wciśnięciu jakiegoś przycisku w terminalu
    #po wpisaniu AZ5 wsunięcie wszystkich prętów kontrolnych
if __name__ == "__main__":
    main()
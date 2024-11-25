import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from colorama import Fore, Style, init
import json

init(autoreset=True)

class EventRequestAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.performers = self.load_performers()

    def load_performers(self):
        """Učitava izvođače iz 'events.json' datoteke."""
        try:
            with open("events.json", "r") as file:
                data = json.load(file)
                return [event["performer"] for event in data]
        except FileNotFoundError:
            print(f"{Fore.RED}[GREŠKA] {Style.BRIGHT}'events.json' nije pronađen!{Style.RESET_ALL}")
            return []
        except KeyError:
            print(f"{Fore.RED}[GREŠKA] {Style.BRIGHT}Pogrešan format 'events.json'! Nedostaje ključ 'performer'.{Style.RESET_ALL}")
            return []

    class RequestSender(CyclicBehaviour):
        async def run(self):
            if not self.agent.performers:
                print(f"{Fore.RED}[INFO] {Style.BRIGHT}Nema izvođača za slanje zahtjeva.{Style.RESET_ALL}")
                await self.agent.stop()
                return

            for performer in self.agent.performers:
                msg = Message(to="quoteagent@localhost")  
                msg.set_metadata("ontology", performer)  
                msg.set_metadata("performative", "request")
                msg.body = f"Daj mi informacije o događaju za {performer}"
                await self.send(msg)
                print(f"{Fore.GREEN}[ZAHTJEV] {Style.BRIGHT}Poslan zahtjev za događaj za izvođača '{Fore.CYAN}{performer}{Style.RESET_ALL}'")

                response = await self.receive(timeout=10)
                if response:
                    if response.metadata["performative"] == "inform":
                        print(f"{Fore.BLUE}[ODGOVOR] {Style.BRIGHT}Primljen odgovor za događaj:\n{Fore.YELLOW}{response.body}{Style.RESET_ALL}")
                    elif response.metadata["performative"] == "not-understood":
                        print(f"{Fore.RED}[GREŠKA] {Style.BRIGHT}Odgovor: {response.body}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[UPOZORENJE] {Style.BRIGHT}Nije primljen odgovor.{Style.RESET_ALL}")

                await asyncio.sleep(3)

            print(f"{Fore.MAGENTA}[KRAJ] {Style.BRIGHT}Svi zahtjevi su poslani.{Style.RESET_ALL}")

            ontology = str(input("Unesite naziv događaja na koji bi ste htijeli otići: ")).strip()
            while True:
                if ontology:
                    msg = Message(to="quoteagent@localhost")
                    msg.set_metadata("ontology", ontology)
                    msg.set_metadata("performative", "request")
                    await self.send(msg)
                    print(f"[ZAHTJEV] Poslan zahtjev na QuoteAgent za događaj '{ontology}'")
                    
                    response = await self.receive(timeout=10)
                    if response:
                        if response.metadata["performative"] == "inform":
                            leaflet_info = response.body
                            print(f"{Fore.YELLOW}[INFO] {Style.BRIGHT}Primljen podatak za kreiranje leaflet-a: {leaflet_info}")
                            
                            leaflet_msg = Message(to="fridge@localhost")
                            leaflet_msg.set_metadata("performative", "inform")
                            leaflet_msg.body = f"{leaflet_info}"
                            
                            await self.send(leaflet_msg)
                            print(f"{Fore.GREEN}[Poslano] {Style.BRIGHT}Poslani podaci '{leaflet_info}' Leaflet Agentu za HTML '{ontology}'")
                    jos = input("Želite li poslati zahtjev za još jedan događaj? (da/ne): ").strip().lower()
                    if jos != "da":
                        print("Završavam rad agenta.")
                        break
            await self.agent.stop()

    async def setup(self):
        behaviour = self.RequestSender()
        self.add_behaviour(behaviour)

async def main():
    agent = EventRequestAgent("requestagent@localhost", "1234")
    await agent.start()
    print(f"{Fore.GREEN}[INFO] {Style.BRIGHT}EventRequestAgent je pokrenut i aktivan.{Style.RESET_ALL}")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

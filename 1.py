import json
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from colorama import Fore, Style, init

init(autoreset=True)

class EventAgent(Agent):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.events = self.load_events()

    def load_events(self):
        with open('events.json', 'r') as file:
            data = json.load(file)
            print(f"{Fore.GREEN}[INFO] {Style.BRIGHT}Učitani podaci o događajima iz 'events.json'.{Style.RESET_ALL}")
            return {item["performer"]: item for item in data}

    class EventReceiver(CyclicBehaviour):
        async def run(self):
            msg = await self.receive()  
            if msg:
                ontology = str(msg.metadata.get("ontology", ""))
                performative = str(msg.metadata.get("performative", ""))
                
                print(f"{Fore.CYAN}[PRIMLJENO] {Style.BRIGHT}Poruka od {msg.sender}: {Style.RESET_ALL}{ontology}")
                
                if performative == "request" and ontology in self.agent.events:
                    event = self.agent.events[ontology]
                    response = Message(to=str(msg.sender))
                    response.set_metadata("ontology", ontology)
                    response.set_metadata("performative", "inform")
                    response.body = (f"Event: {event['performer']}\n"
                                     f"Location: {event['location']}\n"
                                     f"Ticket price: {event['ticket_price']}\n"
                                     f"Date: {event['event_date']}\n"
                                     f"Description: {event['description']}")
                    await self.send(response)  
                    print(f"{Fore.GREEN}[ODGOVOR POSLAN] {Style.BRIGHT}Događaj '{ontology}' pronađen i poslan: {Style.RESET_ALL}{event['performer']}")
                
                elif performative == "request":
                    response = Message(to=str(msg.sender))
                    response.set_metadata("ontology", ontology)
                    response.set_metadata("performative", "not-understood")
                    response.body = f"Nema informacija za događaj: {ontology}"
                    await self.send(response)  
                    print(f"{Fore.RED}[GREŠKA] {Style.BRIGHT}Nema informacija za događaj '{ontology}'.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}[UPOZORENJE] {Style.BRIGHT}Nepoznata performativa: {performative}.{Style.RESET_ALL}")

    async def setup(self):
        print(f"{Fore.CYAN}[INFO] {Style.BRIGHT}Pokrećem EventReceiver...{Style.RESET_ALL}")
        behaviour = self.EventReceiver()
        self.add_behaviour(behaviour)
        print(f"{Fore.CYAN}[SPREMNO] {Style.BRIGHT}Agent je spreman za primanje poruka.{Style.RESET_ALL}")

async def main():
    agent = EventAgent("quoteagent@localhost", "1234")
    await agent.start()
    print(f"{Fore.GREEN}[POKRENUT] {Style.BRIGHT}EventAgent je pokrenut i čeka poruke.{Style.RESET_ALL}")
    await asyncio.Future()  # Drži agenta aktivnim

if __name__ == "__main__":
    asyncio.run(main())

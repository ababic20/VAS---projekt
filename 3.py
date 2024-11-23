from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from colorama import Fore, Style, init
import asyncio
import tkinter as tk
from tkinter import ttk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

init(autoreset=True)

# Funkcija za spremanje leaflet-a kao PDF
def save_as_pdf(info):
    file_name = "leaflet_info.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    
    # Title for the PDF
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Informacije o Događaju")

    # Content of the leaflet
    c.setFont("Helvetica", 12)
    text_object = c.beginText(100, 730)
    text_object.setTextOrigin(100, 730)
    text_object.textLines(info)

    c.drawText(text_object)
    
    # Save PDF to file
    c.save()

    print(f"{Fore.GREEN}[INFO] PDF leaflet saved as {file_name}.")

# Tkinter GUI funkcija
def show_leaflet(info):
    root = tk.Tk()
    root.title("Leaflet Info")
    root.geometry("400x350")
    root.config(bg="#f4f4f9")  # Light background color

    # Naslov za leaflet
    title_frame = tk.Frame(root, bg="#007bff", pady=10)
    title_frame.pack(fill="x")
    title_label = tk.Label(title_frame, text="Informacije o Događaju", font=("Helvetica", 16, "bold"), fg="white", bg="#007bff")
    title_label.pack()

    # Frame for the info with a border
    info_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
    info_frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Informacije o događaju
    info_label = tk.Label(info_frame, text=info, wraplength=380, justify="left", font=("Helvetica", 12), fg="#333")
    info_label.pack()

    # Stilizirani gumb za zatvaranje prozora
    close_button = ttk.Button(root, text="Zatvori", command=root.destroy, style="TButton")
    close_button.pack(pady=20)

    # Custom button style
    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12, "bold"), foreground="#fff", background="#007bff", padding=10)
    style.map("TButton", foreground=[("pressed", "#fff"), ("active", "#fff")], background=[("pressed", "#0056b3"), ("active", "#0056b3")])

    # Dodavanje Print gumba
    print_button = ttk.Button(root, text="Print (Save as PDF)", command=lambda: save_as_pdf(info))
    print_button.pack(pady=10)

    root.mainloop()

class LeafletAgent(Agent):
    class DisplayLeafletInfo(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)  # Čekanje poruke
            if msg:
                if msg.metadata["performative"] == "inform":
                    leaflet_info = msg.body
                    print(f"{Fore.YELLOW}[INFO] {Style.BRIGHT}Primljen podatak za kreiranje leaflet-a:\n{leaflet_info}")
                    
                    # Pokretanje Tkinter GUI-a iz asyncio petlje
                    loop = asyncio.get_event_loop()
                    loop.run_in_executor(None, show_leaflet, leaflet_info)
                else:
                    print(f"{Fore.RED}[GREŠKA] {Style.BRIGHT}Nevažeći performativ u poruci!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[UPOZORENJE] {Style.BRIGHT}Nema novih poruka.{Style.RESET_ALL}")

    async def setup(self):
        behaviour = self.DisplayLeafletInfo()
        self.add_behaviour(behaviour)

async def main():
    leaflet_agent = LeafletAgent("fridge@localhost", "1234")
    await leaflet_agent.start()
    print(f"{Fore.GREEN}[INFO] {Style.BRIGHT}LeafletAgent je pokrenut i aktivan.{Style.RESET_ALL}")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

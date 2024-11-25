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
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

init(autoreset=True)

def save_as_pdf(info):
    file_name = "leaflet_info.pdf"
    c = canvas.Canvas(file_name, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Informacije o Događaju")

    c.setFont("Helvetica", 12)
    text_object = c.beginText(100, 730)
    text_object.setTextOrigin(100, 730)
    text_object.textLines(info)

    c.drawText(text_object)
    
    c.save()
    print(f"{Fore.GREEN}[INFO] PDF leaflet saved as {file_name}.")
    return file_name

def send_email(recipient_email, pdf_file):
    sender_email = ""
    sender_password = ""  

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient_email
        message['Subject'] = "Leaflet Informacije"

        body = "U privitku se nalazi PDF s informacijama o događaju."
        message.attach(MIMEText(body, 'plain'))

        with open(pdf_file, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f"attachment; filename={pdf_file}")
        message.attach(part)

        server.send_message(message)
        server.quit()
        print(f"{Fore.GREEN}[INFO] PDF uspješno poslan na {recipient_email}.")

    except Exception as e:
        print(f"{Fore.RED}[GREŠKA] Neuspješno slanje e-maila: {e}")

def show_leaflet(info):
    def send_pdf_email():
        recipient_email = email_entry.get()
        if recipient_email:
            pdf_file = save_as_pdf(info)
            send_email(recipient_email, pdf_file)
        else:
            print(f"{Fore.RED}[GREŠKA] Molimo unesite valjanu e-mail adresu.")

    root = tk.Tk()
    root.title("Leaflet Info")
    root.geometry("400x400")
    root.config(bg="#f4f4f9")  

    title_frame = tk.Frame(root, bg="#007bff", pady=10)
    title_frame.pack(fill="x")
    title_label = tk.Label(title_frame, text="Informacije o Događaju", font=("Helvetica", 16, "bold"), fg="white", bg="#007bff")
    title_label.pack()

    info_frame = tk.Frame(root, bg="#ffffff", bd=2, relief="solid", padx=10, pady=10)
    info_frame.pack(pady=20, padx=20, fill="both", expand=True)

    info_label = tk.Label(info_frame, text=info, wraplength=380, justify="left", font=("Helvetica", 12), fg="#333")
    info_label.pack()

    email_frame = tk.Frame(root, bg="#f4f4f9")
    email_frame.pack(pady=10)

    email_label = tk.Label(email_frame, text="Unesite e-mail adresu:", font=("Helvetica", 12), bg="#f4f4f9")
    email_label.grid(row=0, column=0, padx=5)
    email_entry = ttk.Entry(email_frame, font=("Helvetica", 12))
    email_entry.grid(row=0, column=1, padx=5)

    send_button = ttk.Button(root, text="Pošalji na e-mail", command=send_pdf_email)
    send_button.pack(pady=10)

    close_button = ttk.Button(root, text="Zatvori", command=root.destroy)
    close_button.pack(pady=10)

    root.mainloop()

class LeafletAgent(Agent):
    class DisplayLeafletInfo(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                if msg.metadata["performative"] == "inform":
                    leaflet_info = msg.body
                    print(f"{Fore.YELLOW}[INFO] {Style.BRIGHT}Primljen podatak za kreiranje leaflet-a:\n{leaflet_info}")
                    
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

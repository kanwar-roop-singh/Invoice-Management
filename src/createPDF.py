from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice
import os
os.environ["INVOICE_LANG"] = "en"

import json

file=open('config.txt')
config=json.load(file)

# Function to create the PDF invoice using InvoiceGenerator package
def CreatePDFButtonFunction(self,invoiceName):
        client = Client(self.clientNameField.get(),phone=self.clientPhoneField.get(),email=self.clientEmailField.get())
        provider = Provider(config["company_name"], address=config["address"], city=config["city"], zip_code=config["zip_code"], phone=config["phone"], email=config["email"], bank_account=config["bank_account"], bank_code=config["bank_code"], bank_name=config["bank_name"])
        creator = Creator(config['owner'])
        invoice = Invoice(client, provider, creator)
        invoice.currency="$"
        for i in range(len(self.CartItems)):
            invoice.add_item(Item(self.CartItems[i]["Quantity"],self.CartItems[i]["Cost Per Unit"],description=self.CartItems[i]["Item"]))
        pdf = SimpleInvoice(invoice)
        if not invoiceName:
            invoiceName="invoice.pdf"
        pdf.gen("invoices/"+invoiceName, generate_qr_code=True)
        os.system(os.path.join('invoices', invoiceName))

# Open the previously created invoices saved in the invoices folder ( From the order history screen)
def downloadInvoice(fileName):
    os.system(os.path.join('invoices', fileName))

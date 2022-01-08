import sqlite3
from tkinter import Tk,Button, Label, Scale, Entry, Listbox, IntVar, END, ACTIVE
from createPDF import CreatePDFButtonFunction, downloadInvoice
from functionList import CompleteOrderFunction, RestockSubmitFunction

import os
# Create the invoices folder if it doesn't exist
if not os.path.exists('invoices'):
    os.makedirs('invoices')

# Import the config file that contains owner details( These can be edited according to the need )
import json
file=open('config.txt')
config=json.load(file)

# Connect the Sqlite database from the data.db file
con = sqlite3.connect('data.db')
cur = con.cursor()

# Creating products and invoices table in the database if they do not exist
cur.execute('''CREATE TABLE if not exists products
               (productId INTEGER PRIMARY KEY AUTOINCREMENT ,productName text, costPrice real, sellPrice real, quantity integer)''')
cur.execute('''CREATE TABLE if not exists invoices
                (invoiceId INTEGER PRIMARY KEY AUTOINCREMENT , fileName text, customerName text, email text, profit real, totalAmount real )''')

# Create the window for the program 
gui = Tk()
gui.title('Invoice Management System')
gui.geometry("800x800")

# Class for Application
class Application():
    def __init__ (self):
        self.CreateMainWindow()  

    # Function that creates the heading and buttons on the main window
    def CreateMainWindow(self):
        self.companyName=Label(gui, text = config["company_name"], font=("Times New Roman", 40,"bold"), bg='#C0C0C0', width='14')
        self.companyName.place(x=100, y=50)
        self.welcomeMessage=Label(gui, text = "Welcome " + config["owner"], font=("Times New Roman", 15), bg='#C0C0C0', width='40')
        self.welcomeMessage.place(x=100, y=130)
        self.addItemButton = Button(gui, text='Add Item', width=20, height=3, bg='#000000', fg='#ffffff',command=lambda: self.addItemFunction() )
        self.addItemButton.place(x=100, y=250)
        self.restockItemButton = Button(gui, text='Restock Item', width=20, height=3, bg='#000000', fg='#ffffff',command=lambda: self.restockItemFunction())
        self.restockItemButton.place(x=300, y=250)
        self.createInvoiceButton = Button(gui, text='Create Invoice', width=20, height=3, bg='#000000', fg='#ffffff',command=lambda: self.createInvoiceFunction() )
        self.createInvoiceButton.place(x=500, y=250)
        self.orderHistoryButton = Button(gui, text='Order History', width=20, height=3, bg='#000000', fg='#ffffff',command=lambda: self.orderHistoryFunction() )
        self.orderHistoryButton.place(x=100, y=350)
        
        
    # Function is used to remove all the widgets from the window     
    def emptyScreen(self):
        for widget in gui.winfo_children():
            widget.destroy()
            
    # Function to go back from a screen to the main window        
    def goBackFunction(self):
        self.emptyScreen() 
        self.CreateMainWindow()
        
    # Function to create the add item screen (Pack function used to add to the window)
    def addItemFunction(self):
        self.emptyScreen()
        self.goBackButton = Button(gui, text='Go Back', width=10, height=1,bg='#000000', fg='#ffffff',command=lambda: self.goBackFunction() )
        self.goBackButton.place(x=10, y=10)
        self.itemNameField = Entry()
        self.itemNameLabel=Label(gui, text = "Item Name")
        self.quantityField = Entry()
        self.quantityLabel=Label(gui, text = "Quantity")
        self.costPriceField = Entry()
        self.costPriceLabel=Label(gui, text = "Cost Price")
        self.sellPriceField = Entry()
        self.sellPriceLabel=Label(gui, text = "Sell Price")
        self.addItemSubmit = Button(gui, text='Submit', width=8, height=3,command=lambda: self.addButtonSubmitFunction() )
        self.addItemMessage=Label(gui, text = "")
        self.itemNameLabel.pack()
        self.itemNameField.pack()
        self.quantityLabel.pack()
        self.quantityField.pack()
        self.costPriceLabel.pack()
        self.costPriceField.pack()
        self.sellPriceLabel.pack()
        self.sellPriceField.pack()
        self.addItemSubmit.pack()
        self.addItemMessage.pack()
        
    # Function to add the input values to the products table in the database
    def addButtonSubmitFunction(self):
        try:
            costPriceFieldValue=float(self.costPriceField.get())
            sellPriceFieldValue=float(self.sellPriceField.get())
            quantityFieldValue=int(self.quantityField.get())
        except:
            self.addItemMessage.configure( text="Enter Correct Values", fg="red"  )
            return
        sql='INSERT INTO products(productName, costPrice, sellPrice, quantity ) values ('+"'"+self.itemNameField.get()+"'"+','+self.costPriceField.get()+','+self.sellPriceField.get()+','+self.quantityField.get()+')'
        try:
            cur.execute(sql)
            con.commit()
            self.addItemMessage.configure( text="Added Item Successfully", fg="green" )
            self.itemNameField.delete(0, 'end')
            self.costPriceField.delete(0, 'end')
            self.sellPriceField.delete(0, 'end')
            self.quantityField.delete(0, 'end')
        except: 
            self.addItemMessage.configure( text="Error Adding Item", fg="red"  )
        
    # Function to create the Create Invoice screen and add different widgets used on the screen
    def createInvoiceFunction(self):
        self.emptyScreen()
        self.goBackButton = Button(gui, text='Go Back', width=10, height=1,bg='#000000', fg='#ffffff',command=lambda: self.goBackFunction() )
        self.goBackButton.place(x=50, y=10)
        self.CartItems=[]
        sql='SELECT * FROM products'
        cur.execute(sql)
        rows = cur.fetchall() 
        tempRows=[]
        for row in rows:
            tempRows.append(list(row))
        self.rows=tempRows
        self.ItemListLabel=Label(gui, text = "Items")
        self.ItemList = Listbox(gui)
        for key,item in enumerate(self.rows):
            self.ItemList.insert(key, item[1]+" ($"+str(item[3])+")")
        self.ItemListLabel.place(x=50, y=80)
        self.ItemList.place(x=50, y=120)
        self.AddToCartButton = Button(gui, text='Add To Cart', width=16, height=3,command=lambda: self.AddToCardButtonFunction() )
        self.AddToCartButton.place(x=250, y=240)
        
        def selectItemFromListFunction(event):
            selection = event.widget.curselection()
            index = selection[0]
            self.scale.set(0)
            self.scale.configure(to=self.rows[index][4])
        
        
        self.ItemList.bind("<<ListboxSelect>>", selectItemFromListFunction)
        var = IntVar()
        self.QuantityLabel=Label(gui, text = "Quantity")
        self.QuantityLabel.place(x=250, y=80)
        self.scale = Scale( gui, variable = var, from_ = 0, to = 0 )
        self.scale.place(x=250, y=120)

        labels=["Item","Quantity","Cost Per Unit","Total Cost"]        
        for i in range(4):
            for j in range(len(self.CartItems)+1):
                if j==0:
                    self.e = Label(gui,text = labels[i], width=12,bg='#000000', fg='#ffffff',font=('Arial',10,'bold'))
                    self.e.grid(row=i, column=j)
                    self.e.place(x=40+i*110,y=390+j*40)
                else:
                    self.e = Entry(gui, width=12, font=('Arial',10))
                    self.e.grid(row=i, column=j)
                    self.e.insert(END, 1)
                    self.e.place(x=40+i*110,y=390+j*40)
        
        
        self.clientNameLabel=Label(gui, text = "Client Name")
        self.clientNameLabel.place(x=550, y=90)
        self.clientNameField = Entry()
        self.clientNameField.place(x=550, y=120)
        
        self.clientPhoneLabel=Label(gui, text = "Phone")
        self.clientPhoneLabel.place(x=550, y=160)
        self.clientPhoneField = Entry()
        self.clientPhoneField.place(x=550, y=190)
        
        self.clientEmailLabel=Label(gui, text = "Email")
        self.clientEmailLabel.place(x=550, y=230)
        self.clientEmailField = Entry()
        self.clientEmailField.place(x=550, y=260)
        
        self.CreatePDFButton = Button(gui, text='Create PDF', width=16, height=3,command=lambda: CreatePDFButtonFunction(self) )
        self.CreatePDFButton.place(x=550, y=300)
        self.CompleteOrderButton = Button(gui, text='Complete Order', width=16, height=3,command=lambda: CompleteOrderFunction(self,cur,con) )
        self.CompleteOrderButton.place(x=550, y=400)
        
    # Function to create the restock item screen and add different widgets and fields    
    def restockItemFunction(self):
        self.emptyScreen()
        self.goBackButton = Button(gui, text='Go Back', width=10, height=1,bg='#000000', fg='#ffffff',command=lambda: self.goBackFunction() )
        self.goBackButton.place(x=50, y=10)
        self.CartItems=[]
        sql='SELECT * FROM products'
        cur.execute(sql)
        self.restockRows = cur.fetchall()
        self.RestockItemListLabel=Label(gui, text = "Items")
        self.RestockItemList = Listbox(gui)
        for key,item in enumerate(self.restockRows):
            self.RestockItemList.insert(key, item[1])
        self.RestockItemListLabel.place(x=50, y=80)
        self.RestockItemList.place(x=50, y=120)
        self.restockQuantityField = Entry()
        self.restockQuantityLabel=Label(gui, text = "Quantity")
        self.restockQuantityLabel.place(x=250, y=80)
        self.restockQuantityField.place(x=250, y=120)
        self.RestockButton = Button(gui, text='Restock Item', width=16, height=3,command=lambda: RestockSubmitFunction(self,cur,con) )
        self.RestockButton.place(x=250, y=200)
        self.restockItemMessage=Label(gui, text = "")
        self.restockItemMessage.place(x=250, y=300)
        
    # Function to add a selected item and its quantity to the cart    
    def AddToCardButtonFunction(self):
        if self.ItemList.get(ACTIVE) and self.scale.get()!=0:
            index=self.ItemList.get(0,"end").index(self.ItemList.get(ACTIVE))
            self.CartItems.append({ "productId":self.rows[index][0], "Item": self.ItemList.get(ACTIVE), "Cost Per Unit":self.rows[index][3], "costBoughtAt":self.rows[index][2], "Quantity":self.scale.get(), "Total Cost": round(self.rows[index][3]*self.scale.get(),2 )})
            labels=["Item","Quantity","Cost Per Unit","Total Cost"] 
            self.rows[index][4]=self.rows[index][4]-self.scale.get()
            self.scale.configure(to=self.rows[index][4])
            # Create and add item to the cart table
            for i in range(4):
                for j in range(len(self.CartItems)+1):
                    if j==0:
                        self.e = Label(gui, text = labels[i] , width=12,font=('Arial',10,'bold'),bg='#000000', fg='#ffffff')
                        self.e.grid(row=i, column=j)
                        self.e.place(x=40+i*110,y=390+j*40)
                    else:
                        self.e = Label(gui, text= str(self.CartItems[j-1][labels[i]]), width=12, font=('Arial',10))
                        self.e.grid(row=i, column=j)
                        self.e.place(x=40+i*110,y=390+j*40)
                        
    # Function to create Order History screen                    
    def orderHistoryFunction(self):
        self.emptyScreen()
        self.goBackButton = Button(gui, text='Go Back', width=10, height=1,bg='#000000', fg='#ffffff',command=lambda: self.goBackFunction() )
        self.goBackButton.place(x=50, y=10)
        sql='SELECT * FROM invoices'
        cur.execute(sql)
        rows = cur.fetchall() 
        tempRows=[]
        for row in rows:
            tempRows.append(list(row))
        self.rows=tempRows
        labels=["Invoice No","Filename","Client Name","Email","Profit","Total Amount"] 
        # Create the order history table
        for i in range(6):
            for j in range(len(self.rows)+1):
                if j==0:
                    self.e = Label(gui, text = labels[i] , width=12,font=('Arial',10,'bold'),bg='#000000', fg='#ffffff')
                    self.e.grid(row=i, column=j)
                    self.e.place(x=40+i*110,y=100+j*40)
                else:
                    if i==1:
                        self.e = Button(gui, text= str(self.rows[j-1][i]), width=10, font=('Arial',10), bg='#808080', fg='#ffffff', command=lambda row=i, column=j: downloadInvoice(str(self.rows[column-1][1])) )
                        self.e.grid(row=i, column=j)
                        self.e.place(x=40+i*110,y=100+j*40)
                    else:
                        self.e = Label(gui, text= str(self.rows[j-1][i]), width=12, font=('Arial',10))
                        self.e.grid(row=i, column=j)
                        self.e.place(x=40+i*110,y=100+j*40)
        

x=Application()

gui.mainloop() 

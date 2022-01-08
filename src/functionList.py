from tkinter import ACTIVE
from createPDF import CreatePDFButtonFunction

def CompleteOrderFunction(self,cur,con):
    profit=0
    totalAmount=0
    for item in self.CartItems:
        query="UPDATE products SET quantity = quantity-"+str(item['Quantity'])+" where productId="+str(item['productId'] )
        cur.execute(query)
        con.commit()
        profit=profit+(item["Cost Per Unit"]-item["costBoughtAt"])*item["Quantity"]
        totalAmount=totalAmount+item["Total Cost"]
    
    query="SELECT invoiceId from invoices"
    cur.execute(query)
    rows = cur.fetchall() 
    print(len(rows),profit,totalAmount)
    print(rows)
    query="INSERT into invoices(invoiceId, fileName, customerName, email, profit, totalAmount) values ("+str(len(rows)+1)+","+"'invoice"+str(len(rows)+1)+".pdf','"+self.clientNameField.get()+"','"+self.clientEmailField.get()+ "',"+str(profit) +','+str(totalAmount) +')' 
    print(query)
    cur.execute(query)
    con.commit()
    CreatePDFButtonFunction(self,"invoice"+str(len(rows)+1)+".pdf")
    self.createInvoiceFunction()
        
def RestockSubmitFunction(self,cur,con):
    try:
        restockQuantityValue=int(self.restockQuantityField.get())
        print(restockQuantityValue,self.RestockItemList.get(ACTIVE))
        if restockQuantityValue<=0:
            raise ValueError('Invalid Value')
        index=self.RestockItemList.get(0,"end").index(self.RestockItemList.get(ACTIVE))
        query="UPDATE products SET quantity = quantity+"+str(self.restockQuantityField.get())+" where productId="+str(self.restockRows[index][0] )
        cur.execute(query)
        con.commit()
        self.restockItemMessage.configure( text="Item Restocked Successfully", fg="green" )
        self.restockQuantityField.delete(0, 'end')
    except: 
        self.restockItemMessage.configure( text="Error Restocking Item", fg="red"  )
    
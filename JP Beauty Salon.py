import flask
import sqlite3
app = flask.Flask(__name__)

def get_db():
    db = sqlite3.connect("JPBeautySalon.db")
    db.row_factory = sqlite3.Row
    return db

def ValidateAddMember(FullName, Gender, Email, Contact, Address):
    #Validate Full Name
    if len(FullName) == 0:
        print("Name not valid.")
        return False
    #Validate Gender
    if Gender != "Male" and Gender != "Female":
        print("Gender not valid.")
        return False
    #Validate Email
    if len(Email) == 0:
        print("Email not valid.")
        return False
    if "@" not in Email or ".com" not in Email:
        print("Email not valid.")
        return False
    #Validate Contact
    if len(Contact) != 8:
        print("Contact Number not valid.")
        return False
    #Validate Address
    if len(Address) == 0:
        print("Address not valid.")
        return False
    return True

def ValidateUpdateMember(Email, Contact):
    #Validate Contact
    if len(Contact) != 8:
        print("Contact not valid.")
        return False
    #Validate Email
    if len(Email) == 0:
        print("Email not valid.")
        return False
    if "@" not in Email or ".com" not in Email:
        print("Email not valid.")
        return False
    return True

def ValidateMemberID(MemberID):
    db = get_db()
    count = db.execute("SELECT COUNT(MemberID) FROM Member WHERE MemberID = ?", ((MemberID, )))
    count = count.fetchone()[0]
    if count == 0:
        print("MemberID not valid. Member does not exist.")
        db.close()
        return False
    return True

def ValidateAddTransaction(FullName, MemberID, TypeOfService):
    #Validate FullName
    if len(FullName) == 0:
        print("Name not valid.")
        return False
    #Validate MemberID
    MemberID = int(MemberID)
    if MemberID != 0:
        db = get_db()
        count = db.execute("SELECT COUNT(*) FROM Member WHERE MemberID = ?", ((MemberID,)))
        count = count.fetchone()[0]
        if count == 0:
            print("MemberID not valid. Member does not exist.")
            db.close()
            return False
        else:
            Name = db.execute("SELECT FullName FROM Member WHERE MemberID = ?", ((MemberID,))).fetchone()[0]
            db.close()
            if FullName != Name:
                print("Name not valid. Name does not match MemberID.")
                return False
    #Validate TypeOfService
    if len(TypeOfService) == 0:
        print("Type Of Service(s) not valid.")
        return False
    return True

@app.route("/")
def homepage():
    return flask.render_template("index.html")

@app.route("/AddMember")
def addmember():
    return flask.render_template("addmember.html")

@app.route("/MemberAdded", methods = ["POST"])
def memberadded():
    #From HTML
    FullName = flask.request.form["FullName"]
    Gender = flask.request.form.get("Gender")
    Email = flask.request.form["Email"]
    Contact = flask.request.form["Contact"]
    Address = flask.request.form["Address"]
    #Validation
    if ValidateAddMember(FullName, Gender, Email, Contact, Address) == True:
        #To SQL
        db = get_db()
        db.execute("INSERT INTO Member (FullName, Gender, Email, Contact, Address) VALUES (?,?,?,?,?);", (FullName, Gender, Email, Contact, Address))
        db.commit()
        db.close()
        return flask.render_template("memberadded.html", FullName = FullName)
    else:
        return flask.render_template("addmember.html")

@app.route("/FindMember", methods = ["GET"])
def findmember():
    return flask.render_template("findmember.html")

@app.route("/UpdateMemberDetails", methods = ["POST"])
def updatemember():
    #From HTML
    MemberID = flask.request.form["MemberID"]
    #To SQL
    db = get_db()
    count = db.execute("SELECT COUNT(MemberID) FROM Member WHERE MemberID = ?", (MemberID))
    count = count.fetchone()[0]
    if count == 1:
        FullName = db.execute("SELECT FullName FROM Member WHERE MemberID = ?", (MemberID)).fetchone()[0]
        CurrentContactNumber = db.execute("SELECT Contact FROM Member WHERE MemberID = ?", (MemberID)).fetchone()[0]
        CurrentEmail = db.execute("SELECT Email FROM Member WHERE MemberID = ?", (MemberID)).fetchone()[0]
        db.close()
        return flask.render_template("updatemember.html", MemberID = MemberID, FullName = FullName, CurrentContactNumber = CurrentContactNumber, CurrentEmail = CurrentEmail)
    else:
        db.close()
        return flask.render_template("findmember.html")
    return flask.render_template("updatemember.html")

@app.route("/MemberUpdated", methods = ["POST"])
def memberupdated():
    #From HTML
    UpdatedEmail = flask.request.form["NewEmail"]
    UpdatedContact = flask.request.form["NewContactNumber"]
    FullName = flask.request.form["FullName"]
    MemberID = flask.request.form["MemberID"]
    if ValidateUpdateMember(UpdatedEmail, UpdatedContact) == True:
        #To SQL
        db = get_db()
        db.execute("UPDATE Member SET Email = ?, Contact = ? WHERE MemberID = ?", (UpdatedEmail, UpdatedContact, MemberID))
        db.commit()
        db.close()
        return flask.render_template("memberupdated.html", FullName = FullName)
    else:
        return flask.render_template("findmember.html")

@app.route("/FindMemberTransactions")
def findmembertransactions():
    return flask.render_template("findmembertransactions.html")

@app.route("/ViewSummaryOfMemberTransactions", methods = ["POST"])
def membertransactionssummary():
    #From HTML
    MemberID = flask.request.form["MemberID"]
    #To SQL
    if ValidateMemberID(MemberID) == True:
        db = get_db()
        count = db.execute("SELECT COUNT(*) FROM 'Transaction' WHERE MemberID = ?", (MemberID,)).fetchone()[0]
        if count > 0:
            db = get_db()
            Row = db.execute("SELECT InvoiceNumber, Date, TotalPayable FROM 'Transaction' WHERE MemberID = ?", (MemberID,)).fetchall()
            ListInvoiceNumber = []
            ListDate = []
            ListTotal = []
            for i in range(len(Row)):
                ListInvoiceNumber.append(Row[i][0])
                ListDate.append(Row[i][1])
                ListTotal.append(Row[i][2])
            print(ListInvoiceNumber)
            print(ListDate)
            print(ListTotal)
            db.close()
            return flask.render_template("membertransactionssummary.html", ListInvoiceNumber = ListInvoiceNumber, ListDate = ListDate, ListTotal = ListTotal)
        else:
            FullName = db.execute("SELECT FullName FROM Member WHERE MemberID = ?", (MemberID)).fetchone()[0]
            db.close()
            return flask.render_template("nomembertransactions.html", FullName = FullName)
    else:
        return flask.render_template("findmembertransactions.html")
    
@app.route("/AddTransaction")
def addtransaction():
    return flask.render_template("addtransaction.html")

@app.route("/TransactionDetails", methods = ["POST"])
def transactiondetails():
    #From HTML
    Date = flask.request.form["Date"]
    FullName = flask.request.form["FullName"]
    MemberID = flask.request.form["MemberID"]
    print(MemberID)
    TypeOfService = flask.request.form.getlist("TypeOfService")
    ListTypeOfService = []
    ListPrice = []
    Discount = 0
    if ValidateAddTransaction(FullName, MemberID, TypeOfService) == True:
        #To SQL
        db = get_db()
        Total = 0
        for service in TypeOfService:
            ListTypeOfService.append(service)
            Price = db.execute("SELECT ROUND(Price, 2) FROM Service WHERE TypeOfService = ?", (service,)).fetchone()[0]
            ListPrice.append(Price)
            Total += Price
            Total = round(Total, 2)
        if int(MemberID) != 0:
            Discount = round(0.1*Total,2)
        Total = round(0.9*Total, 2)
        db.execute("INSERT INTO 'Transaction' (Date, FullName, MemberID, TotalPayable) VALUES (?,?,?,?)",  (Date, FullName, MemberID, Total))
        db.commit()
        InvoiceID = db.execute("SELECT seq FROM sqlite_sequence WHERE name = 'Transaction'").fetchone()[0]
        for service in TypeOfService:
            db.execute("INSERT INTO TransactionDetails(InvoiceID, TypeOfService) VALUES (?, ?)", (InvoiceID, service,))
        db.commit()
        db.close()
        return flask.render_template("transactiondetails.html", InvoiceID = InvoiceID, Date = Date, FullName = FullName, MemberID = MemberID, ListTypeOfService = ListTypeOfService, ListPrice = ListPrice, DiscountGiven = Discount, Total = Total)
    else:
        return flask.render_template("addtransaction.html")

@app.route("/ViewDailyTransactions")
def viewdailytransaction():
    return flask.render_template("viewdailytransaction.html")

@app.route("/ViewSummaryOfDailyTransactions", methods = ["POST"])
def dailytransactionsummary():
    #From HTML
    Date = flask.request.form["Date"]
    #To SQL
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM 'Transaction' WHERE Date = ?", (Date,))
    count = count.fetchone()[0]
    if count > 0:
        db = get_db()
        Row = db.execute("SELECT InvoiceNumber, FullName, TotalPayable FROM 'Transaction' WHERE Date = ?", (Date,)).fetchall()
        ListInvoiceNumber = []
        ListName = []
        ListTotal = []
        print(len(Row))
        for i in range(len(Row)):
            print("i:", i)
            ListInvoiceNumber.append(Row[i][0])
            ListName.append(Row[i][1])
            ListTotal.append(Row[i][2])
        db.close()
        return flask.render_template("dailytransactionssummary.html", ListInvoiceNumber = ListInvoiceNumber, ListName = ListName, ListTotal = ListTotal)
    else:
        db.close() 
        return flask.render_template("notransactions.html", Date = Date)

@app.route("/ViewTransactionDetailsFromView", methods = ["POST"])
def transactiondetailsfromview():
    InvoiceID = flask.request.form["InvoiceID"]
    db = get_db()
    record = db.execute("SELECT Date, FullName, MemberID, TotalPayable FROM 'Transaction' WHERE InvoiceNumber = ?", (InvoiceID)).fetchone()
    Date = record[0]
    FullName = record[1]
    MemberID = record[2]
    Total = record[3]
    if int(MemberID) != 0:
        Discount = round(0.1*Total,2)
    else:
        Discount = 0.00
    ListTypeOfService = []
    ListPrice = []
    services = db.execute("SELECT TypeOfService FROM TransactionDetails WHERE InvoiceID = ?", (InvoiceID)).fetchall()
    for service in services:
        ListTypeOfService.append(service[0])
        Price = db.execute("SELECT ROUND(Price, 2) FROM Service WHERE TypeOfService = ?", (service[0],)).fetchone()[0]
        ListPrice.append(Price)
    db.close()
    return flask.render_template("transactiondetailsfromview.html", InvoiceID = InvoiceID, Date = Date, FullName = FullName, MemberID = MemberID, ListTypeOfService = ListTypeOfService, ListPrice = ListPrice, DiscountGiven = Discount, Total = Total)

@app.route("/FindMonth")
def findmonth():
    return flask.render_template("findmonth.html")

@app.route("/ViewMonthlyRevenue", methods = ["POST"])
def viewmonthlyrevenue():
    Month = flask.request.form["Month"]
    StartingMonth = Month + "-01"
    EndingMonth = Month + "-31"
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM 'Transaction' WHERE Date >= ? AND Date <= ?", (StartingMonth, EndingMonth))
    count = count.fetchone()[0]
    if count > 0:
        record = db.execute("SELECT InvoiceNumber, Date, TotalPayable FROM 'Transaction' WHERE Date >= ? AND Date <= ?", (StartingMonth, EndingMonth)).fetchall()
        ListInvoiceNumber = []
        ListDate = []
        ListRevenue = []
        Total = 0
        for row in record:
            ListInvoiceNumber.append(row[0])
            ListDate.append(row[1])
            ListRevenue.append(row[2])
            Total += row[2]
        db.close()
        return flask.render_template("viewmonthlyrevenue.html", ListInvoiceNumber = ListInvoiceNumber, ListDate = ListDate, ListRevenue = ListRevenue, Total = Total, Month = Month)
    else:
        db.close()
        return flask.render_template("norevenue.html", Month = Month)

if __name__ == '__main__':
    app.run(port=12345, debug=True)
app.run(debug=True)

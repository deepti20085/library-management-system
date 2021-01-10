
import mysql.connector
from queue import Queue
from datetime import datetime
from datetime import timedelta
import sys
class DBhandler:

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="AP12345678@g",
        auth_plugin='mysql_native_password',
        database="oopddatabase"
        )

    def open_connect(self):
        mycursor = self.connection.cursor()
        return mycursor,self.connection


    def close_connect(self):
        self.connection.close()
        print("Database is disconnected..")

class Borrower:

    def __init__(self,name,uid):
        self.name = name
        self.uid = uid

    # Functionality to display a particular user details and books issued by him/her
    def Borrower_Details(self,mycursor):
        # Firstly checking whether atleast one book is issued by user if yes than records are displayed..

        # Checking whether borrower has issued atleast one book before
        no_book = Count_UserBooks()
        a = no_book.count_books(mycursor,self.uid)
        if (a > 0):
            mycursor.execute("Select * From users where U_id=" + str(self.uid))
            myres = mycursor.fetchall()
            for i in myres:
                if(i[1]==(self.name)):
                    print("User Name: " + i[1] + " ,Expected return date " + str(i[3]) + "  ,Id of book Reserved: " + str(
                        i[4]))
                else:
                    print("Wrong username is inputted")
                    sys.exit()
        else:
            print("No books for this user..")

class Books_in_lib:

    # Functionality to display all books in library , this is required to user when issueing book
    def show_all_books(self, mycursor):
        # Following code is to retrieve all books from database
        mycursor.execute("Select * From books")
        myres = mycursor.fetchall()

        # Printing books in database..
        for i in myres:
            print("ID : " + str(i[0]) + " , NAME of BOOK: " + i[1] + "  , NAME of AUTHOR: " + i[2])

class Valid_Bookid:

    def isValid_bid(self,mycursor,bid):
        sqlform1 = "select b_id from books"
        mycursor.execute(sqlform1)
        myres = mycursor.fetchall()
        valid_bid = []
        for i in myres:
            valid_bid.append(int(i[0]))
        if (int(bid) not in valid_bid):
            return True
        return False

class Book:

    def __init__(self,id,bname,aname):
        self.id = id
        self.bname = bname
        self.aname = aname

class CreateBook:

    def create_book(self,mycursor,bid):
        v_bookid = Valid_Bookid()
        id = 0
        b_name = ""
        a_name = ""
        mycursor.execute("Select * from books where b_id = "+str(bid))
        myres = mycursor.fetchall()
        for i in myres:
               id = i[0]
               b_name = i[1]
               a_name = i[2]
        B1 = Book(id,b_name,a_name)
        return B1

class Valid_Userbook:

    # function to validate whether a valid book id is entered by the user
    def check_valid_userbook(self,mycursor,uid,bid):

        # retrieving all book id's of books reserved and then checking whether the given book was issued or not.
        mycursor.execute("Select b_id From users where U_id=" + str(uid))
        myres = mycursor.fetchall()

        for i in myres:
            if (i[0] == int(bid)):
                return True
        return False

class Issue_Book:
    # Issuing book
    def Issuing_Book(self,mycursor,conn,borrower):
        borrower.Borrower_Details(mycursor)
        #   Keeping track of not more than maximum(4) books are issued
        C1 = Count_UserBooks()
        num_books = C1.count_books(mycursor,borrower.uid)

        # Keeping track of number of books issued as more than 4 books cannot be issued.
        if (num_books < 4):
            books_lib = Books_in_lib()
            books_lib.show_all_books(mycursor)
            print("Now enter the book id which you want to borrow")
            bid = input()
            # print(bid)
            # Checking for valid user id
            v_bookid = Valid_Bookid()
            # print(v_bookid.isValid_bid(mycursor,bid))
            if(v_bookid.isValid_bid(mycursor,bid) == True):
                   print("Not a valid book id entered ")
            else:
                   Val_book = Valid_Userbook()
                   is_booked = Val_book.check_valid_userbook(mycursor,borrower.uid,bid)
                   creat_b = CreateBook()
                   book = creat_b.create_book(mycursor,bid)
                   # print(str(book.id)+" "+str(book.bname))
                   if (is_booked):
                        print("You have issued this book.")
                   else:
                        issue_date = (datetime.date(datetime.now()))
                        end_date = datetime.date(datetime.now() + timedelta(days=7))
                        user_book1 =Add_user_book()
                        user_book1.db_user_book(mycursor,conn,borrower, book, issue_date, end_date)
                        print("book is issued")
                        #move book to issued_books tables once it is issued by user
                        isb=Insert_Issued_Books()
                        isb.insert_issu_books(mycursor,book)
        else:
            print("Cannot issue more than 4 books")

class Return_Book:
    # Keeping track of 2 things:
    #  1. Whether the entred bookid was issued or not
    #  2. whether the book is returned in time or not
    def Returning_Book(self,mycursor,borrower):
        no_userb = Count_UserBooks()
        a = no_userb.count_books(mycursor,borrower.uid)
        # print(type(i[2]))
        if (a > 0):
            borrower.Borrower_Details(mycursor)
            bid = input("Enter book id")
            v_book = Valid_Userbook()
            flag = v_book.check_valid_userbook(mycursor,borrower.uid,bid)
            # print(flag)

            if (flag):
                mycursor.execute("Select * From users where U_id=" + str(u_id) + " and b_id=" + str(bid))
                myres = mycursor.fetchall()
                # Checking whther the book is returned in time or is returned late

                format = "%Y-%m-%d"
                end_date = datetime.strptime(myres[0][3], format)
                time = datetime.now()

                # time=datetime(2020,10,19)
                if end_date < time:
                    d = time - end_date
                    pun = Punish()
                    amt = pun.get_invoice(d.days)
                    print("You are", d.days, "days delay please pay amt", amt)

                else:
                    print("Thanks for returning book on time")
                del_book = Delete_UserBooks()
                del_book.delete_userbook(mycursor,conn,borrower.uid,bid)
                dib=Delete_Issued_Books()
                dib.delete_issu_books(mycursor,bid)
                prb=Pop_reserved_book()
                prb.book_reservation_pop(bid)
            else:
                print("This book is not issued..")

        else:
            print("No book is issued..")

class Count_UserBooks:

    # Functionality to get the number of books issued by the user.
    def count_books(self,mycursor,uid):
        #   Counting number of books issued to a user
        mycursor.execute("Select count(*) From users where U_id=" + str(uid))
        myres = mycursor.fetchall()
        return myres[0][0]

class Delete_UserBooks:

    # Funtionality to delete user record for corresponding returned book
    def delete_userbook(self,mycursor ,conn , uid , bid):
        # Deleting record in user record..
        sqlform2 = "Delete from users where b_id=" + str(bid) + " and U_id=" + str(uid)
        mycursor.execute(sqlform2)
        conn.commit()

        print(str(mycursor.rowcount) + " rows deleted")

class Add_user_book:

    # Funtionality when a user issues a book , entering its record
    def db_user_book(self,mycursor,conn,borrower, book, issue_date, end_date):
        # Inserting user details along with bookid of issued book and dates (issue date and expected return date)
        sqlform = "Insert into users(U_id,U_name,issue_date,return_date,b_id) values(%s,%s,%s,%s,%s)"
        i_item = (borrower.uid, borrower.name, issue_date, end_date, book.id)
        p_books = [i_item]
        mycursor.executemany(sqlform, p_books)
        conn.commit()

class Punish:

    lprice = 5

    # Function to generate invoice when book is returned late
    # fine is 5 rupee per day
    def get_invoice(self,d):
        return d * self.price

class Punish_price(Punish):

    def change_price(self,price):
        self.lprice = price

class Add_book_lib(Book):

    def adding_book(self,mycursor,conn):
        sqlform = "Insert into books(B_id,B_name,A_name) values(%s,%s,%s)"
        i_item = (self.id, self.bname, self.aname)
        p_books = [i_item]
        mycursor.executemany(sqlform, p_books)
        conn.commit()
        print("Book is added")
        
class Display_issued_books:
    # Functionality to display issued_books in library for reserving them for maintaining the queue
    def show_issued_books(self, mycursor):
            # Following code is to retrieve all books from database
            mycursor.execute("Select * From issued_books")
            myres = mycursor.fetchall()
            # Printing books in database..
            for i in myres:
                print("ID : " + str(i[0]) + " , NAME of BOOK: " + i[1] + "  , NAME of AUTHOR: " + i[2])
                
class Valid_Res_Bookid:
    #check whether the input bid is available or not
    def isValidres_bid(self,mycursor,bid):
        sqlform1 = "select IB_id from issued_books"
        mycursor.execute(sqlform1)
        myres = mycursor.fetchall()
        valid_bid = []
        for i in myres:
            valid_bid.append(int(i[0]))
        if (int(bid) not in valid_bid):
            return True
        return False
            
class Reserve_Book:
    #This is used for reserving a books if it's not available for issuing
    def book_reservation_insert(self,mycursor,u_id,u_name):
        dib=Display_issued_books()
        dib.show_issued_books(mycursor)
        print("Now enter the book id which you want to reserve")
        bid = input()
        vr_bookid = Valid_Res_Bookid()
        # print(v_bookid.isValid_bid(mycursor,bid))
        if(vr_bookid.isValidres_bid(mycursor,bid) == True):
                print("Not a valid book id entered ")
        else:
            mycursor.execute("Select count(*) From reservation where book_id=" + str(bid)+" and U_id="+str(u_id))
            myres = mycursor.fetchall()
            if(myres[0][0]==0):
                mycursor.execute("Select max(priority) From reservation where book_id=" + str(bid))
                myres = mycursor.fetchall()
                #print(myres[0][0])
                if(myres[0][0]==5):
                    print("queue is full")
                else:
                    if(myres[0][0]==None):
                        count=1
                    else:
                        count=myres[0][0]+1
                    sqlform = "Insert into reservation(U_id,book_id,priority,U_name) values(%s,%s,%s,%s)"
                    i_item = (u_id, bid, count,u_name)
                    res = [i_item]
                    mycursor.executemany(sqlform, res)
                    conn.commit()
                    print("You are assigned in the queue")
            else:
                print("You are already waiting in this queue")
        
        
class Insert_Issued_Books:
    #Here the books when issuing are moved from books table to issued_books table
        def insert_issu_books(self,mycursor,book):
            sqlform1 = "Insert into issued_books(IB_id,IB_name,IA_name) values(%s,%s,%s)"
            i_item = (book.id, book.bname, book.aname)
            p_books=[i_item]
            mycursor.executemany(sqlform1, p_books)
            sqlform2 = "Delete from books where B_id="+str(book.id)
            mycursor.execute(sqlform2)
            conn.commit()


class Delete_Issued_Books:        
    #here the books are moved back to books table from issued_table when user returns the book
       def delete_issu_books(self,mycursor,bid):
            mycursor.execute("Select * from issued_books where IB_id = "+str(bid))
            myres = mycursor.fetchall()
            for i in myres:
                id = i[0]
                b_name = i[1]
                a_name = i[2]
            A1 = Add_book_lib(id,b_name,a_name)
            A1.adding_book(mycursor,conn)
            sqlform2 = "Delete from issued_books where IB_id="+str(bid)
            mycursor.execute(sqlform2)
            conn.commit()
            
class Pop_reserved_book:           
    #here user i search who is on the top of the queue is removed and issued a book
    def book_reservation_pop(self,b_id):
            mycursor.execute("Select U_id From reservation where book_id=" + str(b_id)+" and priority=1")
            myres = mycursor.fetchall()
            if(len(myres)==0):
                print('queue is empty')
            else:
                u_id=myres[0][0]
                mycursor.execute("Select U_name From reservation where book_id=" + str(b_id)+" and U_id="+str(u_id))
                myres = mycursor.fetchall()
                u_name=myres[0][0]
                b1 = Borrower(u_name, u_id)
                ibq=Issue_Book_Queue_Top()
                ibq.issue_book_qutop(b1,b_id)
                sqlform ="Delete from reservation where book_id="+str(b_id)+ " and U_id="+str(u_id)+ "  and priority=1"
                mycursor.execute(sqlform)
                sqlform1 ="Update reservation SET priority=priority-1 where book_id="+str(b_id)
                mycursor.execute(sqlform1)
                conn.commit()
            
class Issue_Book_Queue_Top:
    #here user who is on the top of the queue is issued a book
     def issue_book_qutop(self,borrower,b_id):
         C1 = Count_UserBooks()
         num_books = C1.count_books(mycursor,borrower.uid)
         # Keeping track of number of books issued as more than 4 books cannot be issued.
         if (num_books < 4):
             Val_book = Valid_Userbook()
             is_booked = Val_book.check_valid_userbook(mycursor,borrower.uid,b_id)
             creat_b = CreateBook()
             book = creat_b.create_book(mycursor,b_id)
             # print(str(book.id)+" "+str(book.bname))
             if (is_booked):
                 print("You have issued this book.")
             else:
                 issue_date = (datetime.date(datetime.now()))
                 end_date = datetime.date(datetime.now() + timedelta(days=7))
                 user_book1 =Add_user_book()
                 user_book1.db_user_book(mycursor,conn,borrower, book, issue_date, end_date)
                 print("book is issued")
                 #move book to issued books tables------
                 isb=Insert_Issued_Books()
                 isb.insert_issu_books(mycursor,book)
                 print("Book is issued to top of the queue to "+str(borrower.uid))
         else:
             print("Cannot issue more than 4 books")
         
# Main()
# Taking input from console
print("1:Display Borrower details")
print("2:Display books")
print("3:Reserve a book")
print("4:Issue Book")
print("5:Return Book")
print("6:Insert book")
choice = int(input("Enter your choice"))

# Opening database as all parts involve either of crud operations
db = DBhandler()
mycursor , conn =db.open_connect()
# Looping the operations to be performed
while choice < 7:

    if choice == 1:
        u_id = int(input("Enter user id"))
        if(u_id != 5001):
            u_name = input("Enter your name")
            b1 = Borrower(u_name, u_id)
            b1.Borrower_Details(mycursor)
        else:
            print("Librarian id is entered ,cannot perform this operation")
            
    elif choice == 2:
        lib_book = Books_in_lib()
        lib_book.show_all_books(mycursor)
        
    elif choice == 3:
        mycursor.execute("Select count(*) From issued_books")
        myres = mycursor.fetchall()
        if(myres[0][0]==0):
            print("No books available for reservation")
        else:
             u_id = int(input("Enter user id"))
             if(u_id != 5001):
                u_name = input("Enter your name")
             rb=Reserve_Book()
             rb.book_reservation_insert(mycursor,u_id,u_name)
         
    elif choice == 4:
        u_id = int(input("Enter user id"))
        if(u_id != 5001):
                u_name = input("Enter your name")
                b1 = Borrower(u_name, u_id)
                ib1 = Issue_Book()
                ib1.Issuing_Book(mycursor,conn,b1)
        else:
            print("Librarian id is entered ,cannot perform this operation")
    
    elif choice==5:
        u_id = int(input("Enter user id"))
        if(u_id != 5001):
            u_name = input("Enter your name")
            b1 = Borrower(u_name, u_id)
            rt1 = Return_Book()
            rt1.Returning_Book(mycursor,b1)
        else:
            print("Librarian id is entered ,cannot perform this operation")
    
    else:
        u_id = int(input("Enter user id"))
        if(u_id == 5001 ):
          b_id = input("Enter book id of book ")
          b_name = input("Enter book name")
          a_name = input("Enter author name")
          A1 = Add_book_lib(b_id,b_name,a_name)
          A1.adding_book(mycursor,conn)
        else:
            print("Not a valid librarian id thus books cannot be added")
    print("1:Display Borrower details")
    print("2:Display books")
    print("3:Reserve a book")
    print("4:Issue Book")
    print("5:Return Book")
    print("6:Insert book")
    choice = int(input("Enter your choice"))
    

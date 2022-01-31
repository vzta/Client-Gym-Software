import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

#Process to connect to Google Sheet Api
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'creds.json'
creds = None

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

SAMPLE_SPREADSHEET_ID = '1lnw5LKsE8z7LqqzABfnE0xpHardHwP27016BPbKIegY'
service = build('sheets', 'v4', credentials=creds)
sheet1 = service.spreadsheets()


Base = declarative_base()
engine = sqlalchemy.create_engine('postgresql:///alkemy', echo=False)

#In some functions you'll probably see a 'dni' variable which means in Spanish 'National Document of Identity'
#that variable works as ID for the tables.
#Yes I am lazy as fuck
#In reality at first i wrote the entire code in my language and I got tired translating it
#anyways lets go.

#Creating the tables of the DataBase

#Client Table
class Cliente(Base):
    __tablename__ = 'Cliente'
    ID = Column(Integer(), primary_key=True, unique=True)
    Name = Column(String(1000), unique=True)
    Age = Column(Integer)
    Objetivo = Column(String(100))
    Email = Column(String(1000), unique=True)
    Date = Column(Date(), default=datetime.now().date())
    children = relationship("Body_Composition", backref='Cliente')
    children2= relationship('RM', backref='Cliente')

    def __str__(self):
        template = 'Name: {0.Name}\nAge: {0.Age}\nE-mail: {0.Email}\nObjetivo: {0.Objetivo}\nID: {0.ID}'
        return template.format(self)


#Table with your Body composition data
class Body_Composition(Base):
    __tablename__ = 'composition'
    id = Column(Integer(), primary_key=True)
    Weight = Column(Integer)
    IMC = Column(Integer)
    BodyFat = Column(Integer)
    FFMI = Column(Integer)
    alumno_id = Column(Integer(), ForeignKey('Cliente.ID'))

    def __str__(self):
        template = 'Peso: {0.Weight}\nIMC: {0.IMC}\nBODYFAT: {0.BodyFat}\nFFMI: {0.FFMI}\nID: {0.alumno_id}'
        return template.format(self)


#Table which shows your current Training maxes in KG
class RM(Base):
    __tablename__ = 'Cambio RM'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer(), ForeignKey('Cliente.ID'))
    Bench = Column(Integer)
    Deadlift = Column(Integer)
    Squat = Column(Integer)
    Date = Column(Date(), default=datetime.now().date())

    def __str__(self):
        template = 'Bench: {0.Bench}\nDeadlift: {0.Deadlift}\nSquat: {0.Squat}\n'
        return template.format(self)


Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    Base.metadata.create_all(engine)

    def modify_data():

        global age, dni1
        dni=int(input("Ingrese el Dni del usuario a modificar: "))


        name=str(input("Ingrese Name: "))

        email=str(input("Ingrese su E-mail: "))

        try:
            age=int(input("Ingrese Age: "))
        except ValueError:
            print("Ingreso de dato inválido")
            return modify_data()
        try:
            dni1=int(input("Ingrese ID: "))
        except ValueError:
            print("Ingreso de dato inválido")
            return modify_data()

        session.query(Cliente).filter(
            Cliente.ID == dni
        ).update(
            {
                Cliente.ID: f"{dni1}",
                Cliente.Name: f"{name}",
                Cliente.Age: f"{age}",
                Cliente.Email:f"{email}",
            }

        )
        session.commit()
    def consultar():
        dni=input('Enter the ID of the Client you want to see: ')
        user=session.query(Cliente).filter(
            Cliente.ID == f'{dni}'
        ).first()

        print("\nName:", user.Name, "\nEmail:",
              user.Email,"\nAge:",
              user.Age, "\nObjetivo:",
              user.Objetivo)

    def Delete_record():
        dni=input('Enter the ID of the Client you want to delete its record: ')
        session.query(Cliente).filter(
            Cliente.ID == dni
        ).delete()
        session.commit()

    def Create_Client():
        try:
            dni=int(input("Enter the Client ID: "))  #which is the Documnent Number
            name=input('Enter the first and last name of the Client : ')
            edad=int(input('Enter the Age: '))
            objetivo=input('Enter the Objective: ')
            email=input('Enter the E-mail: ')
        except ValueError:
            print('Try Again')
            return Create_Client()
        User=Cliente(ID=f'{dni}', Name=f'{name}', Age=f'{edad}', Objetivo=f'{objetivo}', Email=f'{email}')
        print(User)
        session.add(User)
        session.commit()


    def body_data():
        try:
            weight=int(input("Enter the bodyweight in KG: "))
            imc=int(input("Enter the BMI: "))
            bfat=int(input('Enter the BodyFat percentage: '))
            ffmi=int(input("Enter the Free Fat Mass Index :"))
            id=int(input('Enter the Client ID: '))
        except ValueError:
            print("the input only admits numbers")
            return body_data()
        user=Body_Composition(Peso=weight, IMC=imc, BodyFat=bfat, FFMI=ffmi, alumno_id=id)
        session.add(user)
        session.commit()
        print(user)

    def Strength():
        id=input('Enter the Client ID: ')
        bench = input("Enter the RM in Bench: ")
        deadlift = input("Enter the RM in Deadlift: ")
        squat = input("Enter the RM in Squat: ")
        cambios_fuerza = {
            'parent_id': [f'{id}'],
            'Bench': [f'{bench}'],
            'Deadlift': [f'{deadlift}'],
            'Squat': [f'{squat}']
        }
        df_RM=pd.DataFrame(data=cambios_fuerza)
        df_RM['fecha'] = str(datetime.now())
        df_RM['fecha'] = pd.to_datetime(df_RM.fecha)
        df_RM['Date'] = df_RM['fecha'].dt.date
        df_RM = df_RM.drop(['fecha'], axis=1)
        print(df_RM)
        df_RM.to_sql('Cambio RM', if_exists='append', con=engine, index=False)

    #the next function is for plotting your performance in Bench, Squat , and Deadlifts
    def plot_performance():
        try:
            dni=int(input("Enter the ID: "))
        except ValueError:
            print("Invalid Character, only admit numbers")
            return plot_performance()

        query='select * from "Cambio RM"' \
              'WHERE parent_id={}'.format(dni)
        df=pd.read_sql(query, engine)
        print(df)
        df.plot(x='Date', y=['Bench','Squat','Deadlift'])
        plt.show()


    def general_query():   #by using a SQL query we
        dni=int(input("Enter the ID: "))
        q=session.query(Cliente, Body_Composition, RM).filter(Cliente.ID == Body_Composition.alumno_id == RM.parent_id).filter(
            Cliente.ID == dni
            ).order_by(RM.Bench.desc()).first()
        for i in q:
            print(i)


    def Strength_programs():
        d = str(input("Enter the program you want see: \na-Sheiko begginers\nb-Calgary Barbell\nc-High Frequency by Greg Nuckols\nd-5/3/1 for PL\n\n"))
        #With this I choose the values needed to make the Query in Google Sheet API
        #In S_program the 'S' refers to Strength
        S_program = {
            'a': 'fuerza!A5:U44',
            'b': 'fuerza!A46:AC171',
            'c': 'fuerza!A175:Q215',
            'd': 'fuerza!A218:W231'
        }
        print(S_program[d])
        #making the request to google sheet api where the programs/routines are stored
        request = sheet1.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=S_program[d]).execute()
        #I convert the request to a Dataframe to make a better handle of it
        Datos = request.get('values', [])
        dataframe = pd.DataFrame(Datos)
        dataframe.to_excel('Fuerza.xlsx')  #I make this if just in case do you want to download the Sheet in your device
        print(dataframe)

    #Create_client()
    #Delete_record()
    #general_query()
    #consultar()
    #modify_data()
    #plot_performance()
    #Strength()
    #body_data()
    #Strength_programs()
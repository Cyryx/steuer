############################################################################
# ABSCHNITT 1: Importiere notwendige Module und initialisiere Flask-App
############################################################################

# Importiere Flask-Modul
from datetime import datetime
from flask import flash, request, send_from_directory
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, request, redirect, url_for
# Importiere SQLAlchemy-Modul
from sqlalchemy import create_engine
# Importiere Datei-Modul
import os
# Importiere Python-Logging-Modul
import logging

# Erstelle Flask-App
app = Flask(__name__)

# Initialisiere SQLAlchemy-Engine
engine = create_engine("sqlite:///database.db")

# Erstelle SQLAlchemy-Session
Session = sessionmaker(bind=engine)
session = Session()

# Erstelle Logger-Instanz
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Erstelle Datei-Handler und setze Format
file_handler = logging.FileHandler("app.log")
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
file_handler.setFormatter(formatter)
# Füge Datei-Handler zum Logger hinzu
logger.addHandler(file_handler)

############################################################################
# ABSCHNITT 1 ENDE
############################################################################
############################################################################
# ABSCHNITT 2: Definiere Flask-Route für Hauptseite
############################################################################

# Definiere Flask-Route für Hauptseite


@app.route("/")
def home():
    # Ermittle alle Krypto-Provider aus der Datenbank
    providers = session.query(Provider).all()
    # Erstelle leere Liste für Transaktionen
    transactions = []
    # Iteriere über alle Provider
    for provider in providers:
        # Füge Transaktionen des Providers zur Liste hinzu
        transactions += session.query(Transaction).filter_by(
            provider_id=provider.id).all()
    # Berechne Gesamtbetrag aller Transaktionen
    total = sum([t.amount for t in transactions])
    # Berechne Gewinn/Verlust aller Transaktionen
    total = sum([t.amount for t in transactions])
    # Berechne Gewinn/Verlust aller Transaktionen
    profit = sum([t.amount - t.price for t in transactions])
    # Sende Daten an Hauptseiten-Template
    return render_template("home.html", transactions=transactions, total=total, profit=profit)

############################################################################
# ABSCHNITT 2 ENDE
############################################################################
############################################################################
# ABSCHNITT 3: Definiere Flask-Route für Aktualisierungsseite
############################################################################

# Definiere Flask-Route für Aktualisierungsseite


@app.route("/update")
def update():
    # Ermittle alle Krypto-Provider aus der Datenbank
    providers = session.query(Provider).all()
    # Iteriere über alle Provider
    for provider in providers:
        # Hole Transaktionen des Providers
        get_transactions(provider)
    # Weiterleitung zur Hauptseite
    return redirect(url_for("home"))

############################################################################
# ABSCHNITT 3 ENDE
############################################################################
############################################################################
# ABSCHNITT 4: Definiere Klassen und Funktionen für Verarbeitung von
# Krypto-Transaktionen
############################################################################

# Importiere abstrakte Basisklasse von SQLAlchemy für Datenmodelle
# Importiere Funktionen für Spalten-Typ-Mapping von SQLAlchemy
# Importiere ORM-Funktionen von SQLAlchemy


# Definiere abstrakte Basisklasse für Datenmodelle
Base = declarative_base()

# Definiere Klasse für Krypto-Transaktionen


class Transaction(Base):
    # Definiere Tabelle "transactions"
    __tablename__ = "transactions"
    # Definiere Spalten
    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer)
    amount = Column(Float)
    currency = Column(String)
    price = Column(Float)
    date = Column(DateTime)
    bought = Column(Boolean)

    def __repr__(self):
        # Rückegabe der Transaktion als String
        return f"<Transaction(provider='{self.provider_id}', amount='{self.amount}', currency='{self.currency}', price='{self.price}', date='{self.date}', bought='{self.bought}')>"

# Definiere Klasse für Krypto-Provider


class Provider(Base):
    # Definiere Tabelle "providers"
    __tablename__ = "providers"
    # Definiere Spalten
    id = Column(Integer, primary_key=True)
    name = Column(String)
    api_key = Column(String)

    def __repr__(self):
        # Rückgabe des Providers als String
        return f"<Provider(name='{self.name}', api_key='{self.api_key}')>"

# Erstelle alle Tabellen
Base.metadata.create_all(bind=engine)

# Definiere Funktion zum Holen von Krypto-Transaktionen


def get_transactions(provider):
    # Importiere Provider-Modul
    module = __import__("providers." + provider.name, fromlist=["providers"])
    # Hole Transaktionen von Provider
    transactions = module.get_transactions(provider.api_key)
    # Iteriere über alle Transaktionen
    for transaction in transactions:
        # Erstelle neue Transaktion
        t = Transaction(provider_id=provider.id, amount=transaction["amount"],
                currency=transaction["currency"], price=transaction["price"], date=datetime.strptime(
                    transaction["date"], "%Y-%m-%d %H:%M:%S"), bought=transaction["bought"])
        # Füge Transaktion zur Datenbank hinzu
        session.add(t)
        # Speichere Änderungen
        session.commit()

############################################################################
# ABSCHNITT 5: Starte Flask-App
############################################################################

# Setze Debug-Modus der Flask-App
app.debug = True
# Starte Flask-App
app.run()

############################################################################
# ABSCHNITT ENDE
############################################################################

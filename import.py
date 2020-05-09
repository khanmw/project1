import os
from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv

DATABASE_URL="postgres://uqomdazskmxxsr:db2a79e862a3e486ceb8c5b8905ccf5cf9f65931a583e1945d13acdc8bc8dca4@ec2-34-202-7-83.compute-1.amazonaws.com:5432/ddcuv1vgb1p4op"
engine=create_engine(DATABASE_URL)
db =scoped_session(sessionmaker(bind=engine))

def main():
    db.execute('DROP TABLE IF EXISTS users')
    db.execute('DROP TABLE IF EXISTS reviews')
    db.execute('DROP TABLE IF EXISTS books')

    db.execute('CREATE TABLE users ('
               'id SERIAL PRIMARY KEY,'
               'username VARCHAR NOT NULL,'
               'password VARCHAR NOT NULL)'
               )
    db.execute('CREATE TABLE reviews ('
               'isbn VARCHAR NOT NULL,'
               'review VARCHAR NOT NULL,'
               'rating INTEGER NOT NULL,'
               'username VARCHAR NOT NULL)'
               )
    db.execute('CREATE TABLE books ('
               'isbn VARCHAR PRIMARY KEY,'
               'title VARCHAR NOT NULL,'
               'author VARCHAR NOT NULL,'
               'year VARCHAR NOT NULL)'
               )
    f=open(r"C:\Temp\books.csv")
    reader = csv.reader(f)
    for isbn,title,author,year in reader:
        if year == "year":
            print('ignore header')
        else:
            db.execute('INSERT INTO books ('
                       'isbn, title, author, year)'
                       'VALUES (:a,:b,:c,:d)',
                            {'a':isbn,
                             'b':title,
                             'c':author,
                             'd':year
                            }
                       )
    db.commit()

if __name__ == "__main__":
    main()
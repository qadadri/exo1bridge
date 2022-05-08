from flask import Flask, request, render_template, jsonify
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import sqlite3

app = Flask(__name__)


@app.before_first_request
def parsing():
    reg = re.compile(r"(<[\/]?br[\/]?>)+")
    page = requests.get('https://fr.wikipedia.org/wiki/Liste_de_ponts_d%27Italie').text
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find('table', class_="wikitable sortable")
    table_text = re.sub(reg, "\n", str(table))
    df = pd.read_html(table_text)
    df = pd.concat(df)
    df = df.drop(df.columns[[0, 1, -1]], axis=1)
    conn = sqlite3.connect('bridge_db') 
    df.to_sql('bridges', conn, if_exists='replace', index = False)   
    conn.commit()
    conn.close()

@app.route('/')
def show_page():
    conn = sqlite3.connect('bridge_db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM bridges") 
    df_show = pd.DataFrame(cur.fetchall(), columns=[i[0] for i in cur.description])
    result = df_show.to_html().replace("class=", "id=") 
    conn.commit()
    conn.close()
    return(render_template('index.html' ,result=result))

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
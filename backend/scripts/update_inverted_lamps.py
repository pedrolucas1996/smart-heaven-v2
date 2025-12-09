#!/usr/bin/env python3
"""Mark L_Quarto as inverted in the database."""
import pymysql

conn = pymysql.connect(
    host='192.168.31.153',
    user='pedro',
    password='395967',
    database='smartheaven'
)

try:
    cur = conn.cursor()
    
    # Mark L_Quarto as inverted
    cur.execute("UPDATE lampada SET invertido = 1 WHERE nome = 'L_Quarto'")
    conn.commit()
    print(f'✓ Updated {cur.rowcount} row(s) - L_Quarto marked as inverted')
    
    # Show all lamps
    cur.execute('SELECT nome, estado, invertido FROM lampada ORDER BY nome')
    rows = cur.fetchall()
    
    print('\n📋 All lamps:')
    print('-' * 50)
    for nome, estado, invertido in rows:
        inv_flag = '⚡ INVERTED' if invertido else ''
        print(f'{nome:20} | estado={estado} | invertido={invertido} {inv_flag}')
    
    cur.close()
finally:
    conn.close()

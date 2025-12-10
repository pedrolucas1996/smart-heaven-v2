#!/usr/bin/env python3
"""Check lamp states in database."""
import pymysql

conn = pymysql.connect(
    host='192.168.31.153',
    user='pedro',
    password='395967',
    database='smartheaven'
)

try:
    cur = conn.cursor()
    cur.execute('SELECT nome, estado, invertido FROM lampada ORDER BY nome')
    rows = cur.fetchall()
    
    print('🔦 Estado das lâmpadas no banco:')
    print('=' * 70)
    for nome, estado, invertido in rows:
        # Se invertido=1, o display inverte: estado=0 mostra LIGADA
        display_state = "🟢 LIGADA" if (invertido and not estado) or (not invertido and estado) else "⚫ APAGADA"
        inv_flag = " (⚡invertido)" if invertido else ""
        print(f'{nome:20} | DB estado={estado} | {display_state}{inv_flag}')
    
    cur.close()
finally:
    conn.close()

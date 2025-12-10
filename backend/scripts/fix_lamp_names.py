"""Fix lamp name case inconsistencies."""
import pymysql

conn = pymysql.connect(
    host='192.168.31.153',
    user='pedro',
    password='395967',
    database='smartheaven'
)

cur = conn.cursor()

print("Corrigindo nomes de lâmpadas...")
print("-" * 60)

# Update L_Mesa to lowercase L_mesa
cur.execute("UPDATE lampada SET nome = 'L_mesa' WHERE nome = 'L_Mesa'")
print(f"✓ Renomeado L_Mesa → L_mesa ({cur.rowcount} registro)")

# Update L_Mesa_Amarela to lowercase
cur.execute("UPDATE lampada SET nome = 'L_mesa_amarela' WHERE nome = 'L_Mesa_Amarela'")
print(f"✓ Renomeado L_Mesa_Amarela → L_mesa_amarela ({cur.rowcount} registro)")

# Update apelido for L_mesa_amarela
cur.execute("UPDATE lampada SET apelido = 'MesaAma' WHERE nome = 'L_mesa_amarela'")
print(f"✓ Atualizado apelido de L_mesa_amarela")

conn.commit()

print("-" * 60)
print("Verificando lâmpadas atualizadas...")

cur.execute("SELECT id, nome, apelido, estado FROM lampada WHERE nome LIKE '%mesa%' ORDER BY nome")
rows = cur.fetchall()
for r in rows:
    print(f"ID={r[0]:2} | {r[1]:20} | Apelido: {r[2]:15} | Estado: {r[3]}")

cur.close()
conn.close()

print("\n✅ Correções concluídas!")

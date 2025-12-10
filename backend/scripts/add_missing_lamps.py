"""Script to add missing lamps to the database."""
import pymysql

# Database connection
conn = pymysql.connect(
    host='192.168.31.153',
    user='pedro',
    password='395967',
    database='smartheaven'
)

cur = conn.cursor()

# Get Base_B ID (most of these lamps are on Base_B)
cur.execute("SELECT id FROM base WHERE nome = 'Base_B'")
base_b_id = cur.fetchone()[0]

# Lamps to add
new_lamps = [
    ('L_Antessala', 'Antessala', base_b_id),
    ('L_Balcao', 'Balcao', base_b_id),
    ('L_Cozinha', 'Cozinha', base_b_id),
    ('L_CozinhaGeral', 'CozinhaG', base_b_id),  # Master lamp for group
    ('L_mesa', 'mesa', base_b_id),  # lowercase version
    ('L_mesa_amarela', 'mesaAma2', base_b_id),  # lowercase version
]

print("Adicionando lâmpadas faltantes...")
print("-" * 60)

for nome, apelido, base_id in new_lamps:
    # Check if lamp already exists
    cur.execute("SELECT id FROM lampada WHERE nome = %s", (nome,))
    existing = cur.fetchone()
    
    if existing:
        print(f"✓ {nome:20} já existe (ID={existing[0]})")
    else:
        # Insert new lamp
        cur.execute(
            """INSERT INTO lampada (base_id, nome, apelido, estado, invertido) 
               VALUES (%s, %s, %s, 0, 0)""",
            (base_id, nome, apelido)
        )
        conn.commit()
        print(f"✓ {nome:20} adicionada com apelido '{apelido}'")

print("-" * 60)
print("Verificando lâmpadas cadastradas...")

cur.execute("SELECT COUNT(*) FROM lampada")
total = cur.fetchone()[0]
print(f"Total de lâmpadas: {total}")

cur.close()
conn.close()

print("\n✅ Script concluído!")

"""
Script para criar backup do banco de dados MySQL
"""
import pymysql
from datetime import datetime
import os
import sys

# Adiciona o diretório pai ao path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.core.config import settings
from sqlalchemy.engine.url import make_url

def backup_database():
    """Cria um backup completo do banco de dados"""
    
    # Parse da URL do banco de dados
    db_url = make_url(settings.DATABASE_URL.replace("+aiomysql", ""))
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_smartheaven_{timestamp}.sql'
    backup_path = os.path.join(os.path.dirname(__file__), '..', backup_file)
    
    print(f"Criando backup do banco de dados em: {backup_file}")
    print(f"Conectando em: {db_url.host}:{db_url.port}/{db_url.database}")
    
    try:
        # Conecta ao banco de dados
        connection = pymysql.connect(
            host=db_url.host,
            port=db_url.port or 3306,
            user=db_url.username,
            password=db_url.password,
            database=db_url.database,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        with open(backup_path, 'w', encoding='utf8') as f:
            # Cabeçalho do backup
            f.write(f"-- MySQL Backup\n")
            f.write(f"-- Database: {db_url.database}\n")
            f.write(f"-- Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"--\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")
            
            # Obtém todas as tabelas
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            print(f"Fazendo backup de {len(tables)} tabelas...")
            
            for table in tables:
                print(f"  - {table}")
                
                # Estrutura da tabela
                cursor.execute(f"SHOW CREATE TABLE `{table}`")
                create_table = cursor.fetchone()[1]
                f.write(f"--\n-- Table structure for `{table}`\n--\n\n")
                f.write(f"DROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_table};\n\n")
                
                # Dados da tabela
                cursor.execute(f"SELECT * FROM `{table}`")
                rows = cursor.fetchall()
                
                if rows:
                    f.write(f"--\n-- Data for table `{table}`\n--\n\n")
                    f.write(f"LOCK TABLES `{table}` WRITE;\n")
                    
                    # Obtém os nomes das colunas
                    cursor.execute(f"DESCRIBE `{table}`")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    for row in rows:
                        values = []
                        for value in row:
                            if value is None:
                                values.append('NULL')
                            elif isinstance(value, (int, float)):
                                values.append(str(value))
                            elif isinstance(value, datetime):
                                values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                            else:
                                # Escapa aspas simples
                                escaped = str(value).replace("'", "\\'")
                                values.append(f"'{escaped}'")
                        
                        f.write(f"INSERT INTO `{table}` VALUES ({', '.join(values)});\n")
                    
                    f.write("UNLOCK TABLES;\n\n")
            
            f.write("SET FOREIGN_KEY_CHECKS=1;\n")
        
        print(f"\n✅ Backup criado com sucesso: {backup_file}")
        print(f"   Localização: {os.path.abspath(backup_path)}")
        print(f"   Tamanho: {os.path.getsize(backup_path) / 1024:.2f} KB")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"\n❌ Erro ao criar backup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    backup_database()

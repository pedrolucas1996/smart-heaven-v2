"""
Script para testar o sistema de autenticação.
Execute após criar a tabela de usuários no banco.
"""
import asyncio
import httpx


BASE_URL = "http://localhost:8000/api/v1"


async def test_authentication():
    """Testa todo o fluxo de autenticação."""
    async with httpx.AsyncClient() as client:
        print("🧪 Testando Sistema de Autenticação\n")
        
        # 1. Registrar novo usuário
        print("1️⃣ Registrando novo usuário...")
        register_data = {
            "username": "admin",
            "email": "admin@smartheaven.com",
            "password": "admin123"
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/auth/register",
                json=register_data
            )
            
            if response.status_code == 201:
                user = response.json()
                print(f"   ✅ Usuário criado: {user['username']} ({user['email']})")
            elif response.status_code == 400:
                print(f"   ⚠️  Usuário já existe (isso é normal)")
            else:
                print(f"   ❌ Erro: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Erro ao registrar: {e}")
            return
        
        # 2. Fazer login
        print("\n2️⃣ Fazendo login...")
        login_data = {
            "username": register_data["username"],
            "password": register_data["password"]
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                data=login_data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data["access_token"]
                print(f"   ✅ Login bem-sucedido!")
                print(f"   🔑 Token: {access_token[:50]}...")
            else:
                print(f"   ❌ Erro no login: {response.text}")
                return
        except Exception as e:
            print(f"   ❌ Erro ao fazer login: {e}")
            return
        
        # 3. Obter dados do usuário
        print("\n3️⃣ Obtendo dados do usuário autenticado...")
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = await client.get(
                f"{BASE_URL}/auth/me",
                headers=headers
            )
            
            if response.status_code == 200:
                user = response.json()
                print(f"   ✅ Dados obtidos com sucesso!")
                print(f"   👤 Usuário: {user['username']}")
                print(f"   📧 Email: {user['email']}")
                print(f"   🟢 Ativo: {user['is_active']}")
                print(f"   📅 Criado em: {user['created_at']}")
            else:
                print(f"   ❌ Erro ao obter dados: {response.text}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        # 4. Testar token inválido
        print("\n4️⃣ Testando token inválido...")
        headers = {"Authorization": "Bearer token_invalido"}
        
        try:
            response = await client.get(
                f"{BASE_URL}/auth/me",
                headers=headers
            )
            
            if response.status_code == 401:
                print(f"   ✅ Token inválido corretamente rejeitado!")
            else:
                print(f"   ⚠️  Resposta inesperada: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Erro: {e}")
        
        print("\n" + "="*50)
        print("✅ Todos os testes concluídos!")
        print("="*50)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏠 Smart Heaven v2 - Teste de Autenticação")
    print("="*50 + "\n")
    print("⚠️  Certifique-se de que:")
    print("  1. O banco de dados está rodando")
    print("  2. A tabela 'users' foi criada")
    print("  3. O backend está rodando (porta 8000)")
    print("")
    
    try:
        asyncio.run(test_authentication())
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")

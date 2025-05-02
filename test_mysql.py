import mysql.connector
import socket
from datetime import datetime
import time

def check_port(host, port):
    try:
        print(f"Tentando conectar em {host}:{port}...")
        start_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            result = s.connect_ex((host, port))
            elapsed = time.time() - start_time
            print(f"Resultado do teste de porta: {result} (tempo: {elapsed:.2f}s)")
            return result == 0
    except Exception as e:
        print(f"Erro no teste de porta: {e}")
        return False

def test_connection():
    config = {
        'host': '127.0.0.1',
        'user': 'pythonuser',
        'password': 'senha123',
        'port': 3306,
        'auth_plugin': 'caching_sha2_password',  # Alterado para o plugin moderno
        'connect_timeout': 5,
        'buffered': True,
        'ssl_disabled': True  # Adicionado para evitar problemas SSL
    }   
    
    print(f"\nTeste iniciado em: {datetime.now()}")
    
    # Verificação detalhada da porta
    print("\n[1/3] Verificando porta 3306...")
    port_open = check_port(config['host'], config['port'])
    
    if not port_open:
        print("\n❌ Falha crítica: Porta MySQL não respondendo")
        print("👉 Soluções:")
        print("1. Verifique se o MySQL está rodando (services.msc)")
        print("2. Confira se o firewall não está bloqueando (netsh advfirewall firewall show rule name=all)")
        return
    
    print("\n✅ Porta 3306 está aberta e respondendo")
    
    # Teste de conexão com MySQL
    print("\n[2/3] Testando conexão com MySQL...")
    try:
        start_time = time.time()
        print("Iniciando conexão...")
        conn = mysql.connector.connect(**config)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Conexão bem-sucedida! (tempo: {elapsed:.2f}s)")
        print(f"Versão do servidor: {conn.get_server_info()}")
        
        # Teste de consulta básica
        print("\n[3/3] Testando consulta básica...")
        cursor = conn.cursor()
        cursor.execute("SELECT 1+1")
        result = cursor.fetchone()
        print(f"Resultado da consulta: {result[0]}")
        
        conn.close()
        print("\n🎉 Todos os testes passaram com sucesso!")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Erro na conexão (código: {err.errno}):")
        print(f"Mensagem: {err.msg}")
        
        if err.errno == 1045:  # Access denied
            print("\n👉 Soluções para erro de acesso:")
            print("1. Verifique usuário/senha")
            print("2. Execute no MySQL:")
            print("   ALTER USER 'pythonuser'@'localhost' IDENTIFIED WITH mysql_native_password BY 'novasenha';")
            print("   FLUSH PRIVILEGES;")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("=== TESTE DE CONEXÃO MYSQL ===")
    test_connection()
    input("\nPressione Enter para sair...")
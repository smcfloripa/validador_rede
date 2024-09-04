import time
import json
import os
import psutil
from ping3 import ping
import speedtest
from datetime import datetime

# Caminho para salvar o arquivo JSON
DATA_FILE = 'dados.json'

# Função para carregar o arquivo JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    return {'conexao': [], 'maquina': []}

# Função para salvar dados no arquivo JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

# Função para formatar bytes em MB, GB, etc.
def format_size(bytes_value):
    # Converte bytes para um formato legível (MB, GB, etc.)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024

# Função para verificar status da rede
def check_network():
    hostname = "8.8.8.8"  # Google DNS
    response_time = ping(hostname, timeout=2)
    
    if response_time:
        print(f"Conexão estável. Tempo de resposta: {response_time:.2f} ms")
        return response_time
    else:
        print("Conexão instável ou sem conexão.")
        return None

# Função para realizar o Speedtest
def run_speedtest():
    print("Executando Speedtest...")
    st = speedtest.Speedtest()

    # Seleciona o melhor servidor
    st.get_best_server()

    # Faz o teste de download e upload
    download_speed = st.download() / 1_000_000  # Convertendo para Mbps
    upload_speed = st.upload() / 1_000_000      # Convertendo para Mbps
    ping_result = st.results.ping

    print(f"Ping: {ping_result:.2f} ms")
    print(f"Velocidade de download: {download_speed:.2f} Mbps")
    print(f"Velocidade de upload: {upload_speed:.2f} Mbps")
    
    return {
        "data_hora": datetime.now().isoformat(),
        "ping": ping_result,
        "download_speed_mbps": download_speed,
        "upload_speed_mbps": upload_speed
    }

# Função para coletar informações sobre o sistema
def get_system_info():
    print("Coletando informações da máquina...")

    # Uso de CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # Memória
    memory = psutil.virtual_memory()
    memory_percent = memory.percent
    
    # Disco (Leitura e Escrita)
    disk_io = psutil.disk_io_counters()
    read_bytes = format_size(disk_io.read_bytes)  # Formatar para tamanho legível
    write_bytes = format_size(disk_io.write_bytes)  # Formatar para tamanho legível
    
    # Rede
    net_io = psutil.net_io_counters()
    bytes_sent = format_size(net_io.bytes_sent)  # Formatar para tamanho legível
    bytes_recv = format_size(net_io.bytes_recv)  # Formatar para tamanho legível

    return {
        "data_hora": datetime.now().isoformat(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory_percent,
        "disk_read": read_bytes,
        "disk_write": write_bytes,
        "network_sent": bytes_sent,
        "network_recv": bytes_recv
    }

def main():
    # Carregar dados existentes do arquivo JSON
    data = load_data()
    
    # Tempo para rodar as verificações
    network_check_interval = 3600  # 1 hora para o Speedtest
    system_check_interval = 900    # 15 minutos para o monitoramento da máquina

    last_network_check = time.time() - network_check_interval
    last_system_check = time.time() - system_check_interval

    while True:
        current_time = time.time()

        # Verificar conexão e realizar Speedtest a cada 1 hora
        if current_time - last_network_check >= network_check_interval:
            print("Verificando status da rede...")
            response_time = check_network()
            if response_time is not None:
                # Executar o Speedtest se a rede estiver estável
                speedtest_data = run_speedtest()
                data['conexao'].append(speedtest_data)
                save_data(data)
            last_network_check = current_time

        # Coletar informações da máquina a cada 15 minutos
        if current_time - last_system_check >= system_check_interval:
            system_data = get_system_info()
            data['maquina'].append(system_data)
            save_data(data)
            last_system_check = current_time

        # Dormir por 1 minuto antes de checar novamente
        time.sleep(60)

if __name__ == "__main__":
    main()

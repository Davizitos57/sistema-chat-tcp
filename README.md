# Jogo da Velha Online (TCP/SSL com Descoberta Automática)

Este projeto consiste num sistema de Jogo da Velha multijogador que utiliza sockets TCP para a comunicação, criptografia SSL para segurança e um protocolo de descoberta automática via UDP Broadcast para facilitar a conexão em redes locais.

## 📋 Pré-requisitos

* **OpenSSL** instalado (necessário para gerar os certificados de segurança).
* As máquinas devem estar conectadas à **mesma rede local**.

## 🔐 Configuração de Segurança (Certificados)

O servidor exige uma conexão segura (SSL/TLS). Para que ele inicie corretamente, deves gerar um par de chaves (`cert.pem` e `key.pem`) na pasta raiz do servidor.

No teu terminal `/jogo_da_velha_socket`, executa o seguinte comando:

```bash
openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
```

Nota: Quando solicitado, pode pressionar Enter em todos os campos. Somente no **"Comum Name"** que deve ser passado o valor **"localhost"**

## 📡 Configuração de Rede e Firewall

Para que as máquinas se encontrem automaticamente através do sinal de broadcast, deves permitir o tráfego nas seguintes portas no Firewall do Windows/Linux:
* Porta 5000 (TCP): Conexão principal do jogo e tráfego de dados SSL.
* Porta 5001 (UDP): Sinal de descoberta automática (Broadcast).

## 🚀 Como Executar
**1. Iniciar o Servidor**

No computador que servirá como host da partida, execute dentro de `/jogo_da_velha_socket`:
```
python servidor.py
```
O servidor começará a escutar conexões e a enviar sinais de presença na rede local através da porta UDP 5001.

**2. Iniciar os Clientes**

Em qualquer computador da rede (incluindo o próprio computador do servidor), dentro de `/jogo_da_velha_socket` execute:

```
python cliente.py
```

O cliente exibirá a mensagem "A procurar servidor na rede local..." no terminal. Assim que o sinal do servidor for detectado, o IP será configurado automaticamente e a interface gráfica do jogo será aberta.

## 🛠️ Tecnologias Utilizadas
* **Socket (TCP/UDP):** Comunicação robusta entre processos em rede.
* **SSL/TLS:** Camada de segurança para criptografia de ponta a ponta dos dados transmitidos.
* **Threading:** Gerenciamento de múltiplos clientes, timers de jogada e descoberta em segundo plano.
* **Tkinter:** Interface gráfica nativa para a experiência do usuário.

## 📂 Estrutura de Arquivos
* `servidor.py`: Gerencia a lógica do jogo, validação de jogadas, turnos, vitórias e o anúncio do servidor na rede.
* `cliente.py`: Interface do usuário, tabuleiro interativo e lógica de descoberta dinâmica de IP.
* `cert.pem / key.pem`: Arquivos de certificado e chave privada necessários para o túnel SSL.
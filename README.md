# Almox-System

Sistema de Correspondências + Empréstimo de Ferramentas

## Descrição

O Almox-System é uma aplicação web desenvolvida para gerenciar operações de almoxarifado, incluindo o controle de correspondências (mails) e empréstimos de ferramentas. O sistema permite registrar, rastrear e atualizar o status de correspondências, além de gerenciar empréstimos e devoluções de ferramentas com captura de fotos e logs detalhados.

## Funcionalidades

### Correspondências (Mails)
- **Registro de Correspondências**: Cadastro de novas correspondências com código de rastreio, nome, fantasia, tipo, prioridade e status.
- **Recebimento**: Atualização do status ao receber correspondências, incluindo informações de recebedor e liberador.
- **Envio e Devolução**: Registro de envios e devoluções com captura de imagens e extração de texto via OCR da Google Vision.
- **Consulta**: Busca e listagem de correspondências com filtros e ordenação.

### Empréstimo de Ferramentas
- **Registro de Ferramentas**: Cadastro e gerenciamento de ferramentas disponíveis.
- **Empréstimo e Devolução**: Check-out e check-in de ferramentas com captura automática de fotos.
- **Logs de Movimentação**: Registro detalhado de todas as movimentações, incluindo data, hora e tipo (saída/entrada).
- **Relatórios**: Visualização de ferramentas emprestadas e histórico de movimentações.
- **Marcação como Perdida**: Possibilidade de marcar ferramentas como perdidas.

## Tecnologias Utilizadas

- **Backend**: Python com Flask
- **Banco de Dados**: SQLite
- **Real-time**: Flask-SocketIO com Eventlet
- **OCR**: Extração de texto de imagens para processamento de correspondências
- **Câmera**: Integração com serviço de câmera para captura de fotos
- **Frontend**: HTML, CSS, JavaScript
- **Outros**: SQLite3, Datetime, Shutil, Re

## Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/seu-usuario/almox-system.git
   cd almox-system
   ```

2. **Instale as dependências**:
   Certifique-se de ter Python 3.x instalado. Instale as bibliotecas necessárias:
   ```bash
   pip install flask flask-socketio eventlet
   ```

3. **Configure o banco de dados**:
   O banco de dados SQLite (`almoxarifado.sqlite`) já está incluído. Se necessário, ajuste o caminho no código.

4. **Execute o servidor**:
   ```bash
   python server.py
   ```
   O servidor será iniciado na porta 80 (host 0.0.0.0).

## Uso

- Acesse a aplicação no navegador: `http://localhost` (ou o IP do servidor).
- **Página Inicial**: Gerenciamento de correspondências.
- **Ferramentas**: Acesse `/tool-loans/` para empréstimos de ferramentas.
- **Registros**: Visualize logs e relatórios em `/tool-loans/registers`.

## Estrutura do Projeto

- `server.py`: Arquivo principal do servidor Flask.
- `static/`: Arquivos estáticos (CSS, JS, imagens).
- `templates/`: Templates HTML.
- `static/py/`: Módulos Python auxiliares (sqlite_core, cam_service, imareocr).
- `pictures/`: Diretório para armazenar imagens capturadas.
- `almoxarifado.sqlite`: Banco de dados SQLite.

## Contribuição

Contribuições são bem-vindas! Siga estes passos:

1. Fork o projeto.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`).
4. Push para a branch (`git push origin feature/nova-feature`).
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Contato

Para dúvidas ou sugestões, entre em contato com a equipe de desenvolvimento.

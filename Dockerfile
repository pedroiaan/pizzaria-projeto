# Usar a imagem base do Python
FROM python:3.12-slim

# Definir o diretório de trabalho
WORKDIR /app

# Atualizar o pip e instalar as bibliotecas necessárias
RUN pip install --upgrade pip && \
    pip install bottle eventlet python-socketio reportlab jinja2 pytz filelock beaker werkzeug




COPY . .

EXPOSE 8080

# Comando para executar a aplicação
CMD ["python3", "route.py"]


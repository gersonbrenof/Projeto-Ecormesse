# Imagem base com Python 3.11 slim
FROM python:3.11-slim

# Variável ambiente para não criar arquivos .pyc e para saída de logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias (exemplo: gcc, libs para psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiar código do projeto
COPY . .

# Rodar coleta de arquivos estáticos do Django
RUN python manage.py collectstatic --noinput

# Expôr a porta que o gunicorn vai usar
EXPOSE 8000

# Comando para rodar gunicorn, ouvindo em todas as interfaces na porta 8000
CMD ["gunicorn", "lojaproject.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

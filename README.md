## Instalação

### 1. Clone o repositório:

```bash
git clone https://github.com/gersonbrenof/Projeto-Ecormesse
cd GerenciadorTarefasAPI
python -m venv venv
source venv/bin/activate   # Para sistemas Linux/Mac
venv\Scripts\activate    # PARA WINDOWS
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

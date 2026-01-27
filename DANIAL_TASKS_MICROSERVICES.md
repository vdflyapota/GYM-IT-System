# Danial's Tasks - Microservices Architecture

## 🚨 ВАЖНО: Изменение архитектуры!

**Профессор требует микросервисную архитектуру, иначе проект не пройдет!**

Yazan переделывает проект на микросервисы. Это значит, что вместо одного монолитного приложения будет несколько отдельных сервисов.

---

## 📚 Что такое микросервисы? (Простыми словами)

**Было (монолит):**
```
Одно приложение:
- main.py (все роутеры вместе)
- routers/auth.py
- routers/tournaments.py
- routers/challenges.py
- routers/notifications.py
```

**Стало (микросервисы):**
```
Отдельные сервисы:
- auth-service/ (Yazan)
- tournament-service/ (ТЫ - Danial)
- challenge-service/ (Yeldana)
- notification-service/ (Shattyk)
- frontend/ (общий)
```

**Каждый сервис:**
- Имеет свой собственный код
- Работает на своем порту
- Имеет свою базу данных (или общую, но изолированную схему)
- Может быть развернут отдельно
- Общается с другими сервисами через HTTP API

---

## 🎯 Твоя новая задача: Tournament Service

### Структура, которую нужно создать:

```
tournament-service/
├── main.py                 # FastAPI приложение для Tournament
├── requirements.txt        # Зависимости
├── Dockerfile              # Контейнеризация
├── database.py             # Подключение к БД
├── models/
│   └── tournament_models.py
├── routers/
│   └── tournaments.py      # API endpoints
├── schemas.py              # Pydantic схемы
└── .env                    # Конфигурация (порт, БД)
```

### Порты сервисов (примерно):
- `auth-service`: порт 8001
- `tournament-service`: порт 8002 (ТВОЙ)
- `challenge-service`: порт 8003
- `notification-service`: порт 8004
- `frontend`: порт 3000

---

## ✅ Что нужно сделать (по приоритету):

### 1. 🔴 СРОЧНО: Создать Tournament Service

**Шаг 1: Создать структуру сервиса**

Создай папку `tournament-service/` и перенеси туда:
- `routers/tournaments.py` → `tournament-service/routers/tournaments.py`
- `models/tournament_models.py` → `tournament-service/models/tournament_models.py`
- Tournament схемы из `schemas.py` → `tournament-service/schemas.py`

**Шаг 2: Создать main.py для сервиса**

```python
# tournament-service/main.py
from fastapi import FastAPI
from database import engine, Base
from models import tournament_models
from routers import tournaments

# Создать таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tournament Service",
    description="Microservice for Tournament Management",
    version="1.0.0"
)

app.include_router(tournaments.router)
```

**Шаг 3: Настроить database.py**

```python
# tournament-service/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Используй отдельную БД для tournament service
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tournament.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Шаг 4: Создать requirements.txt**

```txt
fastapi
uvicorn
sqlalchemy
pydantic
```

**Шаг 5: Запустить сервис**

```bash
cd tournament-service
uvicorn main:app --reload --port 8002
```

---

### 2. 🟡 Docker для Tournament Service

**Создать Dockerfile:**

```dockerfile
# tournament-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

**Обновить docker-compose.yml (глобальный):**

Yazan должен создать общий `docker-compose.yml`, который запускает все сервисы:

```yaml
version: '3.8'

services:
  tournament-service:
    build: ./tournament-service
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=sqlite:///./tournament.db
    volumes:
      - ./tournament-service:/app

  auth-service:
    # Yazan делает
    
  challenge-service:
    # Yeldana делает
    
  notification-service:
    # Shattyk делает
    
  frontend:
    # Общий
```

---

### 3. 🟢 Kubernetes для Tournament Service

**Создать k8s/tournament-service-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tournament-service
spec:
  replicas: 3  # Для масштабируемости
  selector:
    matchLabels:
      app: tournament-service
  template:
    metadata:
      labels:
        app: tournament-service
    spec:
      containers:
      - name: tournament-service
        image: tournament-service:latest
        ports:
        - containerPort: 8002
        env:
        - name: DATABASE_URL
          value: "sqlite:///./tournament.db"
        livenessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8002
          initialDelaySeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: tournament-service
spec:
  selector:
    app: tournament-service
  ports:
  - port: 8002
    targetPort: 8002
  type: ClusterIP
```

---

### 4. 🔵 API Gateway / Service Communication

**Важно:** Сервисы должны общаться друг с другом!

**Пример: Tournament Service вызывает Auth Service для проверки пользователя:**

```python
# tournament-service/routers/tournaments.py
import httpx

async def verify_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://auth-service:8001/users/{user_id}")
        if response.status_code == 200:
            return response.json()
        return None

@router.post("/tournaments/")
async def create_tournament(t: schemas.TournamentCreate, user_id: int):
    # Проверить, что пользователь существует через auth-service
    user = await verify_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")
    
    # Создать турнир
    # ...
```

---

## 📋 Чеклист задач:

### Phase 1 (СРОЧНО):
- [ ] Создать папку `tournament-service/`
- [ ] Перенести tournament код в отдельный сервис
- [ ] Создать `main.py` для сервиса
- [ ] Настроить `database.py` для сервиса
- [ ] Создать `requirements.txt`
- [ ] Протестировать запуск сервиса на порту 8002
- [ ] Убедиться, что API работает: `http://localhost:8002/docs`

### Phase 2:
- [ ] Создать `Dockerfile` для tournament-service
- [ ] Обновить `docker-compose.yml` (или создать свой)
- [ ] Протестировать `docker-compose up`

### Phase 3:
- [ ] Создать Kubernetes манифесты для tournament-service
- [ ] Настроить replicas (3-5 для масштабируемости)
- [ ] Добавить health checks
- [ ] Протестировать деплой в K8s

### Phase 4:
- [ ] Добавить health endpoint: `GET /health`
- [ ] Настроить общение с auth-service (для проверки пользователей)
- [ ] Настроить общение с notification-service (для уведомлений о матчах)
- [ ] Обновить frontend для работы с tournament-service (порт 8002)

---

## 🔗 Как сервисы общаются:

### Вариант 1: Прямые HTTP вызовы
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("http://auth-service:8001/users/123")
```

### Вариант 2: API Gateway (рекомендуется)
- Один входной порт (например, 8080)
- Gateway маршрутизирует запросы к нужным сервисам
- Frontend обращается только к Gateway

### Вариант 3: Service Mesh (продвинутый)
- Istio, Linkerd
- Для более сложных проектов

---

## 💡 Примеры команд:

### Запустить Tournament Service:
```bash
cd tournament-service
uvicorn main:app --reload --port 8002
```

### Тест API:
```bash
curl http://localhost:8002/tournaments/
curl -X POST http://localhost:8002/tournaments/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "start_date": "2024-01-15T10:00:00", "max_participants": 8}'
```

### Docker:
```bash
cd tournament-service
docker build -t tournament-service .
docker run -p 8002:8002 tournament-service
```

---

## ⚠️ Важные моменты:

1. **Независимость:** Tournament Service должен работать сам по себе
2. **База данных:** Можешь использовать отдельную БД или общую (но изолированную схему)
3. **Порты:** Каждый сервис на своем порту
4. **Общение:** Через HTTP API между сервисами
5. **Ошибки:** Если auth-service недоступен, tournament-service должен обработать это gracefully

---

## 🆘 Что делать сейчас:

1. **Дождись, пока Yazan запушит новую структуру**
2. **Посмотри, как он организовал auth-service** (это будет пример)
3. **Создай tournament-service по аналогии**
4. **Протестируй работу сервиса отдельно**
5. **Интегрируй с docker-compose и Kubernetes**

---

## 📞 Если что-то непонятно:

- Микросервисы = несколько маленьких приложений вместо одного большого
- Каждый сервис делает свою работу (Tournament, Auth, Challenges, Notifications)
- Сервисы общаются через HTTP API
- Это нужно для масштабируемости и чтобы профессор принял проект

**Главное:** Не паникуй! Это просто разделение кода на отдельные части. Логика остается той же, просто код в разных папках.

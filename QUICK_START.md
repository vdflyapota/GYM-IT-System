# 🚀 Быстрый старт - Tournament Service

## ✅ Что уже сделано:

1. ✅ Создан `tournament-service/` как отдельный микросервис
2. ✅ Dockerfile и docker-compose.yml
3. ✅ Kubernetes манифесты с репликами и HPA
4. ✅ Health endpoint для оркестрации
5. ✅ Полная документация

---

## 📋 Что делать СЕЙЧАС:

### Шаг 1: Протестировать локально

```bash
cd tournament-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

Открой: http://localhost:8002/docs

### Шаг 2: Протестировать Docker

```bash
cd tournament-service
docker-compose up --build
```

Или:
```bash
docker build -t tournament-service .
docker run -p 8002:8002 tournament-service
```

### Шаг 3: Коммитить в GitHub

Следуй плану из `GIT_COMMIT_PLAN.md`:

```bash
# Первый коммит - структура
git add tournament-service/
git commit -m "feat: create tournament-service microservice structure

- Add tournament-service as independent microservice
- Port 8002, separate database
- FastAPI application with health endpoint
- Part of microservices architecture refactoring"

git push
```

---

## 🎯 План коммитов (минимум для показа активности):

### Коммит 1: Структура
```bash
git add tournament-service/main.py tournament-service/database.py tournament-service/requirements.txt
git commit -m "feat: initialize tournament-service microservice"
```

### Коммит 2: Модели и API
```bash
git add tournament-service/models/ tournament-service/schemas.py tournament-service/routers/
git commit -m "feat: add tournament API endpoints and data models"
```

### Коммит 3: Docker
```bash
git add tournament-service/Dockerfile tournament-service/docker-compose.yml tournament-service/.dockerignore
git commit -m "feat: add Docker containerization for tournament-service"
```

### Коммит 4: Kubernetes
```bash
git add tournament-service/k8s/
git commit -m "feat: add Kubernetes deployment with HPA for scalability"
```

### Коммит 5: Документация
```bash
git add tournament-service/README.md
git commit -m "docs: add tournament-service documentation"
```

---

## 📊 Что это покажет преподавателю:

✅ **Микросервисная архитектура** - отдельный сервис  
✅ **Docker** - контейнеризация  
✅ **Kubernetes** - оркестрация с репликами  
✅ **Scalability** - HPA для масштабирования  
✅ **Активность** - коммиты в GitHub  

---

## 🔥 Быстрый тест (1 минута):

```bash
# 1. Запустить сервис
cd tournament-service
uvicorn main:app --port 8002 &

# 2. Проверить health
curl http://localhost:8002/health

# 3. Создать турнир
curl -X POST "http://localhost:8002/tournaments/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "start_date": "2024-01-15T10:00:00", "max_participants": 8}'

# 4. Посмотреть список
curl http://localhost:8002/tournaments/
```

---

## 💡 Следующие шаги (когда Yazan готов):

1. Интегрировать с auth-service (проверка пользователей)
2. Интегрировать с notification-service (уведомления о матчах)
3. Обновить frontend для работы с портом 8002
4. Добавить API Gateway (опционально)

---

## ⚠️ Важно:

- **НЕ коммить** `.db` файлы
- **Коммить** код, Docker, K8s, документацию
- **Делай коммиты постепенно** - покажи активность
- **Пиши понятные сообщения** - что сделал и зачем

---

## 📞 Если что-то не работает:

1. Проверь, что порт 8002 свободен
2. Проверь зависимости: `pip install -r requirements.txt`
3. Проверь логи: `uvicorn main:app --reload --port 8002`
4. Проверь Docker: `docker-compose logs`

---

**Готово! Теперь у тебя есть полноценный микросервис, который можно коммитить в GitHub! 🎉**

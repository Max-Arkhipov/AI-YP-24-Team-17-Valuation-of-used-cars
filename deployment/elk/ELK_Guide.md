
# Подробный гайд ELK-стека (Elasticsearch, Logstash, Kibana)

## Требования

Для развертывания ELK-стека вам потребуется:

- **Docker** и **Docker Compose** (установите их, если ещё не сделано)

---

## Шаги по настройке и запуску

### 1. Настройте конфигурационные файлы

Эти файлы задают основные параметры для Elasticsearch, Logstash и Kibana
Все файлы должны находиться в директории `elk/`

#### **elasticsearch.yml**

Конфигурация для Elasticsearch:

```yaml
http.host: "0.0.0.0"
xpack.security.enabled: false
xpack.license.self_generated.type: basic
```

- `http.host` позволяет слушать все подключения
- `xpack.security.enabled` отключает встроенную безопасность!!!
- `xpack.license.self_generated.type` устанавливает бесплатную лицензию Basic

#### **kibana.yml**

Конфигурация для Kibana:

```yaml
server.name: kibana
server.host: "0.0.0.0"
elasticsearch.hosts: ["http://elasticsearch:9200"]
elasticsearch.username: "test_user"
elasticsearch.password: "MyPw123"
```

- `server.host` позволяет подключаться к интерфейсу Kibana из любой сети
- `elasticsearch.hosts` задаёт адрес Elasticsearch.
- `elasticsearch.username` и `elasticsearch.password` используются для аутентификации

#### **logstash.yml**

Конфигурация для Logstash:

```yaml
api.http.host: "0.0.0.0"
xpack.monitoring.enabled: true
xpack.monitoring.elasticsearch.hosts: ["http://elasticsearch:9200"]
```

- `api.http.host` открывает HTTP API Logstash
- `xpack.monitoring.enabled` включает мониторинг Logstash
- `xpack.monitoring.elasticsearch.hosts` указывает адрес Elasticsearch для мониторинга

#### **logstash-nginx.conf**

Пример конвейера Logstash для сбора логов:

```plaintext
input {
  tcp {
    port => 5000
    codec => json_lines { target => "logstash_data" }
  }
}
output {
  elasticsearch {
    hosts => ["http://elasticsearch:9200"]
    index => "backend-logs-%{+YYYY.MM.dd}"
  }
  stdout {
    codec => rubydebug
  }
}
```

- Входные данные принимаются по порту `5000`. (Важно чтобы не был занят другим процессом)
- Логи отправляются в Elasticsearch в индекс с именем `backend-logs-YYYY.MM.dd`

---

### 2. Создайте **docker-compose.yml**

Этот файл объединяет все компоненты в одном стеке

```yaml
version: "3.9"
services:
  elasticsearch:
    image: elasticsearch:8.17.0
    container_name: es
    environment:
      discovery.type: single-node
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
      ELASTIC_USERNAME: "test_user"
      ELASTIC_PASSWORD: "MyPw123"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - ./elk/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml
      - ./els/data:/usr/share/elasticsearch/data

  logstash:
    image: logstash:8.17.0
    container_name: logstash
    depends_on:
      - elasticsearch
    ports:
      - "5000:5000"
    volumes:
      - ./elk/logstash.yml:/usr/share/logstash/config/logstash.yml
      - ./elk/logstash-nginx.conf:/usr/share/logstash/pipeline/logstash-nginx.config

  kibana:
    image: kibana:8.17.0
    container_name: kibana
    depends_on:
      - elasticsearch
    ports:
      - "5601:5601"
    volumes:
      - ./elk/kibana.yml:/usr/share/kibana/config/kibana.yml
```

---

### 3. Запустите стек

Используйте следующую команду для запуска всех контейнеров:

```bash
docker-compose up -d
```

### Альтернативный способ загрузки образов Docker вручную

Если образы Elasticsearch, Logstash и Kibana не загружаются автоматически, выполните команды для их загрузки:

```bash
docker pull elasticsearch:8.17.0
docker pull logstash:8.17.0
docker pull kibana:8.17.0
```

После загрузки повторно запустите `docker-compose up -d`

---

## Проверка

### Тестирование Logstash

Используйте файл `test_logstash.py` в папке `backend/tests/` для тестирования конфигурации Logstash. Запустите его командой:

```bash
python backend/tests/test_logstash.py
```

### Доступ к сервисам

- **Elasticsearch**: [http://localhost:9200](http://localhost:9200) (логин: `test_user`, пароль: `MyPw123`)
- **Kibana**: [http://localhost:5601](http://localhost:5601)

---

## Полезные команды

### Управление контейнерами Docker

- Запуск контейнеров: `docker-compose up -d`
- Остановка контейнеров: `docker-compose down`
- Перезапуск контейнеров: `docker-compose restart`
- Проверка состояния: `docker ps`

### Логи контейнеров

- Просмотр логов контейнера:

  ```bash
  docker logs <container_name>
  ```

- Потоковое отображение логов:

  ```bash
  docker logs -f <container_name>
  ```

### Elasticsearch

- Проверка доступности:

  ```bash
  curl -u test_user:MyPw123 http://localhost:9200
  ```

- Список индексов:

  ```bash
  curl -u test_user:MyPw123 http://localhost:9200/_cat/indices?v
  ```

### Logstash

- Тестирование конфигурации:

  ```bash
  docker exec -it logstash logstash --config.test_and_exit -f /usr/share/logstash/pipeline/logstash-nginx.config
  ```

### Kibana

- Перезапуск:

  ```bash
  docker restart kibana
  ```

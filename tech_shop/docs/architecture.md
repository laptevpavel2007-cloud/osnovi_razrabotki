# Архитектура системы

## Обзор
Проект построен по принципу **слоистой архитектуры** с явным разделением ответственности. Бизнес-логика полностью отделена от слоя представления.

```mermaid
graph TD
    subgraph Presentation Layer
        UI[app/main.py<br/>Tkinter GUI]
    end
    
    subgraph Domain Layer
        CORE[packages/core<br/>Бизнес-логика и сервисы]
    end
    
    subgraph Data Layer
        DB[(SQLite DB<br/>store.db)]
        CSV[data/*.csv]
    end

    UI -->|Вызов методов| CORE
    CORE -->|SQL запросы| DB
    CORE -->|Чтение при инициализации| CSV

## 1. Основные сущности (Entities)

Доменная модель разделена на справочные данные и транзакционные данные.

### 1.1. Справочные сущности

#### Employee (Сотрудник)
Представляет работника магазина.
* **Атрибуты:**
  * `id_employee` (Integer, PK): Уникальный идентификатор.
  * `name` (Text): Имя.
  * `surname` (Text): Фамилия.
  * `id_job_title` (Integer, FK): Ссылка на должность.
* **Бизнес-смысл:** Сотрудник, который может выступать в роли кассира при оформлении чека.

#### JobTitle (Должность)
Справочник должностей сотрудников.
* **Атрибуты:**
  * `id_job_title` (Integer, PK): Уникальный идентификатор.
  * `name` (Text): Название должности (например, "Кассир", "Продавец-консультант").

#### Category (Категория товара)
Группировка товаров по типу.
* **Атрибуты:**
  * `id_category` (Integer, PK): Уникальный идентификатор.
  * `name_category` (Text): Название категории (например, "Бытовая техника", "Комплектующие для ПК").

#### Product (Товар)
Основная сущность каталога.
* **Атрибуты:**
  * `id_product` (Integer, PK): Уникальный идентификатор (SKU).
  * `name_of_product` (Text): Полное наименование товара.
  * `price` (Real): Розничная цена в рублях.
  * `id_category` (Integer, FK): Ссылка на категорию.
  * `quantity_at_storage` (Real): Текущий физический остаток на складе.

### 1.2. Транзакционные сущности

#### Receipt (Чек / Продажа)
Факт совершения покупки, зафиксированный в системе.
* **Атрибуты:**
  * `id_check` (Integer, PK): Уникальный номер чека.
  * `created_at` (Real): Точное время создания (timestamp).
  * `date` (Text): Строковое представление даты (YYYY-MM-DDTHH:MM:SS).
  * `id_cashier` (Integer, FK): Идентификатор сотрудника, оформившего продажу.

#### SaleItem (Позиция чека)
Конкретный товар в составе чека.
* **Атрибуты:**
  * `id_sale` (Integer, PK): Уникальный идентификатор позиции.
  * `id_check` (Integer, FK): Ссылка на родительский чек.
  * `id_product` (Integer, FK): Ссылка на проданный товар.
  * `quantity` (Real): Количество проданного товара.
  * `date` (Text): Дата продажи (для удобства агрегации статистики).

#### Return (Возврат товара)
Факт частичного или полного возврата товара из продажи.
* **Атрибуты:**
  * `id_return` (Integer, PK): Уникальный идентификатор возврата.
  * `id_sale` (Integer, FK): Ссылка на конкретную позицию чека (`SaleItem`), из которой делается возврат.
  * `return_date` (Real): Точное время возврата.
  * `date` (Text): Строковое представление даты.
  * `quantity_returned` (Real): Количество возвращенных единиц.
  * `reason` (Text): Текстовая причина возврата (например, "Брак", "Не подошёл").


## 2. Схема связей (ERD)

Связи между сущностями реализованы через механизм внешних ключей (Foreign Keys) в SQLite.

```mermaid
erDiagram
    JOBS_TITLES ||--o{ EMPLOEES : "assigns"
    EMPLOEES ||--o{ RESEIPTS : "processes"
    CATEGORIES ||--o{ PRODUCRS : "groups"
    PRODUCRS ||--o{ SALE_ITEMS : "included_in"
    RESEIPTS ||--o{ SALE_ITEMS : "contains"
    SALE_ITEMS ||--o{ RETURNS : "generates"

    JOBS_TITLES {
        int id_job_title PK
        string name
    }
    
    EMPLOEES {
        int id_employee PK
        string name
        string surname
        int id_job_title FK
    }
    
    CATEGORIES {
        int id_category PK
        string name_category
    }
    
    PRODUCRS {
        int id_product PK
        string name_of_product
        float price
        int id_category FK
        float quantity_at_storage
    }
    
    RESEIPTS {
        int id_check PK
        float created_at
        string date
        int id_cashier FK
    }
    
    SALE_ITEMS {
        int id_sale PK
        int id_check FK
        int id_product FK
        float quantity
        string date
    }
    
    RETURNS {
        int id_return PK
        int id_sale FK
        float return_date
        float quantity_returned
        string reason
    }
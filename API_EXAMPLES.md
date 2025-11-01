# Примеры использования API

## Базовый URL

```
http://127.0.0.1:8000/api/
```

## Документация API

- Swagger UI: http://127.0.0.1:8000/api/docs/
- ReDoc: http://127.0.0.1:8000/api/redoc/

## 1. Получение списка категорий

### Все категории

```bash
curl -X GET "http://127.0.0.1:8000/api/categories/"
```

### Поиск категории по названию

```bash
curl -X GET "http://127.0.0.1:8000/api/categories/?search=Шарф"
```

### Получение конкретной категории

```bash
curl -X GET "http://127.0.0.1:8000/api/categories/1/"
```

## 2. Расчет юнит-экономики

### Пример запроса (режим габаритов)

```bash
curl -X POST "http://127.0.0.1:8000/api/calculate/" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 21,
    "price": 805,
    "weight": 0.15,
    "dimension_mode": "dimensions",
    "length": 27,
    "width": 24,
    "height": 2,
    "tax_rate": 6,
    "buyout_rate": 90,
    "delivery_time": 45,
    "ad_costs_rate": 10,
    "cost_price": 215,
    "other_costs": 10,
    "monthly_sales": 1000
  }'
```

### Пример запроса (режим объема)

```bash
curl -X POST "http://127.0.0.1:8000/api/calculate/" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 21,
    "price": 805,
    "weight": 0.15,
    "dimension_mode": "volume",
    "volume": 1.296,
    "tax_rate": 6,
    "buyout_rate": 90,
    "delivery_time": 45,
    "ad_costs_rate": 10,
    "cost_price": 215,
    "other_costs": 10,
    "monthly_sales": 1000
  }'
```

## 3. Пример ответа

```json
{
  "fbo_results": {
    "scheme": "FBO",
    "price": "805.00",
    "price_percent": "100.00",
    "ozon_reward": "-112.70",
    "ozon_reward_percent": "14.00",
    "acquiring": "-16.10",
    "acquiring_percent": "2.00",
    "processing_delivery": "-88.88",
    "processing_delivery_percent": "11.04",
    "returns_cancellations": "-8.05",
    "returns_cancellations_percent": "1.00",
    "total_ozon_costs": "-225.73",
    "total_ozon_costs_percent": "28.04",
    "profit_before_costs": "579.27",
    "profit_before_costs_percent": "71.96",
    "cost_price": "-215.00",
    "cost_price_percent": "26.71",
    "profit_tax": "-21.86",
    "profit_tax_percent": "2.72",
    "other_costs": "-10.00",
    "other_costs_percent": "1.24",
    "net_profit_per_unit": "332.41",
    "net_profit_per_unit_percent": "41.29",
    "net_profit_total": "332410.00"
  },
  "fbs_results": {
    "scheme": "FBS",
    "price": "805.00",
    "price_percent": "100.00",
    "ozon_reward": "-112.70",
    "ozon_reward_percent": "14.00",
    "acquiring": "-16.10",
    "acquiring_percent": "2.00",
    "processing_delivery": "-88.88",
    "processing_delivery_percent": "11.04",
    "returns_cancellations": "-8.05",
    "returns_cancellations_percent": "1.00",
    "total_ozon_costs": "-225.73",
    "total_ozon_costs_percent": "28.04",
    "profit_before_costs": "579.27",
    "profit_before_costs_percent": "71.96",
    "cost_price": "-215.00",
    "cost_price_percent": "26.71",
    "profit_tax": "-21.86",
    "profit_tax_percent": "2.72",
    "other_costs": "-10.00",
    "other_costs_percent": "1.24",
    "net_profit_per_unit": "332.41",
    "net_profit_per_unit_percent": "41.29",
    "net_profit_total": "332410.00"
  }
}
```

## 4. Коды ответов

- `200 OK` - Успешный расчет
- `400 Bad Request` - Ошибка валидации входных данных
- `404 Not Found` - Категория не найдена
- `500 Internal Server Error` - Ошибка при расчете

## 5. Параметры запроса

### category_id
ID категории товара. Можно получить из `/api/categories/`

### price
Цена товара в рублях (decimal, min: 0.01)

### weight
Вес товара в килограммах (decimal, min: 0.001)

### dimension_mode
Режим ввода размеров:
- `dimensions` - Ввод габаритов (длина, ширина, высота)
- `volume` - Прямой ввод объема

### length, width, height
Габариты товара в сантиметрах (обязательны для режима `dimensions`)

### volume
Объем товара в литрах (обязателен для режима `volume`)

### tax_rate
Налог на прибыль в процентах (0-100)

### buyout_rate
Процент выкупа (0-100)

### delivery_time
Время доставки в часах (integer, min: 1)

### ad_costs_rate
Доля рекламных расходов в процентах (0-100)

### cost_price
Себестоимость за 1 штуку в рублях (decimal, min: 0)

### other_costs
Прочие затраты на 1 штуку в рублях (decimal, min: 0)

### monthly_sales
Количество продаж в месяц в штуках (integer, min: 1)














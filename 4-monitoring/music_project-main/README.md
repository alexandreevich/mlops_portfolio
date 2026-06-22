# Репозиторий для обучения основам мониторинга

В качестве модели для мониторинга используется сервис рекомендации музыкальных треков.

## Для начала работы:

1. Убедитесь, что в папке app актуальный код для работы с FastAPI сервисом;
2. Убедитесь. что существует файл docker-compose.yaml с необходимыми настройками
3. Деплойте свой сервис на ВМ!

```bash
docker compose up -d
```

### Тестовые запросы к сервису рекомендаций музыкальных треков:
Делаем запрос по треку Yellow Submarine: 

    Внимание адрес 127.0.0.1 только для локальных запросов!
```bash
curl -X 'GET' \
  'http://127.0.0.1:8081/api/recommend/?track_title=Yellow%20Submarine&n=5' \
  -H 'accept: application/json'
```
На выходе должны получить что-то вот такое:
```
{
  "requested_track": "Love",
  "recommendations": [
    {
      "track_name": "No One",
      "artists": "Alicia Keys",
      "album_name": "As I Am (Expanded Edition)"
    },
    {
      "track_name": "Wild (feat. Gary Clark Jr.)",
      "artists": "John Legend;Gary Clark Jr.",
      "album_name": "Bigger Love"
    },
    {
      "track_name": "You & I (Nobody in the World)",
      "artists": "John Legend",
      "album_name": "Love In The Future (Expanded Edition)"
    },
    {
      "track_name": "Forrest Gump",
      "artists": "Frank Ocean",
      "album_name": "channel ORANGE"
    },
    {
      "track_name": "Girl on Fire",
      "artists": "Alicia Keys",
      "album_name": "Girl on Fire (Remixes) - EP"
    }
  ],
  "similarity_scores": [
    1,
    1,
    0.99,
    0.99,
    0.99
  ]
}
```


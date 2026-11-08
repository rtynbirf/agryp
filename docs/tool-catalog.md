# 📚 ЕДИНЫЙ КАТАЛОГ ИНСТРУМЕНТОВ-ИСПОЛНИТЕЛЕЙ — ПОЛНЫЙ СВОД (v3)

**Источники:** `unified_tool_catalog.md` (1159) + все дополнения из `инструмменты.txt` (включая ранее веб-верифицированную версию v2 на 2075 позиций).

**Метод («антигаллюцинации»):** полная дедупликация по нормализованным именам (регистр/пробелы/дефисы/подчёркивания/точки не учитываются); уверенные алиасы склеены; записи, которые сам источник пометил как сомнительные («(?)», «СТОП! галлюцинирую»-зоны), удалены; все новые Python-пакеты проверены по официальному реестру PyPI (единичные непроверяемые имена исключены с указанием причины — см. Приложение). Категории и инструменты внутри каждой категории отсортированы по алфавиту.

**Всего инструментов:** 2444  
**Категорий:** 34

> Примечание: `fabric (AI)` и `fabric`, `ollama (client)` и `ollama`, `dash (shell)` и `dash` — это разные инструменты-однофамильцы (AI-агент и SSH-библиотека; CLI-клиент и Python-клиент; оболочка и Plotly Dash), а не неудаляемые дубликаты.

---

## 1. Agent/MCP/LLM-инфраструктура

| Инструмент | Описание |
|-----------|----------|
| mcp-registry | каталог/обнаружение MCP-серверов |
| OpenAI Agents SDK | агентный runtime, tools, handoffs, tracing |

## 2. AI/LLM CLI-инструменты

| Инструмент | Описание |
|-----------|----------|
| aichat | Универсальный чат с LLM в терминале |
| aider | AI-парное программирование (git-интеграция) |
| amp | Агентный AI-кодинг от Sourcegraph (ampcode.com) |
| claude | Anthropic Claude CLI |
| cline | AI coding agent с доступом к терминалу, файлам, браузеру и MCP |
| codex | OpenAI Codex CLI |
| continue | CLI для Continue.dev (AI-ассистент кодинга) |
| copilot | GitHub Copilot CLI (агентный кодинг в терминале) |
| crush | AI-кодинг-агент для терминала (Charmbracelet) |
| cursor-agent | Cursor Agent CLI (агентный кодинг в терминале) |
| droid | Factory Droid — AI-кодинг-агент в терминале |
| elia | Клавиатурно-ориентированный TUI для LLM (Textual) |
| fabric (AI) | AI-фреймворк с паттернами промптов (Daniel Miessler; не путать с Python-библиотекой Fabric для SSH) |
| garak | LLM vulnerability scanner |
| gemini | Google Gemini CLI (открытый AI-агент в терминале) |
| gh-copilot | GitHub Copilot в CLI (через gh extension) |
| goose | Открытый расширяемый AI-агент (Block) |
| gptme | Автономный агент-ассистент в терминале |
| Grok CLI | CLI-агент от xAI |
| Kilo CLI | CLI-агент от Kilo Code |
| kilocode | ~20k stars, объединил функции Roo Code + Cline |
| Kimi CLI | Moonshot AI terminal agent |
| llama-bench | Бенчмарк производительности локальных LLM |
| llama-cli | CLI-инференс локальных LLM (llama.cpp) |
| llama-cpp | от ggerganov, основа многих локальных инструментов |
| llama-server | OpenAI-совместимый локальный сервер LLM (llama.cpp) |
| llamafile | Запуск LLM одним исполняемым файлом (Mozilla) |
| llm | Simon Willison's llm (универсальный фронтенд к API) |
| llm-cli | универсальный интерфейс к LLM API |
| lm-studio | Графический интерфейс для локальных LLM |
| localai | ~25k stars, mudler, поддержка CPU/CUDA/ROCm/Metal |
| mcp-cli | Клиент протокола Model Context Protocol — расширение возможностей AI-агентов |
| mcp-inspector | инспекция, тестирование и отладка MCP-серверов |
| mistral-vibe | Терминальный coding agent Mistral |
| mods | Charmbracelet's AI в терминале |
| ollama | Pull/run/ps/rm моделей локально |
| open-interpreter | Интерпретатор с LLM (выполняет код) |
| opencode | Открытый AI-кодинг-агент в терминале (sst) |
| OpenHands | Autonomous sandboxed platform (Docker, CI) |
| oterm | TUI-клиент для Ollama и локальных LLM |
| Pi | ~54k stars (по данным обзора 2026), Armin Ronacher & Mario Zechner. Менее известен, данные из единственного массового обзора |
| plandex | AI-движок разработки для крупных проектов в терминале |
| Qwen Code | Qwen Code — терминальный AI coding agent |
| semantic-kernel | SDK и CLI-подход к оркестрации AI-агентов Microsoft |
| sgpt | Генерация shell-команд через LLM (shell-gpt) |
| shell-gpt | Генерация shell-команд через LLM |
| swe-agent | SWE-agent-v2, академический, sandboxed Docker |
| tabby | Self-hosted AI coding assistant и сервер автодополнения |
| terminal-jarvis | CLI-агент с интерфейсом Jarvis |
| tgpt | ChatGPT в терминале без API-ключа |

## 3. Python-библиотеки

| Инструмент | Описание |
|-----------|----------|
| accelerate | Ускорение и распределение PyTorch (Hugging Face) |
| agno | Фреймворк AI-агентов (бывш. phidata) |
| aio-pika | Асинхронный клиент RabbitMQ |
| aiobotocore | AWS SDK (async) |
| aiofiles | Асинхронная работа с файлами |
| aiogram | Боты для Telegram |
| aiohttp | Асинхронный HTTP-клиент и сервер |
| aiomysql | Клиент MySQL (async) |
| aioquic | Реализация QUIC и HTTP/3 |
| aioredis | Клиент Redis (async) |
| aiosmtplib | Асинхронный SMTP клиент |
| aiosqlite | Асинхронный SQLite |
| airflow | Оркестрация data pipelines |
| albumentations | Быстрая аугментация изображений |
| alembic | Миграции для SQLAlchemy |
| algoliasearch | Algolia Search API |
| alive-progress | Прогресс-бары |
| altair | Декларативная визуализация |
| annotated-types | Type hints с аннотациями |
| ansible | Инфраструктурная автоматизация |
| ansible-core | Инфраструктурная автоматизация |
| anthropic | Официальный SDK к API LLM |
| anyio | Асинхронный фреймворк (основа httpx/starlette) |
| apache-libcloud | Единый API к облакам: VM, storage, DNS, LB |
| apispec | Генерация OpenAPI-спецификаций из кода |
| apprise | Отправка уведомлений в 100+ сервисов (единый API) |
| apscheduler | Планировщик задач в процессе (cron-подобный) |
| argon2-cffi | Хеширование паролей Argon2 |
| argostranslate | Офлайн нейронный перевод (OpenNMT) |
| argparse | Создание CLI |
| arq | Асинхронная очередь задач на Redis |
| arrow | Человеко-дружелюбные даты |
| asana | Таск-трекеры |
| astropy | Астрономия: координаты, время, FITS |
| asyncpg | Клиент PostgreSQL (async) |
| asyncpraw | Reddit API |
| asyncua | OPC UA |
| atlassian-python-api | Jira и Confluence API |
| atproto | SDK Bluesky / AT Protocol |
| attrs | Классы без шаблонного кода (декларативные) |
| austin | Визуализация и sampling-профилировщики |
| authlib | OAuth 1/2, OIDC, JWT-клиенты и серверы |
| autoflake | Удаление неиспользуемых импортов и переменных |
| autogen | Мультиагентные разговорные системы (Microsoft) |
| autopep8 | Форматирование и линтинг |
| azure-identity | Microsoft Azure SDK |
| azure-storage-blob | Microsoft Azure SDK |
| backtrader | Бэктестинг торговых стратегий |
| bandit | Линтеры и сканер безопасности |
| bcrypt | Хеширование паролей bcrypt |
| beanie | Асинхронный ODM MongoDB на pydantic |
| beartype | O(1) runtime-проверка типов |
| BeautifulSoup | Парсинг HTML |
| beautifulsoup4 | Парсинг HTML (правильное имя) |
| biopython | Биоинформатика: последовательности, BLAST, PDB |
| black | Форматирование и линтинг |
| bleak | Bluetooth Low Energy (кроссплатформенный, async) |
| blessed | TUI для терминала |
| bokeh | Интерактивная визуализация |
| boto3 | AWS SDK |
| botocore | Низкоуровневый AWS SDK |
| bottle | Однофайловый WSGI-фреймворк |
| bpy | Blender как Python-модуль (headless) |
| braintree | Платёжные API |
| browser-use | Браузерная автоматизация для AI-агентов |
| cachetools | Кэши (LRU, TTL, LFU) |
| cairosvg | Конвертация SVG в PNG/PDF |
| camel | Multi-agent framework (CAMEL-AI), агентные общества, synthetic data |
| camelot-py | Извлечение таблиц из PDF |
| captum | Объяснимость моделей PyTorch |
| cassandra-driver | Клиент Cassandra/DataStax |
| catboost | Градиентный бустинг |
| category_encoders | Кодирование категориальных признаков |
| ccxt | Единый API к 100+ криптобиржам |
| cdk8s | Infrastructure as Code |
| cdktf | Infrastructure as Code |
| celery | Distributed task queues |
| censys | SDK Censys (данные о хостах и сертификатах) |
| certifi | Пакет сертификатов CA (root certificates) |
| cffi | C Foreign Function Interface (вызов C код из Python) |
| chromadb | Клиент векторных БД |
| cirq | Квантовые схемы (Google) |
| clearml | ML-трекинг |
| click | Создание CLI |
| cloudscraper | Обход Cloudflare-антибота |
| cohere | SDK Cohere (embed, rerank, chat) |
| colorama | Цвета и стили вывода (кроссплатформенно, включая Windows) |
| commitizen | Стандартизация commit-сообщений |
| concurrencytest | Тестирование параллелизма |
| configparser | Парсинг конфигов (встроенный) |
| confluent-kafka | Официальный высокопроизводительный клиент Kafka |
| connectorx | Чтение БД с ускорением |
| connexion | Spec-first фреймворк из OpenAPI |
| control | Теория управления (python-control) |
| cookiecutter | Шаблонизация проектов |
| copier | Шаблонизация проектов |
| coqui-tts | Нейронный TTS (продолжение Mozilla TTS) |
| coverage.py | Измерение покрытия кода |
| cprofile | Профилирование производительности |
| crc32c | CRC32C checksum (быстро) |
| crewai | Мульти-агентные фреймворки (библиотека) |
| croniter | Парсинг cron-выражений в Python |
| cryptography | Криптопримитивы и X.509 (pyca) |
| curl_cffi | HTTP с подменой TLS-отпечатков браузеров |
| customtkinter | Современный вид Tkinter |
| cvxpy | Выпуклая оптимизация |
| cyclopts | Современный декларативный CLI-фреймворк |
| cython | Компиляция Python-подобного кода в C |
| dagster | Оркестрация data pipelines |
| daphne | ASGI/HTTP2-сервер (Django Channels) |
| darts | Удобное прогнозирование (модели от ARIMA до N-BEATS) |
| dash | Быстрые веб-интерфейсы для ML |
| dask | Параллельные вычисления над большими данными |
| dataclasses-json | Двусторонняя сериализация dataclasses |
| datasets | Датасеты и метрики Hugging Face |
| datasette | Публикация SQLite как JSON API |
| datashader | Растеризация больших объёмов точек на графиках |
| dateparser | Даты из естественного языка (мультиязычно) |
| db-url | Парсинг DATABASE_URL переменных |
| dbm | БД shelve/dbm (встроенный) (модуль stdlib) |
| deap | Эволюционные алгоритмы и генетическое программирование |
| dearpygui | GPU-ускоренный GUI для инструментов |
| deep-translator | Перевод и словари (много провайдеров) |
| deepdiff | Глубокое сравнение и поиск изменений объектов |
| deepeval | Юнит-тесты для LLM-выходов |
| deepface | Анализ лиц: верификация, возраст, эмоции |
| deepspeed | масштабирование AI-моделей |
| demjson | JSON5 парсер |
| demucs | Разделение трека на стемы (Meta) |
| deptry | Поиск устаревших/неиспользуемых зависимостей |
| diagrams | Диаграммы облачной архитектуры как код |
| diff-match-patch | Diff и patch операции |
| difflib | Сравнение последовательностей (встроенный) (модуль stdlib) |
| diffusers | Диффузионные модели: генерация изображений/аудио |
| dill | Сохранение функций и лямбда-выражений (pickle++) |
| dirtree | Вывод структуры каталогов |
| dirty-equals | Читаемые частичные сравнения в тестах |
| discord.py | Боты для Discord |
| diskcache | Дисковый кэш с SQLite-метаданными |
| django | Классический web-фреймворк |
| dlib | Детекция лиц и объектов, landmarks |
| dnspython | DNS-запросы |
| docker | Docker SDK |
| docker-compose | Docker SDK |
| docopt | CLI-парсер прямо из docstring |
| docx2txt | Извлечение текста из .doc |
| docxtpl | Шаблоны Word через Jinja2 |
| dopamine-rl | DeepMind Dopamine RL framework |
| dotenv-python | Загрузка переменных из .env |
| dramatiq | Distributed task queues |
| drission | Браузерная автоматизация |
| dspy | Программирование LLM-пайплайнов вместо промптов (Stanford) |
| dtale | Интерактивный просмотр DataFrame в браузере |
| dulwich | Программная работа с Git |
| dynaconf | Многоисточниковая конфигурация (env, toml, vault) |
| ebooklib | Создание и чтение EPUB |
| editdistance | Расстояние Левенштейна (быстро) |
| elasticsearch-dsl | Клиент Elasticsearch |
| email | Работа с email-протоколами |
| email-validator | Строгая валидация email-адресов |
| emoji | Данные эмодзи: поиск, замена, демоизации |
| encodings | Встроенные кодировки (модуль stdlib) |
| ensurepip | Pip инсталлер (встроенный) (модуль stdlib) |
| environs | Управление переменными окружения |
| errorhandler | Обработка ошибок с контекстом |
| etcd3 | etcd v3 клиент |
| exchangelib | Microsoft Exchange |
| fabric | SSH-автоматизация |
| face_recognition | Простое распознавание лиц (на dlib) |
| facebook-sdk | Facebook Graph API |
| factory_boy | Фабрики тестовых данных |
| faiss | Быстрый векторный поиск миллиардов векторов (Meta) |
| fake-useragent | Ротация актуальных User-Agent |
| faker | Генерация фейковых данных |
| fakeredis | Мокирование БД |
| falcon | Минималистичный REST-фреймворк |
| fastapi | Веб-фреймворк |
| fastdiff | Быстрое вычисление diff |
| fastdownload | Быстрое скачивание (fastai) |
| fastembed | Лёгкие локальные эмбеддинги (ONNX) |
| fasteners | Файловые блокировки |
| faster-whisper | Whisper в 4 раза быстрее (CTranslate2) |
| fastkml | KML парсер (географический) |
| fasttext | Классификация текста и эмбеддинги (Meta) |
| feature-engine | Библиотека трансформаций признаков |
| featuretools | Автоматический feature engineering (DFS) |
| feedparser | Парсинг RSS/Atom |
| fiftyone | Курирование и оценка датасетов компьютерного зрения |
| fiona | Геопространственный анализ |
| fire | Создание CLI |
| fireworks | Workflow-оркестрация |
| flair | NLP-фреймворк: NER, POS, эмбеддинги (Zalando) |
| flake8 | Линтеры и сканер безопасности |
| flask | Классический web-фреймворк |
| flask-migrate | Миграции БД в Flask (Alembic) |
| flask-restful | REST API построение в Flask |
| flax | Дифференцируемые вычисления (Google) |
| flet | Flutter-подобные интерфейсы на чистом Python |
| fn-py | Функциональное программирование в Python |
| fonttools | Работа с шрифтами (.ttf, .otf) |
| forking | Fork функциональность |
| fpdf2 | Простое создание PDF |
| freezegun | Мокирование времени |
| frost | Объекты с freeze поддержкой |
| frozendict | Неизменяемый словарь |
| ftfy | Исправление битого Unicode (mojibake) |
| funcy | Прагматичные функциональные утилиты |
| furl | Удобный парсинг URL |
| future | Совместимость Python 2 и 3 (legacy) |
| fuzzywuzzy | Нечёткий поиск строк (fuzzy matching) |
| gambit | Решение игр (game theory) |
| gamepad | Работа с геймпадом |
| gamma | Гамма-функции и специальные функции |
| gaphas | Диаграммные инструменты (Dia format) |
| gardenpy | Управление садом (IoT проект) |
| gatepy | Gate контроль доступа |
| gauge | Манометр визуализация |
| gaussianblur | Размытие Гаусса (PIL) |
| gazpacho | Веб-скреипинг (удобнее BeautifulSoup) |
| gdal | Работа с геоспациальными данными (GDAL bindings) |
| gdelt | GDELT (Global Database of Events) |
| gdiff | Визуальный diff |
| gdrive | Google Drive API (неофициальный) |
| gensim | Тематическое моделирование, word2vec |
| geocoder | Геокодирование (множество провайдеров) |
| geofence | Геофенсинг |
| geograph | Географические графы |
| geohash | Кодирование географических координат |
| geoip | IP геолокация |
| geoip2 | MaxMind GeoIP2 API |
| geojson | GeoJSON парсинг и валидация |
| geopandas | Геопространственный анализ |
| geopy | Геокодирование и расчёт расстояний |
| geopython | Родной python геопространственный код |
| georasters | Растровые географические данные |
| geosplit | Разделение географических областей |
| gerby | Кешированием модули (?) |
| gestate | Формирование состояния |
| getch | Получение символа без ввода |
| geturl | Получение URL-а |
| gevent | Кооперативная многозадачность на greenlet |
| gfx | Графика (различные реализации) |
| ggplot | Grammar of Graphics (похоже на R ggplot2) |
| ghapi | GitHub API |
| ghexplorer | Исследователь GitHub |
| ghl | GitHub Linguist (определение языка кода) |
| ghstars | GitHub звёзды трекер |
| ghtoken | GitHub token управление |
| ghviz | GitHub визуализация |
| giant | Большие объекты (?) |
| giantbomb | Giant Bomb (видеоигры база) |
| gibberish | Фильтр спама |
| gibe | Насмешка / таскание файлов |
| giblets | Обрезки данных |
| giddy | Геопространственный анализ динамики |
| giffer | GIF создание |
| gigapixel | Гигапиксельные изображения |
| gild | Позолоченные объекты |
| giles | Управление библиотеками (GILES) |
| gillespie | Алгоритм Гиллеспи (стохастика) |
| gitlab | GitLab API |
| gitpython | Программная работа с Git |
| glfw | OpenGL Window Framework (python-glfw) |
| glob2 | Расширенный glob с recursive |
| glom | Цепочки трансформаций вложенных данных |
| gnureadline | GNU readline в Python |
| goatools | Gene Ontology анализ |
| google-adk | Agent Development Kit для Gemini (Google) |
| google-api-python-client | Универсальный Google API client |
| google-auth | Аутентификация Google (OAuth2, service accounts) |
| google-cloud-bigquery | Google Cloud SDK |
| google-cloud-storage | Google Cloud SDK |
| google-cloud-translate | Google Cloud Translate API |
| google-cloud-vision | Google Cloud Vision API (распознавание изображений) |
| google-genai | Новый единый SDK Google для Gemini |
| google-generativeai | Официальный SDK к API LLM |
| google-search-results | Google SerpAPI парсер |
| goose3 | Извлечение основного содержимого статей |
| gpiozero | Raspberry Pi GPIO |
| gptcache | Кеширование LLM запросов |
| gpustat | Мониторинг NVIDIA GPU |
| gradients | Вычисление градиентов |
| gradio | Быстрые веб-интерфейсы для ML |
| granian | ASGI/WSGI-сервер на Rust |
| graph-tool | Обработка больших графов (C++) |
| graphql-core | GraphQL implementation |
| grapnel | Веб-скрейпинг утилиты |
| grappa | Assertion-фреймворк (Python testing) |
| grass | GRASS GIS Python bindings |
| graviton | Обработка гравитационных данных (?) |
| gravy | Подлива к стаканам (?) - не уверен |
| great-expectations | Валидация данных |
| groq | SDK Groq API (сверхбыстрый инференс) |
| grpc | gRPC - высокопроизводительный RPC фреймворк |
| grpcio | gRPC Python implementation |
| gspread | Работа с Google Sheets |
| gtts | TTS через Google Translate |
| guardrails | Валидация и исправление выходов LLM |
| guidance | Программирование потока генерации LLM (Microsoft) |
| gunicorn | WSGI-сервер |
| gymnasium | Среды обучения с подкреплением (Farama) |
| h11 | HTTP/1.1 парсер |
| h2 | HTTP/2 парсер |
| h5py | Работа с HDF5 |
| haystack | RAG и NLP-пайплайны (deepset) |
| helm | Kubernetes SDK |
| hnswlib | Приближённый kNN-поиск (HNSW) |
| holoviews | Декларативная аннотированная визуализация (HoloViz) |
| html2text | Конвертация HTML в Markdown |
| html5lib | Парсинг HTML |
| httpcore | Низкоуровневый HTTP клиент |
| httptools | Парсинг HTTP (на C++) |
| httpx | HTTP-запросы (синхронный и асинхронный) |
| huey | Лёгкая очередь задач (Redis/SQLite) |
| huggingface-hub | Загрузка моделей из HuggingFace Hub |
| humanize | Человеко-читаемые размеры, числа, время |
| hvac | Клиент HashiCorp Vault |
| hydra-core | Управление конфигурацией приложений (Meta) |
| hypercorn | ASGI-сервер с HTTP/2 и HTTP/3 |
| hypothesis | Property-based testing |
| ib_insync | Асинхронный API Interactive Brokers |
| icalendar | Работа с .ics (iCal) |
| icecream | Дебаг-печать переменных (ic(var)) |
| igraph | Анализ графов и сетей |
| ijson | Потоковый парсинг больших JSON |
| imagehash | Перцептивные хеши изображений |
| imageio | Дополнительные инструменты для изображений |
| imageio-ffmpeg | Видео-манипуляции |
| imagesize | Определение размеров изображений без загрузки |
| imap-tools | Удобные обёртки для email |
| imaplib | Работа с email-протоколами |
| imbalanced-learn | Борьба с дисбалансом классов |
| img2pdf | Lossless-склейка изображений в PDF |
| impacket | Низкоуровневые сетевые протоколы (Windows) |
| importlib-metadata | Метаданные установленных пакетов |
| importlib-resources | Доступ к ресурсам пакета |
| InquirerPy | Интерактивные CLI-диалоги (async) |
| insightface | 2D/3D-анализ лиц (SOTA-модели) |
| instagrapi | Instagram API |
| instaloader | Instagram API |
| instructor | Структурированные выходы LLM через Pydantic |
| ipaddress | IP-адреса |
| ipykernel | IPython-ядро для Jupyter |
| ipywidgets | Интерактивные виджеты в ноутбуках |
| isodate | Парсинг ISO 8601 дат |
| isort | Форматирование и линтинг |
| jax | Дифференцируемые вычисления (Google) |
| jedi | Статический анализ и автодополнение |
| jellyfish | Фонетические алгоритмы и расстояния |
| jieba | Сегментация китайского текста |
| jinja2 | Шаблонизаторы |
| jira | Jira и Confluence API |
| jmespath | Декларативные запросы к JSON |
| joblib | Параллелизм, кэширование (движок sklearn) |
| jsonlines | Чтение/запись JSONL файлов |
| jsonpath | JSON querying |
| jsonpath-ng | JSONPath-запросы к JSON |
| jsonschema | Парсинг конфигов |
| jsonschema-specifications | JSON Schema спецификации |
| jupyter | Мета-пакет экосистемы Jupyter |
| jupyter-client | Клиент Jupyter kernel |
| jupyter-core | Ядро Jupyter |
| jupyterlab | Среда JupyterLab |
| jupytext | Двусторонняя синхронизация .ipynb и Markdown/скриптов |
| kafka-python | Чистый Python клиент Kafka |
| kaleido | Статические экспорт графиков Plotly |
| keras | TensorFlow |
| keyboard | Глобальные хуки клавиатуры |
| keyring | Хранение credentials |
| keywords | Работа с ключевыми словами Python |
| kivy | Мультиплатформенный GUI (мобильный, тач) |
| kornia | Дифференцируемое CV для PyTorch |
| kubernetes | Kubernetes SDK |
| kubetest | Тестирование Kubernetes приложений |
| lab | Юпитер Lab (альтернативное имя) |
| label-studio | Мультиформатное аннотирование данных |
| labelme | Аннотирование изображений (полигоны, маски) |
| lancedb | Встраиваемая векторная БД (columnar) |
| langchain | Оркестраторы (библиотека) |
| langdetect | Определение языка текста |
| langfuse | Трейсинг и наблюдаемость LLM-приложений |
| langgraph | Оркестраторы (библиотека) |
| langsmith | Отладка LangChain приложений |
| lasio | Чтение LAS файлов (скважинные данные) |
| latexcodec | LaTeX кодировка |
| latexify-py | Превращение Python функций в LaTeX |
| lazyxml | Ленивый парсинг XML |
| ldap3 | Клиент LDAP v3 |
| ldb | LDB база данных (SAM database from Windows) |
| ldplayer | Эмулятор Android |
| lease | Управление лизингом (?) |
| lebowski | Ссылка на фильм "The Big Lebowski" (?) |
| leech | Скачивание контента (?) |
| leek | Лук (овощ) - не Python пакет (?) |
| leep | Сон (?) |
| legacy | Поддержка legacy кода |
| leghorn | Порода курицы (?) |
| letta | Агенты с персистентной памятью (бывш. MemGPT) |
| levenshtein | Быстрое расстояние Левенштейна |
| lhafile | Работа с LHA архивами |
| libclang | Python bindings к Clang |
| libcst | Трансформация кода с сохранением форматирования (Meta) |
| libmagic | Определение типа файла (magic numbers) |
| librosa | Аудио-анализ и обработка |
| libusb1 | USB-устройства |
| libzero | Работа с нулевыми значениями (?) |
| license | MIT, Apache и другие лицензии |
| licensename | Определение лицензии проекта |
| licenser | Выдающий лицензию (?) |
| licenses | Множество лицензий |
| licensing | Система лицензирования |
| lightgbm | Градиентный бустинг |
| lightning | Структурирование PyTorch-исследований (PL) |
| lime | Локальные интерпретируемые объяснения |
| line_profiler | Профилирование производительности |
| litellm | Унифицированный интерфейс к 100+ LLM-провайдерам |
| litestar | Современный высокопроизводительный ASGI-фреймворк |
| llama-cpp-python | LLaMA-инференс на CPU/GPU (bindings llama.cpp) |
| llama-parse | Продвинутый парсинг документов |
| llamaindex | RAG-фреймворк (индексация, retrieval) |
| lm-eval | Бенчмаркинг LLM на академических задачах (EleutherAI) |
| lmdb | Lightning Memory-Mapped Database |
| logfury | Логирование с стилизацией |
| logstash-formatter | Форматирование в Logstash JSON |
| loguru | Логирование |
| lxml | Парсинг HTML |
| lzma | Сжатие LZMA (встроенный в Python 3) (модуль stdlib) |
| madmom | Аудио-анализ и обработка |
| mail-parser | Удобные обёртки для email |
| mailgun | Email-рассылки |
| mako | Шаблонизаторы |
| mammoth | Конвертация DOCX в HTML |
| manim | Математические анимации (движок 3Blue1Brown) |
| marimo | reactive Python notebooks |
| markdownify | Парсинг и генерация Markdown |
| marker-pdf | PDF → Markdown (научные статьи) |
| marshmallow | Сериализация и валидация схем |
| Mastodon.py | Клиент Mastodon API |
| matplotlib | Построение графиков |
| matrix-nio | Клиент протокола Matrix |
| mechanicalsoup | Stateful-браузер на BeautifulSoup |
| mechanize | Stateful браузер |
| mediapipe | Кроссплатформенный ML-перцепшн (Google): позы, лица, руки |
| memory_profiler | Профилирование производительности |
| memray | Профилировщик памяти с flamegraphs (Bloomberg) |
| mesa | Агентно-ориентированное моделирование |
| mido | Чтение и запись MIDI |
| mimesis | Генерация фейковых данных |
| minio | Клиент S3-совместимых хранилищ MinIO |
| missingno | Визуализация пропусков в данных |
| mistralai | SDK Mistral AI |
| mistune | Парсинг и генерация Markdown |
| mlflow | эксперименты и развертывание ML |
| mlxtend | Ассоциативные правила, ансамбли, утилиты |
| modbus-tk | Протокол Modbus |
| model_bakery | Фабрики тестовых данных |
| modin | Масштабируемый pandas (Ray/Dask) |
| monai | Медицинский глубокий ИИ на PyTorch |
| mongoengine | ODM поверх pymongo |
| mongomock | Мокирование БД |
| monkeytype | Автоматический вывод аннотаций типов (Instagram) |
| more-itertools | Дополнительные итераторы и рецепты |
| moto | Мокирование AWS-сервисов в тестах |
| motor | Клиент MongoDB (async) |
| moviepy | Видео-манипуляции |
| mpmath | Арифметика произвольной точности |
| msgpack | Компактная бинарная сериализация |
| msgspec | Быстрая сериализация/валидация (JSON, MessagePack) |
| mss | Сверхбыстрые скриншоты |
| mujoco | Физдвижок для робототехники (DeepMind) |
| music21 | Анализ музыкальных партитур (MIT) |
| mutmut | Мутационное тестирование |
| mypy | Статический анализ типов |
| mypyc | Компиляция типизированного Python в C |
| nameko | Микросервисный фреймворк (RPC, события) |
| nats-py | Асинхронный клиент NATS |
| nbconvert | Конвертация ноутбуков в HTML/PDF/скрипты |
| nbdev | Разработка библиотек прямо в ноутбуках (fast.ai) |
| nbformat | Модель и валидация формата .ipynb |
| neptune | ML-эксперименты |
| netaddr | IP-адреса |
| netCDF4 | Формат netCDF (климатология, океанология) |
| networkx | Анализ графов и сетей |
| neuralprophet | Нейросетевой наследник Prophet |
| nevergrad | Градиент-free оптимизация (Meta) |
| newspaper3k | Извлечение новостей и статей |
| nextcord | Боты для Discord |
| nibabel | Чтение NIfTI и нейровизуализационных форматов |
| nicegui | Веб-GUI из Python-кода в реальном времени |
| nilearn | Статистика и ML для нейровизуализации |
| nltk | NLP (токенизация, NER, парсинг) |
| nose2 | Тестирование |
| notebook | Классический Jupyter Notebook |
| notion-client | Notion API |
| nougat | PDF → Markdown (научные статьи) |
| nox | Тестирование в разных окружениях |
| numba | JIT-компиляция Python в машинный код |
| numexpr | Быстрые числовые выражения над массивами |
| numpy | Основные массивы и линейная алгебра |
| oauthlib | Логика OAuth (основа requests-oauthlib) |
| odfpy | Чтение и запись OpenDocument (.ods/.odt) |
| ollama (client) | Клиент локальной Ollama для Python (приватные LLM) |
| omegaconf | Иерархические конфиги с интерполяцией |
| onnx | Универсальный формат моделей ML |
| onnxruntime | Универсальный формат моделей ML |
| opcua | OPC UA |
| open3d | Облака точек, меши, регистрация |
| openai | Официальный SDK к API LLM |
| openai-agents | OpenAI Agents SDK (агентные рабочие процессы) |
| openai-whisper | Распознавание речи Whisper (OpenAI) |
| opencv-python | Компьютерное зрение (cv2) |
| openpyxl | Работа с .xlsx, .xls |
| opentelemetry-api | Distributed tracing |
| opentelemetry-sdk | Distributed tracing |
| optax | Дифференцируемые вычисления (Google) |
| orjson | Самый быстрый JSON (Rust) |
| ortools | Линейное/целочисленное программирование, VRP (Google) |
| outlines | Гарантированно структурная генерация LLM |
| paho-mqtt | MQTT-клиент |
| pandas | DataFrame для анализа данных |
| pandas-datareader | Данные из FRED, World Bank, Stooq |
| pandas-ta | Технические индикаторы для pandas |
| pandera | Валидация данных |
| panel | Интерактивная визуализация |
| papermill | Параметризованное выполнение ноутбуков |
| paramiko | SSH-автоматизация |
| parsel | XPath/CSS-селекторы (движок Scrapy) |
| passlib | Фреймворк хеширования паролей |
| patool | Универсальная обёртка над архиваторами |
| pdf2image | Низкоуровневый парсинг PDF |
| pdfkit | Обёртка над wkhtmltopdf |
| pdfplumber | Извлечение текста из PDF |
| pedalboard | Аудио-эффекты и обработка (Spotify) |
| peewee | Лёгкий выразительный ORM |
| peft | Parameter-efficient fine-tuning (LoRA и др.) |
| pendulum | Даты и таймзоны без сюрпризов |
| pennylane | Квантовое машинное обучение |
| pexpect | Управление интерактивными процессами |
| pg8000 | Чистый Python клиент PostgreSQL |
| phonenumbers | Валидация и форматирование телефонов |
| pika | Клиент RabbitMQ (AMQP 0-9-1) |
| pikepdf | Мощные PDF-манипуляции на базе qpdf |
| pillow | Обработка изображений (PIL) |
| pinecone | Клиент управляемой векторной БД Pinecone |
| pint | Физические единицы измерения и проверки размерностей |
| piper-tts | Быстрый локальный TTS для edge-устройств |
| plotly | Построение графиков |
| plotnine | Статистическая визуализация |
| plyer | Кроссплатформенные уведомления и доступ к железу |
| pmdarima | Auto-ARIMA поверх statsmodels |
| pocketsphinx | Распознавание речи (офлайн) |
| polars | DataFrame на Rust (быстрее pandas) |
| postmark | Email-рассылки |
| praw | Reddit API |
| prefect | Оркестрация data pipelines |
| pretty_midi | Анализ и синтез MIDI |
| prettytable | Таблицы в терминале |
| prisma-client-py | Prisma ORM для Python |
| prometheus-client | Экспорт метрик для Prometheus |
| prompt_toolkit | Интерактивные приглашения ввода (основа IPython/pgcli) |
| promptfoo | Тестирование и сравнение промптов и моделей |
| prophet | Прогнозирование с сезонностью (Meta) |
| psycopg | Современный клиент PostgreSQL (psycopg3) |
| psycopg2 | Клиент PostgreSQL |
| pulp | Линейное программирование |
| pulsar-client | Клиент Apache Pulsar |
| pulumi | IaC на Python |
| py-spy | Визуализация и sampling-профилировщики |
| py7zr | Работа с 7z-архивами |
| pyannote.audio | Диаризация спикеров, VAD |
| pyarrow | Колоночный формат данных |
| pyaudio | Запись и воспроизведение аудио (PortAudio) |
| pyautogui | Автоматизация мыши и клавиатуры |
| pybluez | Bluetooth |
| pybullet | Физическая симуляция и робототехника |
| pycountry | Данные о странах, языках, валютах (ISO) |
| pycryptodome | Шифры, хеши, MAC (замена PyCrypto) |
| pydantic | Валидация данных |
| pydantic-ai | Типизированные AI-агенты (от создателей Pydantic) |
| pydantic-settings | Управление переменными окружения |
| pydicom | Чтение и запись DICOM |
| pydocstyle | Проверка docstrings по PEP 257 |
| pydub | Аудио-анализ и обработка |
| pyfacebook | Facebook Graph API |
| pyfiglet | ASCII-арт баннеры из текста |
| pygal | SVG-графики |
| pygame | Игры и мультимедиа |
| pygit2 | Программная работа с Git |
| PyGithub | GitHub API |
| pyinstrument | Статистический профилировщик с call stack |
| pyjwt | Кодирование и проверка JWT |
| pylint | Линтеры и сканер безопасности |
| pymatgen | Материаловедение: кристаллы, структуры |
| pymeshlab | Обработка и очистка 3D-мешей |
| pymilvus | Клиент векторных БД |
| pymisp | Threat intelligence |
| pymodbus | Протокол Modbus |
| pymongo | Клиент MongoDB |
| pymoo | Многокритериальная оптимизация (NSGA-II/III) |
| pymupdf | Извлечение текста из PDF |
| pymysql | Клиент MySQL |
| pynacl | Криптография NaCl/libsodium |
| pynput | Глобальный контроль мыши/клавиатуры |
| pyomo | Математическое моделирование и оптимизация |
| pyotp | TOTP/HOTP для 2FA |
| pypdf | Современная работа с PDF (преемник PyPDF2) |
| PyPDF2 | Извлечение текста из PDF |
| PyPortfolioOpt | Оптимизация инвестиционного портфеля |
| PyQt6 | Привязки Qt6 для GUI |
| pyquery | Альтернативные парсеры HTML |
| pyramid | Гибкий классический фреймворк |
| pyreadstat | Чтение SPSS/SAS/Stata-файлов |
| pyright | Статический анализ типов |
| pyrogram | Асинхронный Telegram MTProto-клиент |
| pyscard | Работа со смарт-картами |
| pyserial | Управление COM-портами |
| PySide6 | Официальные привязки Qt6 (LGPL) |
| pysnmp | SNMP |
| pyspark | Apache Spark для Python |
| pystray | Иконки в системном трее |
| pytesseract | Python-обёртка Tesseract OCR |
| pytest | Тестирование |
| pytest-asyncio | Асинхронные тесты pytest |
| pytest-bdd | Gherkin BDD-сценарии |
| pytest-cov | Измерение покрытия кода |
| pytest-django | Фикстуры и утилиты для Django |
| pytest-httpx | Мокирование HTTP в тестах |
| pytest-mock | Фикстура mocker (обёртка unittest.mock) |
| pytest-playwright | Фикстуры Playwright для pytest |
| pytest-xdist | Параллельный запуск тестов |
| python-calamine | Очень быстрое чтение Excel (Rust) |
| python-can | CAN-шина |
| python-dateutil | Парсинг, арифметика и таймзоны дат |
| python-decouple | Вынос параметров в переменные окружения |
| python-doctr | OCR на TensorFlow/PyTorch (Mindee) |
| python-docx | Создание и чтение Word |
| python-dotenv | Управление переменными окружения |
| python-json-logger | Структурированные JSON-логи |
| python-nmap | Обёртка для nmap |
| python-pptx | Создание презентаций PowerPoint |
| python-slugify | Генерация URL-слагов |
| python-socketio | Протокол Socket.IO для Python |
| python-telegram-bot | Боты для Telegram |
| pyttsx3 | Офлайн TTS через системные движки |
| pytube | Скачивание видео с YouTube |
| pytype | Статический анализ типов |
| pyupgrade | Автообновление синтаксиса до новой версии Python |
| pyusb | USB-устройства |
| pyvisa | Управление измерительными приборами (SCPI/GPIB/USB) |
| pyvista | 3D-визуализация и анализ сеток (VTK) |
| pywebview | Десктоп-окно с web-содержимым |
| pywin32 | Windows API, COM, службы |
| pywinauto | Автоматизация GUI Windows |
| pywinrm | Windows Remote Management (WinRM) |
| pyyaml | Парсинг конфигов |
| pyzbar | Генерация и чтение QR-кодов |
| qdrant-client | Клиент векторных БД |
| qiskit | Квантовые вычисления (IBM) |
| qrcode | Генерация и чтение QR-кодов |
| quantlib | Количественные финансы (fixed income, опционы) |
| quart | Асинхронный Flask-совместимый фреймворк |
| questionary | Интерактивные диалоги-вопросы для CLI |
| radon | Метрики сложности (cyclomatic, maintainability) |
| ragas | Оценка качества RAG-пайплайнов |
| rapidfuzz | Быстрое нечёткое сравнение строк (C++) |
| rapidocr-onnxruntime | Быстрый OCR на ONNX Runtime |
| rarfile | Чтение RAR-архивов |
| rasterio | Геопространственный анализ |
| ray | Распределённые вычисления, Ray Tune/Train/Serve |
| rdkit | Хемоинформатика: молекулы, дескрипторы, реакции |
| recurring-ical-events | Работа с .ics (iCal) |
| redis-py | Клиент Redis |
| rembg | Удаление фона с изображений |
| reportlab | Программное создание PDF |
| requests | HTTP-запросы (синхронный) |
| requests-cache | Прозрачное кэширование HTTP-запросов |
| requests-oauthlib | OAuth-авторизация для requests |
| responses | Мокирование HTTP в тестах |
| returns | Функциональное программирование: Result, Maybe, IO |
| rich | TUI для терминала |
| robobrowser | Stateful браузер |
| rope | Рефакторинг Python-кода |
| rpi.gpio | Raspberry Pi GPIO |
| rq | Distributed task queues |
| ruamel.yaml | YAML с сохранением комментариев и форматирования |
| ruff | Форматирование и линтинг |
| safetensors | Безопасное быстрое хранение тензоров |
| safety | Линтеры и сканер безопасности |
| sanic | Быстрый асинхронный веб-фреймворк |
| scalene | Профилировщик CPU+GPU+память |
| scapy | Сетевые пакеты |
| schedule | Простое периодическое выполнение функций |
| schemathesis | Фаззинг API по OpenAPI-спецификации |
| scikit-image | Дополнительные инструменты для изображений |
| scikit-learn | Классическое ML |
| scipy | Научные вычисления (оптимизация, интегралы, сигналы) |
| scrapy | Фреймворк для веб-скрейпинга |
| sdv | Генерация синтетических табличных данных |
| seaborn | Статистическая визуализация |
| segment-anything | Универсальная сегментация (SAM, Meta) |
| selectolax | Альтернативные парсеры HTML |
| selenium | Браузерная автоматизация |
| sendgrid | Email-рассылки |
| sentence-transformers | Эмбеддинги предложений |
| sentencepiece | Самообучаемая токенизация |
| sentry-sdk | Мониторинг ошибок |
| sglang | Быстрый инференс LLM со структурными выходами |
| shap | Объяснимость предсказаний (SHAP values) |
| shapely | Геопространственный анализ |
| shodan | Shodan API |
| SimpleITK | Регистрация и сегментация медицинских изображений |
| simpy | Дискретно-событийное моделирование |
| sktime | Унифицированный фреймворк временных рядов |
| skyfield | Высокоточные эфемериды планет и спутников |
| slack-bolt | Приложения для Slack |
| slack-sdk | Приложения для Slack |
| smbprotocol | Клиент SMB2/3 |
| smolagents | Агенты (HuggingFace библиотека) |
| smtplib | Работа с email-протоколами |
| snakeviz | Визуализация и sampling-профилировщики |
| snscrape | Скрейпинг постов соцсетей без API |
| sounddevice | Аудио ввод/вывод (PortAudio, numpy-ориентированный) |
| soundfile | Чтение/запись WAV/FLAC (libsndfile) |
| spacy | NLP (токенизация, NER, парсинг) |
| speechbrain | Речевые модели: ASR/TTS/дипфейки (PyTorch) |
| speechrecognition | Распознавание речи (офлайн) |
| splinter | Единая обёртка над браузерными драйверами |
| splunk-sdk | Splunk API |
| sqlalchemy | ORM и работа с БД |
| sqlite-utils | Утилиты для SQLite |
| sqlmodel | ORM на SQLAlchemy + Pydantic (автор FastAPI) |
| stable-baselines3 | Готовые RL-алгоритмы на PyTorch |
| stanza | NLP (токенизация, NER, парсинг) |
| starlette | ASGI-фреймворк (фундамент FastAPI) |
| statsmodels | Эконометрика, тесты, временные ряды |
| streamlit | Быстрые веб-интерфейсы для ML |
| stripe | Платёжные API |
| structlog | Логирование |
| surya-ocr | OCR и анализ layout на 90+ языках |
| svglib | Чтение SVG для ReportLab |
| sweetviz | Автоматические EDA-отчёты в HTML |
| sympy | Символьная математика (CAS) |
| syrupy | Современные snapshot-тесты |
| TA-Lib | Классический технический анализ |
| tabula-py | Извлечение таблиц из PDF |
| tabulate | Табличный вывод данных |
| taskiq | Асинхронный distributed task manager |
| tavern | Декларативное тестирование API на YAML |
| telethon | Telegram-клиент (MTProto) |
| tenacity | Повторные попытки с backoff |
| tensorflow | TensorFlow |
| termcolor | Раскраска текста в терминале |
| terraform-python | Infrastructure as Code |
| testcontainers | Зависимости тестов в Docker-контейнерах |
| textblob | Простой NLP поверх NLTK |
| textdistance | Расстояния между строками (30+ алгоритмов) |
| textual | TUI для терминала |
| thefuzz | Нечёткое сравнение строк (бывш. fuzzywuzzy) |
| thehive4py | SOAR-платформа |
| tiktoken | Подсчёт токенов для моделей |
| time-machine | Мокирование времени |
| timm | Коллекция предобученных image-моделей (PyTorch) |
| together | SDK Together AI (открытые модели) |
| tokenizers | Подсчёт токенов для моделей |
| tomli | Парсинг конфигов |
| tomlkit | TOML с сохранением стиля (используется poetry) |
| toolz | Функциональные утилиты для итераторов и словарей |
| torch | PyTorch |
| torchaudio | PyTorch audio |
| torchmetrics | Метрики для PyTorch |
| torchvision | PyTorch vision |
| tornado | Классический web-фреймворк |
| tortoise-orm | Асинхронный ORM с автогенерацией схем |
| tox | Тестирование в разных окружениях |
| tqdm | Прогресс-бары |
| trafilatura | Извлечение статей и метаданных с веб-страниц |
| transformers | Загрузка и использование предобученных LLM (Hugging Face) |
| translators | Перевод через Google/Bing/Яндекс и др. |
| trello | Таск-трекеры |
| trimesh | Загрузка и обработка 3D-мешей |
| trio | Асинхронный фреймворк со структурированной конкурентностью |
| trl | Обучение с RLHF/DPO трансформеров |
| truststore | Использование системного хранилища CA в Python |
| tsfresh | Автоматическое извлечение признаков временных рядов |
| tweepy | Twitter/X API |
| twilio | SMS и голосовые звонки |
| twython | Twitter/X API |
| txtai | Эмбеддинг-база, поиск и RAG в одном |
| typeguard | Runtime-проверка типов |
| typer | Создание CLI |
| typing-extensions | Бэкпорты новых возможностей typing |
| ultralytics | YOLOv8/YOLO11: детекция, сегментация, позы, трекинг |
| undetected-chromedriver | Анти-детект патчинг Selenium |
| unidecode | Транслитерация Unicode в ASCII |
| unittest | Тестирование |
| unstructured | Извлечение текста из любых документов |
| unstructured-ingest | Извлечение текста из любых документов |
| urllib3 | Фундаментальный HTTP-клиент (база requests) |
| uvicorn | ASGI-сервер |
| uvloop | Быстрая замена event loop asyncio (libuv) |
| uwsgi | WSGI-сервер (классика продакшн-деплоя) |
| vaex | Out-of-core DataFrame для миллиардов строк |
| vcrpy | Мокирование HTTP в тестах |
| vectorbt | Векторизованный быстрый бэктестинг |
| vega | Декларативная визуализация |
| viztracer | Трассировка выполнения с timeline |
| vllm | Высокопроизводительный инференс LLM (PagedAttention) |
| vobject | Парсинг vCard |
| voila | Превращение ноутбуков в интерактивные дашборды |
| voluptuous | Валидация данных (конфигурации) |
| vonage | SMS и голосовые звонки |
| vosk | Офлайн ASR для 20+ языков |
| vt-py | VirusTotal API |
| vulture | Поиск мёртвого кода |
| waitress | Чистый Python WSGI-сервер (кроссплатформенный) |
| wand | Привязка ImageMagick для Python |
| wandb | ML-трекинг и визуализация |
| watchdog | Кроссплатформенный мониторинг файловой системы |
| watchfiles | Быстрый мониторинг файлов (Rust, движок uvicorn --reload) |
| weaviate-client | Клиент векторных БД |
| web3 | Взаимодействие с Ethereum и смарт-контрактами |
| websockets | Библиотека WebSocket-клиентов и серверов |
| whisperx | Whisper с выравниванием слов и диаризацией |
| wordfreq | Частотности слов в 30+ языках |
| wxPython | Нативные GUI-виджеты |
| xarray | N-мерные помеченные массивы (метеорология, океанография) |
| xgboost | Градиентный бустинг |
| xhtml2pdf | HTML → PDF |
| xlrd | Работа с .xlsx, .xls |
| xlsxwriter | Работа с .xlsx, .xls |
| xlwings | Автоматизация Excel (Windows/macOS) |
| yapf | Форматировщик кода (Google) |
| ydata-profiling | Профилирование датасетов (бывш. pandas-profiling) |
| yfinance | Рыночные данные Yahoo Finance |
| z3-solver | SMT-решатель (доказательство теорем) |
| zarr | Чанкованные сжатые N-мерные массивы |

## 4. Автоматизация интерактивных программ

| Инструмент | Описание |
|-----------|----------|
| echo | Форматированный вывод |
| expect | Автоматизация интерактивных программ (TCL) |
| printf | Форматированный вывод |
| script | Запись терминальной сессии |
| scriptreplay | Воспроизведение терминальной сессии |
| unbuffer | Снятие буферизации stdout (для пайпов) |
| yes | Автоматический ответ y на все вопросы |

## 5. Архиваторы и файловые утилиты

| Инструмент | Описание |
|-----------|----------|
| 7z | Работа с .7z, .zip, .rar, .cab, .iso и др. |
| ar | Создание статических библиотек (.a) |
| arc | Архиватор ARC (редкий формат) |
| arj | Архиватор ARJ |
| atool | Универсальная обёртка для архиваторов (aunpack, apack, als) |
| b2sum | Контрольные суммы BLAKE2 |
| basename | Имя файла без пути |
| bat | Улучшенный cat с подсветкой синтаксиса |
| broot | Интерактивный браузер директорий с поиском и переходом |
| brotli | Сжатие/распаковка .br (алгоритм Google) |
| bzip2 | Распаковка .bz2 |
| cksum | Контрольные суммы CRC32 |
| clifm | Файловый менеджер, живущий внутри оболочки |
| cmp | Побайтовое сравнение файлов |
| cp | Копирование файлов и директорий |
| cpio | Архивирование в стиле Unix (initramfs) |
| croc | Простая и безопасная передача файлов между машинами |
| csplit | Нарезка файла по контексту/регулярке |
| dcfldd | Улучшенный dd с хешированием и прогрессом |
| dd | Низкоуровневое копирование и конвертация образов |
| ddrescue | Восстановление данных с повреждённых носителей |
| dirname | Путь без имени файла |
| dtrx | Интеллектуальная распаковка с сохранением структуры |
| dust | Визуальный du (bar-chart disk usage) |
| entr | Запуск команды при изменении файлов |
| eza | Современная замена ls с иконками |
| f2 | Быстрое и безопасное переименование файлов |
| fclones | Эффективный поиск и удаление дубликатов файлов |
| fd | Быстрый поиск файлов (альтернатива find) |
| fdupes | Поиск дубликатов файлов |
| find | Поиск файлов по критериям |
| fzf | Fuzzy-поиск для интерактивного выбора файлов/строк |
| genisoimage | Создание ISO-образов |
| gunzip | Распаковка .gz |
| gzip | Сжатие/распаковка .gz |
| inotifywait | Мониторинг файловых событий Linux |
| inotifywatch | Мониторинг файловых событий Linux |
| joshuto | Файловый менеджер в стиле Ranger с vi-биндингами |
| kondo | Поиск и удаление артефактов сборки |
| lf | Быстрый и настраиваемый файловый менеджер |
| lha | Архиватор LHA (Amiga/PC-98) |
| lla | ls с плагинной системой |
| ln | Жёсткие и символические ссылки |
| ls | Список файлов в директории |
| lsar | Просмотр содержимого архива (спутник unar) |
| lsd | LSDeluxe — ls с иконками и цветами |
| lz4 | Экстремально быстрое сжатие |
| lzop | Быстрое сжатие на основе LZO |
| magic-wormhole | Безопасная передача файлов по кодовому слову (PAKE) |
| mc | Midnight Commander – файловый менеджер с просмотром архивов |
| md5sum | Контрольные суммы MD5 |
| mkdir | Создание директорий |
| mktemp | Безопасное создание временных файлов/директорий |
| mv | Перемещение/переименование файлов |
| ncdu | Интерактивный анализатор дискового пространства |
| nnn | Минималистичный и быстрый файловый менеджер |
| nomino | Переименование файлов с regex и сортировкой |
| ouch | Универсальный compress/decompress |
| plocate | Быстрый поиск по индексу ФС (современный locate) |
| procs | Альтернатива ps с цветом, фильтрацией и деревом процессов |
| rar | Проприетарный архиватор WinRAR (создание .rar) |
| rclone | Синхронизация с облачными хранилищами (S3, GDrive, Dropbox) |
| readlink | Чтение значения символической ссылки |
| realpath | Канонический абсолютный путь |
| rip | Безопасное удаление файлов с подтверждением и предпросмотром (альтернатива rm) |
| ripgrep | Рекурсивный поиск текста по файлам (быстрее grep) |
| rm | Удаление файлов/директорий |
| rsync | Дельта-синхронизация файлов по сети (локально и удалённо) |
| s3cmd | Клиент S3-совместимых хранилищ |
| s5cmd | Очень быстрый параллельный клиент S3 (Go) |
| sha1sum | Контрольные суммы SHA-1 |
| sha256sum | Контрольные суммы SHA-256 |
| split | Нарезка файла на части по размеру/строкам |
| stat | Метаданные файлов (размер, права, время) |
| superfile | Современный и красивый TUI-файловый менеджер |
| symlinks | Управление символическими ссылками |
| syncthing | Децентрализованная непрерывная синхронизация файлов |
| tar | Работа с .tar, .tar.gz, .tgz (создание, распаковка, просмотр) |
| touch | Создание пустых файлов, обновление временных меток |
| trash-cli | Безопасное удаление с перемещением в корзину |
| tre | tree с Git-интеграцией |
| tre-command | Дерево каталогов с интеграцией Git и preview |
| tree | Визуализация дерева директорий |
| unar | Распаковка архивов (rar, zip, tar, 7z и др.) с автодетектом кодировки |
| unison | Двунаправленная синхронизация файлов |
| unrar | Распаковка .rar (бесплатная версия) |
| unzip | Распаковка .zip |
| watchexec | Запуск команд при изменении файлов (Rust) |
| watchman | Файловый watcher от Meta (отслеживание изменений) |
| xplr | Минималистичный, быстрый TUI-файловый менеджер |
| xz | Распаковка .xz |
| yazi | Современный файловый менеджер в терминале на Rust с превью |
| zoo | Архиватор Zoo |
| zstd | Сжатие/распаковка .zst (высокая скорость) |

## 6. Безопасность, криптография и аудит

| Инструмент | Описание |
|-----------|----------|
| 1password-cli | CLI-доступ к 1Password vaults |
| aa-enforce | AppArmor профили |
| aa-status | Состояние AppArmor |
| acme.sh | Альтернативный ACME-клиент (чистый shell) |
| actionlint | Статический анализ workflow GitHub Actions |
| aegis | управление доступом |
| age | Современное простое шифрование файлов (X25519) |
| aircrack-ng | Аудит Wi-Fi: захват рукопожатий, взлом WEP/WPA |
| amass | Глубокая разведка поддоменов и альтернативных имён (OWASP) |
| apparmor_parser | Загрузка и проверка AppArmor-профилей |
| apparmor_status | AppArmor профили |
| arjun | Поиск скрытых HTTP-параметров |
| auditctl | Linux Audit Framework |
| ausearch | Linux Audit Framework |
| bettercap | Фреймворк MITM-атак: Wi-Fi, BLE, HID, сети |
| bw | Bitwarden CLI (менеджер паролей) |
| cargo-geiger | Поиск unsafe-кода в зависимостях |
| certbot | Автоматический выпуск Let's Encrypt |
| certipy | Атаки и перечисление Active Directory Certificate Services |
| certstrap | Простое создание CA и сертификатов без интерактива |
| cewl | Генерация словарей из содержимого сайтов |
| cfssl | PKI инфраструктура от Cloudflare |
| cfssljson | PKI инфраструктура от Cloudflare |
| chkrootkit | Проверка на руткиты |
| codeql | semantic security analysis |
| crunch | Генератор словарей заданной структуры |
| dependabot | dependency updates/security alerts |
| detect-secrets | Поиск секретов в коде (Yelp, enterprise-подход) |
| dirb | Классический брутфорс веб-директорий |
| dirsearch | Сканер веб-путей |
| dnsrecon | DNS reconnaissance |
| dnsx | Многофункциональный DNS-инструментарий (ProjectDiscovery) |
| droopescan | Сканер плагинов и тем Drupal |
| drush | Управление Drupal из командной строки |
| dsniff | Набор снифферов и MITM-утилит (arpspoof, urlsnarf) |
| enum4linux-ng | Перечисление SMB/Windows-хостов |
| ettercap | Классический перехват трафика (MITM) |
| fail2ban-client | Управление банами по IP |
| feroxbuster | Рекурсивный поиск контента (Rust) |
| ffuf | Быстрый веб-фаззер (Go) |
| firewall-cmd | CLI firewalld |
| firewalld-cmd | Файрвол RHEL/CentOS |
| gau | Сбор известных URL из Common Crawl, Wayback и др. |
| gitleaks | Обнаружение секретов в git-истории |
| gobuster | Брутфорс директорий, DNS, виртуальных хостов |
| gopass | Менеджер паролей pass для команд (Go) |
| gophish | Платформа моделирования фишинговых кампаний |
| gosec | Статический анализ безопасности Go |
| gpg | PGP-подписи, шифрование файлов, доверие |
| gpg2 | PGP-подписи, шифрование файлов, доверие |
| hakrawler | Быстрый веб-краулер для сбора эндпоинтов |
| hashcat | Восстановление хешей на GPU |
| hashid | Определение типа хеша |
| hostapd | Точка доступа Wi-Fi и обмен EAPOL |
| hydra | Брутфорс логинов по сети |
| in-toto-run | Формирование attestations |
| john | John the Ripper — восстановление паролей |
| joomscan | Сканер уязвимостей Joomla |
| jwt-cli | Декодирование и подпись JWT |
| katana | Продвинутый веб-краулер (ProjectDiscovery) |
| keepassxc-cli | Работа с базами KeePass без GUI |
| kerbrute | Брутфорс и енумерация пользователей Kerberos |
| kinit | Получение Kerberos ticket |
| kismet | Детектор и сниффер беспроводных сетей |
| klist | Просмотр Kerberos tickets |
| kubescape | Аудит Kubernetes-конфигурации |
| ligolo-ng | Туннелирование и пивоты как VPN (пентест) |
| lynis | Аудит безопасности системы |
| macchanger | Подмена MAC-адреса |
| massdns | массовый DNS resolution |
| medusa | Модульный брутфорс сетевых сервисов |
| metasploit-framework | Penetration testing (msfconsole) |
| minisign | Простое подписание файлов (ed25519) |
| mkcert | Локальные доверенные TLS-сертификаты для разработки |
| msfconsole | Penetration testing |
| naabu | Быстрый сканер портов (ProjectDiscovery) |
| name-that-hash | Определение типа хеша с выводом в JSON |
| ncrack | Брутфорс сетевой аутентификации (семейство nmap) |
| netexec | Универсальный инструмент сетевого пентеста (бывш. CrackMapExec) |
| nikto | Сканер уязвимостей веб-серверов |
| nuclei | Сканер уязвимостей на основе шаблонов (ProjectDiscovery) |
| op | 1Password CLI |
| openbao | open-source secrets management |
| openssl | Сертификаты X.509, TLS-тесты, шифрование |
| osv-scanner | Сканер уязвимостей зависимостей по базе OSV (Google) |
| pass | Минималистичный менеджер паролей на GPG + git |
| patator | Мультипоточный брутфорс с модулями протоколов |
| pip-audit | Аудит уязвимостей установленных Python-пакетов (PyPA) |
| proxychains | Прогон любого приложения через цепочку прокси |
| rage | Реализация age на Rust |
| reaver | Атака на WPS (Pixie Dust) |
| recon-ng | Модульный фреймворк веб-разведки (OSINT) |
| rekor-cli | Прозрачный журнал подписей |
| responder | Отравление LLMNR/NBT-NS/mDNS в локальной сети |
| ripsecrets | Поиск секретов в файлах и Git-истории |
| rkhunter | Проверка на руткиты |
| secretlint | Проверка секретов в репозиториях |
| semanage | SELinux политики |
| semgrep | Статический анализ кода с семантическим поиском |
| sestatus | SELinux политики |
| sigstore | инфраструктура доверенной подписи |
| sliver | Открытый фреймворк C2 (adversary emulation) |
| slsa-verifier | Проверка SLSA provenance |
| sops | Шифрование YAML, JSON, ENV и других конфигураций |
| sqlmap | Автоматический SQL-инъекции сканер |
| ssh-add | Управление SSH-ключами в памяти |
| ssh-agent | Управление SSH-ключами в памяти |
| ssh-keygen | Генерация SSH-ключей (RSA, ED25519) |
| step | Smallstep PKI (мини-CA) |
| step-ca | Smallstep PKI (мини-CA) |
| step-cli | PKI/certificates/identity automation |
| subfinder | Пассивный поиск поддоменов (ProjectDiscovery) |
| testssl.sh | TLS/SSL audit |
| tfsec | Terraform security scanning |
| theHarvester | OSINT: сбор e-mail, поддоменов, имён из открытых источников |
| tpm2-tools | Работа с TPM 2.0 |
| trufflehog | Поиск секретов и ключей в репозиториях (400+ детекторов) |
| vault | Управление секретами и шифрование (HashiCorp) |
| wafw00f | Определение и фингерпринт WAF |
| wavemon | Мониторинг Wi-Fi (TUI) |
| waybackurls | Извлечение URL из Wayback Machine |
| wfuzz | Классический веб-фаззер |
| whatweb | Фингерпринт веб-технологий |
| wifite | Автоматизация атак на Wi-Fi |
| wp-cli | Управление WordPress из командной строки |
| wpscan | Сканер уязвимостей WordPress |
| yara | Язык правил и поиск вредоносных паттернов (VirusTotal) |
| ykman | Управление YubiKey |
| zaproxy | OWASP ZAP — прокси и сканер веб-уязвимостей (headless) |
| zgrab2 | application-layer network scanner |
| zizmor | security audit GitHub Actions |

## 7. Браузерная и веб-автоматизация

| Инструмент | Описание |
|-----------|----------|
| chromedriver | Chrome WebDriver |
| chromium | headless/browser runtime |
| firefox | browser automation target |
| geckodriver | Firefox WebDriver |
| wappalyzer | technology fingerprinting |
| web-ext | Firefox extension development |

## 8. Брокеры сообщений, очереди и потоковая обработка

| Инструмент | Описание |
|-----------|----------|
| beanstalkd | Простая очередь задач |
| kafka-configs | Изменение конфигурации топиков |
| kafka-console-consumer | Чтение топиков Kafka |
| kafka-console-producer | Запись в топик Kafka |
| kafka-topics | Управление топиками (create, delete, describe) |
| kcat | Универсальный Kafka consumer/producer (ранее kafkacat) |
| mosquitto_pub | MQTT публикация |
| mosquitto_sub | MQTT подписка |
| mqtt-cli | Универсальный MQTT клиент |
| nats | Универсальный CLI-клиент NATS (pub/sub, KV, Object Store) |
| nats-server | Сервер NATS (лёгкий messaging) |
| nsq | NSQ очередь сообщений |
| nsq_pub | NSQ очередь сообщений |
| nsq_tail | NSQ очередь сообщений |
| pulsar-admin | Apache Pulsar CLI |
| rabbitmqadmin | REST-API клиент для RabbitMQ |
| rabbitmqctl | Управление нодой RabbitMQ |
| rpk | CLI Redpanda (Kafka-совместимый брокер) |

## 9. Встраиваемые системы и электроника

| Инструмент | Описание |
|-----------|----------|
| arduino-cli | Сборка и загрузка скетчей Arduino |
| avrdude | Прошивка микроконтроллеров AVR |
| dfu-util | Загрузка прошивок по USB DFU |
| esptool | Прошивка ESP8266/ESP32 (Espressif) |
| flashrom | Чтение/запись флеш-памяти BIOS/UEFI |
| openfpgaloader | Прошивка FPGA множества семейств |
| openocd | Отладка и прошивка через JTAG/SWD |
| picotool | Управление RP2040/RP2350 (Raspberry Pi Pico) |
| platformio | Кроссплатформенная сборка embedded-проектов (pio) |
| probe-rs | Современная отладка микроконтроллеров (Rust) |
| sigrok-cli | Работа с логическими анализаторами и осциллографами |
| st-flash | Прошивка STM32 (stlink-tools) |
| west | Мультиинструмент проекта Zephyr RTOS |

## 10. Диаграммы и графики (CLI)

| Инструмент | Описание |
|-----------|----------|
| asymptote | Векторная графика для технических иллюстраций |
| blockdiag | Блочные диаграммы из простого текста |
| d2 | Современный декларативный язык диаграмм (Terrastruct) |
| ditaa | ASCII-схемы в PNG |
| gnuplot | Классические научные графики и функции |
| graphviz | Графы по описанию на DOT (dot, neato, circo) |
| mermaid-cli | diagrams from text |
| mmdc | Mermaid-диаграммы в PNG/SVG/PDF (mermaid-cli) |
| pikchr | Язык диаграмм для документации (SQLite) |
| plantuml | UML-диаграммы из текстового описания |
| svgbob | ASCII-арт в SVG |

## 11. Диски, файловые системы и разметка

| Инструмент | Описание |
|-----------|----------|
| badblocks | Поиск повреждённых блоков |
| blkid | UUID блочных устройств |
| btrfs | Файловая система Btrfs (снапшоты, сжатие) |
| cfdisk | Интерактивная разметка дисков (curses) |
| chattr | Атрибуты ext-файлов |
| cryptsetup | Шифрование разделов LUKS/dm-crypt |
| df | Свободное место |
| dmsetup | Низкоуровневое управление device-mapper |
| du | Размер директорий |
| dua | Анализ дискового пространства с быстрым интерактивным интерфейсом |
| duf | Альтернатива df — читаемый вывод с цветом и сортировкой |
| e2fsck | Проверка и исправление ФС |
| fdisk | Разметка дисков (MBR/GPT) |
| filefrag | Анализ фрагментации файлов |
| fsck | Проверка и исправление ФС |
| fstrim | TRIM для SSD |
| gdisk | Разметка дисков (MBR/GPT) |
| gdu | Быстрый disk usage analyzer на Go |
| gocryptfs | Шифрованная ФС поверх каталога (FUSE) |
| hdparm | Низкоуровневые параметры дисков |
| losetup | Управление loop-устройствами |
| lsattr | Просмотр ext-атрибутов |
| lsblk | Дерево блочных устройств |
| lvm | Управление LVM (pvcreate/vgcreate/lvcreate) |
| mdadm | Управление программным RAID |
| mkfs.ext4 | Создание файловых систем |
| mkfs.vfat | Создание файловых систем |
| mkfs.xfs | Создание файловых систем |
| mount | Монтирование/размонтирование ФС |
| nvme | Управление NVMe-накопителями |
| parted | Разметка дисков (MBR/GPT) |
| partprobe | Обновление таблицы разделов ядра |
| partx | Уведомление ядра об изменении таблицы разделов |
| resize2fs | Изменение размера ФС online |
| sdparm | Низкоуровневые параметры дисков |
| sfdisk | Скриптовое разбиение дисков (MBR/GPT) |
| sgdisk | Скриптовая разметка GPT (семейство gdisk) |
| smartctl | S.M.A.R.T. диагностика дисков |
| sync | Принудительная запись буферов на диск |
| tune2fs | Параметры ext2/3/4 |
| udevadm | Управление событиями устройств (udev) |
| umount | Монтирование/размонтирование ФС |
| wipefs | Стирание сигнатур ФС/RAID с устройства |
| xfs_growfs | Изменение размера ФС online |
| xfs_repair | Проверка и исправление ФС |
| zfs | ZFS: пулы, снапшоты, сжатие, RAID-Z |
| zpool | Управление ZFS pools |

## 12. Документы и OCR

| Инструмент | Описание |
|-----------|----------|
| a2ps | Anything to PostScript |
| abiword | Лёгкий текстовый процессор с конвертацией |
| antiword | Извлечение текста из .doc (Word 97-2003) |
| asciidoc | Классический AsciiDoc |
| asciidoctor | Процессор AsciiDoc |
| aspell | Проверка орфографии |
| biber | Управление библиографией LaTeX |
| bibtex | Управление библиографией LaTeX |
| calamari | OCR на TensorFlow |
| catdoc | Извлечение текста из старых MS Office |
| catppt | Извлечение текста из старых MS Office |
| cmark | CommonMark парсер |
| cmark-gfm | GitHub Flavored Markdown парсер |
| comparepdf | Визуальное сравнение PDF |
| cpdf | Манипуляции с PDF-страницами |
| cuneiform | OCR (русский, английский, многоязычный) |
| dblatex | Конвертация DocBook в PDF через LaTeX |
| decktape | HTML-презентации → PDF |
| diff-pdf | Визуальное сравнение PDF |
| djvused | OCR и манипуляции с DjVu |
| djvutxt | OCR и манипуляции с DjVu |
| docusaurus | documentation platform |
| docutils | Библиотека для reStructuredText (есть CLI) |
| doxygen | Генерация документации из исходного кода |
| doxywizard | Генерация документации из исходного кода |
| easyocr | OCR на PyTorch (80+ языков) |
| enscript | Текст → PostScript |
| fop | XSL-FO → PDF (Apache FOP) |
| ghostscript | Интерпретатор PostScript/PDF (gs): конвертация и оптимизация |
| gocr | GNU OCR |
| godoc | Генератор документации для Go |
| grip | Просмотр Markdown в терминале |
| groff | Классическая Unix вёрстка (man pages) |
| help2man | Генерация man-страниц из --help |
| hugo | static publishing |
| hunspell | Проверка орфографии (словари LibreOffice/Firefox) |
| javadoc | Генератор документации для Java |
| kraken | OCR для исторических документов |
| kramdown | Ruby-библиотека для Markdown (CLI) |
| latexdiff | Визуальная разница версий LaTeX-документов |
| latexindent | Форматирование LaTeX-кода |
| latexmk | Автоматизация сборки LaTeX |
| libreoffice | Headless-режим для конвертации офисных документов |
| lowdown | Парсер CommonMark |
| lualatex | Компилятор LaTeX |
| mandoc | Современный процессор man-страниц |
| markdown | Парсер Markdown (CLI) |
| marp | Markdown → презентации (HTML/PPTX/PDF) |
| mdv | Просмотр Markdown в терминале |
| mkdocs | documentation sites |
| mockoon | API дизайн и мокирование |
| multimarkdown | Компилятор Markdown с расширениями |
| mutool | Универсальный PDF-инструментарий (MuPDF) |
| nroff | Классическая Unix вёрстка (man pages) |
| ocrmypdf | OCR + оптимизация PDF (обёртка над tesseract) |
| ocropus | OCR для исторических документов |
| olefile | Анализ OLE-структур (макровирусы, метаданные) |
| oletools | Анализ OLE-структур (макровирусы, метаданные) |
| openapi-generator | Генерация клиентов/серверов из OpenAPI |
| paddleocr | OCR от Baidu (китайский, английский, многоязычный) |
| pandoc | Конвертер между форматами (Markdown, HTML, DOCX, PDF, LaTeX) |
| paps | Текст → PostScript |
| pdf-parser.py | Форензика Office-документов (из oletools) |
| pdf2ps | Конвертация PDF → PostScript |
| pdf2svg | PDF → SVG |
| pdfarranger | Перестановка страниц PDF (headless) |
| pdflatex | Компилятор LaTeX |
| pdfminer.six | Низкоуровневый парсинг PDF (CLI) |
| pdfseparate | Разделение PDF на страницы (poppler) |
| pdftk | Манипуляции с PDF (merge, split, rotate) |
| pdftocairo | Конвертация PDF в изображения/HTML (poppler) |
| pdftohtml | Конвертация PDF в изображения/HTML (poppler) |
| pdftoppm | Конвертация PDF в изображения/HTML (poppler) |
| pdftotext | Извлечение текста из PDF (poppler) |
| pdfunite | Объединение PDF (poppler) |
| playwright | Генерация PDF из HTML через headless браузер (CLI) |
| pod2html | Perl POD → HTML |
| pod2man | Perl POD → man |
| prince | Коммерческий HTML/XML → PDF |
| prism | Mock-сервер из OpenAPI |
| ps2ascii | PostScript → текст |
| ps2pdf | Конвертация PostScript → PDF |
| puppeteer | Headless Chrome для PDF (CLI) |
| pydoc | Генератор документации для Python |
| qpdf | Структурные манипуляции с PDF |
| quarto | Публикация из Markdown/Jupyter в PDF/HTML/Word |
| redoc-cli | Рендеринг OpenAPI спецификаций |
| redocly | Рендеринг OpenAPI спецификаций |
| reveal-md | Markdown → Reveal.js презентации |
| ronn | Markdown → man-страница |
| rst2html | reStructuredText конвертер |
| rst2man | reStructuredText конвертер |
| rst2pdf | reStructuredText конвертер |
| rtfobj.py | Форензика Office-документов (из oletools) |
| rustdoc | Генератор документации для Rust |
| scdoc | Простой формат для man-страниц |
| soffice | Алиас libreoffice |
| spectral | Линтер OpenAPI |
| sphinx | technical documentation |
| stapler | Манипуляции с PDF-страницами (Python) |
| stoplight | API design и mocking |
| swagger-codegen | Генерация клиентов/серверов из Swagger |
| tesseract | OCR (распознавание текста на изображениях) + языковые пакеты |
| texlive | Система вёрстки LaTeX (pdflatex, xelatex, etc.) |
| troff | Классическая Unix вёрстка (man pages) |
| typst | Современная вёрстка LaTeX-уровня (Rust, мгновенная компиляция) |
| unoconv | Конвертация офисных документов через LibreOffice |
| unoconv2 | Конвертация офисных документов через LibreOffice |
| vale | Линтер прозы и стиля документации |
| weasyprint | HTML → PDF (CLI) |
| wkhtmltopdf | HTML → PDF (старый, но работает) |
| wvWare | Парсер .doc (Word 97-2003) |
| xelatex | Компилятор LaTeX |
| xls2csv | Извлечение данных из .xls |
| zipdump.py | Форензика Office-документов (из oletools) |

## 13. Интерпретаторы и компиляторы

| Инструмент | Описание |
|-----------|----------|
| abcl | Common Lisp на JVM |
| bash | Shell-интерпретатор (скрипты, пайпы) |
| bun | JavaScript/TypeScript runtime, bundler, package manager |
| cargo | Менеджер пакетов Rust и билд-система |
| chapel | Язык параллельного программирования от Cray |
| chicken | Компилятор Scheme в C |
| clang | Компилятор C/C++/Objective-C на инфраструктуре LLVM |
| clisp | Интерпретатор Common Lisp |
| clojure | Lisp на JVM |
| crystal | Ruby-подобный компилируемый язык |
| csc | Компилятор C# (Roslyn) |
| dart | Язык от Google (Flutter) |
| deno | Современный runtime TypeScript/JavaScript (безопасный) |
| dotnet | Runtime .NET (C#, F#, VB.NET) |
| ecl | Встраиваемый Common Lisp |
| elixir | Язык на BEAM (Erlang VM) |
| emcc | Компиляция C/C++ в WebAssembly (Emscripten) |
| erlang | Runtime Erlang |
| factor | Компилируемый стековый язык |
| fennel | Lisp-синтаксис, транслируемый в Lua |
| flutter | CLI для сборки мобильных/desktop/web приложений |
| fsharpc | Компилятор F# |
| fsharpi | Интерпретатор F# |
| gap | Система вычислительной дискретной алгебры |
| gawk | Версия awk от GNU |
| gcc | Компилятор GNU для C/C++/Fortran/Go |
| gforth | Реализация языка Forth |
| ghc | Glasgow Haskell Compiler |
| gnu-apl | Интерпретатор APL |
| go | Компилятор и runtime Go |
| groovy | Динамический JVM-язык |
| gst | GNU Smalltalk интерпретатор |
| guile | Интерпретатор Scheme (GNU) |
| hare | Системный язык с безопасным управлением памятью |
| haxe | Компилятор языка Haxe (кроссплатформенный) |
| include-what-you-use | Анализ include-зависимостей |
| io | Интерпретатор языка Io (акторная модель) |
| ipython | Интерактивный Python |
| j | Язык программирования J (из семейства APL) |
| jai | Экспериментальный игровой язык (CLI) |
| janet | Язык для встраивания с компилятором в байт-код |
| java | JVM runtime |
| javac | Компилятор Java |
| julia | Математические и научные вычисления |
| k | Язык K (из семейства APL) |
| kotlin | Kotlin/JVM, Kotlin/Native, Kotlin/JS |
| lean | Формальная верификация (Lean 4) |
| lua | Легковстраиваемый скриптовый язык |
| luajit | Just-in-time компилятор Lua |
| mathematica | Wolfram Language (научные вычисления) |
| matlab | Инженерные и научные вычисления |
| mawk | Альтернативная реализация awk |
| maxima | Компьютерная алгебра (CAS) |
| mix | Сборщик Elixir |
| mono | Кроссплатформенный runtime .NET (C#/F#) |
| newlisp | Легковесный интерпретатор Lisp |
| nim | Системный язык с Python-подобным синтаксисом |
| nimble | Менеджер пакетов Nim |
| node | JavaScript runtime (Node.js) |
| nvcc | Компилятор CUDA (NVIDIA) |
| ocaml | OCaml runtime |
| octave | Open-source альтернатива MATLAB |
| odin | Язык, альтернатива C, простой синтаксис |
| opam | Менеджер пакетов OCaml |
| perl | Скриптовый язык (обработка текста, системное администрирование) |
| php | Интерпретатор PHP (CLI) |
| picolisp | Минималистичный Lisp |
| prolog | Логическое программирование |
| python3 | Главный интерпретатор Python |
| q | Язык запросов для временных рядов (kdb+) |
| racket | Среда для языков на основе Scheme |
| reason | Синтаксис на основе OCaml, транслируемый в JS |
| Rscript | Статистический анализ R |
| ruby | Интерпретатор Ruby |
| rustc | Компилятор Rust |
| sage | Математическая система на базе Python |
| sbcl | Steel Bank Common Lisp (компилятор) |
| scala | Функциональный JVM-язык |
| scalac | Компилятор Scala |
| self | Среда исполнения языка Self |
| sh | Shell-интерпретатор (скрипты, пайпы) |
| sml | Стандартный ML (SML/NJ) |
| swift | Язык Apple (доступен на Linux) |
| swipl | SWI-Prolog интерпретатор |
| tcc | Tiny C Compiler — сверхбыстрая компиляция C |
| tcl | Tool Command Language (скриптование, GUI) |
| tk | GUI toolkit для Tcl |
| ts-node | Выполнение TypeScript без предварительной компиляции |
| v | Простой компилируемый язык (vlang) |
| wasmer | Runtime WebAssembly (WASI) |
| wasmtime | Runtime WebAssembly (WASI) |
| wolframscript | Wolfram Language (научные вычисления) |
| zig | Язык системного программирования |

## 14. Клиенты баз данных

| Инструмент | Описание |
|-----------|----------|
| algolia | CLI для Algolia search-as-a-service |
| arangosh | Клиент ArangoDB (multi-model) |
| atlas | Декларативные миграции схемы как код (Ariga) |
| bq | CLI Google BigQuery |
| clickhouse-client | Клиент ClickHouse (OLAP) |
| cockroach | CLI для CockroachDB (distributed SQL) |
| cqlsh | CQL shell для Cassandra / ScyllaDB |
| cypher-shell | Клиент для Neo4j (графовая БД) |
| databricks-cli | Управление Databricks (кластеры, jobs, DBFS) |
| db2 | CLI для IBM DB2 |
| dbeaver | универсальный GUI database client |
| dbmate | Лёгкий инструмент миграций |
| dolt | Git для данных (версионированная SQL БД) |
| duckdb | Встраиваемая аналитическая СУБД (SQL over CSV/Parquet) (CLI) |
| elasticsearch | Клиент Elasticsearch (esql) |
| faasdb | serverless БД |
| fauna-shell | Клиент FaunaDB |
| firebase-cli | CLI для Firebase (Firestore, Auth, Storage) |
| flyway | Инструмент миграций БД (универсальный) |
| graphdb-console | CLI для GraphDB (RDF) |
| gremlin-console | Клиент для графовых запросов Apache TinkerPop |
| influx | CLI для InfluxDB (time-series) |
| iredis | Клиент Redis с автодополнением и подсветкой |
| isql | Универсальный ODBC-клиент |
| kdb+ | Клиент для финансовой time-series БД (q) |
| knex | CLI для миграций (Node.js) |
| liquibase | Универсальный инструмент миграций |
| litecli | Клиент SQLite с автодополнением |
| litestream | Репликация SQLite в реальном времени |
| meilisearch-cli | Клиент для поискового движка Meilisearch |
| memcached-tool | Утилиты для Memcached |
| migrate | Миграции БД (golang-migrate) |
| mongosh | Клиент MongoDB |
| mssql-cli | Клиент MS SQL Server с автодополнением |
| mycli | Клиент MySQL с автодополнением |
| mysql | Клиент MySQL |
| mysql-workbench | GUI для MySQL (headless скриптинг) |
| neonctl | CLI для Neon (serverless PostgreSQL) |
| opensearch-cli | Клиент OpenSearch (форк Elasticsearch) |
| orientdb-console | CLI для OrientDB |
| pg_repack | online PostgreSQL table reorganization |
| pg_top | Мониторинг процессов PostgreSQL (top-стиль) |
| pgadmin4 | GUI для PostgreSQL (скриптовый режим) |
| pgbackrest | Резервное копирование и восстановление PostgreSQL |
| pgbadger | Анализатор логов PostgreSQL |
| pgbench | Нагрузочное тестирование PostgreSQL |
| pgbouncer | PostgreSQL connection pooling |
| pgcenter | Администрирование и диагностика PostgreSQL (TUI) |
| pgcli | Клиент PostgreSQL с автодополнением и подсветкой |
| pgmodeler | Генерация и визуализация схемы PostgreSQL |
| planetscale | CLI для PlanetScale (Vitess-based) |
| prisma | ORM + миграции + Studio |
| psql | Клиент PostgreSQL |
| questdb | CLI для QuestDB (time-series) |
| redis-cli | Клиент Redis |
| rqlite | Distributed SQLite (Raft) |
| schemaspy | Генерация ER-диаграмм из БД |
| scylla-cli | Клиент ScyllaDB (альтернатива Cassandra) |
| searchd | Клиент Sphinx Search (full-text) |
| sequelize-cli | CLI для миграций (Node.js) |
| snowsql | CLI Snowflake |
| solr-cli | Клиент Apache Solr |
| sqitch | Миграции БД без фреймворков (VCS-ориентированные) |
| sqlcipher | Шифрованная SQLite |
| sqlcmd | CLI для Microsoft SQL Server |
| sqlite3 | Клиент SQLite (встроенная БД) |
| sqlplus | CLI для Oracle Database |
| sqsh | Интерактивный клиент для Sybase (и MS SQL) |
| studio3t | GUI для MongoDB (headless скриптинг) |
| supabase-cli | CLI для Supabase (PostgreSQL платформа) |
| tarantool | in-memory БД |
| tbls | Генерация документации схемы БД |
| timescaledb | CLI для TimescaleDB (PostgreSQL + time-series) |
| trino | CLI Trino (распределённые SQL-запросы, бывш. Presto) |
| turso | CLI для Turso (SQLite на edge) |
| typeorm | CLI для миграций (Node.js) |
| typesense-server | CLI для Typesense (self-hosted поиск) |
| usql | Универсальный CLI к десяткам СУБД (аналог psql для всего) |
| victoria-metrics | CLI для VictoriaMetrics (time-series) |
| vmctl | CLI для VictoriaMetrics (time-series) |
| yugabytedb | Клиент YugabyteDB (distributed SQL) (ysqlsh, ycqlsh) |

## 15. Контейнеризация, оркестрация и виртуализация

| Инструмент | Описание |
|-----------|----------|
| argocd | GitOps-доставка в Kubernetes (Argo CD CLI) |
| buildah | Сборка OCI-образов без демона |
| buildkit | Современный билд-движок (buildctl) |
| chroot | Изменение root filesystem |
| cilium | networking/security/observability Kubernetes |
| colima | Контейнерные рантаймы на macOS/Linux ( Lima-подход) |
| conftest | Тестирование конфигураций политиками Rego/OPA |
| containerd | container runtime |
| cosign | Подписание и проверка контейнеров (Sigstore) |
| crane | Манипуляции образами в registry без Docker (go-containerregistry) |
| crictl | Отладка CRI (container runtime interface) |
| ctr | CLI для containerd |
| dive | Анализ слоёв Docker-образа |
| firecracker | Микровиртуалки для serverless (AWS Lambda/Fargate) |
| flux | GitOps-инструментарий (Flux CD) |
| grype | Сканер уязвимостей контейнерных образов (Anchore) |
| hadolint | Линтер Dockerfile |
| helmfile | Декларативное управление набором Helm-релизов |
| incus | Системные контейнеры (LXD-форк) |
| k3d | Лёгкие кластеры k3s в Docker |
| k3s | Облегчённый Kubernetes (Rancher) |
| k9s | TUI-управление кластерами Kubernetes |
| kaniko | Сборка образов в Kubernetes без Docker-демона |
| kata-containers | виртуализованные контейнеры |
| kind | Kubernetes-in-Docker для локальных кластеров |
| ko | Быстрая сборка образов из Go-кода |
| kompose | Конвертация docker-compose в Kubernetes |
| krew | Менеджер плагинов kubectl |
| kube-bench | Проверка соответствия кластера CIS Benchmark |
| kube-hunter | Поиск уязвимостей в Kubernetes |
| kubectl | Управление Kubernetes-кластером |
| kubectx | Быстрое переключение контекстов kubectl |
| kubens | Быстрое переключение namespace (спутник kubectx) |
| kustomize | Шаблононезависимая кастомизация YAML-манифестов |
| kyverno | Менеджер политик Kubernetes (Kubernetes-native) |
| lima | Linux-виртуалки на macOS (под капотом colima) |
| lxc | Системные контейнеры |
| minikube | Локальный Kubernetes (множество драйверов) |
| nerdctl | Docker-подобный CLI для containerd |
| nomad | HashiCorp workload orchestrator |
| nsenter | Подключение к namespaces процесса |
| opa | Движок политик как код (Open Policy Agent) |
| oras | OCI Registry as Storage — произвольные артефакты в registry |
| pack | Сборка образов через Cloud Native Buildpacks |
| packer | Сборка образов машин для множества платформ (HashiCorp) |
| podman | Rootless-альтернатива Docker |
| qemu-img | Создание/конвертация образов дисков VM |
| regctl | registry/image management |
| runc-debug | отладка container runtime |
| runv | альтернативный container runtime |
| skaffold | Цикл build-push-deploy для Kubernetes (Google) |
| skopeo | Копирование образов между registry (без демона) |
| stern | Хвост логов нескольких подов/контейнеров сразу |
| syft | Генерация SBOM (спутник grype) |
| systemd-nspawn | Лёгкие системные контейнеры |
| talosctl | Управление Talos Linux |
| tilt | Локальная разработка микросервисов в Kubernetes |
| toolbox | Контейнерные development environments |
| trivy | Сканер уязвимостей образов, IaC, репозиториев |
| unshare | Linux namespaces |
| vboxmanage | Управление VirtualBox headless |
| velero | Бэкап, восстановление и миграция кластеров Kubernetes |
| virsh | Управление KVM/QEMU виртуалками |

## 16. Мониторинг, метрики и логирование

| Инструмент | Описание |
|-----------|----------|
| alertmanager | Маршрутизация и дедупликация алертов |
| alloy | Единый агент сборки метрик/логов/трейсов (Grafana) |
| collectd | Классический сборщик системной статистики |
| filebeat | Shipper логов (Elastic) |
| fluent-bit | Лёгкий сборщик и маршрутизатор логов |
| grafana-cli | управление дашбордами |
| iotop | Дисковый I/O по процессам |
| loki | Горизонтально масштабируемое лог-хранилище (Grafana) |
| monit | Мониторинг и автоматический ремонт процессов/файлов |
| netdata | Мониторинг в реальном времени с автодетектом сервисов |
| node_exporter | Экспортёр метрик хоста для Prometheus |
| perfetto | tracing/performance analysis |
| prometheus | Сбор и запрос метрик (TSDB) |
| prometheus-operator | управление мониторингом в K8s |
| promtail | Сбор логов и отправка в Loki |
| promtool | CLI администрирования Prometheus и проверка правил |
| telegraf | Агент сбора метрик (InfluxDB) |
| vector | Высокопроизводительный пайплайн логов/метрик (Rust) |
| zabbix-agent2 | Агент мониторинга Zabbix (Go) |
| zabbix_get | Опрос Zabbix-агентов из CLI |

## 17. Мультимедиа

| Инструмент | Описание |
|-----------|----------|
| aacgain | Нормализация громкости AAC (ReplayGain) |
| abcde | Риппинг CD-дисков |
| aomenc | AV1 кодек от Alliance for Open Media |
| atomicparsley | Редактирование метаданных MP4/M4A |
| av1an | кодировщик AV1 |
| avifdec | Конвертация в/из AVIF |
| avifenc | Конвертация в/из AVIF |
| beets | Менеджер музыкальной библиотеки с автотегированием |
| blender | 3D-рендеринг и обработка (headless режим) |
| cdparanoia | Риппинг аудио-CD |
| cjpeg | Кодирование JPEG (из libjpeg-turbo) |
| cjxl | JPEG XL формат |
| cmus | Музыкальный плеер для терминала |
| cwebp | Конвертация в WebP |
| darktable-cli | Обработка RAW-фотографий |
| dav1d | декодер AV1 |
| djxl | JPEG XL формат |
| dwebp | Декодирование WebP |
| espeak-ng | TTS |
| exiftool | Чтение/запись метаданных (500+ форматов) |
| exiv2 | Манипуляции EXIF-метаданными |
| eyeD3 | Редактирование ID3-тегов MP3 |
| faac | Кодирование AAC |
| faad | Декодирование AAC |
| ffmpeg | Конвертация, нарезка, извлечение кадров, изменение кодеков |
| ffplay | Проигрыватель на базе FFmpeg |
| ffprobe | Анализ медиа-файлов |
| ffprobe-json | анализ медиа в JSON |
| flac | Кодирование FLAC |
| flameshot | Скриншоты с аннотированием (CLI-режим) |
| gallery-dl | Скачивание изображений с 1000+ сайтов |
| gifsicle | Оптимизация и манипуляции GIF |
| graphicsmagick | Форк ImageMagick (быстрее в некоторых операциях) |
| grim | Скриншоты для Wayland |
| handbrake-cli | Конвертация видео (H.264, H.265, AV1) |
| id3v2 | Редактирование ID3-тегов MP3 |
| imagemagick | Командная строка для работы с изображениями (convert, mogrify, identify) |
| inkscape | Векторная графика SVG (headless) |
| jpegoptim | Оптимизация JPEG |
| jxl | JPEG XL формат |
| kid3-cli | Редактирование тегов аудиофайлов |
| lame | Кодирование MP3 |
| liquidsoap | Язык и сервер для потокового аудио (радио) |
| mac | Monkey's Audio (APE lossless) |
| maim | Скриншоты с выбором области |
| mediainfo | Подробная техническая информация о медиа |
| metaflac | Редактирование метаданных FLAC |
| mkvextract | Работа с Matroska (.mkv) (mkvtoolnix) |
| mkvmerge | Работа с Matroska (.mkv) (mkvtoolnix) |
| moviepy-cli | обработка видео из CLI |
| mp3gain | Нормализация громкости MP3 (без перекодирования) |
| mp3split | Разделение MP3 по времени |
| mp3wrap | Объединение MP3 без перекодирования |
| mp4box | Манипуляции с MP4-контейнерами (GPAC) |
| mpc | Клиент управления MPD |
| mpd | Сервер-демон воспроизведения музыки |
| mplayer | Классический медиаплеер |
| mpv | Медиаплеер с богатым CLI и scriptable API |
| obs-cli | Управление OBS Studio |
| obs-websocket | Управление OBS Studio |
| oggdec | Ogg Vorbis декодирование |
| oggenc | Ogg Vorbis кодирование |
| optipng | Оптимизация PNG |
| opusdec | Opus кодек (лучший для голоса) |
| opusenc | Opus кодек (лучший для голоса) |
| piper | локальный text-to-speech |
| playerctl | Управление MPRIA-плеерами (play/pause/next) |
| pngcrush | Оптимизация PNG |
| pngquant | Сжатие PNG |
| potrace | Растр → вектор (bitmap tracing) |
| rav1e | Кодировщик AV1 на Rust |
| rawtherapee-cli | Обработка RAW-фотографий |
| scrot | Скриншоты из командной строки |
| shntool | Работа с lossless аудио (cue+flac/wav) |
| slurp | Выбор области экрана (Wayland, спутник grim) |
| sox | Обработка аудио |
| speexdec | Speex кодек |
| speexenc | Speex кодек |
| streamlink | Извлечение потоков из Twitch, YouTube Live |
| svt-av1 | Кодировщик AV1 от Intel |
| twolame | Кодирование MP2 |
| v4l2-ctl | Управление веб-камерами и захватом видео (v4l-utils) |
| vips | Обработка изображений с низким потреблением памяти |
| vipsthumbnail | Обработка изображений с низким потреблением памяти |
| vlc | Медиаплеер и конвертер (headless через cvlc) |
| vorbiscomment | Редактирование комментариев Ogg Vorbis |
| vpxdec | VP8/VP9 кодек от Google |
| vpxenc | VP8/VP9 кодек от Google |
| wavpack | WavPack (lossless с хорошим сжатием) |
| webp | Конвертация в/из WebP |
| wf-recorder | Запись экрана на Wayland |
| whisper | speech-to-text |
| whisper.cpp | native/local Whisper inference |
| wvunpack | WavPack (lossless с хорошим сжатием) |
| x264 | Кодировщик H.264 |
| x265 | Кодировщик H.265 |
| xorriso | Создание и запись ISO/образов (cdrecord-наследник) |
| yt-dlp | Скачивание видео с YouTube и 1000+ сайтов |

## 18. Облака, IaC и платформы

| Инструмент | Описание |
|-----------|----------|
| aliyun | Alibaba Cloud CLI |
| ansible-playbook | Конфигурация хостов по SSH |
| atlantis | Автоматизация terraform plan/apply через pull-запросы |
| aws | AWS CLI (EC2, S3, Lambda, IAM, CloudFormation) |
| az | Microsoft Azure CLI |
| checkov | Сканер безопасности IaC (Terraform, K8s, CloudFormation) |
| doctl | DigitalOcean CLI |
| exo | Exoscale CLI |
| flyctl | Fly.io (edge-deploy приложений) |
| gcloud | Google Cloud SDK |
| hcloud | Hetzner Cloud CLI |
| heroku | Heroku CLI |
| ibmcloud | IBM Cloud CLI |
| infracost | Оценка стоимости облака из Terraform-кода |
| linode-cli | Linode/Akamai CLI |
| netlify | Деплой и управление проектами Netlify |
| oci | Oracle Cloud Infrastructure CLI |
| railway | Деплой приложений на Railway |
| scaleway-cli | Scaleway CLI |
| serverless | Framework для AWS Lambda |
| tencentcloud-cli | Tencent Cloud CLI |
| terraform | IaC: провайдеры для 300+ облаков |
| terraform-docs | Генерация документации из модулей Terraform |
| terragrunt | Обёртка над Terraform: DRY-конфигурация и удалённые состояния |
| tflint | Линтер конфигураций Terraform |
| tofu | OpenTofu — открытый форк Terraform (Linux Foundation) |
| up | Upbound / Crossplane (управление облаками через K8s) |
| vagrant | Локальное поднятие VM для тестов |
| vercel | Деплой frontend/Vercel Functions |
| vultr-cli | Управление инфраструктурой Vultr |
| wrangler | CLI Cloudflare Workers/Pages/R2/D1 |

## 19. Оболочки (shell) и расширения CLI

| Инструмент | Описание |
|-----------|----------|
| atuin | Синхронизация и SQL-поиск по истории команд |
| dash (shell) | Быстрый POSIX shell (Debian /bin/sh) |
| direnv | Переменные окружения по директории (.envrc) |
| elvish | Экспрессивная оболочка с конвейерами структурных данных |
| fish | Дружелюбная оболочка с автопредложениями |
| fzf-tab | Интеллектуальное автодополнение в терминале |
| Ghostty | Быстрый кроссплатформенный терминал на Rust с аппаратным ускорением |
| hstr | Интерактивный просмотр истории bash/zsh |
| ksh | KornShell |
| mcfly | Умный поиск истории команд на нейросети |
| nushell | Структурированная оболочка: данные как таблицы |
| osh | Oil shell — совместимый bash с строгими режимами |
| pay-respects | Быстрая альтернатива thefuck (Rust) |
| pwsh | PowerShell (кроссплатформенный, объектные пайпы) |
| skim | Fuzzy-поиск (Rust, альтернатива fzf) |
| starship | Быстрое кастомизируемое приглашение командной строки |
| tcsh | C shell с дополнениями |
| thefuck | Автоисправление ошибочных команд |
| warp | Современный терминал с AI-интеграцией, разделением и облачной синхронизацией |
| Warp CLI | AI-терминал с встроенной командной строкой |
| xonsh | Оболочка на Python (Python + shell) |
| zoxide | Умная смена директорий (современный z/autojump) |
| zsh | Мощная оболочка (macOS по умолчанию) |

## 21. Обработка текста и структурированных данных

| Инструмент | Описание |
|-----------|----------|
| ack | Программистский поиск по коду, уважает .gitignore по умолчанию |
| awk | Мощный язык обработки текста (колоночные данные) |
| carapace | Умное контекстно-зависимое автодополнение |
| cheat | Локальные редактируемые cheatsheets |
| choose | Выборка столбцов с регулярными выражениями |
| cjson | Проверка и форматирование JSON |
| column | Форматирование данных в таблицы |
| comm | Сравнение отсортированных файлов построчно |
| csvgrep | Набор инструментов для CSV (csvkit) |
| csvkit | Набор инструментов для CSV (stat, sort, join, etc.) |
| csvsql | SQL-запросы прямо к CSV-файлам |
| csvtool | Ещё один обработчик CSV (OCaml) |
| cut | Вырезание колонок (столбцов) |
| dasel | Универсальный селектор данных (JSON, YAML, TOML, XML, CSV) |
| datamash | Статистика по текстовым файлам (sum, mean, median) |
| diff | Сравнение файлов |
| dos2unix | Конвертация окончаний строк |
| enca | Автоопределение кодировки |
| fselect | Поиск файлов с SQL-подобными запросами |
| fx | Интерактивный просмотр JSON (JavaScript) |
| grep | Поиск по регулярным выражениям |
| grit | AI-индексирование кодовой базы, поиск по смыслу а не по тексту |
| gron | Преобразует JSON в плоский, grep-дружественный формат |
| hjson | Конвертер между HJSON и JSON |
| htmlq | jq для HTML (CSS-селекторы) |
| hurl | Тестирование HTTP-запросов с декларативным синтаксисом |
| iconv | Транскодирование текста |
| ifne | Выполняет команду, если stdin не пуст (moreutils) |
| jd | Сравнение JSON-структур |
| jid | Интерактивный просмотр JSON с фильтрацией |
| jless | Пейджер для JSON с подсветкой |
| jo | Генерация JSON из shell |
| join | Объединение строк из двух файлов по общему полю |
| jq | Парсинг и преобразование JSON |
| json-diff | Сравнение JSON-структур |
| json-merge-patch | Операции RFC 7386 |
| json-patch | Операции RFC 6902 |
| jsonlint | Валидация JSON-файлов |
| look | Бинарный поиск в отсортированном файле |
| miller | Швейцарский нож для CSV, TSV, JSON (mlr) |
| navi | Интерактивные шпаргалки команд с параметрами |
| nq | jq для 1Password (и других) |
| numfmt | Форматирование чисел (GNU coreutils) |
| parallel | Параллельное выполнение команд |
| paste | Объединение строк из нескольких файлов |
| patch | Применение патчей (diff) |
| ptx | Пермутированный индекс (KWIC) |
| pup | CSS-селекторы для HTML в терминале |
| recode | Конвертация между кодировками |
| rev | Переворачивание строк |
| ripgrep-all | Расширение ripgrep — поиск не только в тексте, но и в PDF, архивах, офисных документах |
| sd | Интуитивная замена sed (проще синтаксис) |
| sed | Потоковое редактирование текста (замены, фильтрация) |
| shellcheck | Линтинг shell-скриптов |
| shfmt | Форматирование shell-скриптов |
| shuf | Перемешивание строк |
| sort | Сортировка строк |
| sponge | Перезапись файла «на месте» в пайпе (moreutils) |
| tac | Обратный cat |
| tealdeer | Быстрый Rust-клиент справочника команд |
| tldr | Упрощённые man-страницы с примерами |
| tomll | Валидация TOML |
| tomlq | jq-подобный инструмент для TOML |
| tr | Преобразование символов (замена, удаление) |
| ts | Добавляет временные метки к строкам (moreutils) |
| tsort | Топологическая сортировка |
| tsv-utils | Высокопроизводительная обработка TSV от eBay |
| uchardet | Автоопределение кодировки |
| uniq | Удаление повторяющихся строк (в отсортированном файле) |
| unix2dos | Конвертация окончаний строк |
| vidir | Редактирование списка файлов в редакторе (moreutils) |
| vipe | Вставляет редактор в пайплайн (moreutils) |
| wc | Подсчёт строк, слов, байт |
| wdiff | Построчное сравнение с подсветкой слов |
| xargs | Построение команд из stdin |
| xidel | Обработка XML из командной строки |
| xmlstarlet | XML shell |
| xmltk | Обработка XML из командной строки |
| xq | jq для XML |
| xsv | Ultra-fast CSV обработка на Rust |
| yamlfmt | Форматирование YAML |
| yamllint | Линтер YAML |
| yj | Конвертер между JSON, YAML, TOML, XML, HCL |
| yq | Парсинг и преобразование YAML |

## 22. Отладка, профилирование и реверс-инжиниринг

| Инструмент | Описание |
|-----------|----------|
| bcc | Инструменты eBPF-трассировки (execsnoop, biolatency и др.) |
| bpftool | Инспекция и управление eBPF-программами и картами |
| bpftrace | Высокоуровневая трассировка ядра на eBPF |
| cachegrind | Профилирование кэша и вызовов (Valgrind) |
| callgrind | Профилирование кэша и вызовов (Valgrind) |
| datefudge | Сдвиг времени для тестируемых процессов |
| faketime | Подмена системного времени для процесса (libfaketime) |
| file | Определение типа файла по магическим байтам |
| ftrace | Kernel tracing |
| gdb | Отладчик C/C++/Rust/Go |
| ghidra | Фреймворк реверс-инжиниринга с headless-режимом (NSA) |
| heaptrack | Профилирование кучи (Qt) |
| hexdump | Hex-дамп произвольных файлов |
| ldconfig | Обновление кэша shared libraries |
| ldd | Список shared libraries бинаря |
| lldb | Отладчик от LLVM |
| ltrace | Трассировка библиотечных вызовов |
| nm | Символы в объектном файле |
| objdump | Дизассемблирование и заголовки ELF |
| od | Hex-дамп произвольных файлов |
| perf | Профилирование ядра и пользовательского кода |
| radare2 | UNIX-подобный фреймворк реверс-инжиниринга |
| readelf | Дизассемблирование и заголовки ELF |
| rizin | Форк/развитие radare2 (форензика, отладка, дизасм) |
| strace | Трассировка системных вызовов процесса |
| strings | Извлечение строк из бинарника |
| trace-cmd | Внешний интерфейс к ftrace (ядро Linux) |
| valgrind | Поиск утечек памяти и гонок |
| xxd | Hex-дамп произвольных файлов |

## 23. Пакетные менеджеры

| Инструмент | Описание |
|-----------|----------|
| ant | Java build tool |
| apk | Пакетный менеджер Alpine Linux |
| apt | Debian/Ubuntu |
| apt-get | Debian/Ubuntu |
| asdf | Универсальный менеджер версий для множества языков |
| boot | Менеджеры для Clojure |
| brew | Алиас homebrew |
| bundle | Менеджер зависимостей Ruby |
| bundler-audit | Аудит уязвимостей Ruby-гемов (patch-level) |
| cabal | Менеджер пакетов Haskell |
| cargo-audit | Аудит уязвимостей в зависимостях Rust |
| cargo-deny | Проверка лицензий, дубликатов и уязвимостей Rust |
| choco | Chocolatey — пакетный менеджер Windows |
| cocoapods | Менеджер зависимостей для iOS/macOS |
| codespell | поиск опечаток в исходниках и документации |
| comma | Запуск инструментов из nixpkgs без глобальной установки |
| composer | Менеджер зависимостей PHP |
| conan | Менеджер пакетов C++ |
| conda | Менеджер окружений для data science (кросс-языковой) |
| cpan | Менеджер пакетов Perl |
| cpanm | Менеджер пакетов Perl |
| dnf | RHEL/CentOS/Fedora |
| dpkg | Debian/Ubuntu |
| dub | Менеджер пакетов для D языка |
| emerge | Пакетный менеджер Portage (Gentoo) |
| eslint | статический анализ JavaScript/TypeScript |
| flatpak | Универсальные пакеты Linux |
| fnm | Менеджеры версий для конкретных языков |
| fpm | Сборка пакетов deb/rpm/... из файлов и директорий |
| gem | Менеджер пакетов Ruby |
| go get | Менеджер модулей Go |
| go install | Менеджер модулей Go |
| go mod | Менеджер модулей Go |
| goenv | Менеджеры версий для конкретных языков |
| gradle | Java build tool |
| guix | GNU Guix (альтернатива Nix) |
| hatch | Современный менеджер Python |
| hex | Менеджер для Elixir |
| homebrew | macOS package manager (brew) |
| hunter | C++ package manager (CMake) |
| leiningen | Менеджеры для Clojure |
| luarocks | Менеджер пакетов Lua |
| lychee | проверка битых ссылок |
| macports | Пакетный менеджер macOS |
| mamba | Менеджер окружений для data science (кросс-языковой) |
| markdownlint-cli2 | structural Markdown lint |
| maven | Java build tool (mvn) |
| micromamba | Менеджер окружений для data science (кросс-языковой) |
| mise | Менеджер версий dev-инструментов, env и задач (бывш. rtx) |
| mvn | Алиас maven |
| nala | Современный фронтенд apt |
| nfpm | Сборка deb/rpm/APK без конфигов (Go) |
| nix | Воспроизводимые сборки (NixOS) |
| nix-env | Воспроизводимые сборки (NixOS) |
| nix-shell | Воспроизводимые сборки (NixOS) |
| npm | Менеджеры пакетов JavaScript |
| npx | Запуск Node-пакетов без установки |
| nuget | .NET package manager |
| nvm | Менеджеры версий для конкретных языков |
| oxlint | быстрый JS/TS linter |
| pacman | Arch Linux |
| paket | Менеджер зависимостей для .NET (альтернатива NuGet) |
| paru | Arch Linux |
| pdm | Менеджер проектов Python по современным PEP |
| pear | PHP extensions |
| pecl | PHP extensions |
| pip | Python package managers |
| pip-tools | Python package managers |
| pipenv | Управление зависимостями и окружениями Python |
| pipx | Python package managers |
| pixi | Системный пакетный менеджер на conda-экосистеме (Rust) |
| pkg | Пакетный менеджер FreeBSD |
| pnpm | Менеджеры пакетов JavaScript |
| poetry | Современный Python (зависимости, сборка) |
| prettier | форматирование кода/данных |
| pub | Dart/Flutter package manager |
| pyenv | Менеджеры версий для конкретных языков |
| pyrefly | статический анализ/type checking Python |
| rbenv | Менеджеры версий для конкретных языков |
| rebar3 | Менеджер для Erlang |
| renovate | Автоматическое обновление зависимостей |
| rpm | RHEL/CentOS/Fedora |
| rug | openSUSE |
| rustup | Установщик и менеджер версий Rust |
| rye | Python (от создателя Flask) |
| sbt | Scala build tool |
| scoop | Пакетный менеджер Windows для CLI-инструментов |
| snap | Универсальные пакеты Linux |
| spack | Менеджер пакетов для HPC (суперкомпьютеры) |
| stack | Менеджер пакетов Haskell (альтернатива cabal) |
| swift package | Swift Package Manager |
| tools.deps | Менеджеры для Clojure |
| ty | быстрый type checker Python |
| uv | Сверхбыстрый менеджер пакетов и проектов Python (Astral, Rust) |
| uvx | Одноразовый запуск Python CLI в изолированной среде |
| vcpkg | C++ библиотечный менеджер от Microsoft |
| verdaccio | приватный npm-репозиторий |
| vfox | Универсальный менеджер версий на Go |
| virtualenv | Классические виртуальные окружения Python |
| winget | Официальный пакетный менеджер Windows |
| xbps | Пакетный менеджер Void Linux |
| yarn | Менеджеры пакетов JavaScript |
| yay | Arch Linux |
| yum | RHEL/CentOS/Fedora |
| zig fetch | Менеджер пакетов Zig |
| zypper | openSUSE |

## 24. Простой текстовый учёт и заметки

| Инструмент | Описание |
|-----------|----------|
| beancount | Учёт двойной записью на Python |
| cointop | Курс криптовалют в терминале (TUI) |
| fava | Веб-интерфейс для beancount |
| hledger | Дружелюбный аналог ledger (Haskell) |
| ledger | Двойная запись в текстовом файле |
| nb | Заметки и база знаний с git-синхронизацией |
| taskwarrior | Менеджер задач из командной строки |
| ticker | Тикеры акций и криптовалют в терминале |
| timewarrior | Учёт времени (спутник taskwarrior) |
| vit | TUI-интерфейс к taskwarrior |
| zk | Zettelkasten-заметки в терминале |

## 26. Резервное копирование и снапшоты

| Инструмент | Описание |
|-----------|----------|
| borg | Дедуплицирующий бэкап с шифрованием и сжатием |
| borgmatic | Декларативная обёртка над borg (YAML-конфиги) |
| btrbk | Бэкап и репликация снапшотов btrfs |
| dar | Disk Archive: бэкап с инкрементами и шифрованием |
| duplicity | Инкрементальный бэкап с GPG на любые хранилища |
| fsarchiver | Сохранение/восстановление ФС с содержимым |
| kopia | Бэкап с шифрованием, дедупликацией и версионированием |
| partclone | Клонирование разделов (умный копировщик занятых блоков) |
| rdiff-backup | Инкрементальный бэкап с reverse-diff |
| restic | Быстрый безопасный бэкап с дедупликацией (Go) |
| rsnapshot | Снапшоты на rsync + hardlinks |
| snapper | Управление снапшотами btrfs/LVM |
| timeshift | Системные снапшоты (восстановление ОС) |
| wal-g | backup PostgreSQL/other DB |

## 27. Сборка, CI/CD и тестирование

| Инструмент | Описание |
|-----------|----------|
| ab | Простое HTTP-бенчмаркинг (Apache Bench) |
| act | Локальный запуск GitHub Actions |
| argo-workflows | workflow engine |
| artillery | Нагрузочное тестирование |
| ast-grep | Структурный поиск и rewrite по AST |
| autoconf | GNU build system |
| automake | GNU build system |
| bazel | Монорепо-сборка (Google стиль) |
| bazelisk | управление версиями Bazel |
| bombardier | Быстрый HTTP load-тест (Go) |
| browserslist | browser compatibility targeting |
| buck2 | Монорепо-сборка (Meta стиль) |
| cargo-nextest | Быстрый и удобный runner тестов Rust |
| ccache | Кэш компиляции для gcc/clang |
| clang-format | Автоформатирование C/C++/JS (LLVM) |
| clang-tidy | Статический анализ и автофиксы C/C++ |
| clangd | Language Server для C/C++ (LLVM) |
| cmake | Кроссплатформенная сборка C++ |
| comby | Структурный поиск и преобразование кода |
| cppcheck | Статический анализ C/C++ |
| dagger | CI/CD-пайплайны как код (программируемые) |
| distcc | Распределённая компиляция C/C++ |
| dprint | Высокопроизводительный formatter на Rust |
| drone | CI/CD сервер |
| earthly | Повторяемые сборки и CI в контейнерах (Earthly) |
| fio | Бенчмарк дисковых подсистем и I/O |
| gatling | Нагрузочное тестирование (Scala-DSL, CLI-раннер) |
| gitbatch | Управление несколькими Git-репозиториями в одном месте |
| gitlab-ci | инструменты CI/CD |
| gitlab-runner | Локальный раннер GitLab CI |
| golangci-lint | Агрегатор Go linters |
| hey | HTTP load generator на Go |
| hyperfine | Точное бенчмаркирование CLI-команд |
| ioping | Замер латентности диска |
| jmeter | Нагрузочное и функциональное тестирование (Apache, CLI) |
| just | Удобный раннер команд для проектов (casey/just) |
| k6 | Нагрузочное тестирование |
| locust | Нагрузочное тестирование Python |
| mage | Раннер задач на чистом Go |
| make | Классические Makefile |
| mask | Раннер задач, определённых в Markdown |
| meson | Современная сборка (GNOME, systemd) |
| mold | Сверхбыстрый линкер (современная альтернатива ld/gold) |
| newman | CLI для коллекций Postman |
| ninja | Современная сборка (GNOME, systemd) |
| oha | HTTP load-генератор с TUI (Rust) |
| pact | Contract testing |
| pants | Сборка и тестирование монорепозиториев (Python/Go/JS/Java) |
| sccache | Кэш компиляции с облачным хранением (Mozilla) |
| scons | Альтернативные билд-системы |
| siege | Классический HTTP load-тест |
| staticcheck | Статический анализ Go |
| stress | Простая нагрузка на CPU/память/диск |
| stress-ng | Расширенный стресс-тест системных подсистем |
| sysbench | Бенчмарк CPU/памяти/БД/файловых систем |
| task | Современный Makefile-альтернатива на YAML (go-task) |
| tekton | Kubernetes-native pipelines |
| vegeta | HTTP load testing |
| waf | Альтернативные билд-системы |
| wrk | HTTP benchmarking |
| wrk2 | HTTP benchmarking |

## 28. Сетевые инструменты

| Инструмент | Описание |
|-----------|----------|
| apache | Веб-сервер Apache HTTP (httpd, apachectl) |
| aria2c | Многопоточное скачивание (HTTP, FTP, BitTorrent) |
| arp | Управление ARP-кэшем |
| arp-scan | Сканирование локальной сети по ARP |
| autossh | Автоматический перезапуск SSH-туннелей |
| axel | Лёгкий акселератор загрузок |
| bind9 | Классический DNS-сервер (named, rndc) |
| bmon | Мониторинг полосы с графиками |
| bore | Минималистичные публичные туннели к localhost |
| bridge-utils | Настройка сетевых мостов |
| caddy | Reverse proxy с автоматическим TLS |
| calicoctl | управление сетевыми политиками в K8s |
| capinfos | Статистика pcap-файлов (Wireshark) |
| consul | Service discovery и распределённая конфигурация |
| coredns | Расширяемый DNS-сервер (DNS Kubernetes) |
| crowdsec | Краудсорс-защита от брутфорса (современный fail2ban) |
| curl | Отправка HTTP-запросов, работа с API |
| curlie | curl с эргономикой httpie |
| dig | DNS-запросы (полная информация) |
| dnsmasq | Лёгкий DNS/DHCP/TFTP (локальные сети) |
| dog | Современный DNS-клиент, альтернатива dig с JSON-выводом |
| doggo | Современный DNS-клиент с DoH/DoT (Rust) |
| drill | DNS-запросы (утилита из ldns) |
| editcap | Разделение/фильтрация pcap (Wireshark) |
| envoy | Service proxy для облачных сред |
| etcd | Распределённое хранилище ключ-значение |
| ethtool | Настройка сетевых карт |
| evans | Интерактивный gRPC-клиент |
| falco | Runtime-безопасность: аномалии в syscall (CNCF) |
| gost | Мультипротокольные прокси и туннели (GO Simple Tunnel) |
| gping | Пинг с графиком в реальном времени |
| haproxy | Load balancer и reverse proxy |
| headscale | Self-hosted координатор для Tailscale |
| host | Простой DNS-запрос (альтернатива dig) |
| hping3 | Генератор произвольных TCP/IP-пакетов |
| httpie | Человеко-читаемый HTTP-клиент |
| httping | Ping по HTTP/HTTPS с временем ответа |
| httpstat | Визуализация статистики HTTP-запроса (curl-обёртка) |
| iftop | Трафик по соединениям интерфейса (TUI) |
| ip | Универсальная утилита для интерфейсов, маршрутов, туннелей (iproute2) |
| ipcalc | Расчёт подсетей IPv4/IPv6 |
| iperf3 | Измерение пропускной способности сети |
| ipfs | Distributed Web: IPFS-нода и CLI (kubo) |
| ipset | Управление наборами IP для iptables |
| iptables | Фильтрация пакетов (firewall) |
| iptraf | Мониторинг трафика (TUI) |
| ipv6calc | Расчёты и конвертация IPv6-адресов |
| knot | Высокопроизводительный авторитативный DNS |
| ldapsearch | Поиск по LDAP (OpenLDAP) |
| lighttpd | Лёгкий высокопроизводительный веб-сервер |
| linkerd | service mesh |
| lsof | Список открытых файлов и сокетов |
| masscan | Асинхронный сканер портов (очень быстрый) |
| mergecap | Слияние pcap-файлов (Wireshark) |
| mitmproxy | Интерактивный HTTPS-прокси для отладки (CLI/TUI/веб) |
| mktorrent | Создание .torrent-файлов |
| mole | Простое создание SSH-туннелей |
| mosh | Мобильный SSH с устойчивостью к переключению сетей |
| mount.cifs | Монтирование SMB shares |
| mtr | Traceroute + ping в реальном времени |
| nc | «Швейцарский армейский нож» для TCP/UDP (netcat) |
| ncat | Улучшенная версия netcat (SSL, прокси) |
| nebula | Масштабируемая overlay-сеть (Slack) |
| netbird | Открытая mesh-VPN платформа (WireGuard) |
| nethogs | Сетевой трафик по процессам |
| netstat | Просмотр сетевых соединений |
| networkctl | Диагностика systemd-networkd |
| nftables | Фильтрация пакетов (firewall) |
| nginx | Веб-сервер и reverse proxy |
| ngrep | grep для сетевого трафика |
| nload | Графики трафика интерфейса (TUI) |
| nmap | Сканер портов и сетевой разведки |
| nmcli | CLI NetworkManager |
| nmtui | TUI NetworkManager |
| nslookup | DNS-запросы (простой) |
| ntopng | Анализ трафика в реальном времени (веб-UI) |
| nuttcp | Измерение пропускной способности |
| openvpn | VPN-клиент/сервер |
| osquery | SQL-запросы к состоянию системы (безопасность) |
| paping | TCP-пинг с измерением задержки |
| ping | Проверка доступности хостов (ICMP) |
| posting | Терминальный HTTP API-клиент с коллекциями |
| privoxy | Прокси с фильтрацией контента |
| Railway CLI | Deploy backends |
| rathole | Быстрые туннели/реверс-прокси (Rust, frp-альтернатива) |
| resolvectl | Управление и диагностика systemd-resolved |
| route | Просмотр/изменение таблиц маршрутизации |
| rpcinfo | Диагностика RPC |
| rtorrent | BitTorrent-клиент для терминала |
| s1h | SSH + SCP + менеджер паролей в одном CLI |
| scp | Копирование файлов по SSH |
| sish | SSH-based туннели к localhost (self-hosted ngrok) |
| smbclient | Клиент SMB/CIFS (Samba) |
| snort | Классический IDS/IPS |
| socat | Мультиплексор потоков (мощнее netcat) |
| speedtest-cli | Замер скорости интернета (Ookla/CLI) |
| squid | Кэширующий прокси-сервер |
| ss | Просмотр сетевых соединений (альтернатива netstat) |
| ssh | Удалённое подключение (Secure Shell) |
| sshfs | Монтирование удалённых директорий через SSH |
| Stripe CLI | Payments + webhooks (agent-ready) |
| strongswan | IPsec VPN |
| stunnel | SSL-обёртка для любого TCP-соединения |
| suricata | Сетевой IDS/IPS и NSM-движок |
| tailscale | Mesh-VPN на WireGuard с нулевой настройкой |
| tc | Traffic control (QoS, шейпинг) (iproute2) |
| tcpdump | Захват и анализ пакетов |
| tcpflow | Извлечение TCP-потоков в файлы |
| tcping | Ping через TCP-порты |
| tcptraceroute | Traceroute через TCP (обходит ICMP-блокировки) |
| tcptrack | Отслеживание TCP-соединений |
| termshark | TUI-версия Wireshark (tshark) |
| tinc | Mesh-VPN классической школы |
| tinyproxy | Лёгкий HTTP/HTTPS-прокси |
| tor | Анонимная сеть Tor |
| torsocks | Прогон приложений через Tor |
| traceroute | Трассировка маршрута |
| traefik | Современный reverse proxy для микросервисов |
| traefik-mesh | современный service mesh |
| trafficserver | Кэширующий прокси Apache Traffic Server |
| transmission-cli | BitTorrent-клиент (CLI) |
| trippy | Современный комбайн mtr/traceroute (Rust) |
| tshark | CLI-версия Wireshark (анализ трафика) |
| ufw | Фильтрация пакетов (firewall) |
| unbound | Валидирующий рекурсивный DNS-резолвер |
| varnish | HTTP-ускоритель и кэш (varnishd, varnishadm) |
| vnstat | Сбор статистики по сетевым интерфейсам |
| wakeonlan | Включение компьютеров по сети (Wake-on-LAN) |
| websocat | WebSocket/stdio bridge |
| wget | Скачивание файлов по URL |
| wget2 | Улучшенная версия wget с HTTP/2 |
| whois | Запрос информации о домене |
| wireguard | Современный VPN с высокой производительностью |
| wireshark | Анализ трафика (GUI, есть CLI) |
| wstunnel | Туннелирование трафика через WebSocket/HTTP2 |
| xh | Дружелюбный HTTP-клиент (Rust, httpie-совместимый) |
| zeek | Платформа сетевой безопасности-аналитики (бывш. Bro) |
| zerotier | Виртуальные сети уровня L2/L3 |
| zmap | Интернет-сканер (сканирование всего интернета за 45 мин) |
| zookeeper | Координация распределённых систем |

## 29. Системное администрирование и процессы

| Инструмент | Описание |
|-----------|----------|
| at | Одноразовые отложенные задачи |
| atop | Мониторинг системных ресурсов с историей |
| atq | Одноразовые отложенные задачи |
| atrm | Одноразовые отложенные задачи |
| bc | Калькулятор произвольной точности |
| bottom | Кроссплатформенный монитор ресурсов (btm, Rust) |
| btop | Красивый монитор ресурсов (CPU/RAM/сеть/диски) |
| cal | Календарь в терминале |
| chronic | Запускает команду тихо, если она успешна |
| chrony | Синхронизация времени NTP (chronyc) |
| circus | Менеджер процессов и сокетов (Python) |
| combine | Объединение строк из двух файлов с булевыми операциями |
| cpulimit | Ограничение CPU-потребления процесса |
| crontab | Пользовательский планировщик задач |
| date | Вывод/установка даты и времени |
| dc | RPN-калькулятор |
| disown | Запуск в фоне, независимый от терминала |
| dmesg | Сообщения ядра (OOM, USB, драйверы) |
| dmidecode | Данные DMI/SMBIOS (BIOS, железо) |
| dstat | Комбинированная статистика ресурсов (универсальная замена vmstat/iostat) |
| env | Переменные окружения |
| errno | Поиск описаний ошибок по номеру errno |
| fastfetch | Быстрый вывод информации о системе (neofetch-наследник) |
| foreman | Классический менеджер Procfile |
| free | RAM и swap статистика |
| fuser | Процессы, использующие файл/сокет |
| getent | Запрос NSS-баз |
| glances | Мониторинг в реальном времени на Python (CLI) |
| groups | Группы пользователя |
| hivemind | Менеджер Procfile (Go) |
| honcho | Менеджер Procfile-приложений (Python) |
| hostctl | Управление файлом /etc/hosts |
| hostname | Имя хоста |
| htop | Интерактивный просмотр процессов (улучшенный top) |
| hwinfo | Детальная информация об оборудовании |
| id | Текущий пользователь и права |
| ifdata | Получение информации о сетевом интерфейсе |
| insmod | Модули ядра |
| inxi | Сводная информация о системе и железе |
| iostat | RAM, swap, CPU, I/O статистика |
| ipcs | Информация о System V IPC |
| journalctl | Чтение системных логов (фильтры по unit, время, приоритет) |
| kill | Отправка сигналов процессам |
| killall | Отправка сигналов процессам по имени |
| logger | Запись сообщений в syslog из скриптов |
| loginctl | Управление user sessions и logind |
| logrotate | Ротация, сжатие и отправка логов |
| lscpu | Сведения о процессоре |
| lshw | Полная информация об оборудовании |
| lsmod | Модули ядра |
| lspci | Список PCI-устройств |
| lstopo | Топология железа (hwloc) |
| lsusb | Список USB-устройств |
| mispipe | Связывает две команды с проверкой ошибок |
| modprobe | Модули ядра |
| mpstat | RAM, swap, CPU, I/O статистика |
| neofetch | Отображение информации о системе с ASCII-артом |
| nice | Приоритеты процессов |
| nmon | Монитор производительности (IBM) |
| nodemon | Автоперезапуск Node-процессов при изменениях |
| nohup | Запуск в фоне, независимый от терминала |
| nproc | Число доступных процессорных ядер |
| ntp | Классический демон NTP |
| numactl | Управление политиками NUMA |
| overmind | Менеджер Procfile на tmux |
| pgrep | Поиск процессов по имени/регулярке |
| pidstat | Статистика процессов (sysstat) |
| pkill | Убийство процессов по имени/регулярке |
| pm2 | Менеджер процессов Node.js с кластеризацией |
| pmap | Карта памяти процесса |
| powertop | Анализ энергопотребления (Intel) |
| printenv | Переменные окружения |
| process-compose | Оркестрация процессов с зависимостями и TUI |
| ps | Снимок процессов (aux, -eo pid,ppid,cmd) |
| renice | Приоритеты процессов |
| rmmod | Модули ядра |
| rsyslogd | Высокопроизводительный syslog-сервер |
| runit | Простой init и супервизор (runsvdir) |
| s-tui | TUI стресс-тест и мониторинг CPU/температур |
| s6 | Иерархия супервизоров процессов (s6-svscan) |
| sar | Сбор и отчёт по активности системы (sysstat) |
| sensors | Температуры и напряжения (lm-sensors) |
| seq | Генерация последовательностей чисел |
| slabtop | Статистика kernel slab-кэшей |
| sleep | Пауза в скриптах |
| supervisord | Управление демонами и процессами (supervisorctl) |
| sysctl | Runtime-параметры ядра (vm.swappiness, net.core.*) |
| syslog-ng | Сбор и маршрутизация логов |
| systemctl | Управление systemd-сервисами (start/stop/status/enable) |
| systemd-analyze | Анализ загрузки, зависимостей и времени запуска systemd |
| taskset | Привязка процессов к ядрам CPU |
| time | Замер времени выполнения команды (GNU time) |
| timeout | Принудительное ограничение времени выполнения |
| top | Классический просмотр процессов |
| tsx | Прямой запуск TypeScript для Node (esbuild) |
| uname | Информация о ядре |
| units | Конвертация физических единиц |
| uptime | Аптайм |
| vmstat | RAM, swap, CPU, I/O статистика |
| wall | Сообщение всем пользователям системы |
| watch | Периодический запуск команды с выводом |
| whereis | Поиск бинарников, исходников и man-страниц |
| which | Поиск исполняемого файла в PATH |
| whoami | Текущий пользователь |

## 30. Системы контроля версий

| Инструмент | Описание |
|-----------|----------|
| bb | Алиас bitbucket |
| bfg | Быстрая очистка репозитория от секретов и мусора |
| bitbucket | Bitbucket CLI (bb) |
| bzr | Распределённая VCS от Canonical (Bazaar) |
| cargo-release | Релизы Rust crate'ов |
| changesets | Монорепо versioning (JavaScript) |
| chezmoi | Управление dotfiles |
| cocogitto | Conventional Commits и автоматические релизы |
| commitlint | Линтинг commit-сообщений |
| cvs | Concurrent Versions System (legacy) |
| darcs | Patch-oriented VCS (Haskell) |
| delta | Улучшенный просмотр диффов с синтаксической подсветкой и выравниванием |
| diff-so-fancy | Улучшенное оформление diff |
| difftastic | Структурный diff, понимающий синтаксис |
| fork | GUI-клиент для Git (headless-режим) |
| fossil | VCS + bug tracker + wiki |
| gh | GitHub CLI (issues, PR, codespaces, copilot) |
| ghq | Управление локальными копиями удалённых репозиториев |
| git | Основная распределённая VCS |
| git-absorb | Автоматические fixup-коммиты |
| git-appraise | Code review, встроенный в Git (Google) |
| git-bug | Распределённый баг-трекер в Git |
| git-chglog | Генерация CHANGELOG из коммитов |
| git-cliff | Генерация CHANGELOG из коммитов |
| git-crypt | Шифрование секретов в Git |
| git-cvs | Интеграция с CVS |
| git-delta | Подсветка и постраничный просмотр git diff |
| git-extras | 60+ полезных Git-команд (git-ignore, git-changelog) |
| git-fast-import | Импорт в Git |
| git-filter-repo | Мощная перезапись истории Git |
| git-flow | Расширение ветвления по модели git-flow |
| git-lfs | Large File Storage для Git |
| git-machete | Управление стеками веток (stacked PR) |
| git-open | Открытие GitHub/GitLab repository в браузере |
| git-revise | Переписывание коммитов без переключения веток |
| git-secret | Шифрование секретов в Git |
| git-sim | Визуализация Git-операций |
| git-standup | Отчёт по недавней активности разработчика |
| git-submodule | Управление вложенными репозиториями |
| git-subrepo | Управление вложенными репозиториями |
| git-subtree | Управление вложенными репозиториями |
| git-svn | Интеграция с SVN |
| git-town | Высокоуровневое управление Git-ветками и release workflow |
| gitea | Gitea CLI (tea) |
| gitkraken | GUI-клиент (headless скриптинг) |
| gitui | TUI для Git (Rust) |
| glab | GitLab CLI |
| goreleaser | Релизы Go-приложений |
| hg | Алиас mercurial |
| homeshick | Управление dotfiles |
| hub | Предшественник gh (устаревает) |
| husky | Git hooks для Node.js проектов |
| jj | Jujutsu — Git-совместимая VCS нового поколения |
| lazygit | TUI для Git (Go, удобный) |
| lefthook | Быстрые git-хуки для любого стека (Go) |
| lerna | Монорепо менеджмент |
| lint-staged | Линтинг только изменённых файлов (Node.js) |
| mani | Управление несколькими Git-репозиториями |
| mercurial | Распределённая VCS (Facebook, Mozilla) (hg) |
| nx | Монорепо менеджмент |
| pijul | Математически обоснованная VCS |
| pre-commit | Git hooks framework (CLI) |
| radicle | Децентрализованная P2P-коллаборация поверх git |
| release-it | Интерактивный релизный инструмент |
| repo | Google-инструмент для управления множеством Git-репо |
| semantic-release | Автоматическая семантическая версионность |
| sl | Sapling — масштабируемая VCS от Meta (клиент sl) |
| sourcetree | GUI-клиент (headless скриптинг) |
| standard-version | Альтернатива semantic-release |
| stow | Управление dotfiles |
| svn | Apache Subversion |
| tea | Алиас gitea |
| tig | Интерактивный TUI для Git |
| transcrypt | Прозрачное шифрование файлов в Git |
| turborepo | Монорепо менеджмент |
| vcsh | VCS для $HOME (dotfiles) |
| yadm | Управление dotfiles |

## 31. Текстовые редакторы (CLI)

| Инструмент | Описание |
|-----------|----------|
| ed | Прародитель всех редакторов (POSIX) |
| emacs | Редактор/среда с server-mode (emacsclient) |
| helix | Модальный редактор с LSP и tree-sitter из коробки |
| kakoune | Редактор с моделью selection-first |
| micro | Понятный модульный редактор с хоткеями GUI |
| nano | Простой редактор по умолчанию |
| neovim | Модернизированный Vim с Lua и LSP |
| vim | Классический модальный редактор |

## 32. Терминальные мультиплексоры и управление сеансами

| Инструмент | Описание |
|-----------|----------|
| abduco | Альтернатива dtach + dvtm |
| Alacritty | GPU-accelerated терминалы (если нужны эмуляторы) |
| byobu | Фронтенд к screen/tmux с горячими клавишами |
| dtach | Лёгкая отсоединяемая сессия без окон |
| Rio | GPU-accelerated терминалы (если нужны эмуляторы) |
| screen | Классический мультиплексор |
| tmux | Современный мультиплексор (панели, окна, сессии) |
| wezterm | GPU-терминал с мультиплексором и SSH-клиентом |
| zellij | Мультиплексор на Rust с layout-файлами |

## 33. Управление пользователями, правами и ACL

| Инструмент | Описание |
|-----------|----------|
| chage | Пароли и сроки действия |
| chgrp | Права доступа к файлам |
| chmod | Права доступа к файлам |
| chown | Права доступа к файлам |
| getcap | Просмотр file capabilities |
| getfacl | POSIX Access Control Lists |
| getfattr | Расширенные атрибуты файлов |
| groupadd | Управление группами |
| groupdel | Управление группами |
| groupmod | Управление группами |
| last | История входов |
| lastlog | История входов |
| namei | Разбор пути и разрешений по компонентам |
| passwd | Пароли и сроки действия |
| setcap | Linux file capabilities |
| setfacl | POSIX Access Control Lists |
| setfattr | Расширенные атрибуты файлов |
| su | Смена пользователя |
| sudo | Выполнение от имени root |
| useradd | Управление пользователями |
| userdel | Управление пользователями |
| usermod | Управление пользователями |
| visudo | Безопасное редактирование sudoers |
| w | Активные пользователи |
| who | Активные пользователи |

## 34. Управление удалёнными машинами

| Инструмент | Описание |
|-----------|----------|
| chisel | TCP/UDP туннели over HTTP |
| cloudflared | Туннели Cloudflare (zero-trust) |
| clusterssh | Одновременный SSH на кластер |
| cssh | Одновременный SSH на кластер (clusterssh) |
| eternal-terminal | SSH-сессии, устойчивые к разрывам сети (et) |
| frp | Быстрый реверс-прокси туннель (frpc/frps) |
| frpc | Быстрый реверс-прокси туннель |
| frps | Быстрый реверс-прокси туннель |
| ngrok | Публичные туннели к localhost |
| parallel-ssh | Параллельный SSH на множество хостов |
| pdsh | Parallel distributed shell |
| pssh | Параллельный SSH на множество хостов |
| sshx | Коллаборативный терминал в браузере |
| teleport | Zero-trust доступ к SSH/K8s/БД с аудитом |
| tmate | Мгновенный shared terminal over SSH |
| upterm | Мгновенное шаринг-подключение к терминальной сессии |

## 35. Форензика и восстановление данных

| Инструмент | Описание |
|-----------|----------|
| binwalk | Анализ и извлечение встроенных образов прошивок |
| bulk_extractor | Массовое извлечение артефактов из образов |
| foremost | Карвинг файлов по заголовкам |
| photorec | Восстановление файлов по сигнатурам (спутник testdisk) |
| plaso | Супертаёмлайн из артефактов системы (log2timeline) |
| scalpel | Быстрый файловый карвер |
| sleuthkit | Форензика файловых систем (fls, icat, mmls) |
| testdisk | Восстановление разделов и загрузочных записей |
| volatility3 | Форензика дампов оперативной памяти |

## 36. Электронная почта (CLI)

| Инструмент | Описание |
|-----------|----------|
| aerc | Эффективный почтовый TUI для разработчиков |
| fetchmail | Забор почты по POP3/IMAP |
| himalaya | Email-клиент на основе CLI (Rust) |
| mailx | Отправка почты из скриптов (s-nail) |
| mbsync | Двусторонняя синхронизация IMAP (isync) |
| msmtp | Лёгкий SMTP-клиент для отправки |
| mutt | Классический почтовый клиент |
| neomutt | Активно развиваемый форк mutt |
| notmuch | Молниеносный индекс и поиск почты |
| offlineimap | Синхронизация IMAP в локальный maildir |
| sendmail | Классический интерфейс отправки почты |
| swaks | Швейцарский нож для тестирования SMTP |

---

## Приложение А. Исключённые записи (антигаллюцинационная фильтрация)

| Имя | Причина исключения |
|-----|--------------------|
| asynciter | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| colorconsistency | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| detectron2 | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ethicsml | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| fairs | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| farrow | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| fasterxml-jackson | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| fastzero | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| feedstock | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| formatters | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| fusioncharts | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| garin | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gasper | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geolite2 | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geoni | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geoq | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geospatial-data | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geotiles | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geoyaml | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geramod | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| getnows | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| getpath | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| getprotobyname | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| getters | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| geverify | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gf2 | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gflags | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ggrapt | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghas | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghcn | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghissues | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghmac | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghmail | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghoracle | помечено источником как сомнительное «(?)» |
| ghpage | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghsearch | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghubeapi | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghweb | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ghz | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giantpandas | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gibber | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gigabytes | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gigantor | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gigging | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gigpipe | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gigsearch | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gigwise | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilded | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilian | помечено источником как сомнительное «(?)» |
| gillan | помечено источником как сомнительное «(?)» |
| gilled | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillets | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilley | помечено источником как сомнительное «(?)» |
| gillice | помечено источником как сомнительное «(?)» |
| gillie | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillied | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillies | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilligan | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillion | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillnets | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillray | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gills | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillsy | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilly | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillyfell | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillygander | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillyglow | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillygod | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillying | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillyman | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gillyweed | помечено источником как сомнительное «(?)» |
| gillywork | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilmazine | помечено источником как сомнительное «(?)» |
| gilneys | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilour | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilpy | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilruth | помечено источником как сомнительное «(?)» |
| gilson | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilt | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltage | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltcup | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilte | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilted | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilten | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltenesse | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilter | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilthood | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilthorse | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilticide | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltier | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltiest | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltily | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltiness | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilting | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltings | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltish | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltist | помечено источником как сомнительное «(?)» |
| giltite | помечено источником как сомнительное «(?)» |
| giltless | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltlike | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltly | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltman | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltness | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gilts | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltseed | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltsman | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltspar | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltspot | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltstrip | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| giltwork | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| glvq | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gopkg | помечено источником как сомнительное «(?)» |
| gpt-neox | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grappelli | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grasper | помечено источником как сомнительное «(?)» |
| grassroots | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| gratipay | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grawal | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| graya | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayed | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayed-out | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayer | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayest | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayish | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| graylag | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayling | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| graymail | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayness | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grays | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| grayware | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| hashlib-extended | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| immutatypes | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ipgetter | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| juptyer | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| kodi | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| labelmg | помечено источником как сомнительное «(?)» |
| latex2unicode | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| lazydocker | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| lazyframes | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| lddtree | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ldml | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| leader-follower | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| league-of-legends-api | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| learned-embedding | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| learning-curve | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| learnpython | помечено источником как сомнительное «(?)» |
| least-squares | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| lebenshtein | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| led-display | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ledc | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| ledpy | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| leem | помечено источником как сомнительное «(?)» |
| leers | помечено источником как сомнительное «(?)» |
| leftwm | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| legal-csv-parser | помечено источником как сомнительное «(?)» |
| legality | помечено источником как сомнительное «(?)» |
| legalized | помечено источником как сомнительное «(?)» |
| legapython | помечено источником как сомнительное «(?)» |
| legato | помечено источником как сомнительное «(?)» |
| legehosen | помечено источником как сомнительное «(?)» |
| legend | помечено источником как сомнительное «(?)» |
| legends | помечено источником как сомнительное «(?)» |
| legged | помечено источником как сомнительное «(?)» |
| leggier | помечено источником как сомнительное «(?)» |
| leggiest | помечено источником как сомнительное «(?)» |
| leggin | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| legging | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| leggings | помечено источником как сомнительное «(?)» |
| leggins | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| leggy | помечено источником как сомнительное «(?)» |
| libpq | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| libreoffice-python | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| licensed | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| licensee | помечено источником как сомнительное «(?)» |
| licenseheader | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| licenseplate | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| licenseurl | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| licenseware | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| licenseware-client | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| lichat | помечено источником как сомнительное «(?)» |
| lichee | помечено источником как сомнительное «(?)» |
| lichen | помечено источником как сомнительное «(?)» |
| lichenca | помечено источником как сомнительное «(?)» |
| lichgate | помечено источником как сомнительное «(?)» |
| lichtenstein | помечено источником как сомнительное «(?)» |
| lichthouse | помечено источником как сомнительное «(?)» |
| lichtwellenleiter | помечено источником как сомнительное «(?)» |
| llm-eval | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| lmsys | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| Python-библиотеки | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| transformers-cli | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| Автоматизация интерактивных программ | не найден в PyPI (единственное вхождение, признак галлюцинации) |
| Обработка LLM и RAG | не найден в PyPI (единственное вхождение, признак галлюцинации) |

## Приложение Б. Склеенные алиасы (устранение дублей)

| Вариант из дополнений | Присоединён к |
|----------------------|---------------|
| claude-code | claude |
| cline-cli | cline |
| codex-cli | codex |
| gemini-cli | gemini |
| github-copilot-cli | copilot |
| kimi-cli | kimi |
| qwen-code | qwen |
| warp-ai | warp |

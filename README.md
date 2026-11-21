# GitLab MCP Server

Подключите ваш AI-ассистент к GitLab. Задавайте вопросы прямо в чате: _"Покажи открытые merge request'ы"_, _"Покажи ревью для MR #123"_, _"Найди merge request'ы для ветки feature/auth"_.

## 🚀 Быстрая установка

### Требования

Проект использует [uv](https://github.com/astral-sh/uv) для управления Python-пакетами.

**Установка uv:**

```bash
# macOS и Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Или через pip
pip install uv
```

### Установка

1. **Установите сервер:**

   ```bash
   git clone https://github.com/QuestGuideRF/gitlab-mcp-server.git
   cd gitlab-mcp-server
   uv venv
   source .venv/bin/activate  # На Windows: .venv\Scripts\activate
   uv pip install -e .
   chmod +x run-mcp.sh
   ```

2. **Получите токен GitLab:**

   - Перейдите в GitLab → Settings → Access Tokens
   - Создайте токен с правами **`read_api`**
   - Скопируйте токен

3. **Настройте проект:**

   Создайте файл `gitlab-mcp.env` в директории вашего проекта:

   ```env
   GITLAB_PROJECT_ID=12345
   GITLAB_ACCESS_TOKEN=replace_with_your_gitlab_access_token
   GITLAB_URL=https://gitlab.com
   ```

4. **Подключите к Cursor:**

   Создайте `.cursor/mcp.json` в вашем проекте:

   ```json
   {
     "mcpServers": {
       "gitlab-mcp": {
         "command": "/путь/к/gitlab-mcp-server/run-mcp.sh",
         "cwd": "/путь/к/вашему-проекту"
       }
     }
   }
   ```

5. **Перезапустите Cursor** и начните задавать вопросы о GitLab!

## 💬 Что можно делать

После подключения попробуйте эти команды в чате:

- _"Покажи открытые merge request'ы"_
- _"Покажи детали merge request #456"_
- _"Покажи ревью и обсуждения для MR #123"_
- _"Покажи сводку тестов для MR #456"_
- _"Какие тесты упали в merge request #789?"_
- _"Покажи pipeline для MR #456"_
- _"Покажи логи упавшего job для merge request #789"_
- _"Покажи обсуждения коммитов для MR #456"_
- _"Найди merge request'ы для ветки feature/auth-improvements"_
- _"Ответь на обсуждение abc123 в MR #456: 'Спасибо за фидбек!'"_

## 📋 Основные возможности

### Merge Request'ы

- Просмотр списка MR с фильтрацией по статусу и ветке
- Детальная информация о конкретном MR
- Поиск MR по имени ветки

### Ревью и обсуждения

- Просмотр всех ревью и обсуждений в MR
- Ответы на существующие обсуждения
- Создание новых комментариев
- Разрешение обсуждений

### Тесты и Pipeline

- **Сводка тестов** — быстрый обзор результатов (количество пройденных/упавших тестов)
- **Детальный отчет** — полная информация о тестах с ошибками и стектрейсами
- **Pipeline** — обзор всех job'ов и их статусов
- **Логи job'ов** — просмотр вывода конкретного job'а

### Коммиты

- Просмотр всех обсуждений на коммитах в MR
- История комментариев по каждому коммиту

## ⚙️ Конфигурация

### Настройка проекта (рекомендуется)

Каждый проект имеет свой файл `gitlab-mcp.env` с настройками GitLab. Не добавляйте токены в систему контроля версий.

### Глобальная настройка

Можно задать переменные окружения глобально:

```bash
export GITLAB_PROJECT_ID=12345
export GITLAB_ACCESS_TOKEN=replace_with_your_gitlab_access_token
export GITLAB_URL=https://gitlab.com
```

### Как найти Project ID

- Перейдите в GitLab проект → Settings → General → Project ID
- Или посмотрите в URL: `https://gitlab.com/username/project` (используйте числовой ID)

## 🔧 Решение проблем

**Ошибка аутентификации**: Проверьте, что токен имеет права `read_api` и не истёк.

**Проект не найден**: Убедитесь, что Project ID указан правильно (это число, а не название проекта).

**Проблемы с подключением**: Проверьте, что URL GitLab доступен и указан верно.

**Скрипт не найден**: Убедитесь, что путь в конфигурации MCP указывает на правильное расположение сервера и скрипт исполняемый.

## 📚 Справочник инструментов

| Инструмент                          | Описание                          | Параметры                                    |
| ----------------------------------- | --------------------------------- | -------------------------------------------- |
| `list_merge_requests`               | Список merge request'ов          | `state`, `target_branch`, `limit`            |
| `get_merge_request_details`         | Детали MR                         | `merge_request_iid`                          |
| `get_pipeline_test_summary`         | Сводка тестов (быстрый обзор)     | `merge_request_iid`                          |
| `get_merge_request_test_report`     | Детальный отчет о тестах          | `merge_request_iid`                          |
| `get_merge_request_pipeline`        | Pipeline со всеми job'ами         | `merge_request_iid`                          |
| `get_job_log`                       | Логи конкретного job'а            | `job_id`                                     |
| `get_merge_request_reviews`         | Ревью и обсуждения                | `merge_request_iid`                          |
| `get_commit_discussions`            | Обсуждения на коммитах            | `merge_request_iid`                          |
| `get_branch_merge_requests`         | Поиск MR по ветке                 | `branch_name`                                |
| `reply_to_review_comment`           | Ответ на обсуждение               | `merge_request_iid`, `discussion_id`, `body` |

---

Автор: legenda  
Telegram: [@LEGENDA_SD](https://t.me/LEGENDA_SD)

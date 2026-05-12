"""
JSON-схемы для всех 55 инструментов из Приложения А (v1).

Расширенная структура (vs v1):
{
    "label_kk": "...", "label_ru": "...",   ← человекочитаемое имя инструмента
    "description_kk": "...", "description_ru": "...",
    "domain": ["banking", ...],
    "input": [
        {
            "key": "sender_iin",
            "type": "iin",
            "required": True,
            "label_kk": "Жіберуші ИИН",
            "label_ru": "ИИН отправителя",
            "placeholder": "981020300123",
            "hint_ru": "12 цифр + контрольная сумма",
            "hint_kk": "12 сан + бақылау сомасы",
        },
        ...
    ],
    "output": [
        {
            "key": "balance_kzt",
            "type": "amount_kzt",
            "label_kk": "Баланс (теңге)",
            "label_ru": "Баланс (тенге)",
            ...
        },
    ],
}

Поля в output все рассматриваются как обязательные для mock_result —
аннотатор должен заполнить весь шаблон ответа сервера.

Типы (теперь с подсказкой, какой HTML-инпут использовать):
    "string"      → <input type="text">
    "iin"         → <input type="text" pattern="\\d{12}">
    "bin"         → <input type="text" pattern="\\d{12}">
    "phone_kz"    → <input type="text" pattern="\\+7\\d{10}">
    "amount_kzt"  → <input type="number" min="0" step="1">
    "date"        → <input type="date">
    "datetime"    → <input type="text">
    "integer"     → <input type="number" step="1">
    "boolean"     → <select>true/false</select>
    "url"         → <input type="url">
    "email"       → <input type="email">
    "object"      → <textarea> (свободный JSON)
    "array"       → <textarea> (свободный JSON)
    {"enum": ["a","b","c"]} → <select>
"""

import re

# ─────────────────────────────────────────────────────────────────────────────
# Схемы по инструментам
# ─────────────────────────────────────────────────────────────────────────────

TOOL_SCHEMAS = {

    # ==============================  БАНКИНГ  ===============================
    "kaspi.balance": {
        "label_ru": "Kaspi: проверить баланс",
        "label_kk": "Kaspi: балансты тексеру",
        "description_ru": "Запрашивает баланс счёта клиента по ИИН.",
        "description_kk": "Клиенттің ИИН-і бойынша шот балансын сұрайды.",
        "domain": ["banking"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН клиента", "label_kk": "Клиенттің ИИН-і",
             "placeholder": "981020300123"},
            {"key": "account_type", "type": {"enum": ["main", "deposit", "credit"]}, "required": False,
             "label_ru": "Тип счёта", "label_kk": "Шот түрі"},
        ],
        "output": [
            {"key": "balance_kzt", "type": "amount_kzt",
             "label_ru": "Баланс (тенге)", "label_kk": "Баланс (теңге)"},
            {"key": "currency", "type": "string",
             "label_ru": "Валюта", "label_kk": "Валюта", "placeholder": "KZT"},
            {"key": "as_of", "type": "datetime",
             "label_ru": "На момент времени", "label_kk": "Дерек алынған уақыт"},
        ],
    },
    "kaspi.transfer": {
        "label_ru": "Kaspi: перевод",
        "label_kk": "Kaspi: аударым",
        "description_ru": "Перевод денег с одного счёта на другой по ИИН.",
        "description_kk": "ИИН бойынша бір шоттан екіншісіне ақша аудару.",
        "domain": ["banking"],
        "input": [
            {"key": "sender_iin", "type": "iin", "required": True,
             "label_ru": "ИИН отправителя", "label_kk": "Жіберуші ИИН"},
            {"key": "recipient_iin", "type": "iin", "required": True,
             "label_ru": "ИИН получателя", "label_kk": "Алушы ИИН"},
            {"key": "amount_kzt", "type": "amount_kzt", "required": True,
             "label_ru": "Сумма (тенге)", "label_kk": "Сома (теңге)"},
            {"key": "comment", "type": "string", "required": False,
             "label_ru": "Комментарий к переводу", "label_kk": "Аударым түсіндірмесі"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["ok", "rejected", "pending"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "transaction_id", "type": "string",
             "label_ru": "ID транзакции", "label_kk": "Транзакция ID"},
            {"key": "fee_kzt", "type": "amount_kzt",
             "label_ru": "Комиссия (тенге)", "label_kk": "Комиссия (теңге)"},
        ],
    },
    "kaspi.pay": {
        "label_ru": "Kaspi: оплата услуги",
        "label_kk": "Kaspi: қызмет ақысын төлеу",
        "description_ru": "Оплата услуги мерчанта (ЖКХ, связь, штрафы и т.п.).",
        "description_kk": "Мерчант қызметін төлеу (КОЖ, байланыс, айыппұлдар т.б.).",
        "domain": ["banking"],
        "input": [
            {"key": "payer_iin", "type": "iin", "required": True,
             "label_ru": "ИИН плательщика", "label_kk": "Төлеуші ИИН"},
            {"key": "merchant_id", "type": "string", "required": True,
             "label_ru": "ID мерчанта", "label_kk": "Мерчант ID"},
            {"key": "amount_kzt", "type": "amount_kzt", "required": True,
             "label_ru": "Сумма (тенге)", "label_kk": "Сома (теңге)"},
            {"key": "service_code", "type": "string", "required": False,
             "label_ru": "Код услуги", "label_kk": "Қызмет коды"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["ok", "rejected"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "receipt_number", "type": "string",
             "label_ru": "Номер чека", "label_kk": "Чек нөмірі"},
        ],
    },
    "kaspi.dispute": {
        "label_ru": "Kaspi: оспорить транзакцию",
        "label_kk": "Kaspi: транзакцияға шағым",
        "description_ru": "Открыть спор по существующей транзакции.",
        "description_kk": "Бар транзакция бойынша дау ашу.",
        "domain": ["banking"],
        "input": [
            {"key": "transaction_id", "type": "string", "required": True,
             "label_ru": "ID транзакции", "label_kk": "Транзакция ID"},
            {"key": "claimant_iin", "type": "iin", "required": True,
             "label_ru": "ИИН заявителя", "label_kk": "Шағым берушінің ИИН-і"},
            {"key": "reason", "type": {"enum": ["unauthorized", "duplicate", "wrong_amount", "service_not_received"]},
             "required": True,
             "label_ru": "Причина спора", "label_kk": "Шағым себебі"},
            {"key": "description", "type": "string", "required": False,
             "label_ru": "Описание", "label_kk": "Сипаттама"},
        ],
        "output": [
            {"key": "case_id", "type": "string",
             "label_ru": "Номер дела", "label_kk": "Іс нөмірі"},
            {"key": "expected_resolution_date", "type": "date",
             "label_ru": "Ожидаемая дата решения", "label_kk": "Болжамды шешім күні"},
        ],
    },
    "halyk.balance": {
        "label_ru": "Halyk Bank: баланс",
        "label_kk": "Halyk Bank: баланс",
        "description_ru": "Запрашивает баланс счёта Halyk по ИИН.",
        "description_kk": "Halyk шотының балансын ИИН бойынша сұрайды.",
        "domain": ["banking"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "balance_kzt", "type": "amount_kzt",
             "label_ru": "Баланс (тенге)", "label_kk": "Баланс (теңге)"},
            {"key": "currency", "type": "string",
             "label_ru": "Валюта", "label_kk": "Валюта"},
        ],
    },
    "halyk.transfer": {
        "label_ru": "Halyk Bank: перевод",
        "label_kk": "Halyk Bank: аударым",
        "description_ru": "Перевод денег между клиентами Halyk.",
        "description_kk": "Halyk клиенттері арасында ақша аудару.",
        "domain": ["banking"],
        "input": [
            {"key": "sender_iin", "type": "iin", "required": True,
             "label_ru": "ИИН отправителя", "label_kk": "Жіберуші ИИН"},
            {"key": "recipient_iin", "type": "iin", "required": True,
             "label_ru": "ИИН получателя", "label_kk": "Алушы ИИН"},
            {"key": "amount_kzt", "type": "amount_kzt", "required": True,
             "label_ru": "Сумма (тенге)", "label_kk": "Сома (теңге)"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["ok", "rejected"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "transaction_id", "type": "string",
             "label_ru": "ID транзакции", "label_kk": "Транзакция ID"},
        ],
    },
    "halyk.card_block": {
        "label_ru": "Halyk Bank: блокировка карты",
        "label_kk": "Halyk Bank: картаны бұғаттау",
        "description_ru": "Блокирует карту Halyk при утере/краже/компрометации.",
        "description_kk": "Жоғалу/ұрлық/бұзу жағдайында Halyk картасын бұғаттайды.",
        "domain": ["banking"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН владельца", "label_kk": "Иесінің ИИН-і"},
            {"key": "card_last4", "type": "string", "required": True,
             "label_ru": "Последние 4 цифры карты", "label_kk": "Картаның соңғы 4 саны",
             "placeholder": "1234"},
            {"key": "reason", "type": {"enum": ["lost", "stolen", "compromised"]}, "required": True,
             "label_ru": "Причина", "label_kk": "Себебі"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["blocked", "failed"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "blocked_at", "type": "datetime",
             "label_ru": "Заблокирована в", "label_kk": "Бұғатталды"},
        ],
    },
    "forte.balance": {
        "label_ru": "ForteBank: баланс",
        "label_kk": "ForteBank: баланс",
        "description_ru": "Баланс счёта ForteBank по ИИН.",
        "description_kk": "ИИН бойынша ForteBank шот балансы.",
        "domain": ["banking"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "balance_kzt", "type": "amount_kzt",
             "label_ru": "Баланс (тенге)", "label_kk": "Баланс (теңге)"},
        ],
    },
    "jusan.balance": {
        "label_ru": "Jusan Bank: баланс",
        "label_kk": "Jusan Bank: баланс",
        "description_ru": "Баланс счёта Jusan Bank по ИИН.",
        "description_kk": "ИИН бойынша Jusan Bank шот балансы.",
        "domain": ["banking"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "balance_kzt", "type": "amount_kzt",
             "label_ru": "Баланс (тенге)", "label_kk": "Баланс (теңге)"},
        ],
    },

    # ==============================  EGOV.KZ  ==============================
    "egov.login": {
        "label_ru": "egov.kz: вход на портал",
        "label_kk": "egov.kz: порталға кіру",
        "description_ru": "Авторизация на портале egov.kz по ИИН и методу аутентификации.",
        "description_kk": "egov.kz порталында ИИН және аутентификация әдісі арқылы кіру.",
        "domain": ["egov"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
            {"key": "auth_method", "type": {"enum": ["sms", "ekey", "qr", "biometric"]}, "required": True,
             "label_ru": "Метод аутентификации", "label_kk": "Аутентификация әдісі"},
        ],
        "output": [
            {"key": "session_token", "type": "string",
             "label_ru": "Токен сессии", "label_kk": "Сессия токені"},
            {"key": "expires_at", "type": "datetime",
             "label_ru": "Действителен до", "label_kk": "Жарамдылық мерзімі"},
        ],
    },
    "egov.service_request": {
        "label_ru": "egov.kz: заказать услугу",
        "label_kk": "egov.kz: қызметке тапсырыс",
        "description_ru": "Подаёт заявление на госуслугу через egov.kz.",
        "description_kk": "egov.kz арқылы мемлекеттік қызметке өтініш береді.",
        "domain": ["egov"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
            {"key": "service_code", "type": "string", "required": True,
             "label_ru": "Код услуги", "label_kk": "Қызмет коды"},
            {"key": "params", "type": "object", "required": False,
             "label_ru": "Параметры запроса (JSON)", "label_kk": "Сұрау параметрлері (JSON)"},
        ],
        "output": [
            {"key": "request_id", "type": "string",
             "label_ru": "ID заявки", "label_kk": "Өтініш ID"},
            {"key": "expected_completion", "type": "date",
             "label_ru": "Ожидаемая дата готовности", "label_kk": "Дайын болатын болжамды күн"},
            {"key": "status", "type": {"enum": ["accepted", "rejected"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },
    "egov.status": {
        "label_ru": "egov.kz: статус заявки",
        "label_kk": "egov.kz: өтініш мәртебесі",
        "description_ru": "Проверяет текущий статус заявки на госуслугу.",
        "description_kk": "Мемлекеттік қызметке берілген өтініштің ағымдағы мәртебесін тексереді.",
        "domain": ["egov"],
        "input": [
            {"key": "request_id", "type": "string", "required": True,
             "label_ru": "ID заявки", "label_kk": "Өтініш ID"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["pending", "in_progress", "completed", "rejected"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "updated_at", "type": "datetime",
             "label_ru": "Обновлено в", "label_kk": "Жаңартылды"},
        ],
    },
    "egov.gbdfl_lookup": {
        "label_ru": "egov.kz: справка из ГБД ФЛ",
        "label_kk": "egov.kz: ЖТ ДДҚ-нан анықтама",
        "description_ru": "Выписка из Государственной базы данных «Физические лица» по ИИН.",
        "description_kk": "ИИН бойынша «Жеке тұлғалар» мемлекеттік деректер қорынан үзінді.",
        "domain": ["egov"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "full_name_kk", "type": "string",
             "label_ru": "ФИО (на казахском)", "label_kk": "Толық аты-жөні (қазақша)"},
            {"key": "birth_date", "type": "date",
             "label_ru": "Дата рождения", "label_kk": "Туған күні"},
            {"key": "citizenship", "type": "string",
             "label_ru": "Гражданство", "label_kk": "Азаматтығы", "placeholder": "KZ"},
        ],
    },
    "egov.verify_iin": {
        "label_ru": "egov.kz: проверить ИИН",
        "label_kk": "egov.kz: ИИН-ді тексеру",
        "description_ru": "Проверяет, существует ли ИИН и валиден ли он.",
        "description_kk": "ИИН-нің бар-жоғын және жарамдылығын тексереді.",
        "domain": ["egov"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "valid", "type": "boolean",
             "label_ru": "Валиден (контр. сумма)", "label_kk": "Жарамды (бақылау сомасы)"},
            {"key": "exists", "type": "boolean",
             "label_ru": "Существует в БД", "label_kk": "Базада бар"},
        ],
    },
    "egov.get_certificate": {
        "label_ru": "egov.kz: получить справку",
        "label_kk": "egov.kz: анықтама алу",
        "description_ru": "Заказывает официальную справку (о рождении, браке, несудимости и т.д.).",
        "description_kk": "Ресми анықтаманы (туу, неке, соттылықтың болмауы т.б.) тапсырыс береді.",
        "domain": ["egov"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
            {"key": "certificate_type", "type": {"enum": ["birth", "marriage", "no_criminal_record", "address", "no_debt", "education"]},
             "required": True,
             "label_ru": "Тип справки", "label_kk": "Анықтама түрі"},
        ],
        "output": [
            {"key": "certificate_id", "type": "string",
             "label_ru": "ID справки", "label_kk": "Анықтама ID"},
            {"key": "issued_at", "type": "datetime",
             "label_ru": "Выдана в", "label_kk": "Берілген уақыт"},
            {"key": "pdf_url", "type": "url",
             "label_ru": "PDF-ссылка", "label_kk": "PDF сілтемесі"},
        ],
    },
    "egov.law_lookup": {
        "label_ru": "egov.kz: поиск закона",
        "label_kk": "egov.kz: заң іздеу",
        "description_ru": "Поиск нормативно-правовых актов по ключевому запросу.",
        "description_kk": "Кілт сұрау бойынша нормативтік құқықтық актілерді іздеу.",
        "domain": ["egov", "legal"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Поисковый запрос", "label_kk": "Іздеу сұрауы"},
            {"key": "law_type", "type": {"enum": ["constitution", "code", "law", "decree"]}, "required": False,
             "label_ru": "Тип акта", "label_kk": "Акт түрі"},
        ],
        "output": [
            {"key": "matches", "type": "array",
             "label_ru": "Найденные акты (массив)", "label_kk": "Табылған актілер (массив)"},
            {"key": "total", "type": "integer",
             "label_ru": "Всего совпадений", "label_kk": "Барлық сәйкестіктер"},
        ],
    },

    # ===============================  КГД  =================================
    "kgd.tax_status": {
        "label_ru": "КГД: налоговая задолженность",
        "label_kk": "ҚГД: салық берешегі",
        "description_ru": "Проверяет текущую налоговую задолженность по ИИН.",
        "description_kk": "ИИН бойынша ағымдағы салық берешегін тексереді.",
        "domain": ["tax"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "debt_kzt", "type": "amount_kzt",
             "label_ru": "Сумма долга (тенге)", "label_kk": "Берешек сомасы (теңге)"},
            {"key": "deadline", "type": "date",
             "label_ru": "Срок погашения", "label_kk": "Өтеу мерзімі"},
            {"key": "has_pending_declaration", "type": "boolean",
             "label_ru": "Есть несданные декларации", "label_kk": "Тапсырылмаған декларация бар"},
        ],
    },
    "kgd.declaration_status": {
        "label_ru": "КГД: статус декларации",
        "label_kk": "ҚГД: декларация мәртебесі",
        "description_ru": "Статус сданной налоговой декларации за указанный год.",
        "description_kk": "Көрсетілген жылғы тапсырылған салық декларациясының мәртебесі.",
        "domain": ["tax"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
            {"key": "year", "type": "integer", "required": True,
             "label_ru": "Год декларации", "label_kk": "Декларация жылы"},
            {"key": "form_code", "type": "string", "required": False,
             "label_ru": "Код формы", "label_kk": "Форма коды"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["submitted", "accepted", "rejected", "not_filed"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "submitted_at", "type": "datetime",
             "label_ru": "Подана в", "label_kk": "Тапсырылған уақыт"},
        ],
    },
    "kgd.deadline": {
        "label_ru": "КГД: срок сдачи декларации",
        "label_kk": "ҚГД: декларация тапсыру мерзімі",
        "description_ru": "Срок сдачи указанной налоговой формы.",
        "description_kk": "Көрсетілген салық формасын тапсыру мерзімі.",
        "domain": ["tax"],
        "input": [
            {"key": "form_code", "type": "string", "required": True,
             "label_ru": "Код формы (например, 240.00)", "label_kk": "Форма коды (мысалы, 240.00)"},
            {"key": "year", "type": "integer", "required": False,
             "label_ru": "Год", "label_kk": "Жыл"},
        ],
        "output": [
            {"key": "deadline", "type": "date",
             "label_ru": "Срок сдачи", "label_kk": "Тапсыру мерзімі"},
            {"key": "days_remaining", "type": "integer",
             "label_ru": "Осталось дней", "label_kk": "Қалған күндер"},
        ],
    },
    "kgd.bin_lookup": {
        "label_ru": "КГД: справка по БИН",
        "label_kk": "ҚГД: БИН бойынша анықтама",
        "description_ru": "Информация об организации по бизнес-идентификационному номеру.",
        "description_kk": "Бизнес-сәйкестендіру нөмірі бойынша ұйым туралы ақпарат.",
        "domain": ["tax"],
        "input": [
            {"key": "bin", "type": "bin", "required": True,
             "label_ru": "БИН организации", "label_kk": "Ұйымның БИН-і"},
        ],
        "output": [
            {"key": "company_name_kk", "type": "string",
             "label_ru": "Название компании (каз.)", "label_kk": "Компания атауы (қазақша)"},
            {"key": "registered_at", "type": "date",
             "label_ru": "Дата регистрации", "label_kk": "Тіркелген күн"},
            {"key": "is_active", "type": "boolean",
             "label_ru": "Активна", "label_kk": "Қызмет істейді"},
        ],
    },

    # ===============================  ФСМС  ================================
    "fsms.status": {
        "label_ru": "ФСМС: статус застрахованности",
        "label_kk": "ӘМСҚ: сақтандырылу мәртебесі",
        "description_ru": "Проверяет статус обязательного медицинского страхования по ИИН.",
        "description_kk": "ИИН бойынша міндетті медициналық сақтандыру мәртебесін тексереді.",
        "domain": ["fsms", "health"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
        ],
        "output": [
            {"key": "insured", "type": "boolean",
             "label_ru": "Застрахован", "label_kk": "Сақтандырылған"},
            {"key": "category", "type": "string",
             "label_ru": "Категория", "label_kk": "Санаты", "placeholder": "employed"},
            {"key": "valid_until", "type": "date",
             "label_ru": "Действительно до", "label_kk": "Жарамдылық мерзімі"},
        ],
    },
    "fsms.claim_submit": {
        "label_ru": "ФСМС: подать жалобу/претензию",
        "label_kk": "ӘМСҚ: шағым/талап беру",
        "description_ru": "Подаёт жалобу в Фонд социального медицинского страхования.",
        "description_kk": "Әлеуметтік медициналық сақтандыру қорына шағым береді.",
        "domain": ["fsms", "health"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН заявителя", "label_kk": "Шағым берушінің ИИН-і"},
            {"key": "claim_type", "type": {"enum": ["medical_bill", "missing_payment", "wrong_category"]},
             "required": True,
             "label_ru": "Тип жалобы", "label_kk": "Шағым түрі"},
            {"key": "description", "type": "string", "required": False,
             "label_ru": "Описание", "label_kk": "Сипаттама"},
            {"key": "documents", "type": "array", "required": False,
             "label_ru": "Документы (массив URL)", "label_kk": "Құжаттар (URL массиві)"},
        ],
        "output": [
            {"key": "claim_id", "type": "string",
             "label_ru": "Номер жалобы", "label_kk": "Шағым нөмірі"},
            {"key": "expected_response_date", "type": "date",
             "label_ru": "Ожидаемая дата ответа", "label_kk": "Болжамды жауап күні"},
        ],
    },

    # ===============================  ТРУД  ================================
    "enbek.search_job": {
        "label_ru": "Enbek: поиск вакансий",
        "label_kk": "Enbek: бос жұмыс орындарын іздеу",
        "description_ru": "Поиск открытых вакансий на портале enbek.kz.",
        "description_kk": "enbek.kz порталынан ашық бос жұмыс орындарын іздеу.",
        "domain": ["enbek"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Поисковый запрос", "label_kk": "Іздеу сұрауы"},
            {"key": "region", "type": "string", "required": False,
             "label_ru": "Регион", "label_kk": "Аймақ", "placeholder": "Алматы"},
            {"key": "salary_min_kzt", "type": "amount_kzt", "required": False,
             "label_ru": "Минимальная зарплата (тенге)", "label_kk": "Ең төмен жалақы (теңге)"},
            {"key": "remote", "type": "boolean", "required": False,
             "label_ru": "Удалённая работа", "label_kk": "Қашықтан жұмыс"},
        ],
        "output": [
            {"key": "results", "type": "array",
             "label_ru": "Найденные вакансии (массив)", "label_kk": "Табылған вакансиялар (массив)"},
            {"key": "total", "type": "integer",
             "label_ru": "Всего", "label_kk": "Барлығы"},
        ],
    },
    "enbek.apply": {
        "label_ru": "Enbek: откликнуться на вакансию",
        "label_kk": "Enbek: вакансияға өтініш беру",
        "description_ru": "Подаёт заявку на вакансию.",
        "description_kk": "Вакансияға өтініш береді.",
        "domain": ["enbek"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН соискателя", "label_kk": "Өтініш беруші ИИН"},
            {"key": "vacancy_id", "type": "string", "required": True,
             "label_ru": "ID вакансии", "label_kk": "Вакансия ID"},
            {"key": "cover_letter", "type": "string", "required": False,
             "label_ru": "Сопроводительное письмо", "label_kk": "Ілеспе хат"},
        ],
        "output": [
            {"key": "application_id", "type": "string",
             "label_ru": "Номер заявки", "label_kk": "Өтініш нөмірі"},
            {"key": "status", "type": {"enum": ["sent", "duplicate", "vacancy_closed"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },
    "enbek.employer_stats": {
        "label_ru": "Enbek: статистика работодателя",
        "label_kk": "Enbek: жұмыс беруші статистикасы",
        "description_ru": "Показывает статистику работодателя по БИН (открытые вакансии, средняя зарплата).",
        "description_kk": "БИН бойынша жұмыс берушінің статистикасын көрсетеді.",
        "domain": ["enbek"],
        "input": [
            {"key": "bin", "type": "bin", "required": True,
             "label_ru": "БИН работодателя", "label_kk": "Жұмыс беруші БИН"},
        ],
        "output": [
            {"key": "open_vacancies", "type": "integer",
             "label_ru": "Открытые вакансии", "label_kk": "Ашық вакансиялар"},
            {"key": "avg_salary_kzt", "type": "amount_kzt",
             "label_ru": "Средняя зарплата (тенге)", "label_kk": "Орташа жалақы (теңге)"},
        ],
    },

    # =========================  ПОЧТА / ЛОГИСТИКА  =========================
    "kazpost.track": {
        "label_ru": "Казпочта: отследить отправление",
        "label_kk": "Қазпошта: жөнелтілімді бақылау",
        "description_ru": "Отслеживание посылки по трек-номеру.",
        "description_kk": "Трек-нөмір бойынша сәлемдемені бақылау.",
        "domain": ["logistics"],
        "input": [
            {"key": "tracking_number", "type": "string", "required": True,
             "label_ru": "Трек-номер", "label_kk": "Трек-нөмір"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["accepted", "in_transit", "out_for_delivery", "delivered", "returned"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "current_location", "type": "string",
             "label_ru": "Текущее местоположение", "label_kk": "Ағымдағы орналасуы"},
            {"key": "estimated_delivery", "type": "date",
             "label_ru": "Ожидаемая доставка", "label_kk": "Болжамды жеткізу"},
        ],
    },
    "kazpost.estimate": {
        "label_ru": "Казпочта: расчёт стоимости",
        "label_kk": "Қазпошта: құнды есептеу",
        "description_ru": "Рассчитывает стоимость и срок доставки между городами.",
        "description_kk": "Қалалар арасындағы жеткізу құны мен мерзімін есептейді.",
        "domain": ["logistics"],
        "input": [
            {"key": "from_city", "type": "string", "required": True,
             "label_ru": "Город отправления", "label_kk": "Жіберу қаласы"},
            {"key": "to_city", "type": "string", "required": True,
             "label_ru": "Город назначения", "label_kk": "Жеткізу қаласы"},
            {"key": "weight_g", "type": "integer", "required": True,
             "label_ru": "Вес (граммы)", "label_kk": "Салмақ (грамм)"},
            {"key": "service_type", "type": {"enum": ["standard", "express", "registered"]}, "required": False,
             "label_ru": "Тип услуги", "label_kk": "Қызмет түрі"},
        ],
        "output": [
            {"key": "price_kzt", "type": "amount_kzt",
             "label_ru": "Стоимость (тенге)", "label_kk": "Құны (теңге)"},
            {"key": "estimated_days", "type": "integer",
             "label_ru": "Срок (дней)", "label_kk": "Мерзімі (күн)"},
        ],
    },

    # =============================  ОБРАЗОВАНИЕ  ===========================
    "ent.register": {
        "label_ru": "ЕНТ: регистрация на тест",
        "label_kk": "ҰБТ: тестке тіркелу",
        "description_ru": "Регистрация на Единое национальное тестирование.",
        "description_kk": "Ұлттық бірыңғай тестілеуге тіркеу.",
        "domain": ["education"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
            {"key": "exam_year", "type": "integer", "required": True,
             "label_ru": "Год сдачи", "label_kk": "Тапсыру жылы"},
            {"key": "subjects", "type": "array", "required": True,
             "label_ru": "Предметы (массив)", "label_kk": "Пәндер (массив)"},
            {"key": "test_center_city", "type": "string", "required": False,
             "label_ru": "Город тест-центра", "label_kk": "Тест-орталық қаласы"},
        ],
        "output": [
            {"key": "registration_id", "type": "string",
             "label_ru": "Номер регистрации", "label_kk": "Тіркеу нөмірі"},
            {"key": "test_date", "type": "date",
             "label_ru": "Дата тестирования", "label_kk": "Тестілеу күні"},
            {"key": "test_center", "type": "string",
             "label_ru": "Тест-центр", "label_kk": "Тест орталығы"},
        ],
    },
    "edu.university_faq": {
        "label_ru": "ВУЗ: часто задаваемые вопросы",
        "label_kk": "ЖОО: жиі қойылатын сұрақтар",
        "description_ru": "Получает ответы на типовые вопросы об университете.",
        "description_kk": "Университет туралы үлгі сұрақтарға жауап алады.",
        "domain": ["education"],
        "input": [
            {"key": "university_code", "type": "string", "required": True,
             "label_ru": "Код университета", "label_kk": "Университет коды", "placeholder": "kaznu"},
            {"key": "topic", "type": {"enum": ["admission", "tuition", "scholarship", "dormitory", "transfer"]},
             "required": True,
             "label_ru": "Тема", "label_kk": "Тақырып"},
        ],
        "output": [
            {"key": "answer_kk", "type": "string",
             "label_ru": "Ответ (на казахском)", "label_kk": "Жауап (қазақша)"},
            {"key": "official_url", "type": "url",
             "label_ru": "Официальная ссылка", "label_kk": "Ресми сілтеме"},
        ],
    },
    "edu.school_schedule": {
        "label_ru": "Школа: расписание уроков",
        "label_kk": "Мектеп: сабақ кестесі",
        "description_ru": "Расписание уроков для класса на дату.",
        "description_kk": "Сыныптың белгілі күнге арналған сабақ кестесі.",
        "domain": ["education"],
        "input": [
            {"key": "school_id", "type": "string", "required": True,
             "label_ru": "ID школы", "label_kk": "Мектеп ID"},
            {"key": "grade", "type": "string", "required": True,
             "label_ru": "Класс", "label_kk": "Сынып", "placeholder": "9-А"},
            {"key": "date", "type": "date", "required": True,
             "label_ru": "Дата", "label_kk": "Күні"},
        ],
        "output": [
            {"key": "lessons", "type": "array",
             "label_ru": "Уроки (массив)", "label_kk": "Сабақтар (массив)"},
        ],
    },

    # ============================  ЗДРАВООХРАНЕНИЕ  ========================
    "health.find_clinic": {
        "label_ru": "Здоровье: найти клинику",
        "label_kk": "Денсаулық: емхана іздеу",
        "description_ru": "Поиск клиник по специальности и городу.",
        "description_kk": "Мамандық пен қала бойынша емхана іздеу.",
        "domain": ["health"],
        "input": [
            {"key": "specialty", "type": "string", "required": True,
             "label_ru": "Специальность врача", "label_kk": "Дәрігер мамандығы"},
            {"key": "city", "type": "string", "required": True,
             "label_ru": "Город", "label_kk": "Қала"},
            {"key": "accepts_fsms", "type": "boolean", "required": False,
             "label_ru": "Принимает по ФСМС", "label_kk": "ӘМСҚ бойынша қабылдайды"},
        ],
        "output": [
            {"key": "clinics", "type": "array",
             "label_ru": "Клиники (массив)", "label_kk": "Емханалар (массив)"},
            {"key": "total", "type": "integer",
             "label_ru": "Всего", "label_kk": "Барлығы"},
        ],
    },
    "health.book_appointment": {
        "label_ru": "Здоровье: запись на приём",
        "label_kk": "Денсаулық: дәрігерге жазылу",
        "description_ru": "Записывает пациента к врачу на конкретное время.",
        "description_kk": "Пациентті дәрігерге нақты уақытқа жазады.",
        "domain": ["health"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН пациента", "label_kk": "Пациенттің ИИН-і"},
            {"key": "clinic_id", "type": "string", "required": True,
             "label_ru": "ID клиники", "label_kk": "Емхана ID"},
            {"key": "doctor_id", "type": "string", "required": True,
             "label_ru": "ID врача", "label_kk": "Дәрігер ID"},
            {"key": "datetime", "type": "datetime", "required": True,
             "label_ru": "Дата и время", "label_kk": "Күні мен уақыты"},
        ],
        "output": [
            {"key": "appointment_id", "type": "string",
             "label_ru": "ID записи", "label_kk": "Жазылу ID"},
            {"key": "status", "type": {"enum": ["booked", "no_slots", "doctor_unavailable"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },
    "health.prescription_status": {
        "label_ru": "Здоровье: статус рецепта",
        "label_kk": "Денсаулық: рецепт мәртебесі",
        "description_ru": "Статус электронного рецепта.",
        "description_kk": "Электрондық рецепттің мәртебесі.",
        "domain": ["health"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН пациента", "label_kk": "Пациенттің ИИН-і"},
            {"key": "prescription_id", "type": "string", "required": True,
             "label_ru": "ID рецепта", "label_kk": "Рецепт ID"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["active", "filled", "expired"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "valid_until", "type": "date",
             "label_ru": "Действителен до", "label_kk": "Жарамдылық мерзімі"},
        ],
    },

    # ============================  КОММЕРЦИЯ  ==============================
    "shop.search": {
        "label_ru": "Магазин: поиск товара",
        "label_kk": "Дүкен: тауар іздеу",
        "description_ru": "Поиск товаров в каталоге.",
        "description_kk": "Каталогтан тауар іздеу.",
        "domain": ["commerce"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Поисковый запрос", "label_kk": "Іздеу сұрауы"},
            {"key": "price_max_kzt", "type": "amount_kzt", "required": False,
             "label_ru": "Макс. цена (тенге)", "label_kk": "Макс. баға (теңге)"},
            {"key": "category", "type": "string", "required": False,
             "label_ru": "Категория", "label_kk": "Санат"},
        ],
        "output": [
            {"key": "results", "type": "array",
             "label_ru": "Найденные товары (массив)", "label_kk": "Табылған тауарлар (массив)"},
            {"key": "total", "type": "integer",
             "label_ru": "Всего", "label_kk": "Барлығы"},
        ],
    },
    "shop.order_status": {
        "label_ru": "Магазин: статус заказа",
        "label_kk": "Дүкен: тапсырыс мәртебесі",
        "description_ru": "Статус заказа по его ID.",
        "description_kk": "Тапсырыс ID-сі бойынша оның мәртебесі.",
        "domain": ["commerce"],
        "input": [
            {"key": "order_id", "type": "string", "required": True,
             "label_ru": "ID заказа", "label_kk": "Тапсырыс ID"},
        ],
        "output": [
            {"key": "status", "type": {"enum": ["created", "paid", "shipped", "delivered", "cancelled"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
            {"key": "tracking_number", "type": "string",
             "label_ru": "Трек-номер", "label_kk": "Трек-нөмір"},
        ],
    },
    "shop.return_request": {
        "label_ru": "Магазин: возврат товара",
        "label_kk": "Дүкен: тауарды қайтару",
        "description_ru": "Создаёт заявку на возврат товара.",
        "description_kk": "Тауарды қайтаруға өтініш жасайды.",
        "domain": ["commerce"],
        "input": [
            {"key": "order_id", "type": "string", "required": True,
             "label_ru": "ID заказа", "label_kk": "Тапсырыс ID"},
            {"key": "reason", "type": {"enum": ["defective", "wrong_item", "not_as_described", "no_longer_needed"]},
             "required": True,
             "label_ru": "Причина возврата", "label_kk": "Қайтару себебі"},
            {"key": "description", "type": "string", "required": False,
             "label_ru": "Описание", "label_kk": "Сипаттама"},
        ],
        "output": [
            {"key": "return_id", "type": "string",
             "label_ru": "Номер возврата", "label_kk": "Қайтару нөмірі"},
            {"key": "expected_refund_date", "type": "date",
             "label_ru": "Ожидаемая дата возврата средств", "label_kk": "Ақша қайтарудың болжамды күні"},
        ],
    },

    # ==============================  СОБЫТИЯ  ==============================
    "events.search": {
        "label_ru": "События: поиск мероприятий",
        "label_kk": "Іс-шаралар: іздеу",
        "description_ru": "Поиск мероприятий в городе.",
        "description_kk": "Қаладағы іс-шараларды іздеу.",
        "domain": ["commerce", "culture"],
        "input": [
            {"key": "city", "type": "string", "required": True,
             "label_ru": "Город", "label_kk": "Қала"},
            {"key": "category", "type": {"enum": ["concert", "theater", "sport", "exhibition", "festival"]},
             "required": False,
             "label_ru": "Категория", "label_kk": "Санат"},
            {"key": "date_from", "type": "date", "required": False,
             "label_ru": "Дата от", "label_kk": "Күн басталу"},
            {"key": "date_to", "type": "date", "required": False,
             "label_ru": "Дата до", "label_kk": "Күн аяқталу"},
        ],
        "output": [
            {"key": "events", "type": "array",
             "label_ru": "Мероприятия (массив)", "label_kk": "Іс-шаралар (массив)"},
        ],
    },
    "events.book_ticket": {
        "label_ru": "События: бронь билета",
        "label_kk": "Іс-шаралар: билет брондау",
        "description_ru": "Бронирует билет на мероприятие.",
        "description_kk": "Іс-шараға билет брондайды.",
        "domain": ["commerce", "culture"],
        "input": [
            {"key": "event_id", "type": "string", "required": True,
             "label_ru": "ID мероприятия", "label_kk": "Іс-шара ID"},
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН покупателя", "label_kk": "Сатып алушы ИИН"},
            {"key": "tickets_count", "type": "integer", "required": True,
             "label_ru": "Кол-во билетов", "label_kk": "Билет саны"},
            {"key": "seat_preference", "type": "string", "required": False,
             "label_ru": "Предпочтение по месту", "label_kk": "Орын таңдауы"},
        ],
        "output": [
            {"key": "booking_id", "type": "string",
             "label_ru": "Номер брони", "label_kk": "Бронь нөмірі"},
            {"key": "total_kzt", "type": "amount_kzt",
             "label_ru": "Итого (тенге)", "label_kk": "Жиынтығы (теңге)"},
        ],
    },

    # =============================  ПУТЕШЕСТВИЯ  ===========================
    "flights.search": {
        "label_ru": "Полёты: поиск рейсов",
        "label_kk": "Авиабилет: рейс іздеу",
        "description_ru": "Поиск авиарейсов между городами.",
        "description_kk": "Қалалар арасындағы авиарейстерді іздеу.",
        "domain": ["logistics", "commerce"],
        "input": [
            {"key": "from_iata", "type": "string", "required": True,
             "label_ru": "IATA-код вылета", "label_kk": "Ұшып шығу IATA коды", "placeholder": "ALA"},
            {"key": "to_iata", "type": "string", "required": True,
             "label_ru": "IATA-код прилёта", "label_kk": "Қону IATA коды", "placeholder": "NQZ"},
            {"key": "departure_date", "type": "date", "required": True,
             "label_ru": "Дата вылета", "label_kk": "Ұшу күні"},
            {"key": "return_date", "type": "date", "required": False,
             "label_ru": "Дата возврата", "label_kk": "Қайту күні"},
            {"key": "passengers", "type": "integer", "required": False,
             "label_ru": "Пассажиров", "label_kk": "Жолаушылар саны"},
        ],
        "output": [
            {"key": "flights", "type": "array",
             "label_ru": "Рейсы (массив)", "label_kk": "Рейстер (массив)"},
        ],
    },
    "trains.search": {
        "label_ru": "Поезда: поиск рейсов",
        "label_kk": "Пойыздар: рейс іздеу",
        "description_ru": "Поиск ж/д рейсов между городами.",
        "description_kk": "Қалалар арасындағы темір жол рейстерін іздеу.",
        "domain": ["logistics"],
        "input": [
            {"key": "from_city", "type": "string", "required": True,
             "label_ru": "Город отправления", "label_kk": "Жіберу қаласы"},
            {"key": "to_city", "type": "string", "required": True,
             "label_ru": "Город назначения", "label_kk": "Жеткізу қаласы"},
            {"key": "departure_date", "type": "date", "required": True,
             "label_ru": "Дата отправления", "label_kk": "Жөнелу күні"},
            {"key": "class", "type": {"enum": ["plackart", "kupe", "lux"]}, "required": False,
             "label_ru": "Класс вагона", "label_kk": "Вагон класы"},
        ],
        "output": [
            {"key": "trains", "type": "array",
             "label_ru": "Поезда (массив)", "label_kk": "Пойыздар (массив)"},
        ],
    },
    "hotel.search": {
        "label_ru": "Отели: поиск",
        "label_kk": "Қонақүйлер: іздеу",
        "description_ru": "Поиск отелей в городе на даты.",
        "description_kk": "Қаладағы қонақүйлерді белгілі күндерге іздеу.",
        "domain": ["logistics", "commerce"],
        "input": [
            {"key": "city", "type": "string", "required": True,
             "label_ru": "Город", "label_kk": "Қала"},
            {"key": "check_in", "type": "date", "required": True,
             "label_ru": "Заезд", "label_kk": "Кіру күні"},
            {"key": "check_out", "type": "date", "required": True,
             "label_ru": "Выезд", "label_kk": "Шығу күні"},
            {"key": "guests", "type": "integer", "required": False,
             "label_ru": "Гостей", "label_kk": "Қонақтар саны"},
            {"key": "max_price_kzt", "type": "amount_kzt", "required": False,
             "label_ru": "Макс. цена за ночь (тенге)", "label_kk": "Бір түнгі макс. баға (теңге)"},
        ],
        "output": [
            {"key": "hotels", "type": "array",
             "label_ru": "Отели (массив)", "label_kk": "Қонақүйлер (массив)"},
        ],
    },

    # ===============================  СВЯЗЬ  ===============================
    "comm.sms": {
        "label_ru": "SMS: отправить",
        "label_kk": "SMS: жіберу",
        "description_ru": "Отправляет SMS-сообщение на казахстанский номер.",
        "description_kk": "Қазақстан нөміріне SMS-хабар жібереді.",
        "domain": ["other"],
        "input": [
            {"key": "to", "type": "phone_kz", "required": True,
             "label_ru": "Кому (+7XXXXXXXXXX)", "label_kk": "Кімге (+7XXXXXXXXXX)"},
            {"key": "text", "type": "string", "required": True,
             "label_ru": "Текст SMS", "label_kk": "SMS мәтіні"},
        ],
        "output": [
            {"key": "message_id", "type": "string",
             "label_ru": "ID сообщения", "label_kk": "Хабар ID"},
            {"key": "status", "type": {"enum": ["sent", "failed"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },
    "comm.email": {
        "label_ru": "Email: отправить",
        "label_kk": "Email: жіберу",
        "description_ru": "Отправляет электронное письмо.",
        "description_kk": "Электрондық хат жібереді.",
        "domain": ["other"],
        "input": [
            {"key": "to", "type": "email", "required": True,
             "label_ru": "Кому (email)", "label_kk": "Кімге (email)"},
            {"key": "subject", "type": "string", "required": True,
             "label_ru": "Тема", "label_kk": "Тақырып"},
            {"key": "body", "type": "string", "required": True,
             "label_ru": "Текст письма", "label_kk": "Хат мәтіні"},
            {"key": "cc", "type": "array", "required": False,
             "label_ru": "Копия (массив email)", "label_kk": "Көшірме (email массиві)"},
        ],
        "output": [
            {"key": "message_id", "type": "string",
             "label_ru": "ID письма", "label_kk": "Хат ID"},
            {"key": "status", "type": {"enum": ["sent", "queued", "failed"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },
    "comm.call": {
        "label_ru": "Звонок: инициировать",
        "label_kk": "Қоңырау: бастау",
        "description_ru": "Инициирует телефонный звонок.",
        "description_kk": "Телефон қоңырауын бастайды.",
        "domain": ["other"],
        "input": [
            {"key": "to", "type": "phone_kz", "required": True,
             "label_ru": "Кому (+7XXXXXXXXXX)", "label_kk": "Кімге (+7XXXXXXXXXX)"},
        ],
        "output": [
            {"key": "call_id", "type": "string",
             "label_ru": "ID звонка", "label_kk": "Қоңырау ID"},
            {"key": "status", "type": {"enum": ["initiated", "failed"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },

    # ================================  КАРТЫ  ==============================
    "maps.geocode": {
        "label_ru": "Карты: геокодирование",
        "label_kk": "Карталар: геокодтау",
        "description_ru": "Преобразует адрес в координаты.",
        "description_kk": "Мекенжайды координаталарға түрлендіреді.",
        "domain": ["other"],
        "input": [
            {"key": "address", "type": "string", "required": True,
             "label_ru": "Адрес", "label_kk": "Мекенжайы"},
            {"key": "city", "type": "string", "required": False,
             "label_ru": "Город", "label_kk": "Қала"},
        ],
        "output": [
            {"key": "lat", "type": "string",
             "label_ru": "Широта", "label_kk": "Ендік"},
            {"key": "lon", "type": "string",
             "label_ru": "Долгота", "label_kk": "Бойлық"},
            {"key": "formatted_address", "type": "string",
             "label_ru": "Полный адрес", "label_kk": "Толық мекенжай"},
        ],
    },
    "maps.directions": {
        "label_ru": "Карты: маршрут",
        "label_kk": "Карталар: бағыт",
        "description_ru": "Строит маршрут между двумя точками.",
        "description_kk": "Екі нүкте арасындағы бағытты құрады.",
        "domain": ["other"],
        "input": [
            {"key": "from", "type": "string", "required": True,
             "label_ru": "Откуда", "label_kk": "Қайдан"},
            {"key": "to", "type": "string", "required": True,
             "label_ru": "Куда", "label_kk": "Қайда"},
            {"key": "mode", "type": {"enum": ["driving", "walking", "transit", "bicycling"]}, "required": False,
             "label_ru": "Режим", "label_kk": "Жылжу түрі"},
        ],
        "output": [
            {"key": "distance_km", "type": "integer",
             "label_ru": "Расстояние (км)", "label_kk": "Қашықтығы (км)"},
            {"key": "duration_minutes", "type": "integer",
             "label_ru": "Длительность (мин)", "label_kk": "Ұзақтығы (мин)"},
        ],
    },
    "maps.nearby": {
        "label_ru": "Карты: поблизости",
        "label_kk": "Карталар: жақын маңда",
        "description_ru": "Поиск объектов вокруг точки.",
        "description_kk": "Нүкте айналасындағы объектілерді іздеу.",
        "domain": ["other"],
        "input": [
            {"key": "location", "type": "string", "required": True,
             "label_ru": "Точка (координаты или адрес)", "label_kk": "Нүкте (координаталар немесе мекенжай)"},
            {"key": "category", "type": "string", "required": True,
             "label_ru": "Категория объектов", "label_kk": "Объект санаты"},
            {"key": "radius_m", "type": "integer", "required": False,
             "label_ru": "Радиус (метры)", "label_kk": "Радиус (метр)"},
        ],
        "output": [
            {"key": "places", "type": "array",
             "label_ru": "Объекты (массив)", "label_kk": "Объектілер (массив)"},
        ],
    },

    # ================================  ПОИСК  ==============================
    "search.web": {
        "label_ru": "Поиск: в интернете",
        "label_kk": "Іздеу: интернетте",
        "description_ru": "Веб-поиск.",
        "description_kk": "Веб-іздеу.",
        "domain": ["other"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Запрос", "label_kk": "Сұрау"},
            {"key": "lang", "type": {"enum": ["kk", "ru", "en"]}, "required": False,
             "label_ru": "Язык результатов", "label_kk": "Нәтиже тілі"},
        ],
        "output": [
            {"key": "results", "type": "array",
             "label_ru": "Результаты (массив)", "label_kk": "Нәтижелер (массив)"},
        ],
    },
    "search.news": {
        "label_ru": "Поиск: новости",
        "label_kk": "Іздеу: жаңалықтар",
        "description_ru": "Поиск новостей.",
        "description_kk": "Жаңалықтарды іздеу.",
        "domain": ["other"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Запрос", "label_kk": "Сұрау"},
            {"key": "date_from", "type": "date", "required": False,
             "label_ru": "Не старше даты", "label_kk": "Күннен жаңа"},
            {"key": "lang", "type": {"enum": ["kk", "ru", "en"]}, "required": False,
             "label_ru": "Язык", "label_kk": "Тіл"},
        ],
        "output": [
            {"key": "articles", "type": "array",
             "label_ru": "Статьи (массив)", "label_kk": "Мақалалар (массив)"},
        ],
    },
    "search.wiki": {
        "label_ru": "Поиск: Википедия",
        "label_kk": "Іздеу: Уикипедия",
        "description_ru": "Поиск в Википедии.",
        "description_kk": "Уикипедиядан іздеу.",
        "domain": ["other", "education", "culture"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Запрос", "label_kk": "Сұрау"},
            {"key": "lang", "type": {"enum": ["kk", "ru", "en"]}, "required": False,
             "label_ru": "Язык", "label_kk": "Тіл"},
        ],
        "output": [
            {"key": "summary", "type": "string",
             "label_ru": "Краткое описание", "label_kk": "Қысқаша сипаттама"},
            {"key": "url", "type": "url",
             "label_ru": "Ссылка", "label_kk": "Сілтеме"},
        ],
    },
    "search.docs": {
        "label_ru": "Поиск: в документах",
        "label_kk": "Іздеу: құжаттардан",
        "description_ru": "Поиск в технической документации/руководствах/FAQ.",
        "description_kk": "Техникалық құжаттама/нұсқаулықтар/жиі сұрақтардан іздеу.",
        "domain": ["other", "legal"],
        "input": [
            {"key": "query", "type": "string", "required": True,
             "label_ru": "Запрос", "label_kk": "Сұрау"},
            {"key": "doc_type", "type": {"enum": ["regulation", "manual", "faq"]}, "required": False,
             "label_ru": "Тип документа", "label_kk": "Құжат түрі"},
        ],
        "output": [
            {"key": "matches", "type": "array",
             "label_ru": "Совпадения (массив)", "label_kk": "Сәйкестіктер (массив)"},
        ],
    },

    # =============================  РАСПИСАНИЕ  ============================
    "calendar.create_event": {
        "label_ru": "Календарь: создать событие",
        "label_kk": "Күнтізбе: оқиға жасау",
        "description_ru": "Создаёт событие в календаре пользователя.",
        "description_kk": "Пайдаланушының күнтізбесінде оқиға жасайды.",
        "domain": ["other"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН пользователя", "label_kk": "Пайдаланушының ИИН-і"},
            {"key": "title", "type": "string", "required": True,
             "label_ru": "Название события", "label_kk": "Оқиға атауы"},
            {"key": "start", "type": "datetime", "required": True,
             "label_ru": "Начало", "label_kk": "Басталу"},
            {"key": "end", "type": "datetime", "required": True,
             "label_ru": "Окончание", "label_kk": "Аяқталу"},
            {"key": "description", "type": "string", "required": False,
             "label_ru": "Описание", "label_kk": "Сипаттама"},
            {"key": "location", "type": "string", "required": False,
             "label_ru": "Место", "label_kk": "Орны"},
        ],
        "output": [
            {"key": "event_id", "type": "string",
             "label_ru": "ID события", "label_kk": "Оқиға ID"},
            {"key": "status", "type": {"enum": ["created", "conflict"]},
             "label_ru": "Статус", "label_kk": "Мәртебе"},
        ],
    },
    "calendar.availability": {
        "label_ru": "Календарь: свободные слоты",
        "label_kk": "Күнтізбе: бос уақыттар",
        "description_ru": "Возвращает свободные временные слоты на дату.",
        "description_kk": "Белгілі күнге арналған бос уақыт аралықтарын қайтарады.",
        "domain": ["other"],
        "input": [
            {"key": "iin", "type": "iin", "required": True,
             "label_ru": "ИИН", "label_kk": "ИИН"},
            {"key": "date", "type": "date", "required": True,
             "label_ru": "Дата", "label_kk": "Күні"},
        ],
        "output": [
            {"key": "free_slots", "type": "array",
             "label_ru": "Свободные слоты (массив)", "label_kk": "Бос уақыттар (массив)"},
        ],
    },

    # ==============================  СИСТЕМА  ==============================
    "system.now": {
        "label_ru": "Система: текущее время",
        "label_kk": "Жүйе: қазіргі уақыт",
        "description_ru": "Возвращает текущую дату и время.",
        "description_kk": "Қазіргі күн мен уақытты қайтарады.",
        "domain": ["other"],
        "input": [
            {"key": "timezone", "type": "string", "required": False,
             "label_ru": "Часовой пояс", "label_kk": "Уақыт белдеуі", "placeholder": "Asia/Almaty"},
        ],
        "output": [
            {"key": "now", "type": "datetime",
             "label_ru": "Текущее время", "label_kk": "Қазіргі уақыт"},
        ],
    },
    "system.translate": {
        "label_ru": "Система: перевод текста",
        "label_kk": "Жүйе: мәтінді аудару",
        "description_ru": "Переводит текст между языками.",
        "description_kk": "Мәтінді тілдер арасында аударады.",
        "domain": ["other", "education"],
        "input": [
            {"key": "text", "type": "string", "required": True,
             "label_ru": "Исходный текст", "label_kk": "Бастапқы мәтін"},
            {"key": "target_lang", "type": {"enum": ["kk", "ru", "en", "tr", "uz"]}, "required": True,
             "label_ru": "На какой язык", "label_kk": "Қай тілге"},
            {"key": "source_lang", "type": {"enum": ["kk", "ru", "en", "auto"]}, "required": False,
             "label_ru": "С какого языка", "label_kk": "Қай тілден"},
        ],
        "output": [
            {"key": "translated_text", "type": "string",
             "label_ru": "Переведённый текст", "label_kk": "Аударылған мәтін"},
            {"key": "detected_source_lang", "type": "string",
             "label_ru": "Определён исходный язык", "label_kk": "Анықталған бастапқы тіл"},
        ],
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Helpers (для бэкенда и API)
# ─────────────────────────────────────────────────────────────────────────────

def _placeholder_for_type(typ):
    if isinstance(typ, dict) and "enum" in typ:
        return typ["enum"][0]
    return {
        "string": "", "iin": "", "bin": "", "phone_kz": "+7",
        "amount_kzt": 0, "date": "", "datetime": "",
        "integer": 0, "boolean": False, "url": "", "email": "",
        "object": {}, "array": [],
    }.get(typ, "")


def empty_input_for(schema):
    """Скелет input по обязательным полям (для legacy «Заполнить шаблоном»)."""
    if not schema:
        return {}
    skel = {}
    for f in schema.get("input", []):
        if f.get("required"):
            skel[f["key"]] = _placeholder_for_type(f["type"])
    return skel


def empty_output_for(schema):
    """Скелет output (для legacy «Заполнить шаблоном»)."""
    if not schema:
        return {}
    return {f["key"]: _placeholder_for_type(f["type"]) for f in schema.get("output", [])}


def schema_for_form(schema, lang="ru"):
    """Преобразует схему в формат для рендера на клиенте.
    Возвращает только то, что нужно JS — без Python-специфики."""
    if not schema:
        return None

    def field_to_dict(f):
        typ = f["type"]
        d = {
            "key":         f["key"],
            "type":        typ if not isinstance(typ, dict) else "enum",
            "required":    f.get("required", False),
            "label":       f.get(f"label_{lang}") or f.get("label_ru") or f["key"],
            "placeholder": f.get("placeholder", ""),
            "hint":        f.get(f"hint_{lang}") or "",
        }
        if isinstance(typ, dict) and "enum" in typ:
            d["enum"] = typ["enum"]
        return d

    return {
        "tool":          schema.get("label_kk", ""),  # для совместимости
        "label":         schema.get(f"label_{lang}") or schema.get("label_ru", ""),
        "description":   schema.get(f"description_{lang}") or schema.get("description_ru", ""),
        "domain":        schema.get("domain", []),
        "input_fields":  [field_to_dict(f) for f in schema.get("input", [])],
        "output_fields": [field_to_dict(f) for f in schema.get("output", [])],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Валидация значений по типу — без изменений из v1
# ─────────────────────────────────────────────────────────────────────────────

_PHONE_KZ_RE = re.compile(r"^\+7\d{10}$")
_DATE_RE     = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:?\d{2}|Z)?$")
_URL_RE      = re.compile(r"^https?://[^\s]+$")
_EMAIL_RE    = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_BIN_RE      = re.compile(r"^\d{12}$")


def check_value_type(value, typ, validate_iin_fn):
    """Проверяет, соответствует ли value ожидаемому типу.
    Возвращает None если ок, иначе строку-причину."""
    # Enum
    if isinstance(typ, dict) and "enum" in typ:
        if value not in typ["enum"]:
            return f"должно быть одним из {typ['enum']}, получено {value!r}"
        return None
    if isinstance(typ, list):  # старый формат на всякий случай
        if value not in typ:
            return f"должно быть одним из {typ}, получено {value!r}"
        return None

    if typ == "string":
        return None if isinstance(value, str) else f"должно быть строкой, получено {type(value).__name__}"

    if typ == "iin":
        if not isinstance(value, str):
            return f"ИИН должен быть строкой, получено {type(value).__name__}"
        # Тримим пробелы — частая причина «ИИН не принимается»
        cleaned = value.strip()
        if cleaned != value:
            # Подсказка: были пробелы
            if not validate_iin_fn(cleaned):
                return f"ИИН «{value}» содержит пробелы и некорректен по контрольной сумме"
            return None  # после тримминга валиден — пропускаем
        if not validate_iin_fn(value):
            return f"ИИН «{value}» некорректен (12 цифр + контрольная сумма по ГОСТ)"
        return None

    if typ == "bin":
        if not isinstance(value, str) or not _BIN_RE.match(value):
            return f"БИН должен быть 12-значной строкой, получено {value!r}"
        return None

    if typ == "phone_kz":
        if not isinstance(value, str) or not _PHONE_KZ_RE.match(value):
            return f"телефон должен быть в формате +7XXXXXXXXXX, получено {value!r}"
        return None

    if typ == "amount_kzt":
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return f"сумма должна быть неотрицательным целым числом тенге, получено {value!r}"
        return None

    if typ == "date":
        if not isinstance(value, str) or not _DATE_RE.match(value):
            return f"дата должна быть в формате YYYY-MM-DD, получено {value!r}"
        return None

    if typ == "datetime":
        if not isinstance(value, str) or not _DATETIME_RE.match(value):
            return f"datetime должно быть в ISO-8601 (YYYY-MM-DDTHH:MM:SS+TZ), получено {value!r}"
        return None

    if typ == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            return f"должно быть целым числом, получено {type(value).__name__}"
        return None

    if typ == "boolean":
        if not isinstance(value, bool):
            return f"должно быть true/false, получено {type(value).__name__}"
        return None

    if typ == "url":
        if not isinstance(value, str) or not _URL_RE.match(value):
            return f"должно быть URL, получено {value!r}"
        return None

    if typ == "email":
        if not isinstance(value, str) or not _EMAIL_RE.match(value):
            return f"должно быть email, получено {value!r}"
        return None

    if typ == "object":
        return None if isinstance(value, dict) else f"должно быть JSON-объектом, получено {type(value).__name__}"

    if typ == "array":
        return None if isinstance(value, list) else f"должно быть JSON-массивом, получено {type(value).__name__}"

    return None  # неизвестный тип — пропускаем


# ─────────────────────────────────────────────────────────────────────────────
# Адаптер: старая валидация (по плоскому списку required+optional+types) —
# для совместимости с существующим кодом в app.py.
# ─────────────────────────────────────────────────────────────────────────────

def get_input_spec(tool_name):
    """Возвращает {required: [...], optional: [...], types: {key: typ}} в старом формате."""
    schema = TOOL_SCHEMAS.get(tool_name)
    if not schema:
        return None
    required, optional, types = [], [], {}
    for f in schema.get("input", []):
        (required if f.get("required") else optional).append(f["key"])
        types[f["key"]] = f["type"]
    return {"required": required, "optional": optional, "types": types}


def get_output_keys(tool_name):
    """Возвращает множество допустимых ключей output."""
    schema = TOOL_SCHEMAS.get(tool_name)
    if not schema:
        return None
    return {f["key"] for f in schema.get("output", [])}

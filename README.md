# MedApp

Курсовая работа: система учёта домашней аптечки. Аптечки бывают общими — семья, соседи. Система
приватна по замыслу: о человеке не хранится ничего, кроме идентификатора и хеша ключа.

Репозиторий зонтичный: здесь документы курсовой, а части подключены подмодулями — у каждой своя
сборка, свой CI и своя история.

## Части

| часть | что это | репозиторий |
|---|---|---|
| `src/MedAppServer` | REST API: аптечки, упаковки, брони, справочник, синхронизация | [MedAppServer](https://github.com/Kert0n/MedAppServer) |
| `src/AndroidApp` | клиент для Android | [MedAppAndroid](https://github.com/Kert0n/MedAppAndroid) |
| `src/scrapper` | скраппер справочника vidal.ru, код одноразовый | [VidalDataScrap](https://github.com/Kert0n/VidalDataScrap) |

## Клонировать

```bash
git clone --recurse-submodules https://github.com/Kert0n/MedAppDocs.git
```

Без `--recurse-submodules` каталоги частей останутся пустыми. Уже клонировали без него:

```bash
git submodule update --init --recursive
```

Подмодуль закреплён на конкретном коммите части — это и есть смысл: курсовая ссылается на то
состояние кода, которое описано в её документах. Подтянуть свежее:

```bash
git submodule update --remote src/MedAppServer
```

## Документация

| где | что |
|---|---|
| [docs/](docs) | документы курсовой: ТЗ, описание программы, текст программы |
| [docs/plans/](docs/plans) | планы, по которым шёл рефакторинг: фичи с критериями, устройство, ход работ |
| [MedAppServer/README](https://github.com/Kert0n/MedAppServer#readme) | что умеет сервер, как запустить, перечень эндпоинтов |
| [MedAppServer/ARCHITECTURE.md](https://github.com/Kert0n/MedAppServer/blob/main/ARCHITECTURE.md) | модель, слои, доступ, конкурентность, синхронизация |

## История

Этот репозиторий создан при разделении на части. История разработки — в `MedAppServer`: он и есть
прежний `MedApp`, переименованный, чтобы вся история, PR и issue остались при коде, который они
описывают.

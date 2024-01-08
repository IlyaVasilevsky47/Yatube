# Yatube

[![CI](https://github.com/IlyaVasilevsky47/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/IlyaVasilevsky47/hw05_final/actions/workflows/python-app.yml)


Yatube - это онлайн-платформа, предлагающая пользователям возможность общаться, обмениваться информацией, а также находить новых друзей и знакомых.

## Основные возможности:
- Регистрация и аутентификация пользователя.
- Создание, изменение и публикация постов.
- Обсуждение постов.

## Дополнительная возможность:
- Восстановление пароля через email.
- Распределение постов по категориям и избранным пользователям.
- Подписки на определенных пользователей с возможностью просмотра количества их постов, актуальных публикаций и т.д.

## Запуск проекта:
1. Клонируем проект
```bash
git
```

2. Создаем и активируем виртуальное окружение. 
```bash
python -m venv venv
source venv/scripts/activate
```

3. Обновляем менеджер пакетов pip и устанавливаем зависимости из файла requirements.txt.
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Создаем базу данных. 
```bash
python yatube/manage.py migrate 
```

5. Запускаем проект.
```bash
python yatube/manage.py runserver 
```

## Тесты:
В проекте используются написанные тесты. Чтобы запустить их, нужно ввести команды в терминале:
```bash
cd yatube
python manage.py test 
```

## Автор:
- Василевский И.А.
- [Почта](vasilevskijila047@gmail.com)
- [Вконтакте](https://vk.com/ilya.vasilevskiy47)

## Технический стек
- Python 3.7.9
- Django 2.2.16
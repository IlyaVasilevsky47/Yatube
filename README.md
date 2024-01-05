# Yatube

[![CI](https://github.com/IlyaVasilevsky47/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/IlyaVasilevsky47/hw05_final/actions/workflows/python-app.yml)

Yatube - это платформа, которая позволяет людям общаться, обмениваться информацией и находить новых друзей и знакомых.

## Основные возможности:
- Регистрацию и авторизацию пользователей. 
- Создание, редактирование и публикацию постов. 
- Возможность комментировать посты. 

## Дополнительная возможность:
- Разделение постов по группам и по избранным пользователям. П
- одписка на определенных пользователей и просмотр количества их постов и всех публикаций. 

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

## Автор:
- Василевский И.А.
- [Почта](vasilevskijila047@gmail.com)
- [Вконтакте](https://vk.com/ilya.vasilevskiy47)

## Технический стек
- Python 3.7.9
- Django 2.2.16



 
 

"""
Хранение необходимо осуществлять в базе данных.
В качестве СУБД использовать sqlite.
Опорная схема базы данных:
На стороне сервера БД содержит следующие таблицы:
    клиент
        - логин
        - информация
    история_клиента
        - время входа
        - ip-адрес
    список_контактов (составляется на основании выборки всех записей с
        id_владельца)
        - id_владельца
        - id_клиента
"""
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Timestamp
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(64))
    fullname = Column(String(128))
    password = Column(String(64))

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return f"<User({self.name}, {self.fullname}, {self.password})>"


class HistoryUser(Base):
    __tablename__ = 'history_user'
    id = Column(Integer, primary_key=True)
    time = Column(Timestamp(64))
    ip_addr = Column(String(127))

    def __init__(self, time, ip_addr):
        self.time = time
        self.ip_addr = ip_addr


class Contacts(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer)

    def __init__(self, contact_id):
        self.contact_id = contact_id


# Таблица доступна через атрибут класса
users_table = User.__table__
print('Declarative. Table:', users_table)

# Метаданные доступны через класс Base
metadata = Base.metadata
print('Declarative. Metadata:', metadata)

from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)


# Класс Session будет создавать Session-объекты, которые привязаны к базе данных
session = Session()
print('Session:', session)

#                   Добавление новых объектов                      #
####################################################################

# Для сохранения объекта User нужно добавить его к имеющейся сессии
admin_user = User("vasia", "Vasiliy Pypkin", "vasia2000")
session.add(admin_user)


# Простой запрос
q_user = session.query(User).filter_by(name="vasia").first()
print('Simple query:', q_user)

# Добавить сразу несколько записей
session.add_all([User("kolia", "Cool Kolian[S.A.]","kolia$$$"),
                 User("zina", "Zina Korzina", "zk18")])

# Сессия "знает" об изменениях пользователя
admin_user.password = "-=VP2001=-"
print('Session. Changed objects:', session.dirty)

# Атрибут `new` хранит объекты, ожидающие сохранения в базу данных
print('Session. New objects:', session.new)

# Метод commit() фиксирует транзакцию, сохраняя оставшиеся изменения в базу
session.commit()

print('User ID after commit:', admin_user.id)

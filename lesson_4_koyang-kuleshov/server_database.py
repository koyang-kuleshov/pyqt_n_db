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
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, \
    DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from common.variables import SERVER_DATABASE


class ServerDatabase:
    Base = declarative_base()

    class AllUsers(Base):
        __tablename__ = 'all_users'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        last_connect = Column(DateTime)

        def __init__(self, login):
            self.login = login
            self.last_connect = datetime.now()

    class ActiveUsers(Base):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        time_connection = Column(DateTime)

        def __init__(self, user, ip, port, time_connection):
            self.user = user
            self.ip = ip
            self.port = port
            self.time_connection = time_connection

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('all_users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        last_connect = Column(DateTime)

        def __init__(self, user, ip, port, last_connect):
            self.user = user
            self.ip = ip
            self.port = port
            self.last_connect = last_connect

    class UserContacts(Base):
        __tablename__ = 'user_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(String(64), ForeignKey('all_users.id'), unique=True)
        user_contacts = Column(String)

        def __init__(self, user, user_contacts):
            self.user = user
            self.user_contacts = user_contacts

    def __init__(self):
        self.engine = create_engine(SERVER_DATABASE, echo=False,
                                    pool_recycle=7200)
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_addr, port):
        result = self.session.query(self.AllUsers).filter_by(login=username)
        if result.count():
            user = result.first()
            user.last_login = datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
        new_active_user = self.ActiveUsers(user.id, ip_addr, port,
                                           datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, ip_addr, port, datetime.now())
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(login=username).\
            first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def user_list(self):
        query = self.session.query(
            self.AllUsers.login,
            self.AllUsers.last_connect)
        return query.all()

    def active_users_list(self):
        query = self.session.query(
            self.ActiveUsers.user,
            self.ActiveUsers.ip,
            self.ActiveUsers.port,
            self.ActiveUsers.time_connection).join(self.AllUsers)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(self.LoginHistory.user,
                                   self.LoginHistory.last_connect,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.login == username)
        return query.all()


if __name__ == '__main__':
    database = ServerDatabase()
    database.user_login('user_1', '192.168.0.1', 1111)
    database.user_login('user_2', '192.168.0.2', 2222)
    print(database.active_users_list())
    database.user_logout('user_1')
    print(database.active_users_list())
    print(database.login_history('user_1'))
    print(database.user_list())

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


class ClientDatabase:
    Base = declarative_base()

    class KnownUsers(Base):
        __tablename__ = 'known_user'
        id = Column(Integer, primary_key=True)
        username = Column(String)

        def __init__(self, user):
            self.id = None
            self.username = user

    class MessageHistory(Base):
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        from_user = Column(String)
        to_user = Column(String)
        message = Column(String)
        date = Column(DateTime)

        def __init__(self, from_user, to_user, message):
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.now()

    class Contacts(Base):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

        def __init__(self, contact):
            self.contact = contact

    def __init__(self, user):
        self.user = user
        self.engine = create_engine(f'sqlite:///db_{self.user}.sqlite3',
                                    echo=False,
                                    pool_recycle=7200)
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.commit()

    def add_contact(self, contact):
        if not self.session.query(self.Contacts).filter_by(name=contact).\
                count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact):
        self.session.query(self.Contacts).filter_by(name=contact).delete()

    def add_users(self, users_list):
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, from_user, to_user, message):
        message_row = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.Contacts.name
                                                             ).all()]

    def get_users(self):
        return [user[0] for user in self.session.query(self.KnownUsers.
                                                       username).all()]

    def check_user(self, user):
        if self.session.query(self.KnownUsers).filter_by(username=user).\
                count():
            return True
        else:
            return False

    def check_contact(self, contact):
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, from_who=None, to_who=None):
        query = self.session.query(self.MessageHistory)
        if from_who:
            query = query.filter_by(from_user=from_who)
        if to_who:
            query = query.filter_by(to_user=to_who)
        return [(history_row.from_user, history_row.to_user,
                history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    database = ClientDatabase('user_1')
    for i in ['test3', 'test4', 'test5']:
        database.add_contact(i)
    database.add_contact('test4')
    database.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    database.save_message(
        'test1',
        'test2',
        f'Привет! я тестовое сообщение от {datetime.now()}!'
    )
    database.save_message(
        'test2',
        'test1',
        f'Привет! я другое тестовое сообщение от {datetime.now()}!')
    print(database.get_contacts())
    print(database.get_users())
    print(database.check_user('test1'))
    print(database.check_user('test10'))
    print(database.get_history('test2'))
    print(database.get_history(to_who='test2'))
    print(database.get_history('test3'))
    database.del_contact('test4')
    print(database.get_contacts())

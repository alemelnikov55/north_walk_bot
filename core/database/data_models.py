"""
Модуль объявления таблиц базы данных
"""
from sqlalchemy import Column, BigInteger, SmallInteger, String, ForeignKey, DateTime, func, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Определение таблиц

class User(Base):
    """Таблица пользователей

    идентификация происходит по user_id телеграмма
    name: ФИ или username пользователя"""
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(SmallInteger, default=0)
    created_at = Column(DateTime, default=func.now())


class Admin(Base):
    """
    Таблица администраторов
    """
    __tablename__ = 'admins'

    admin_id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())


class WorkoutType(Base):
    """
    Таблица видов тренировок
    """
    __tablename__ = 'workout_types'

    type_id = Column(SmallInteger, primary_key=True)
    type_name = Column(String, nullable=False)


class Workout(Base):
    """
    Таблица тренировок

    workout_id - уникальный идентификатор тренировки
    """
    __tablename__ = 'workouts'

    workout_id = Column(SmallInteger, primary_key=True)
    type_id = Column(SmallInteger, ForeignKey('workout_types.type_id'))
    date = Column(DateTime, nullable=False)
    created_by = Column(BigInteger, ForeignKey('admins.admin_id'))
    created_at = Column(DateTime, default=func.now())


class Status(Base):
    """Таблица статусов тренировок"""
    __tablename__ = 'statuses'

    status_id = Column(SmallInteger, primary_key=True)
    status_name = Column(String, nullable=False)


class Registration(Base):
    """Таблица регистраций пользователей на тренировки

    registration_id - уникальнй идентификатор записи
    в данной таблице будет проводиться проверка оплаты"""
    __tablename__ = 'registrations'

    registration_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    workout_id = Column(SmallInteger, ForeignKey('workouts.workout_id', ondelete='CASCADE'))
    status_id = Column(SmallInteger, ForeignKey('statuses.status_id'), default=1)
    is_payed = Column(Boolean, nullable=True, default=None)
    registered_at = Column(DateTime, default=func.now())


class AttendanceHistory(Base):
    """Лишняя таблица, подлежит удалению"""
    __tablename__ = 'attendance_history'

    history_id = Column(SmallInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    workout_id = Column(SmallInteger, ForeignKey('workouts.workout_id'))
    attended_at = Column(DateTime, default=func.now())

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# Определение таблиц

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    balance = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())


class Admin(Base):
    __tablename__ = 'admins'

    admin_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())


class WorkoutType(Base):
    __tablename__ = 'workout_types'

    type_id = Column(Integer, primary_key=True)
    type_name = Column(String, nullable=False)


class Workout(Base):
    __tablename__ = 'workouts'

    workout_id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('workout_types.type_id'))
    date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey('admins.admin_id'))
    created_at = Column(DateTime, default=func.now())
    #
    # type = relationship("WorkoutType")
    # creator = relationship("Admin")


class Status(Base):
    __tablename__ = 'statuses'

    status_id = Column(Integer, primary_key=True)
    status_name = Column(String, nullable=False)


class Registration(Base):
    __tablename__ = 'registrations'

    registration_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    workout_id = Column(Integer, ForeignKey('workouts.workout_id'))
    status_id = Column(Integer, ForeignKey('statuses.status_id'), default=1)
    registered_at = Column(DateTime, default=func.now())

    # user = relationship("User")
    # workout = relationship("Workout")
    # status = relationship("Status")


class AttendanceHistory(Base):
    __tablename__ = 'attendance_history'

    history_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    workout_id = Column(Integer, ForeignKey('workouts.workout_id'))
    attended_at = Column(DateTime, default=func.now())

    # user = relationship("User")
    # workout = relationship("Workout")

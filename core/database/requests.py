import asyncio
import time
from datetime import timedelta, datetime
# import datetime

from sqlalchemy import text, func
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.psql_engine import async_session, engine
from database.data_models import Base, WorkoutType, Status, User, Workout, Admin, Registration

from loader import MainSettings


class UserRequest:
    @staticmethod
    async def add_user(user_id: int, name: str, balance: int = 0):
        async with async_session() as session:
            new_user = User(user_id=user_id, name=name, balance=balance, created_at=datetime.now())
            # print(new_user.name, new_user.user_id, new_user.balance, new_user.created_at)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            return new_user


class WorkoutsRequests:

    @staticmethod
    async def create_workout(workout_date: datetime, type_id: int, created_by: int):
        async with async_session() as session:
            new_workout = Workout(date=workout_date, type_id=type_id, created_by=created_by)
            session.add(new_workout)
            await session.commit()
            # await session.refresh(new_workout)
            return new_workout

    @staticmethod
    async def show_workouts():
        async with async_session() as session:
            result = await session.execute(
                select(Workout, WorkoutType)
                .where(Workout.date >= datetime.now())
                .join(WorkoutType).order_by(Workout.date)
            )
            workouts = result.all()
            # print(result.scalar_one_or_none())
            return workouts

    @staticmethod
    async def get_type_workout_by_id(workout_id):
        async with async_session() as session:
            result = await session.get(WorkoutType, workout_id)
            type_workout = result
            return type_workout.type_name

    @staticmethod
    async def get_workout_by_id(workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(Workout, WorkoutType)
                .where(Workout.workout_id == workout_id)
                .join(WorkoutType)
            )
            workout = result.all()
        return workout


class RegistrationRequests:

    @staticmethod
    async def is_already_exists(user_id: int, workout_id: int):
        async with async_session() as session:
            result = await session.execute(select(Registration).filter_by(user_id=user_id, workout_id=workout_id))

            existing_registration = result.scalars().first()
            if existing_registration:
                return True
            return False

    @staticmethod
    async def sign_in(user_id: int, workout_id: int):
        async with async_session() as session:
            new_registration = Registration(user_id=user_id, workout_id=workout_id)
            session.add(new_registration)

            try:
                await session.commit()
                # return new_registration
            except IntegrityError:
                await session.rollback()
                print("Ошибка при записи на тренировку.")

    @staticmethod
    async def get_registration_by_workout_id(workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                (Registration, Workout)
                .filter(Registration.workout_id == workout_id)
                .join(Workout)
            )
            registrations = result.all()
            return registrations

    @staticmethod
    async def get_workouts_by_user_id(user_id: int):
        async with async_session() as session:
            result = await session.execute(select(Workout.date, WorkoutType.type_name)
            .join(Registration, Registration.workout_id == Workout.workout_id)
            .join(WorkoutType, Workout.type_id == WorkoutType.type_id)
            .filter(Registration.user_id == user_id).filter(
                Workout.date >= datetime.now())
            )
            # results = [{"workout_date": workout.date, "workout_type": workout.type_name} for workout in result.all()]
            # print(results)
            # for workout in result.all():
            #     # print(workout)
            #     print(f'{workout.date.strftime("%m.%d в %H:%M")} - {workout.type_name}')
            # print('\n'.join(message))
            return result.all()

    @staticmethod
    async def get_all_available_workouts():
        async with async_session() as session:
            result = await session.execute(
                select(Workout, WorkoutType)
                .where(Workout.date >= datetime.now())
                .join(WorkoutType).order_by(Workout.date)
            )
            workouts = result.all()
            return workouts

    @staticmethod
    async def count_sings_for_workouts():
        async with async_session() as session:
            result = await session.execute(
                select(
                    Workout.workout_id,
                    func.count(Registration.user_id).label("registration_count"))
                .join(Registration, Workout.workout_id == Registration.workout_id)
                .filter(Workout.date >= datetime.now())
                .group_by(Workout.workout_id, Workout.date)
                .order_by(Workout.date))

        walks = result.all()
        # id date count
        return walks

    @staticmethod
    async def get_workout_inspect(workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(User.name)
                .join(Registration, Registration.user_id == User.user_id)
                .filter(Registration.workout_id == workout_id)
            )

        users = result.all()
        print(users)
        return users


class ServiceRequests:
    """
    Класс для запуска работы с базой данных PostgreSQL
    """

    @staticmethod
    async def add_workout_types():
        workout_types = ['Руки 💪', 'Ноги 🦶🦶', 'Длительная ⌛️⌛️⌛️', 'Скоростная 🏎']

        async with async_session() as session:
            for workout_type in workout_types:
                # Проверяем, существует ли уже такой тип тренировки
                result = await session.execute(
                    select(WorkoutType).where(WorkoutType.type_name == workout_type)
                )
                existing_type = result.scalar_one_or_none()

                if not existing_type:
                    # Добавляем тип тренировки, если его нет
                    new_type = WorkoutType(type_name=workout_type)
                    session.add(new_type)
                # print(await session.execute(text('SELECT * FROM WorkoutType')))

            await session.commit()

    @staticmethod
    async def add_statuses_types():
        status_types = ['Записан', 'Посетил', 'Ожидает подтверждения', 'Отменил']

        async with async_session() as session:
            for status in status_types:
                # Проверяем, существует ли уже такой тип тренировки
                result = await session.execute(
                    select(Status).where(Status.status_name == status)
                )
                existing_type = result.scalar_one_or_none()

                if not existing_type:
                    # Добавляем тип тренировки, если его нет
                    new_type = Status(status_name=status)
                    session.add(new_type)
                # print(await session.execute(text('SELECT * FROM WorkoutType')))

            await session.commit()

    @staticmethod
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def clear_all_data():
        async with async_session() as session:
            await session.execute(text(
                # "TRUNCATE TABLE users, admins, workout_types, workouts, statuses, registrations, attendance_history RESTART IDENTITY CASCADE"))
                "TRUNCATE TABLE workouts RESTART IDENTITY CASCADE"))
            await session.commit()

    @staticmethod
    async def fetch_all_from_table(table_name: str):
        async with async_session() as session:
            # Заключаем название таблицы в двойные кавычки для учета регистра
            query = text(f"SELECT * FROM {table_name}")
            result = await session.execute(query)

            # Извлекаем все строки результата
            rows = result.fetchall()

            # Возвращаем результат
            return rows

    @staticmethod
    async def add_admin(admin_id, name):
        async with async_session() as session:
            new_admin = Admin(admin_id=admin_id, name=name)
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            print(new_admin)

    @staticmethod
    async def drop_all_base():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


# asyncio.run(ServiceRequests.clear_all_data())
# print((asyncio.run(WorkoutsRequests.get_type_workout_by_id(1))))
# asyncio.run(RegistrationRequests.get_workout_inspect(1))


async def create_and_fill_db():
    await ServiceRequests.create_tables()
    await ServiceRequests.add_workout_types()
    await ServiceRequests.add_statuses_types()
    await ServiceRequests.add_admin(MainSettings.ADMIN_LIST[0], 'Alexey')
    await ServiceRequests.add_admin(MainSettings.ADMIN_LIST[1], 'Natasha')

# asyncio.run(create_and_fill_db())

import asyncio
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import text, func, update
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.psql_engine import async_session, engine
from database.data_models import Base, WorkoutType, Status, User, Workout, Admin, Registration
from utils.workouts_types import workout_types
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
    async def get_workout_by_id(workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(Workout, WorkoutType)
                .where(Workout.workout_id == workout_id)
                .join(WorkoutType)
            )
            workout = result.all()
        return workout

    @staticmethod
    async def delete_workout(workout_id: int):
        async with async_session() as session:
            # query = select(Workout).filter_by(workout_id=workout_id)
            result = await session.execute(
                select(Workout)
                .filter_by(workout_id=workout_id))
            workout = result.scalars().first()

            # Если тренировка найдена, удаляем её
            if workout:
                await session.delete(workout)
                await session.commit()
                print("Тренировка и связанные записи успешно удалены.")
                return "Тренировка и связанные записи успешно удалены."
            else:
                return 'Возникла проблема при удалении просьба обратиться к администраору'


class RegistrationRequests:

    @staticmethod
    async def get_last_week_workouts(day_before: int):

        date = datetime.now() - timedelta(days=day_before)

        async with async_session() as session:
            result = await session.execute(
                select(Workout, WorkoutType)
                .where(Workout.date >= date, Workout.date <= datetime.now())
                .join(WorkoutType)
                .order_by(Workout.date)
            )
        workout_for_check = result.all()

        return workout_for_check

    @staticmethod
    async def is_already_exists(user_id: int, workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(Registration)
                .filter_by(user_id=user_id,
                           workout_id=workout_id,
                           status_id=1)
            )

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
                await RegistrationRequests.change_status(user_id, workout_id)
                # print("Ошибка при записи на тренировку.")

    @staticmethod
    async def change_status(user_id: int, workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(Registration)
                .filter_by(user_id=user_id, workout_id=workout_id)
            )
            registration = result.scalars().first()

            if registration:
                registration.status_id = 1
                await session.commit()
                print("Статус тренировки изменен.")
                return False
            else:
                print("Ошибка при изменении статуса тренировки.")

    @staticmethod
    async def get_workouts_by_user_id(user_id: int):
        async with async_session() as session:
            result = await session.execute(select(Workout.date, WorkoutType.type_name, Registration.registration_id)
            .join(Registration, Registration.workout_id == Workout.workout_id)
            .join(WorkoutType, Workout.type_id == WorkoutType.type_id)
            .filter(Registration.user_id == user_id).filter(
                Workout.date >= datetime.now(),
                Registration.status_id == 1)
            .order_by(Workout.date)
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
                .filter(Workout.date >= datetime.now(), Registration.status_id == 1)
                .group_by(Workout.workout_id, Workout.date)
                .order_by(Workout.date))

        walks = result.all()
        # id date count
        return walks

    @staticmethod
    async def get_workout_users(workout_id: int) -> List[str]:
        """
        Получение имен пользователей, записанных на тренировку

        :param workout_id: id Тренировки
        :return: Список имен пользователей
        """
        async with async_session() as session:
            result = await session.execute(
                select(User.name)
                .join(Registration, Registration.user_id == User.user_id)
                .filter(Registration.workout_id == workout_id, Registration.status_id == 1)
            )
        users = result.all()
        return users

    @staticmethod
    async def get_workout_username_and_id(workout_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(User.name, User.user_id)
                .join(Registration, Registration.user_id == User.user_id)
                .filter(Registration.workout_id == workout_id, Registration.status_id == 1)
            )
            users = result.all()
            return users

    @staticmethod
    async def give_up_registration(registration_id: int):
        async with async_session() as session:
            result = await session.execute(
                update(Registration).where(Registration.registration_id == registration_id).values(status_id=4)
            )
            await session.commit()
            return 'Запись на тренировку успешно отменена.'

    @staticmethod
    async def get_workout_info_by_reg_id(registration_id: int):
        async with async_session() as session:
            result = await session.execute(
                select(Workout.date, WorkoutType.type_name)
                .join(Registration, Registration.workout_id == Workout.workout_id)
                .join(WorkoutType, Workout.type_id == WorkoutType.type_id)
                .filter(Registration.registration_id == registration_id)
            )
            workout_info = result.all()
            return workout_info

    @staticmethod
    async def update_user_status(workout_id: int, user_id: int, status: int):
        async with async_session() as session:
            result = await session.execute(
                update(Registration)
                .filter(Registration.workout_id == workout_id,
                        Registration.user_id == user_id,
                        Registration.status_id == 1)  # Запись не отменялась
                .values(status_id=status, is_payed=True)  # TODO при запуске оплаты изменить на False
            )
            await session.commit()
            if result:
                return 'Статус пользователя успешно изменен.'


class ServiceRequests:
    """
    Класс для запуска работы с базой данных PostgreSQL
    """

    @staticmethod
    async def create_and_fill_db():
        """
        Создание таблиц БД
        """
        await ServiceRequests.create_tables()
        await ServiceRequests.add_workout_types()
        await ServiceRequests.add_statuses_types()
        try:
            await ServiceRequests.add_admin(MainSettings.ADMIN_LIST[0], 'Alexey')
            await ServiceRequests.add_admin(MainSettings.ADMIN_LIST[1], 'Natasha')
        except IntegrityError as e:
            print('\nДанные уже есть в таблице', e)

    @staticmethod
    async def add_workout_types():

        async with async_session() as session:
            for workout_type in workout_types.values():
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
        status_types = ['Записан', 'Посетил', 'Ожидает подтверждения', 'Отменил', 'Не посетил']

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


# asyncio.run(create_and_fill_db())

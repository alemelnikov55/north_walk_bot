"""
Модуль определения запросов к БД
Запросы преимущественно пишутся под конкретную задачу и используются только для нее
Запросы реализованы через методы классов и разделены по месту|таблице применения
"""
import asyncio
from datetime import datetime, timedelta
from typing import List

from sqlalchemy import text, func, update, inspect, Table, Column
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from database.psql_engine import async_session, engine
from database.data_models import Base, WorkoutType, Status, User, Workout, Admin, Registration
from utils.workouts_types import workout_types
from loader import MainSettings


class UserRequest:
    """
    Запросы к таблице users.
    """
    @staticmethod
    async def add_user(user_id: int, name: str, balance: int = 0):
        """
        Добавление пользователя в БД.

        Проверка дублирования реализована средствами SQLAlchemy
        :param user_id:
        :param name:
        :param balance:
        :return: User object
        """
        async with async_session() as session:
            new_user = User(user_id=user_id, name=name, balance=balance, created_at=datetime.now())
            session.add(new_user)

            try:
                await session.commit()
            except IntegrityError as e:
                print(e)
            await session.refresh(new_user)


class WorkoutsRequests:
    """
    Запросы к таблице workouts.
    """

    @staticmethod
    async def create_workout(workout_date: datetime, type_id: int, created_by: int):
        """
        Создание новой тренировки в БД

        :param workout_date:
        :param type_id:
        :param created_by:
        :return:
        """
        async with async_session() as session:
            new_workout = Workout(date=workout_date, type_id=type_id, created_by=created_by)
            session.add(new_workout)
            await session.commit()
            return new_workout

    @staticmethod
    async def show_workouts():
        """
        Запрос всех доступных тренировок.

        Фильтрует тренировки по дате-времени, выдает только тренировки, которые будут
        :return: [Row[tuple[Workout, WorkoutType]]
        """
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
        """
        Запрос тренировки по её ID.

        Фильтрует тренировки по дате-времени, выдает только тренировку с указанным ID
        :param workout_id:
        :return: [tuple[Workout, WorkoutType]]
        """
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
        """
        Удаление тренировки по её ID.

        Проверка наличия тренировки реализована средствами SQLAlchemy
        :param workout_id:
        :return: str
        """
        async with async_session() as session:
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

            return 'Возникла проблема при удалении просьба обратиться к администраору'

    @staticmethod
    async def get_last_week_workouts(day_before: int):
        """
        Запрос прошедших за неделю тренировок.

        Фильтрует тренировки по дате-времени, выдает только тренировки, которые были в течении day_before дней
        :param day_before:
        :return: [Row[tuple[Workout, WorkoutType]]
        """
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


class RegistrationRequests:
    """
    Запросы к таблице registrations.
    """
    # @staticmethod
    # async def is_already_exists(user_id: int, workout_id: int):
    #     """
    #     Запрос на проверку существования записи на тренировку пользователем.
    #
    #     :param user_id:
    #     :param workout_id:
    #     :return: True если регистрация существует
    #     """
    #     async with async_session() as session:
    #         result = await session.execute(
    #             select(Registration)
    #             .filter_by(user_id=user_id,
    #                        workout_id=workout_id,
    #                        status_id=1)
    #         )
    #
    #         existing_registration = result.scalars().first()
    #         if existing_registration:
    #             return True

    @staticmethod
    async def sign_in(user_id: int, workout_id: int):
        """
        Запрос на регистрацию на тренировку пользователем.

        Используется в паре с is_already_exists
        :param user_id:
        :param workout_id:
        """
        # TODO нет проверки выполнения запроса
        async with async_session() as session:
            # проверка есть ли уже такая регистрация со статусом 1
            result = await session.execute(
                select(Registration)
                .filter_by(user_id=user_id,
                           workout_id=workout_id,
                           status_id=1))

            existing_registration = result.scalars().first()
            if existing_registration:
                print('Вы уже записаны на эту тренировку')
                return 'Вы уже записаны на эту тренировку'

            new_registration = Registration(user_id=user_id, workout_id=workout_id)
            session.add(new_registration)

            try:
                await session.commit()
            except Exception as e:
                print("Все пошло не так_________", e)

    # @staticmethod
    # async def change_status(user_id: int, workout_id: int):
    #     """
    #     Запрос на изменение статуса тренировки пользователем в случае повторной попытки записи.
    #
    #     :param workout_id:
    #     :param user_id:
    #     """
    #     async with async_session() as session:
    #         result = await session.execute(
    #             select(Registration)
    #             .filter_by(user_id=user_id, workout_id=workout_id)
    #         )
    #         registration = result.scalars().first()
    #
    #         if registration:
    #             registration.status_id = 1
    #             await session.commit()
    #             print("Статус тренировки изменен.")
    #             return False
    #
    #         print("Ошибка при изменении статуса тренировки.")

    @staticmethod
    async def update_user_status(workout_id: int, user_id: int, status: int, is_payed: bool=True):
        """
        Обновление статуса регистрации|оплаты

        может менять статус оплаты
        :param workout_id: необходим для идентификации
        :param user_id: необходим для идентификации
        :param status: новый статус тренировки
        :param is_payed: новый статус тренировки
        :return: str - если статус успешно изменен возвращает сообщение, что статус изменен
        """
        async with async_session() as session:
            result = await session.execute(
                update(Registration)
                .filter(Registration.workout_id == workout_id,
                        Registration.user_id == user_id,
                        Registration.status_id == 1)  # Запись не отменялась
                .values(status_id=status, is_payed=is_payed)  # TODO при запуске оплаты изменить на False
            )
            await session.commit()
            if result:
                return 'Статус пользователя успешно изменен.'

    @staticmethod
    async def give_up_registration(registration_id: int):
        """
        Отмена записи на тренировку

        :param registration_id: используется для идентификации
        :return: str - сообщение об успешной отмене
        """
        async with async_session() as session:
            await session.execute(
                update(Registration).where(Registration.registration_id == registration_id).values(status_id=4)
            )
            await session.commit()
            return True

    @staticmethod
    async def get_workouts_by_user_id(user_id: int):
        """
        Получение всех записей на тренировки для конкретного пользователя

        :param user_id:
        :return: Workout.date, WorkoutType.type_name, Registration.registration_id
        """
        async with async_session() as session:
            result = await session.execute(select(Workout.date, WorkoutType.type_name, Registration.registration_id)
            .join(Registration, Registration.workout_id == Workout.workout_id)
            .join(WorkoutType, Workout.type_id == WorkoutType.type_id)
            .filter(Registration.user_id == user_id).filter(
                Workout.date >= datetime.now(),
                Registration.status_id == 1)
            .order_by(Workout.date)
            )
            return result.all()

    @staticmethod
    async def get_all_available_workouts():
        """
        Получение всех доступных для записи тренировок

        :return: [tuple[Workout, WorkoutType]]
        """
        async with async_session() as session:
            result = await session.execute(
                select(Workout, WorkoutType)
                .where(Workout.date >= datetime.now())
                .join(WorkoutType).order_by(Workout.date)
            )
            workouts = result.all()
            return workouts

    @staticmethod
    async def count_signs_for_workouts():
        """
        Считает количество зарегистрированных на тренировку пользователей

        :return: [tuple[Workout.workout_id, int]]
        """
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
        """
        Получение Имени пользователя, его ID и информации о тренировке

        Метод для формирования списка пользователей, записанных на тренировку.
        Используется для рассылки и проверки администратору
        :param workout_id:
        :return: [tuple[User.name, User.user_id, Workout.date, WorkoutType.type_name]]
        """
        async with async_session() as session:
            result = await session.execute(
                select(User.name, User.user_id, Workout.date, WorkoutType.type_name)
                .join(Registration, Registration.user_id == User.user_id)
                .join(Workout, Workout.workout_id == Registration.workout_id)
                .join(WorkoutType, WorkoutType.type_id == Workout.type_id)
                .filter(Registration.workout_id == workout_id, Registration.status_id == 1)
            )
            users = result.all()
            return users

    @staticmethod
    async def get_workout_info_by_reg_id(registration_id: int):
        """
        Получение информации о тренировке по registration_id

        :param registration_id:
        :return: [tuple[Workout.date, WorkoutType.type_name]]
        """
        async with async_session() as session:
            result = await session.execute(
                select(Workout.date, WorkoutType.type_name)
                .join(Registration, Registration.workout_id == Workout.workout_id)
                .join(WorkoutType, Workout.type_id == WorkoutType.type_id)
                .filter(Registration.registration_id == registration_id)
            )
            workout_info = result.all()
            return workout_info


class ServiceRequests:
    """
    Класс сервисных запросов PostgreSQL
    """

    @staticmethod
    async def add_workout_types():
        """
        Добавление типов тренировок
        """
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
        """
        Добавление статусов тренировок
        """
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
        """
        Создание таблиц в базе данных PostgreSQL
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def clear_all_data():
        """
        Очистка таблиц от всех данных
        :return:
        """
        async with async_session() as session:
            await session.execute(text(
                # "TRUNCATE TABLE users, admins, workout_types, workouts, statuses, registrations, attendance_history RESTART IDENTITY CASCADE"))
                "TRUNCATE TABLE workouts RESTART IDENTITY CASCADE"))
            await session.commit()

    @staticmethod
    async def fetch_all_from_table(table_name: str):
        """
        Select all для таблицы в аргументе

        :param table_name:
        :return: вся информация из таблицы
        """
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
        """
        Добавление админа в таблицу admins

        :param admin_id:
        :param name:
        :return:
        """
        async with async_session() as session:
            new_admin = Admin(admin_id=admin_id, name=name)
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            print(new_admin)

    @staticmethod
    async def drop_all_base():
        """
        Удаление всех таблиц из БД
        """
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


class StartServiceRequest:
    """
    Класс для запуска работы с базой данных PostgreSQL
    """
    @staticmethod
    async def create_and_fill_db():
        """
        Создание таблиц БД и их заполнение
        """
        await ServiceRequests.create_tables()
        await ServiceRequests.add_workout_types()
        await ServiceRequests.add_statuses_types()
        await StartServiceRequest.check_column_in_tables()
        try:
            await ServiceRequests.add_admin(MainSettings.ADMIN_LIST[0], 'Alexey')
            await ServiceRequests.add_admin(MainSettings.ADMIN_LIST[1], 'Natasha')
        except IntegrityError as e:
            print('\nДанные уже есть в таблице', e)

    @staticmethod
    async def add_column_to_table(conn, table: Table, column: Column):
        """
        Добавляет недостающий столбец в таблицу.
        """
        column_type = column.type.compile(dialect=conn.dialect)
        column_default = f"DEFAULT {column.default}" if column.default is not None else ""
        nullable = "NULL" if column.nullable else "NOT NULL"

        alter_query = f"ALTER TABLE {table.name} ADD COLUMN {column.name} {column_type} {nullable} {column_default}"
        print('Столбец добавлен')
        await conn.execute(text(alter_query))
        await conn.commit()

    @staticmethod
    async def get_existing_columns(table_name, conn):
        """
        Возвращает список имен существующих столбцов в таблице.
        """
        return await conn.run_sync(
            lambda sync_conn: {col["name"] for col in inspect(sync_conn).get_columns(table_name)})

    @staticmethod
    async def check_column_in_tables():
        """
        Проверяет соответствие столбцов БД и столбцов моделей таблиц. Добавляетстолбцы, если в БД их нет
        """
        async with engine.connect() as conn:
            # Получаем список таблиц и их столбцов через sync-инспектор
            for table_name, table in Base.metadata.tables.items():
                # Проверяем, существует ли таблица
                existing_columns = await StartServiceRequest.get_existing_columns(table_name, conn)

                # Сравниваем столбцы и добавляем недостающие
                for column_name, column in table.columns.items():
                    if column_name not in existing_columns:
                        print(f"Добавляем отсутствующий столбец '{column_name}' в таблицу '{table_name}'")
                        await StartServiceRequest.add_column_to_table(conn, table, column)

# asyncio.run(ServiceRequests.clear_all_data())
# print((asyncio.run(WorkoutsRequests.get_type_workout_by_id(1))))
# asyncio.run(RegistrationRequests.get_workout_username_and_id(3))


# asyncio.run(create_and_fill_db())

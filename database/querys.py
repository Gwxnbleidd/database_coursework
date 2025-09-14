from typing import Any
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from database.engine import get_engine
from database.models import Base, Ochered, Rebenok, DoshkolnoeUchrezhdenie, MestaDu, TipDu, Roditel, RoditelRebenka

def get_all_childs(session: Session):
    """
    Ищет всех детей
    :param session:
    :return: заголовки для таблиц и список словарей
    """
    headers = ('ФИО ребенка', 'Дата рождения')

    stmt = select(Rebenok.fio, Rebenok.data_rozhdeniya, Rebenok.id).select_from(Rebenok)

    tmp = session.execute(stmt).all()
    res = [dict(fio=el[0], bd=el[1], id=el[2]) for el in tmp]

    return headers, res


def get_child(session: Session, c_id: int):
    """
    Получает данные о ребенке и о его родителях
    :param session:
    :param c_id: ID ребенка
    :return: словарь ребенка и id,fio его родителей
    """
    stmt = (
        select(Rebenok.id, Rebenok.fio, Rebenok.data_rozhdeniya, Rebenok.adres, Rebenok.kategoriya)
        .where(Rebenok.id == c_id)
    )
    res = session.execute(stmt).one()
    child = dict(id=res[0], fio=res[1], bd=res[2], adres=res[3], category=res[4])

    stmt = (
        select(Roditel.id, Roditel.fio, Roditel.rol)
        .select_from(Roditel)
        .join(RoditelRebenka, RoditelRebenka.roditel_id == Roditel.id)
        .where(RoditelRebenka.rebenok_id == c_id)
        )
    parents = session.execute(stmt).all()
    for parent in parents:
        if parent[2] == 'отец':
            child['f_id'], child['f_fio'], child['f_rol'] = parent[0], parent[1], parent[2]
        else:
            child['m_id'], child['m_fio'], child['m_rol'] = parent[0], parent[1], parent[2]

    return child


def get_childs_attending_DU(session: Session) -> tuple[tuple, list[dict[str, Any]]]:
    """учет детей, посещающих ДУ всех типов
    (ФИО ребенка и его родителей, возраст /дата рождения, сведения о родителях, категория, адрес);
    :param session:
    :return: Заголовки и список словарей, представляющих ребенка и все нужны данные
    """
    headers = ('ФИО ребенка', 'Дата рождения', 'Адрес', 'Категория', 'ФИО родителя',
               'Сведения о родителе', 'Роль родителя')

    stmt = '''
    select reb.fio, reb.data_rozhdeniya, reb.adres, reb.kategoriya,
            rod.fio, rod.svedeniya, rod.rol
    from rebenok as reb
    join roditel_rebenka as rr on rr.rebenok_id = reb.id
    join roditel as rod on rod.id = rr.roditel_id
    join mesta_du as md on reb.id = md.rebenok_id
    '''
    tmp = session.execute(text(stmt)).all()
    return headers, [dict(fio=el[0], bd=el[1], address=el[2], category=el[3], par_fio=el[4],
                 par_info=el[5], rol=el[6]) for el in tmp]


def get_childs_in_queue(session: Session) -> tuple[tuple, list[dict[str, Any]]]:
    """учет детей, стоящих в очереди в ДУ;

    :param session:
    :return: Заголовки и список словарей, представляющих ребенка и все нужны данные
    """
    headers = ('ФИО', 'Дата рождения', 'ДУ, в которое стоит в очереди', 'Приоритет')

    stmt = '''
    select r.fio, r.data_rozhdeniya, du.nazvanie, o.prioritet
    from rebenok as r
    join ochered as o on o.rebenok_id = r.id
    join doshkolnoe_uchregdenie as du on o.du_id = du.id  
    '''

    res = session.execute(text(stmt)).all()
    return headers, [dict(fio=el[0], bd=el[1], du_name=el[2], priority=el[3]) for el in res]

def get_children_need_du(session: Session, age: int = None, category: str = None):
    """
    составление списка детей, нуждающихся в ДУ (по возрасту, категории);
    :param session:
    :return: список словарей с ИД и ФИО детей
    """
    stmt = ''' select id, fio 
                from rebenok
                where id not in (select rebenok_id from mesta_du where rebenok_id is not null)
    '''
    if age:
        stmt += f' and EXTRACT(YEAR FROM data_rozhdeniya) = 2024-{age}'
    if category:
        stmt += f" and kategoriya = '{category}'"

    res = session.execute(text(stmt)).all()
    return [dict(id=el[0], fio=el[1]) for el in res]

def update_info_about_children(session: Session, c_id: int, m_id: int, f_id: int, data):
    """Изменить данные о ребенке

    :param session:
    :param c_id: ID ребенка
    :param m_id: ID матери
    :param f_id: ID отца
    :param data: Новые данные
    :return:
    """
    child = dict(fio=data.get('fio'), data_rozhdeniya=data.get('data_rozhdeniya'), adres=data.get('adres'),
                 kategoriya=data.get('kategoriya'))
    m_info = dict(roditel_id=m_id, rebenok_id=c_id)
    f_info = dict(roditel_id=f_id, rebenok_id=c_id)

    session.execute(update(Rebenok).where(Rebenok.id==c_id).values(**child))
    session.execute(update(RoditelRebenka).where(RoditelRebenka.roditel_id==m_id).values(**m_info))
    session.execute(update(RoditelRebenka).where(RoditelRebenka.roditel_id==f_id).values(**f_info))

    session.commit()

def get_children_from_du(session: Session, du_id: int) -> list:
    """составление списка детей указанного ДУ.
    :param session:
    :param du_id: ID нужного ДУ
    :return: Список ФИО подходящих детей
    """
    stmt = (select(Rebenok.fio)
    .select_from(Rebenok)
    .join(MestaDu, MestaDu.rebenok_id == Rebenok.id)
    .join(DoshkolnoeUchrezhdenie, DoshkolnoeUchrezhdenie.id == MestaDu.du_id)
    .where(DoshkolnoeUchrezhdenie.id == du_id))
    
    res = session.execute(stmt).all()
    return [el[0] for el in res]


def get_all_DU(session: Session):
    """
    Учет дошкольных учреждений города
    :param session:
    :return: Заголовки для таблицы и данные
    """
    headers = ('ID', 'Название', 'Назначение', 'Количество мест', 'Стоимость', 'Тип')

    stmt = (select(DoshkolnoeUchrezhdenie.nazvanie, DoshkolnoeUchrezhdenie.naznachenie,
                   DoshkolnoeUchrezhdenie.kolichestvo_mest, DoshkolnoeUchrezhdenie.stoimost,
                   TipDu.nazvanie, DoshkolnoeUchrezhdenie.id).select_from(DoshkolnoeUchrezhdenie)
            .join(TipDu, TipDu.id == DoshkolnoeUchrezhdenie.tip_id)
            )
    res = session.execute(stmt).all()
    return headers, [dict(du_id=el[5], name=el[0], target=el[1], count_place=el[2], price=el[3],
                          type=el[4]) for el in res]


def get_du_with_free_places(session: Session, vozrast: int) -> list[str]:
    """составление списка ДУ, в которых есть свободные места для детей заданного возраста;
    :param session:
    :param vozrast:
    :return: Список уникальных названий ДУ
    """
    stmt = (select(DoshkolnoeUchrezhdenie.nazvanie.distinct())
            .select_from(DoshkolnoeUchrezhdenie)
            .join(MestaDu, MestaDu.du_id == DoshkolnoeUchrezhdenie.id)
            .where(MestaDu.vozrast == vozrast)
            .where(MestaDu.zanyatost == False))

    res = session.execute(stmt).all()
    return [el[0] for el in res]


def get_all_parents(session: Session):
    """Функция возвращает всех родителей

    :param session:
    :return: список родителей
    """
    stmt = select(Roditel.id, Roditel.fio, Roditel.rol)
    res = session.execute(stmt).all()
    return [dict(id=el[0], fio=el[1], rol=el[2]) for el in res]

# def create_all():
#     engine = get_engine()
#     Base.metadata.drop_all(engine)
#     Base.metadata.create_all(engine)


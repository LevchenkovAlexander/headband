import logging
import hashlib
import uuid



from aiogram.types import User, Chat
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import AppointmentModel, MasterModel, Week, UserModel, \
    OrganizationModel, PriceModel, AdminModel, SpecialOffersModel, GuidesModel

from backend.database.requests import AppointmentCreateRequest, MasterCreateRequest, UserCreateRequest, \
    OrganizationCreateRequest, AdminCreateRequest, PriceCreateRequest, OrganizationUpdateRequest, PriceUpdateRequest, \
    AdminUpdateRequest, OfferCreateRequest, OfferUpdateRequest
from backend.database.responses import AppointmentResponse, AdminResponseOrganizations, AdminResponseMasters, \
    AdminResponseSpecialOffers, AdminResponseInfo
from backend.database.time_helpers import _get_weekday_caps, _time_to_timedelta, _timedelta_to_int_minutes, \
    _get_week_dates, _timedelta_to_time
from datetime import timedelta

from backend.telegram_bot import BOT_URL


async def auth_by_email(email: str, password: str, session: AsyncSession):
    hash_pass = hashlib.sha256(password.encode()).hexdigest()
    status, adm_id = await AdminModel.check_by_email_pass(session=session, email=email, password=hash_pass)
    return status, adm_id

#TODO сделать токен авторизацию
#async def auth_by_token(token: str, session: AsyncSession):
    #hash_pass = hashlib.sha256(password.encode()).hexdigest()
    #status, adm_id = await AdminModel.check_by_email_pass(session=session, email=email, password=hash_pass)
    #return status, adm_id

async def get_organization_filter(user_id: int, session: AsyncSession):
    #TODO получаем все организации из database/init.py
    #organizations = get_func(user_id)
    response_list = []
    for organization in organizations:
        resp = {}
        resp["id"] = organization.id
        resp["name"] = organization.name
        response_list.append(resp)
    if len(response_list) == 0:
        resp = {}
        resp["id"] = uuid.RFC_4122
        resp["name"] = "null_name"
        response_list.append(resp)
        status = "no organizations"
        return status, response_list
    status = "success"
    return status, response_list

async def get_guides(id: int, session: AsyncSession):
    cats = MasterModel.get_cats_by_chat_id(id=id, session=session)
    categories_final = set()
    for cat in cats:
        c = cat.split(" ")
        for t in c:
            categories_final.add(t[0])
    g_fitable = GuidesModel.get_guides(list(categories_final), session=session)
    g_all = GuidesModel.get_guides_all(session=session)
    g_fit_resp = []
    g_all_resp = []
    for g in g_fitable:
        resp = {}
        resp["id"] = g.id
        resp["name"] = g.name
        resp["category"] = g.category
        g_fit_resp.append(resp)
    for g in g_all:
        resp = {}
        resp["id"] = g.id
        resp["name"] = g.name
        resp["category"] = g.category
        g_all_resp.append(resp)
    return "success", g_fit_resp, g_all_resp

async def get_steps(guide_id: uuid.UUID, session: AsyncSession):
    return await GuidesModel.get_by_id(id=guide_id, session=session)

async def check_admin_email(email: str, session: AsyncSession):
    return await AdminModel.check_by_email(session=session, email=email)

async def get_possible_start_time(master_id, date, price_id, session: AsyncSession):
    """Получение возможного времени для записи"""
    master = await MasterModel.get_master_by_id(session = session, id=master_id)
    days_off = master.day_off
    weekday_name = _get_weekday_caps(date)
    weekday = Week[weekday_name].value

    if weekday in days_off:
        return None, "day off"

    else:
        id = []
        id.append(master_id)
        #так как здесь мы работаем в рамках одной организации,
        #нам не за чем знать его записей в других
        appointments, status = await AppointmentModel.get_by_master_and_date(session = session, master_ids=id, date=date)
        day_start = master.working_day_start
        day_end = master.working_day_end
        start_time = []
        end_time = []

        end_time.append(_time_to_timedelta(day_start))
        for appointment in appointments:
            start_time.append(_time_to_timedelta(appointment.start_time))
            end_time.append(_time_to_timedelta(appointment.end_time))
        start_time.append(_time_to_timedelta(day_end))

        price = await PriceModel.get_price_by_id(session = session, id=price_id)
        appointment_approx_time = price.approximate_time
        possible_time_for_start = 0
        possible_starts = []
        ten_minutes_gap = timedelta(minutes=10)
        for i in range(len(start_time)):
            gap = start_time[i]-end_time[i]
            if gap>=_time_to_timedelta(appointment_approx_time):
                free_minutes = gap-_time_to_timedelta(appointment_approx_time)
                k = _timedelta_to_int_minutes(free_minutes)//10
                possible_time_for_start+=(k+1)
                for j in range(k+1):
                    possible_starts.append(_timedelta_to_time(end_time[i]+ten_minutes_gap*j))
        if possible_time_for_start == 0:
            return None, "no time for app"
        else:
            return possible_starts, "success"

async def get_appointments_by_date(master_chat_id, date, session: AsyncSession):
    ids = await MasterModel.get_ids_by_chat_id(session=session, chat_id=master_chat_id)
    appointments, flag = await AppointmentModel.get_by_master_and_date(session = session, master_ids=ids, date=date)
    adresses = []
    names = []
    for a in appointments:
        price_id = a.price_id
        name = await PriceModel.get_name_by_id(session=session, id=price_id)
        org_id = await PriceModel.get_org_id_by_id(session=session, id = price_id)
        address = await OrganizationModel.get_address_by_id(session=session, id=org_id)
        adresses.append(address)
        names.append(name)
    if flag:
        return appointments, len(appointments), "success", adresses, names
    return [], 0, "no appointments today", [], []

async def get_admin_info(id, session: AsyncSession):
    admin = await AdminModel.get_by_id(session=session, id=id)

    #Получаем организации
    organizations = await OrganizationModel.get_organizations_by_adm_id_full(session=session, adm_id=id)
    org_ids = [org.id for org in organizations]
    organizations_response = []
    users_num = 0
    masters_response = []
    offers_response = []
    master_chats = []
    if len(organizations)>0:
        for organization in organizations:
            org_response = AdminResponseOrganizations(
                id=organization.id,
                status="success",
                tg_master=BOT_URL + organization.unique_code_master,
                tg_user=BOT_URL + organization.unique_code_user,
                name=organization.name,
                address=organization.address,
                categories=organization.categories
            )
            organizations_response.append(org_response.model_dump())
        masters = await MasterModel.get_masters_by_org_ids_full(session=session, org_ids=org_ids)
        master_chats = [master.chat_id for master in masters]
        if len(masters) > 0:
            for master in masters:
                master_response = AdminResponseMasters(
                    id=master.id,
                    status="success",
                    username=master.username,
                    full_name=master.full_name,
                    working_day_start=master.working_day_start,
                    working_day_end=master.working_day_end,
                    day_off=master.day_off,
                    categories=master.categories
                )
                masters_response.append(master_response.model_dump())
        else:
            masters_response.append({"status": "no elements"})

        offers = await SpecialOffersModel.get_offers_by_org_ids_full(session=session, org_ids=org_ids)
        if len(offers) > 0:
            for offer in offers:
                offer_response = AdminResponseSpecialOffers(
                    id=offer.id,
                    status="success",
                    organization_id=offer.organization_id,
                    name=offer.name,
                    deadline_start=offer.deadline_start,
                    deadline_end=offer.deadline_end
                )
                offers_response.append(offer_response.model_dump())
        else:
            offers_response.append({"status": "no elements"})
        users_num += await UserModel.get_users_num_by_org_ids(session=session, org_ids=org_ids)

    else:
        organizations_response.append({"status": "no elements"})
        masters_response.append({"status": "no elements"})
        offers_response.append({"status": "no elements"})


    response = AdminResponseInfo(
        id=admin.id,
        status="success",
        email=admin.email,
        end_of_subscription=admin.end_of_subscription,
        num_organizations=len(organizations),
        num_masters=len(set(master_chats)),
        num_users=users_num,
        organizations=organizations_response,
        masters=masters_response,
        offers=offers_response
    )
    return response

async def get_appointments_by_user(chat_id, session: AsyncSession):
    user_ids = await UserModel.get_users_by_chat_id(session=session, chat_id=chat_id)
    appointments, flag = await AppointmentModel.get_by_user(session=session, user_ids=user_ids)
    response_list = []
    for a in appointments:
        aresponse = AppointmentResponse.model_validate(a).model_dump()
        price_id = a.price_id
        name = await PriceModel.get_name_by_id(session=session, id=price_id)
        org_id = await PriceModel.get_org_id_by_id(session=session, id=price_id)
        address = await OrganizationModel.get_address_by_id(session=session, id=org_id)
        aresponse["address"] = address
        aresponse["service_name"] = name
        response_list.append(aresponse)
    return response_list

async def get_masters_by_category_and_user(chat_id, category, session, filter = None):
    if filter == None:
        org_ids = await UserModel.get_organizations_by_chat_id(chat_id=chat_id, session=session)
        masters = await MasterModel.get_masters_by_org_ids_full(org_ids=org_ids, session=session)
        response = []
        for master in masters:
            mresponse = {}
            master_category = (master.categories).split(" ")
            for c in master_category:
                if int(c[0])==int(category):
                    subcategories = c[1:]
                    mresponse["subcategories"] = subcategories
                    mresponse["name"] = master.full_name
                    address = await OrganizationModel.get_address_by_id(id=master.organization_id, session=session)
                    mresponse["address"] = address
                    mresponse["id"] = master.id
                    response.append(mresponse)
        return response, 'success'
    else:
        masters = await MasterModel.get_masters_by_org_ids_full(org_ids=filter, session=session)
        response = []
        for master in masters:
            mresponse = {}
            master_category = (master.categories).split(" ")
            for c in master_category:
                if c[0] == category:
                    subcategories = c[1:]
                    mresponse["subcategories"] = subcategories
                    mresponse["name"] = master.full_name
                    address = OrganizationModel.get_address_by_id(id=master.organization_id, session=session)
                    mresponse["address"] = address
                    mresponse["id"] = master.id
                    response.append(mresponse)
        return response, 'success'


async def get_categories_by_user(chat_id, session: AsyncSession):
    org_ids = await UserModel.get_organizations_by_chat_id(session=session, chat_id=chat_id)
    categories = await OrganizationModel.get_categories_by_org_ids(session=session, ids = org_ids)
    response = []
    for category in categories:
        cat_arr = category.split(" ")
        for c in cat_arr:
            response.append(c[0])
    response = sorted(list(set(response)))
    return "".join(response)
async def get_week_timetable(master_id, date, session: AsyncSession):
    week_list = _get_week_dates(date)
    week_appointments = []
    for day in week_list:
        appointments, count, status, addresses, names = await get_appointments_by_date(master_id, day, session)
        a = []
        for i, appointment in enumerate(appointments):
            aresponse = AppointmentResponse.model_validate(appointment).model_dump()
            aresponse["address"] = addresses[i]
            aresponse["service_name"] = names[i]
            a.append(aresponse)
        week_appointments.append(a)
    return week_appointments, "success"

async def create_appointment(appointment_request: AppointmentCreateRequest, session: AsyncSession):
    price = await PriceModel.get_price_by_id(session = session, id=appointment_request.price_id)
    appointment_dict = appointment_request.model_dump()
    appointment_dict["end_time"] = _timedelta_to_time(_time_to_timedelta(appointment_dict["start_time"])+_time_to_timedelta(price.approximate_time))
    status = await AppointmentModel.create(session = session, data=appointment_dict)
    return status

async def update_master(update_data, session: AsyncSession):
    master_to_upd = update_data.model_dump(exclude_unset=True)
    status = await MasterModel.update(session=session, update_data=master_to_upd)
    return status

async def cancel_appointment(appointment_id, session: AsyncSession):
    status = await AppointmentModel.delete(session = session, id=appointment_id)
    return status

async def create_master(user: User, chat: Chat, organization_id: uuid.UUID, session: AsyncSession):
    organization = await OrganizationModel.get_org_by_id(session=session, id = organization_id)
    master = MasterCreateRequest(chat_id=chat.id,
                                 organization_id=organization_id,
                                 username=user.username,
                                 working_day_start=organization.day_start_template,
                                 working_day_end = organization.day_end_template,
                                 day_off = organization.day_off)
    if await MasterModel.create(session=session, data=master.model_dump()):
        return "success"
    return "unable to create"

async def create_user(user: User, chat: Chat, organization_id: uuid.UUID, session: AsyncSession):
    user = UserCreateRequest(chat_id=chat.id,
                             organization_id=organization_id,
                             username=user.username)
    if await UserModel.create(session=session, data=user.model_dump()):
        return "success"
    return "unable to create"

async def create_organization(org_request: OrganizationCreateRequest, session: AsyncSession):
    org_dict = org_request.model_dump()
    unique_code = str(uuid.uuid4())
    hash_uni = hashlib.sha256(unique_code.encode()).hexdigest()
    org_dict["unique_code_master"] = hash_uni[0:32]
    org_dict["unique_code_user"] = hash_uni[32:64]
    status, org_id = await OrganizationModel.create(session=session, data=org_dict)
    return status, hash_uni[0:32], hash_uni[32:64], org_id

async def update_organization(update_data: OrganizationUpdateRequest, session: AsyncSession):
    org_to_upd = update_data.model_dump(exclude_unset=True)
    status = await OrganizationModel.update(session=session, update_data=org_to_upd)
    return status

async def delete_organization(delete_id: uuid.UUID, session: AsyncSession):
    org = await session.get(OrganizationModel, delete_id)
    if not org:
        return "organization not found"
    await session.delete(org)
    await session.commit()
    return "success"

"""admin fetches"""
async def update_admin(update_data: AdminUpdateRequest, session: AsyncSession):
    org_to_upd = update_data.model_dump(exclude_unset=True)
    obj_id = org_to_upd.pop("id")
    status = await AdminModel.update(session=session, obj_id=obj_id, update_data=org_to_upd)
    return status

async def create_admin(adm_request: AdminCreateRequest, session: AsyncSession):
    admin_dict = adm_request.model_dump()
    if adm_request.password != None:
        hash_pass = hashlib.sha256(adm_request.password.encode()).hexdigest()
        admin_dict["password"] = hash_pass
    adm_id = await AdminModel.create(session=session, data=admin_dict)
    return "success", adm_id


"""price fetches"""
async def create_price_position(price_position: PriceCreateRequest, session: AsyncSession):
    price_dict = price_position.model_dump()
    status, id = await PriceModel.create(session=session, data=price_dict)
    return status, id


async def update_price(update_data: PriceUpdateRequest, session: AsyncSession):
    org_to_upd = update_data.model_dump(exclude_unset=True)
    status = await PriceModel.update(session=session, update_data=org_to_upd)
    return status

async def delete_price(delete_id: uuid.UUID, session: AsyncSession):
    price = await session.get(PriceModel, delete_id)
    if not price:
        return "price not found"

    # Удалит каскадно appointments и individual_prices
    await session.delete(price)
    await session.commit()
    return "success"

async def create_offer(offer: OfferCreateRequest, session: AsyncSession):
    price_dict = offer.model_dump()
    status, id = await SpecialOffersModel.create(session=session, data=price_dict)
    return status, id



async def update_offer(update_data: OfferUpdateRequest, session: AsyncSession):
    off_to_upd = update_data.model_dump(exclude_unset=True)
    status = await SpecialOffersModel.update(session=session, update_data=off_to_upd)
    return status
async def delete_offer(delete_id: uuid.UUID, session: AsyncSession):
    status = await SpecialOffersModel.delete(session=session, id=delete_id)
    return status


async def user_master_deeplink(args: str, session: AsyncSession):
    master_res, master_status = await OrganizationModel.get_by_master_unique(session=session, unique_code=args)
    user_res, user_status = await OrganizationModel.get_by_user_unique(session=session, unique_code=args)
    logging.info(f"user_res {user_res}")
    logging.info(f"master_res {master_res}")
    if master_status:
        return 0, master_res
    elif user_status:
        return 1, user_res
    else:
        return 2, None




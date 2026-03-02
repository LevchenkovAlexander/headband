from enum import Enum


class ServiceCategoryToNum(Enum):
    HAIRSTYLE = "1"
    COSMETOLOGY_SKINCARE = "2"
    MANICURE_PEDICURE = "3"
    BROWS_LASHES = "4"
    DEPILATION_EPILATION = "5"
    MAKEUP = "6"
    CONSULTATIONS = "7"
    TANNING = "8"
    OTHER = "9"

class ServiceCategoryToRus(Enum):
    HAIRSTYLE = "Парикмахерские услуги"
    COSMETOLOGY_SKINCARE = "Косметология & Skincare"
    MANICURE_PEDICURE = "Маникюр и педикюор"
    BROWS_LASHES = "Брови и ресницы"
    DEPILATION_EPILATION = "Депиляция и эпиляция"
    MAKEUP = "Макияж"
    TANNING = "Солярий"
    FULLMAKEUP_CONSULTATIONS = "Консультации"
    OTHER = "Другое"

"""Service enums"""
class HairstyleCategoryToNum(Enum):
    WOMEN = "1"
    MEN = "2"
    CHILDREN = "3"
    COLORING = "4"
    STYLING_HAIRSTYLING = "5"
    HAIR_TREATMENT_CARE = "6"
    OTHER = "7"

class HairstyleCategoryToRus(Enum):
    WOMEN = "Женские стрижки"
    MEN = "Мужские стрижки"
    CHILDREN = "Детские стрижки"
    COLORING = "Окрашивание"
    STYLING_HAIRSTYLING = "Укладка и прически"
    HAIR_TREATMENT_CARE = "Лечение и уход за волосами"
    OTHER = "Другое"

class CosmetologySkincareCategoryToNum(Enum):
    FACIAL_CLEANSING = "1"
    INJECTABLE_TREATMENTS = "2"
    HARDWARE_COSMETOLOGY = "3"
    FACIAL_TREATMENTS = "4"
    SKINCARE_CONSULTATIONS = "5"

class CosmetologySkincareCategoryToRus(Enum):
    FACIAL_CLEANSING = "Чистка лица"
    INJECTABLE_TREATMENTS = "Инъекционная косметология"
    HARDWARE_COSMETOLOGY = "Аппаратная косметология"
    FACIAL_TREATMENTS = "Уходовые процедуры"
    SKINCARE_CONSULTATIONS = "Консультация косметолога"

class ManicurePedicureCategoryToNum(Enum):
    CLASSIC = "1"
    HARDWARE = "2"
    GET_POLISH_APPLICATION = "3"
    NAIL_EXTENSION = "4"
    NAIL_ART_DESIGN = "5"
    MEN = "6"
    THERAPEUTIC_PODOLOGIC = "7"

class ManicurePedicureCategoryToRus(Enum):
    CLASSIC = "Классический (обрезной)"
    HARDWARE = "Аппаратный"
    GET_POLISH_APPLICATION = "Покрытие гель-лаком"
    NAIL_EXTENSION = "Наращивание ногтей"
    NAIL_ART_DESIGN = "Дизайн ногтей"
    MEN = "Мужской"
    THERAPEUTIC_PODOLOGIC = "Лечебный педикюр"

class BrowsLashesCategoryToNum(Enum):
    BROW_SHAPING_TINTING = "1"
    BROW_LASH_LAMINATION = "2"
    EYELASH_EXTENSION = "3"
    EYELASH_TINTING = "4"

class BrowsLashesCategoryToRus(Enum):
    BROW_SHAPING_TINTING = "Коррекция и окрашивание бровей"
    BROW_LASH_LAMINATION = "Ламинирование бровей и ресниц"
    EYELASH_EXTENSION = "Наращивание ресниц"
    EYELASH_TINTING = "Окрашивание ресниц"

class HairRemovalCategoryToNum(Enum):
    WAXING = "1"
    SUGARING = "2"
    LASER_HAIR_REMOVAL = "3"
    ELECTROLYSIS = "4"

class HairRemovalCategoryToRus(Enum):
    WAXING = "Восковая депиляция"
    SUGARING = "Шугаринг"
    LASER_HAIR_REMOVAL = "Лазерная эпиляция"
    ELECTROLYSIS = "Электроэпиляция"

class MakeupCategoryToNum(Enum):
    DAY_EVENING_MAKEUP = "1"
    WEDDING_MAKEUP = "2"
    MAKEUP_LESSONS = "3"

class MakeupCategoryToRus(Enum):
    DAY_EVENING_MAKEUP = "Дневной и вечерний макияж"
    WEDDING_MAKEUP = "Свадебный макияж"
    MAKEUP_LESSONS = "Обучение"

class TanningToNum(Enum):
    TANNING = "1"

class TanningToRus(Enum):
    TANNING = "Солярий"

class BeautyConsultingCategoryToNum(Enum):
    PERSONAL_STYLE = "1"
    HAIRSTYLE_COLOR_CONSULTATION = "2"
    SKINCARE_PRODUCT = "3"
    BEAUTY_BOX_CURATION = "4"

class BeautyConsultingCategoryToRus(Enum):
    PERSONAL_STYLE = "Персональная консультация по стилю"
    HAIRSTYLE_COLOR_CONSULTATION = "Подбор прически или окрашивания"
    SKINCARE_PRODUCT = "Подбор уходовой косметики"
    BEAUTY_BOX_CURATION = "Создание beauty-бокса"

class OtherToNum(Enum):
    OTHER = "1"

class OtherToRus(Enum):
    OTHER = "Другое"

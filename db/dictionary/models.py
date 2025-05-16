from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as label
import unicodedata

from db.base_model import BaseModel


def is_bmp_hanja(c: str) -> bool:
    n = ord(c)
    return 0x3400 <= n <= 0x4DBF or 0x4E00 <= n <= 0x9FFF or 0xF900 <= n <= 0xFA6D or 0xFA70 <= n <= 0xFAD9


def is_sip_hanja(c: str) -> bool:
    n = ord(c)
    return (0x20000 <= n <= 0x2A6DF or 0x2A700 <= n <= 0x2B739 or 0x2B740 <= n <= 0x2B81D or 0x2B820 <= n <= 0x2CEA1
            or 0x2CEB0 <= n <= 0x2EBE0 or 0x2EBF0 <= n <= 0x2EE5D or 0x2F800 <= n <= 0x2FA1D)


def is_tip_hanja(c: str) -> bool:
    n = ord(c)
    return 0x30000 <= n <= 0x3134A or 0x31350 <= n <= 0x323AF


def is_hanja(c: str) -> bool:
    return is_bmp_hanja(c) or is_sip_hanja(c) or is_tip_hanja(c)


def validate_hanja_field(s: str):
    if not all((c in '/▽' or is_hanja(c) for c in s)):
        raise ValidationError(
            label("%(value)s contains non-hanja character(s)."),
            params={"value": s},
        )
    if unicodedata.normalize('NFC', s) != s:
        raise ValidationError(
            label("%(value)s contains non-normalized character(s)."),
            params={"value": s},
        )


def is_hangeul_jamo(c: str) -> bool:
    n = ord(c)
    return 0x3131 <= n <= 0x3163


def is_hangeul_composite(c: str) -> bool:
    n = ord(c)
    return 0xAC00 <= n <= 0xD7A3


def is_hangeul(c: str) -> bool:
    return is_hangeul_composite(c) or is_hangeul_jamo(c)


def validate_hangeul_field(s: str):
    if not all((c in ' ㆍ' or is_hangeul(c) for c in s)):
        raise ValidationError(
            label("%(value)s contains non-hangeul character(s)."),
            params={"value": s},
        )


class Hanja(BaseModel):
    letter = models.CharField(max_length=1, primary_key=True, null=False, validators=[validate_hanja_field])


class KoreanWordCategory(BaseModel):
    category = models.CharField(primary_key=True, null=False, max_length=10)


class KoreanWord(BaseModel):
    class WordUnit(models.IntegerChoices):
        GWANYONGGU = 0, '관용구'
        GU = 1, '구'
        DANEO = 2, '단어'
        SOKDAM = 3, '속담'

    class WordType(models.IntegerChoices):
        NONE = -1, '-'
        GOYUEO = 0, '고유어'
        OIRAEEO = 1, '외래어'
        HANJAEO = 2, '한자어'
        HONJONGEO = 3, '혼종어'

    id = models.IntegerField(primary_key=True, null=False)
    word = models.TextField(null=False, db_index=True, validators=[validate_hangeul_field])
    unit = models.SmallIntegerField(null=False, db_index=True, choices=WordUnit)
    word_type = models.SmallIntegerField(null=False, db_index=True, choices=WordType, default=WordType.NONE)
    hanja = models.TextField(validators=[validate_hanja_field])


class KoreanWordSense(BaseModel):
    class WordPos(models.IntegerChoices):
        NONE = -1, '품사 없음'
        GAMTANSA = 0, '감탄사'
        GWANHYEONGSA = 1, '관형사'
        GU = 2, '구'
        DAEMYEONGSA = 3, '대명사'
        DONGSA = 4, '동사'
        MYEONGSA = 5, '명사'
        BOJO_DONGSA = 6, '보조 동사'
        BOJO_HYEONGYONGSA = 7, '보조 형용사'
        BUSA = 8, '부사'
        SUSA = 9, '수사'
        EOMI = 10, '어미'
        UIJON_MYEONGSA = 11, '의존 명사'
        JEOPSA = 12, '접사'
        JOSA = 13, '조사'
        HYEONGYONGSA = 14, '형용사'

    id = models.IntegerField(primary_key=True, null=False)
    word = models.ForeignKey(KoreanWord, on_delete=models.CASCADE, related_name='senses', null=False)
    pos = models.SmallIntegerField(null=False, db_index=True, choices=WordPos, default=WordPos.NONE)
    categories = models.ManyToManyField(KoreanWordCategory, related_name='senses')
    definition = models.TextField(null=False)
    # empty if equal to definition.
    # elaborates its references to words/senses with w\d+ and s\d+ respectively with no whitespace in between.
    definition_original = models.TextField(null=False)


class HanjaUsage(BaseModel):
    pk = models.CompositePrimaryKey('hanja_id', 'word_id')
    hanja = models.ForeignKey(Hanja, on_delete=models.CASCADE, related_name='usages', null=False)
    word = models.ForeignKey(KoreanWord, on_delete=models.CASCADE, related_name='hanjas', null=False)

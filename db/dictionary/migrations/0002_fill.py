from django.db import migrations, models
import xml.etree.ElementTree as Xml
import re
import unicodedata

from db.dictionary.models import KoreanWord as KW
from db.dictionary.models import KoreanWordSense as KWS


def fill_category(apps, schema_editor):
    categories = ['가톨릭', '건설', '경영', '경제', '고유명 일반', '공업', '공예', '공학 일반', '광업', '교육', '교통', '군사', '기계', '기독교', '농업',
                  '동물', '매체', '무용', '문학', '물리', '미술', '민속', '법률', '보건 일반', '복식', '복지', '불교', '사회 일반', '산업 일반', '생명',
                  '서비스업', '수산업', '수의', '수학', '식물', '식품', '심리', '약학', '언어', '역사', '연기', '영상', '예체능 일반', '음악', '의학',
                  '인명', '인문 일반', '임업', '자연 일반', '재료', '전기·전자', '정보·통신', '정치', '종교 일반', '지구', '지리', '지명', '책명', '천문',
                  '천연자원', '철학', '체육', '한의', '해양', '행정', '화학', '환경']

    KoreanWordCategory = apps.get_model("dictionary", "KoreanWordCategory")
    for cat in categories:
        KoreanWordCategory(category=cat).save()


def fix_korean_word(word_no: int, word: str, word_unit: KW.WordUnit, word_type: KW.WordType, hanja_write: str) \
        -> (str, KW.WordUnit, KW.WordType, str):
    new_word = ''.join([c for c in word if c not in '0123456789-']).replace('^', ' ')

    hanja_write = (
        unicodedata.normalize('NFC', hanja_write)
        .replace('∇', '▽')  # U+2207 -> U+25BD
    )

    match word_no:
        # Remove whitespace
        # 518534 - 경주^감은사지^동서^삼층^석탑: 慶州感恩寺址東西 三層石塔
        # 518541 - 김천^갈항사지^동서^삼층^석탑: 金泉葛項寺址東西 三層石塔
        # 518545 - 전원주^흥법사지^염거^화상^탑: 傳原州興法寺址 廉居和尙塔
        # 518550 - 제천^사자^빈신사지^사사자^구층^석탑: 堤川 獅子頻迅寺址四獅子九層石塔
        case 518534 | 518541 | 518545 | 518550:
            hanja_write = hanja_write.replace(' ', '')

        # 41119 - 권-업02: 權<EQU>𢢜</EQU>
        # 42514 - 권-성: 權<EQU>𢜫</EQU>
        # 61958 - 남삼: <EQU>䰐</EQU>鬖
        # 61959 - 남삼-하다: <EQU>䰐</EQU>鬖
        # 63247 - 내경-부: 內<EQU>𢈴</EQU>部
        case 41119 | 42514 | 61958 | 61959 | 63247:
            hanja_write = hanja_write.replace('<EQU>', '').replace('</EQU>', '')

        # 175157 - 선14: <hanja>12855_1</hanja>
        case 175157:
            hanja_write = '膳'

        # 509965 - 대추-색: <hanja>13020_1</hanja>
        case 509965:
            hanja_write = '色'

        # 124945 - 문화의^달: 文化의달
        case 124945:
            word_type = KW.WordType.HONJONGEO
            hanja_write = '文化'

        # 23828 - 고식05: 苦<equ>&#x27139;</equ>
        case 23828:
            hanja_write = '苦𧄹'

        # 233937 - 영정06: 䴇<equ>&#x29F9A;</equ>
        case 233937:
            hanja_write = '䴇𩾚'

        # 270804 - 이-후03: 李<equ>&#x2AEF6;</equ>
        case 270804:
            hanja_write = '李𪻶'

        # 379699 - 활고자02: 活<equ>&#x2B0DC;</equ>子
        case 379699:
            hanja_write = '活𫃜子'

        # <equ>&#x9396;</equ> -> 鎖
        case 3077 | 5248 | 10166 | 10167 | 14663 | 20739 | 20960 | 21493 | 23169 | 23170 | 25637 | 28167 | 31402 | \
             32033 | 32034 | 40376 | 44713 | 47100 | 47101 | 69808 | 69809 | 79227 | 79965 | 114711 | 120767 | \
             120829 | 122674 | 127258 | 141842 | 150151 | 150152 | 150153 | 151278 | 151279 | 151280 | 151281 | \
             151306 | 151307 | 151596 | 151597 | 151598 | 170274 | 174937 | 178166 | 181299 | 185834 | 190710 | \
             191015 | 191046 | 191198 | 191200 | 191212 | 191617 | 191624 | 191625 | 191649 | 191651 | 191652 | \
             192229 | 192230 | 195972 | 195973 | 195977 | 195978 | 195994 | 195995 | 195999 | 196266 | 196720 | \
             196884 | 196885 | 196886 | 196991 | 196992 | 196994 | 197007 | 197012 | 197013 | 203843 | 203844 | \
             211774 | 229979 | 232855 | 232856 | 232857 | 232858 | 232859 | 232860 | 232861 | 232862 | 232863 | \
             236972 | 236973 | 236974 | 236976 | 236978 | 236979 | 236980 | 236981 | 239518 | 241225 | 251461 | \
             263266 | 266612 | 268529 | 271391 | 284709 | 285116 | 292945 | 293745 | 302591 | 302592 | 314939 | \
             325924 | 334458 | 334459 | 347113 | 351974 | 351975 | 351976 | 351977 | 351978 | 351979 | 351980 | \
             351981 | 351982 | 351984 | 351986 | 355504 | 355505 | 355775 | 355776 | 355777 | 357167 | 361834 | \
             363718 | 364504 | 367553 | 368366 | 368747 | 372684 | 379298 | 379376 | 384220 | 394832 | 402315 | \
             423670 | 431654 | 432394 | 434976 | 434986 | 434987 | 434988 | 434989 | 445360 | 445590 | 445594 | \
             447823 | 447824 | 447836 | 448017 | 448197 | 448198 | 449802 | 451750 | 457888 | 460058 | 460228 | \
             462922 | 462923 | 462924 | 465826 | 466191 | 474757 | 479655 | 481052 | 490690 | 500391 | 500392 | \
             500595 | 500685 | 500786 | 502290 | 507067 | 510866 | 511283 | 512739 | 512740 | 512741 | 513793 | \
             513885 | 514267 | 514711 | 514712 | 514715 | 514725 | 516482 | 516483:
            hanja_write = hanja_write.replace('<equ>&#x9396;</equ>', '鎖')

        # ／(U+FF0F) -> /(U+002F)
        # 292093 - 조당-되다: 阻擋／阻攩
        # 477921 - 조당-하다: 阻擋／阻攩
        case 292093 | 477921:
            hanja_write = '阻擋/阻攩'

        # 244060 - 요분01: 妖<equ>&#x0E004;</equ>
        case 244060:
            hanja_write = '妖氛'

        # 31604 - 관선-창: 官廠
        case 31604:
            new_word = '관담창'
            hanja_write = '官壜廠'

        # 29428 - 공어05: <equ>&#x0E000;</equ>魚
        case 29428:
            hanja_write = '公魚'

        # 201161 - 순장-정과: <equ>&#x0E005;</equ>杖正果
        # 62206 - 낭축01: 螂
        case 201161 | 62206:
            new_word = ''

    return new_word, word_unit, word_type, hanja_write


def fill_dictionary(apps, schema_editor):
    pat = re.compile(r'<word_no>(\d+)</word_no>|<sense_no>(\d+)</sense_no>')

    Hanja = apps.get_model("dictionary", "Hanja")
    KoreanWord = apps.get_model("dictionary", "KoreanWord")
    KoreanWordSense = apps.get_model("dictionary", "KoreanWordSense")
    HanjaUsage = apps.get_model("dictionary", "HanjaUsage")
    KoreanWordCategory = apps.get_model("dictionary", "KoreanWordCategory")

    pos_dict = {c.label: c for c in KWS.WordPos}
    word_unit_dict = {c.label: c for c in KW.WordUnit}
    word_type_dict = {c.label: c for c in KW.WordType}

    tree = Xml.parse('korean_dict.xml')
    for item in tree.getroot().findall('./item'):
        word_no = int(item.findtext('target_code'))

        word_info = item.find('word_info')
        word = word_info.findtext('word')
        word_unit = word_unit_dict[word_info.findtext('word_unit')]
        word_type = word_info.findtext('word_type')
        word_type = word_type_dict[word_type] if word_type else KW.WordType.NONE

        hanja_writes = []
        if word_unit == KW.WordUnit.DANEO and word_type == KW.WordType.HANJAEO or KW.WordType.HONJONGEO:
            original_language = ''
            for original_language_info in word_info.findall('original_language_info'):
                match original_language_info.findtext('language_type'):
                    case '한자':
                        original_language += original_language_info.findtext('original_language')
                    case '/(병기)':
                        if original_language:
                            hanja_writes.append(original_language)
                            original_language = ''
                    case _:
                        pass
            if original_language:
                hanja_writes.append(original_language)

        hanja_write = '/'.join(hanja_writes)

        word, word_unit, word_type, hanja_write = fix_korean_word(word_no, word, word_unit, word_type, hanja_write)
        if not word:
            continue

        word_obj = KoreanWord(id=word_no, word=word, unit=word_unit, word_type=word_type,
                              hanja=hanja_write)
        word_obj.save()

        for char in set(hanja_write.replace('▽', '').replace('/', '')):
            hanja, _ = Hanja.objects.get_or_create(letter=char)
            HanjaUsage(hanja=hanja, word=word_obj).save()

        for pos_info in word_info.findall('pos_info'):
            pos = pos_info.findtext('pos')
            for comm_pattern_info in pos_info.findall('comm_pattern_info'):
                for sense_info in comm_pattern_info.findall('sense_info'):
                    sense_no = int(sense_info.findtext('sense_code'))

                    definition = sense_info.findtext('definition')
                    definition_original = sense_info.findtext('definition_original')
                    if definition_original == definition:
                        definition_original = ''
                    elif matches := re.findall(pat, definition_original):
                        condensed = ''
                        for ref_word_no, ref_sense_no in matches:
                            condensed += ('w' + ref_word_no) if word_no else ('s' + ref_sense_no)
                        definition_original = condensed

                    cats = []
                    for cat_info in sense_info.findall('cat_info'):
                        if (cat := cat_info.findtext('cat')) != '없음':
                            cats.append(KoreanWordCategory.objects.get(category=cat))

                    sense = KoreanWordSense(id=sense_no, word=word_obj, pos=pos_dict.get(pos, KWS.WordPos.NONE),
                                            definition=definition, definition_original=definition_original)
                    sense.categories.add(*cats)
                    sense.save()


class Migration(migrations.Migration):
    dependencies = [
        ('dictionary', '0001_initial'),
    ]
    operations = [
        migrations.RunPython(fill_category),
        migrations.RunPython(fill_dictionary),
    ]

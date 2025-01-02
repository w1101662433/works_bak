import copy
import configparser
import yaml
import xmltodict
import validators
from libs.print_error_info import *
from difflib import SequenceMatcher

test_model = True
split_re_str = r'[\s:：\-=|;；,，/\.、。]+'

global_score_dic = {
    '\t': 4,
    ' ': 2,
    ':': 1.11,
    '：': 1.11,
    '=': 1.11,
    '|': 0.96,
    ';': 0.51,
    '；': 0.51,
    '，': 0.49,
    ',': 0.49,
    '、': 0.55,
    '-': 0.22,
    '/': 0.28,
    '。': 0.31,
    '.': 0.21,
}

minus_dic = {
    '==': -2.22,
    '=;': -1.11,
    '::': -2.22,
    '..': -0.41,
}


def get_score(string):
    score = sum([global_score_dic.get(i) for i in string])
    return score


def intelligent_split(line, split_count=None):
    line = line.strip()
    # show_log('line', line, 'split_count', split_count)
    if line.endswith(','):
        line = line[:-1]
    split_marks = re.findall(split_re_str, line)

    if not split_marks:
        return [line]
    split_marks = set(split_marks)
    score_dic = {}

    for i in split_marks:
        score_dic.setdefault(i, 0)
        score_dic[i] += get_score(i)
        for k, v in minus_dic.items():
            if k in i:
                score_dic[i] += minus_dic[k]

    # score_dic = {i: get_score(i) for i in split_marks}
    score_dic = dict(sorted(score_dic.items(), key=lambda x: x[1], reverse=True))
    # print('score_dic', score_dic)
    if not split_count:
        need_score = 2
        if list(score_dic.keys()):
            max_score = list(score_dic.values())[0]

            if max_score < 2:
                need_score = max_score
        need_replace_marks = [k for k, v in score_dic.items() if v >= need_score]
        re_str = '|'.join([i.replace('|', '\|').replace('-', '\-').replace('.', '\.') for i in need_replace_marks])
        show_log('re_str', re_str)
        res = re.split(re_str, line)
        res = [i for i in res if i.strip()]
        # show_log('res1', res)
    else:
        show_log('score_dic', score_dic)
        res = []
        for n, k in enumerate(score_dic.keys()):
            need_replace_marks = [*score_dic.keys()][:n + 1]
            # show_log('need_replace_marks', need_replace_marks)
            re_str = '|'.join([i.replace('|', '\|').replace('-', '\-') for i in need_replace_marks])
            # show_log('re_str', re_str)

            res = re.split(re_str, line, maxsplit=split_count - 1)
            if len(res) == split_count:
                break
        res = [i for i in res if i.strip()]
        if len(res) < split_count:
            res += [''] * (split_count - len(res))
        # show_log('res2', res)
    return res


def get_similar(a, b):
    s = SequenceMatcher(None, a, b)
    similar = s.ratio()
    return similar


def judge_has_header(lines):
    length = len(lines)
    step = length // 10 + 1
    if length < 3:
        return False
    lines = [re.sub(r'\d', '0', i) for i in lines]

    top_line = lines[0]
    all_similar = [get_similar(top_line, i) for i in lines[1::step]]
    top_similar = sum(all_similar) / len(all_similar)
    show_log('top_similar', top_similar)

    button_line = lines[-1]
    all_similar = [get_similar(button_line, i) for i in lines[1:-1:step]]
    button_similar = sum(all_similar) / len(all_similar)
    show_log('button_similar', button_similar)

    if len(lines) >= 6:
        mid = len(lines) // 2
        middle_line = lines[mid]
        all_similar = [get_similar(middle_line, i) for i in lines[1:mid:step] + lines[mid + 1::step]]
        middle_similar = sum(all_similar) / len(all_similar)
        show_log('middle_similar', middle_similar)
        button_similar = (button_similar + middle_similar) / 2

    if button_similar - top_similar > 0.35 or button_similar - top_similar > 0.25 and top_similar < 0.4:
        return True
    else:
        return False


def excel_to_json(data):
    data = data.strip()
    if test_model:
        show_log('excel_to_json')
    lines = [line.strip() for line in re.split(r'[\n\r]', data) if line.strip()]

    if all(['=' in i for i in lines]):
        has_header = False
    else:
        has_header = judge_has_header(lines)

    show_log('has_header', has_header)
    top_line = intelligent_split(lines[0])
    split_count = len(top_line) if has_header else 2

    show_log('lines[0]', lines[0])
    show_log('len(top_line)', len(top_line))
    if len(top_line) == 1:
        res = lines
    elif not has_header:
        res = {}
        for line in lines:
            kv = intelligent_split(line, split_count=split_count)
            # show_log('kv', kv)
            k = kv[0]
            v = kv[1]
            if not res.get(k):
                res[k] = v
            else:
                if not isinstance(res[k], list):
                    res[k] = [res[k]]
                res[k].append(v)
    elif has_header:
        res = []
        for line in lines[1:]:
            kv = intelligent_split(line, split_count=split_count)
            tmp_dic = dict(zip(top_line, kv))
            res.append(tmp_dic)
    else:
        raise Exception
    # show_log('res', res)
    resp = json.dumps(res, indent=4, ensure_ascii=False)
    return resp


def url_params_to_json(data):
    if test_model:
        show_log('url_params_to_json')
    lines = [line.strip() for line in re.split(r'[\n\r]', data) if line.strip()]
    assert len(lines) == 1
    assert re.match('(.+=.*&?)+', data)
    show_log('data', data)
    if "?" in data:
        url, params = data.split('?', maxsplit=1)
        params_li = [i.split('=') for i in params.split('&') if i.strip()]
        params = {i[0].strip(): i[1].strip() for i in params_li}
        dic = {'url': url, 'params': params}
    else:
        params_li = [i.split('=') for i in data.split('&') if i.strip()]
        dic = {i[0].strip(): i[1].strip() for i in params_li}

    res = json.dumps(dic, indent=4, ensure_ascii=False)
    return res


def xml_to_dict(data):
    if test_model:
        show_log('xml_to_dict')
    dic = xmltodict.parse(data)
    res = json.dumps(dic, indent=4, ensure_ascii=False)
    return res


def yaml_to_json(data):
    _data = data.replace('\t', ' ')
    if test_model:
        show_log('yaml_to_json')
    dic = yaml.load(_data, Loader=yaml.BaseLoader)
    if isinstance(dic, str):
        raise Exception
    # show_log('dic', dic)
    res = json.dumps(dic, indent=4, ensure_ascii=False)
    return res


def dict_to_json(data):
    try:
        dic = ast.literal_eval(data)
    except:
        dic = json.loads(data)
    res = json.dumps(dic, indent=4, ensure_ascii=False)
    return res


def ini_to_json(data):
    config = configparser.ConfigParser()
    config.read_string(data)
    dic = {i: dict(config.items(i)) for i in config.sections()}
    res = json.dumps(dic, indent=4, ensure_ascii=False)
    return res


def judge_category(data):
    is_url = validators.url(data)
    if is_url:
        return 'url'


def split_to_lines(data):
    if data.count(';') >= 2:
        confuse = re.split(r'([ ;,，\t$]+)', data)
    else:
        confuse = re.split(r'([ ;,，\t&$]+)', data)
    lines = [i for n, i in enumerate(confuse) if n % 2 == 0]
    marks = [i for n, i in enumerate(confuse) if n % 2 == 1]
    print('marks', marks)
    for n, item in enumerate(lines):
        print('n, item', n, item)

        if item.strip() and '=' not in item:
            j = 1
            for i_ in range(9999):
                if lines[n - j].strip():
                    lines[n - j] += marks[n - 1]
                    lines[n - j] += item
                    lines[n] = ''
                    break
                else:
                    j += 1
    return [i for i in lines if i]


def trans_to_json(data):
    data = data.strip().strip('"\'').strip()
    data = data.replace(':\n', ': ')

    try:
        return dict_to_json(data)
    except:
        if data.startswith('{') or data.startswith('['):
            pass  # todo 检测json格式错误
        pass

    lines = [line.strip() for line in re.split(r'[\n\r]', data) if line.strip()]
    line_count = len(lines)

    if line_count == 1:
        if judge_category(data) == 'url':
            return url_params_to_json(data)
        elif re.search(r'[=:：]', data):
            if re.search(r'(.+[:：=].+[ ;,，&\t$]+){2}', data):
                lines = split_to_lines(data)
                data = '\n\r'.join(lines)
        else:
            _sp = intelligent_split(data)
            # print('_sp', _sp)
            if len(_sp) >= 3:
                res = json.dumps(_sp, indent=4, ensure_ascii=False)
                return res
    line_count = len(lines)
    show_log(lines)
    if line_count != 1:
        try:
            return xml_to_dict(data)
        except:
            pass

        try:
            return yaml_to_json(data)
        except:
            pass

        try:
            return ini_to_json(data)
        except:
            pass

        try:
            return url_params_to_json(data)
        except:
            pass

        try:
            return excel_to_json(data)
        except:
            print_error_info(log=True)
            pass

    return "/｀ｍ´）ﾉ ~┻━┻\n无法识别\nSorry, I can not recognize"


if __name__ == '__main__':
    content = """
 locale=zh-cn; _gid=GA1.2.2003985192.1701073918; _gat_UA-139060548-5=1; _gat_gtag_UA_1502657_29=1; Hm_lvt_d6d77a17b13354c004d0e51af30fd7e1=1700787353,1700804805,1701049275,1701073923; Hm_lpvt_d6d77a17b13354c004d0e51af30fd7e1=1701073948; _ga_3DK1GYFTH2=GS1.1.1701073512.8.1.1701073947.36.0.0; _ga_D6TGWETPG2=GS1.1.1701073917.1.1.1701073947.30.0.0; _ga=GA1.1.567620845.1701073918; _ga_BQNZ9QC5QS=GS1.1.1701073512.9.1.1701073948.0.0.0
 """
    a = trans_to_json(content)
    show_log(a)

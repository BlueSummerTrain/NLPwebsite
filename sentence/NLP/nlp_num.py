#coding=utf-8
import config as cf

def check_number_unit(seq_data):
    flag = False
    for item in cf.ch_num_unit.keys():
        if item in seq_data:
            flag = True
    return flag

def no_unit_num_trans(number):
    en_str = []
    number_data = list(number)
    for index,item in enumerate(number_data):
        if item == cf.decimal_tag:
            en_str.append('.')
        else:
            if item in cf.ch_nums.keys():
                en_data = cf.ch_nums[item]
                en_str.append(en_data)
            else:
                en_str.append('O')
    return ''.join(en_str)

def trans_list2int(en_str):
    data_index = 0
    sum_data = 0
    while data_index <len(en_str):
        item = en_str[data_index]
        data_int = 0
        if len(item) == 1:
            if data_index + 1 < len(en_str):
                data_unit = en_str[data_index + 1]
                if len(data_unit) > 1:
                    data_int = int(item)*int(data_unit)
                else:
                    raise ValueError
            else:
                data_int = int(item)
        elif len(item) > 1:
            if data_index + 2 >= len(en_str):
                if data_index + 1 >= len(en_str):
                    data_int = int(item)
                else:
                    lower_data = en_str[data_index + 1]
                    data_int = int(item) + int(lower_data)
            else:
                data_unit = en_str[data_index + 2]
                lower_data = en_str[data_index + 1]
                data_int = (int(item) + int(lower_data))*int(data_unit)
        sum_data = sum_data + data_int
        data_index = data_index + 2
    return sum_data

def unit_num_trans(number):
    en_str = []
    number_data = list(number)
    for item in number_data:
        if item in cf.ch_num_unit.keys():
            en_data_unit = cf.ch_num_unit[item]
            en_str.append(en_data_unit)
        elif item in cf.ch_nums.keys():
            en_data_num = cf.ch_nums[item]
            en_str.append(en_data_num)
        elif item == cf.decimal_tag:
            en_str.append('.')
        else:
            en_str.append('O')

    if '0' in en_str:
        en_str.remove('0')

    no_decimal = False
    try:
        decimal_split = en_str.index('.')
    except Exception, e:
        no_decimal = True
    if 'O' not in en_str:
        if not no_decimal:
            int_block = en_str[:decimal_split]
            decimal_block = en_str[decimal_split+1:]
            int_data = trans_list2int(int_block)
            decimal_data = ''.join(decimal_block)
            decimal_all = float(str(int_data)+'.'+decimal_data)
            return decimal_all
        else:
            return trans_list2int(en_str)
    else:
        raise ValueError

def unit_num_split(number):
    data_list = []
    point_bilion_flag = False
    ten_thous_flag = False
    if cf.point_bilion in number:
        point_bilion_flag = True
        data_split = number.split(cf.point_bilion)
        data_list.append(data_split[0])
        if cf.ten_thous in number:
            ten_thous_flag = True
            data_temp = data_split[1].split(cf.ten_thous)
            data_list = data_list + data_temp
        else:
            data_list.append(data_split[1])
    else:
        if cf.ten_thous in number:
            ten_thous_flag = True
            data_list = number.split(cf.ten_thous)
        else:
            data_list = [number]
    en_data = 0
    point_bilion_unit = int(cf.ch_num_unit[cf.point_bilion])
    ten_thou_unit = int(cf.ch_num_unit[cf.ten_thous])
    for index,data_it in enumerate(data_list):
        try:
            data_now = unit_num_trans(data_it)
        except ValueError,e:
            return 'NULL'
        current_num = 0
        if point_bilion_flag:
            if index == 0:
                current_num = data_now * point_bilion_unit
            elif index == 1 and ten_thous_flag:
                current_num = data_now * ten_thou_unit
            else:
                current_num = data_now
        elif ten_thous_flag:
            if index == 0:
                current_num = data_now * ten_thou_unit
            else:
                current_num = data_now
        else:
            current_num = data_now
        en_data = en_data + current_num
    return str(en_data)

def number_check(en_data):
    if en_data.isdigit():
        return True
    else:
        if '.' in en_data:
            data_split = en_data.split('.')
            if data_split[0].isdigit() and data_split[1].isdigit():
                return True
            else:
                return False
        else:
            return False

def ch_num_en_num_recognize(seq_data):
    if number_check(seq_data):
        return seq_data
    else:
        if check_number_unit(seq_data):
            n_data = unit_num_split(seq_data)
            if n_data != 'NULL' and number_check(n_data):
                return n_data
            else:
                return 'NULL'
        else:
            n_data = no_unit_num_trans(seq_data)
            if number_check(n_data):
                return n_data
            else:
                return 'NULL'

if __name__ == '__main__':
    #print ch_num_en_num_recognize('四二一十三'.decode('utf-8'))
    print ch_num_en_num_recognize('一千个伤心的理由'.decode('utf-8'))
    #print ch_num_en_num_recognize('三十点五八'.decode('utf-8'))
    #print ch_num_en_num_recognize('23232')
    #print ch_num_en_num_recognize('23.232')
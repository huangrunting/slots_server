# -*- coding: utf-8 -*-
# from prize_config import *
from random import random

from math_configs.reel_config import *
from slots_math.slots import *
from slots_math.wheel import *
from slots_math.util import *
from math_configs.pay_tree import PAY_TREE
from math_configs.prize_bg import PRIZE_BG
from math_configs.prize_fg import PRIZE_FG
from math_configs.prize_nm import PRIZE_NM
from math_configs.prize_sw import PRIZE_SW
from math_configs.prize_bw import PRIZE_BW
from math_configs.prize_303 import PRIZE_303
from math_configs.prize_hw import PRIZE_HW
from math_configs.prize_sbg import PRIZE_SBG
from math_configs.prize_sfg import PRIZE_SFG
from math_configs.prize_snm import PRIZE_SNM
from math_configs.prize_ssw import PRIZE_SSW
from math_configs.prize_sbw import PRIZE_SBW
from math_configs.prize_shw import PRIZE_SHW


class ThemeMath(LinesSlots):
    def __init__(self, pay_tree_path=''):
        super(ThemeMath, self).__init__(SYMBOLS, REEL_SET, LINE_CONFIG, PAY_TREE, pay_tree_path)
        self.prize = Wheel(PRIZE_CONFIG)
        self.portfolio = Wheel(PORTFOLIO_CONFIG)
        self.coin_trans = Wheel(COIN_TRANS)
        self.respin_coin = Wheel(RESPIN_CONFIG)
        self.super_coin = Wheel(SUPER_COIN_CONFIG)

    def ng_spin(self, bet, bonus_level, fg_info, map_info, remote_prize=0, debug_reels=[], hv=0, snm=0):
        if remote_prize:
            if remote_prize in ONLINE_PRIZE_ID:
                win_info = self.set_prize(bet, bonus_level, fg_info, remote_prize, debug_reels, 0, map_info, hv=hv, snm=snm)
                self.near_miss(win_info, 0)
            else:
                win_info = self.set_test_prize(bet, bonus_level, fg_info, remote_prize, debug_reels, 0, map_info, hv=hv, snm=snm)
        else:
            if snm:
                reel_info = self.gen_reel(0)
            else:
                reel_info = self.spin(reel_index=3) if hv else self.spin(reel_index=0)
            win_info = self.evaluate(reel_info, bet, bonus_level, 0, map_info, remote_prize, fg_info, hv=hv, snm=snm)
            self.near_miss(win_info, 0, snm)
        return win_info

    def fg_spin(self, bet, bonus_level, fg_info, map_info, remote_prize=0,  debug_reels=[], hv=0):
        if remote_prize:
            if remote_prize in ONLINE_PRIZE_ID:
                win_info = self.set_prize(bet, bonus_level, fg_info, remote_prize, debug_reels, 1, map_info)
            else:
                win_info = self.set_test_prize(bet, bonus_level, fg_info, remote_prize, debug_reels, 1, map_info)
        else:
            reel_info = self.spin(reel_index=4) if hv else self.spin(reel_index=1)
            win_info = self.evaluate(reel_info, bet, bonus_level, 1, map_info, remote_prize, fg_info)
            self.near_miss(win_info, 1)
        return win_info

    def post_spin(self, bet, reel_info, prize, fg_info, is_fg, map_info, snm=0):
        item_list_cal = copy.deepcopy(reel_info['item_list'])
        coin_num = 0
        scatter_count = 0
        coin_pos = []
        scatter_pos = []
        for i in range(5):
            for j in range(3):
                if item_list_cal[i][j] in [14, 15]:
                    coin_num += 1
                    coin_pos.append([i, j])
                elif item_list_cal[i][j] == 13:
                    scatter_count += 1
                    scatter_pos.append([i, j])
                elif 20 <= item_list_cal[i][j] <= 60:
                    coin_num += 1
                    coin_pos.append([i, j])
                    item_list_cal[i][j] = T

        if scatter_count >= 3 and coin_num >= 3:
            for i in range(2, coin_num):
                item_list_cal[coin_pos[i][0]][coin_pos[i][1]] = [A, B, C, D][rand_with_weight([1, 1, 2, 2])]
                reel_info['item_list'][coin_pos[i][0]][coin_pos[i][1]] = item_list_cal[coin_pos[i][0]][coin_pos[i][1]]
        elif scatter_count >= 2 and coin_num >= 3:
            item_list_cal[scatter_pos[0][0]][scatter_pos[0][1]] = W
            reel_info['item_list'][scatter_pos[0][0]][scatter_pos[0][1]] = W

        for i in range(5):
            if reel_info['up'][i][0] == 14:
                reel_info['up'][i][0] = self.coin_trans.spin(1) if coin_num < 6 else self.coin_trans.spin(0)
            for j in range(6):
                if reel_info['down'][i][j] == 14:
                    reel_info['down'][i][j] = self.coin_trans.spin(1) if coin_num < 6 else self.coin_trans.spin(0)
            for j in range(3):
                if reel_info['item_list'][i][j] == 14:
                    reel_info['item_list'][i][j] = self.coin_trans.spin(1) if coin_num < 6 else self.coin_trans.spin(0)

        if is_fg:
            if fg_info['sticky_wild']:
                fg_info['sticky_wild'] = [i for i in fg_info['sticky_wild'] if i[2] > 0]
                if len(fg_info['sticky_wild']) >= 7:
                    for i in range(5):
                        for j in range(3):
                            if reel_info['item_list'][i][j] == W:
                                trans_major = [A, B, C, D][rand_with_weight([1, 1, 2, 2])]
                                reel_info['item_list'][i][j] = trans_major
                                item_list_cal[i][j] = trans_major
                for i in fg_info['sticky_wild']:
                    i[2] = i[2] - 1
                    item_list_cal[i[0] - 1][i[1] - 1] = W
        else:
            if rand_with_weight([24, 1]) and prize == 0 and snm == 0:
                trans_major = [A, B, C, D][rand_with_weight([1, 1, 2, 2])]
                for i in range(5):
                    for j in range(3):
                        if reel_info['item_list'][i][j] in [A, B, C, D]:
                            reel_info['item_list'][i][j] = trans_major
                            item_list_cal[i][j] = trans_major

        if map_info['map_level'] == 5 and coin_num >= 6:    # super respin进场时的JP也按照avg bet计算，避免显示产生误解
            for i in range(5):
                for j in range(3):
                    if reel_info['item_list'][i][j] in [35, 36, 37, 38, 39]:
                        reel_info['item_list'][i][j] += 100
        return reel_info, item_list_cal, coin_num, scatter_count

    def check_trigger_fg(self, win_scatters, bet):
        base_win = 0
        win_free = {}
        if win_scatters >= 3:
            base_win = bet
            win_free = {'free_spins': [8, 12, 16][win_scatters - 3],
                        'fg_init_list':  get_item_list_str(PRIZE_NM[np.random.randint(10000)], 3)['item_list'],
                        'free_bet': bet}
        return {'win_free': win_free,
                'base_win': base_win}

    def coin_fall(self, bet, ball_count, respin_time, respin_board, bonus_level, prize, map_info, respin_win_info, coin_miss, super_coin_miss, recovery_miss, coin_id_board):
        map_bet = map_info['avg_bet']   # super respin中新出现的symbol的id均为100+，用avg bet计算，
        coin_cal = []                   # 计算每次coin fall过程中消除的coin
        coin_id_del = []                # 计算每次coin fall过程中消除的coin id
        respin_win_info['add_delta'] = 0
        respin_win_info['respin_multi'] = 0
        respin_win_info['jp_mark'] = []
        respin_win_info['jp_mark_temp'] = []
        respin_win_info['coin_del_list'] = []
        enter_super = [[], [], []]      # 记录super respin中每次掉落的coin，此处仅为过程值，后续不参与super_coin_miss处理
        board_cal = copy.deepcopy(respin_board)
        if respin_time <= 4:
            coin_lv = 0
        elif respin_time <= 8:
            coin_lv = 1
        elif respin_time <= 12:
            coin_lv = 2
        else:
            coin_lv = 3
        if map_info['is_super']:        # respin中进场掉落，理论上后续不会再触发
            for i in [1, 2, 3]:
                board_cal[i] = [x for x in board_cal[i] if x != 0]  # 这一句是完成下落堆叠的过程
                coin_id_board[i] = [x for x in coin_id_board[i] if x != 0]  # 这一句用来准备判断哪些coin id是会被消除的
                for j in range(3):
                    board_cal[i].insert(0, 0)
                    coin_id_board[i].insert(0, 0)
                board_cal[i] = board_cal[i][-3::]
                coin_id_board[i] = coin_id_board[i][-3::]

            for i in [1, 2, 3]:
                for j in range(3)[::-1]:    # 注意此处为逆序计算，便于前端计算
                    if board_cal[i][j] == 0:
                        super_coin = self.super_coin.spin(coin_lv) + 100
                        enter_super[i - 1].append(super_coin)
                        ball_count += 1
                        coin_miss[ball_count] = [[respin_time, [i, 2 - j]]]
                        board_cal[i][j] = super_coin
                        coin_id_board[i][j] = ball_count
                        if ball_count not in super_coin_miss:
                            super_coin_miss[ball_count] = [0, i - 1, len(enter_super[i - 1]) - 1]

        for i in range(5):
            board_cal[i] = [x for x in board_cal[i] if x != 0]  # 这一句是完成下落堆叠的过程
            coin_id_board[i] = [x for x in coin_id_board[i] if x != 0]  # 这一句用来准备判断哪些coin id是会被消除的

        min_length = min(len(board_cal[0]), len(board_cal[1]), len(board_cal[2]), len(board_cal[3]), len(board_cal[4])) # 用于判断是否存在满行
        if min_length:      # 判断是否存在满行，若min_length为0，则不存在满行，也就不需要计算消除
            # board_cal_copy = copy.deepcopy(board_cal)
            for i in range(5):
                for j in range(min_length):
                    coin_cal.append(board_cal[i][-1])   # 添加消除的coin进入待计算的list
                    respin_win_info['coin_del_list'].append(board_cal[i][-1])
                    board_cal[i].pop(-1)                # 完成整个消除过程
                    coin_id_del.append(coin_id_board[i][-1])    # 添加消除的coin id进入消除list
                    coin_id_board[i].pop(-1)

        if coin_id_del:                         # 处理消除的coin id，仅在coin miss, super coin miss和recovery_miss中保留未被消除的coin
            for i in coin_id_del:
                if i in coin_miss:
                    coin_miss.pop(i)
                if i in super_coin_miss:
                    super_coin_miss.pop(i)
                if i in recovery_miss:
                    recovery_miss.pop(i)

        if coin_cal:                                    # 计算过程中通过symbol id是否大于100来判断使用bet还是map bet(avg_bet)
            respin_win_info['coin_del_num'] += len(coin_cal)
            for i in coin_cal:
                if i in [35, 36, 37, 38, 39, 135, 136, 137, 138, 139]:
                    jp_bet = map_bet if i > 100 else bet
                    value_index = i - 100 if i > 100 else i
                    jp_type = 139 - i if i > 100 else 39 - i
                    respin_win_info['jp_win_temp'].append({'jp_win': COIN_SET[value_index] * jp_bet, 'jp_win_type': jp_type})
                    respin_win_info['jp_mark_temp'].append(jp_type)
                    if bonus_level > [4, 3, 9, 2, 1, 0].index(jp_type):     # 这里的9是作为解锁map的bonus level占位符，无实际意义
                        respin_win_info['jp_win'].append({'jp_win': COIN_SET[value_index] * jp_bet, 'jp_win_type': jp_type})
                        respin_win_info['jp_total_win'] += COIN_SET[value_index] * jp_bet
                        respin_win_info['jp_mark'].append(jp_type)
                    else:
                        respin_win_info['total_win'] += COIN_SET[value_index] * jp_bet
                elif i in [15, 115]:
                    pass
                elif i in [41, 42, 43, 141, 142, 143]:
                    respin_win_info['add_times'] += i - 40 if i < 100 else i - 140
                    respin_win_info['add_delta'] += i - 40 if i < 100 else i - 140
                elif i in [51, 52, 53, 151, 152, 153]:
                    respin_win_info['respin_multi'] += i - 50 if i < 100 else i - 150
                else:
                    respin_win_info['total_win'] += COIN_SET[i - 100] * map_bet if i > 100 else COIN_SET[i] * bet

        coin_remaining = copy.deepcopy(board_cal)

        for i in range(5):          # 将coin remaining的牌面填满，保证格式正确
            for j in range(3):
                coin_remaining[i].insert(0, 0)
                coin_id_board[i].insert(0, 0)
            coin_remaining[i] = coin_remaining[i][-3:]
            coin_id_board[i] = coin_id_board[i][-3:]

        if map_info['is_super']:        # 此处单独处理填满super respin的coin情况，先根据当前牌面处理
            respin_win_info['super_board'].append([copy.deepcopy(coin_remaining[1]),
                                                   copy.deepcopy(coin_remaining[2]),
                                                   copy.deepcopy(coin_remaining[3])])
        coin_remaining_origin = copy.deepcopy(coin_remaining)
        for i in range(5):          # 这里对于respin_win_info['super_board']的操作均为过程数据，下方会重新初始化respin_win_info['super_board'][-1]
            if i in [1, 2, 3] and map_info['is_super']:
                for j in range(3):
                    respin_win_info['super_board'][-1][i - 1].insert(0, 0)
                for j in range(len(respin_win_info['super_board'][-1][i - 1])):
                    if respin_win_info['super_board'][-1][i - 1][j] == 0:
                        super_coin = self.super_coin.spin(coin_lv) + 100
                        respin_win_info['super_board'][-1][i - 1][j] = super_coin
                        if j > 2:
                            coin_remaining[i][j - 3] = super_coin       # 对coin remaining赋值

        if respin_win_info['super_board']:
            respin_win_info['super_board'][-1] = [[], [], []]   # 这里重新初始化，并进行真正的super board赋值操作
            for i in [1, 2, 3]:
                for j in range(3)[::-1]:
                    if coin_remaining_origin[i][j] == 0:
                        respin_win_info['super_board'][-1][i - 1].append(coin_remaining[i][j])
                        ball_count += 1     # 更新维护coin miss等数据
                        coin_miss[ball_count] = [[respin_time, [i, j]]]
                        coin_id_board[i][j] = ball_count
                        if ball_count not in super_coin_miss:
                            super_coin_miss[ball_count] = [len(respin_win_info['super_board']) - 1,
                                                           i - 1,
                                                           len(respin_win_info['super_board'][-1][i - 1]) - 1]

        if enter_super != [[], [], []]:     # 对入场时的super board进行操作
            for i in range(3):
                if enter_super[i]:
                    for j in range(len(enter_super[i]))[::-1]:
                        respin_win_info['super_board'][-1][i].insert(0, enter_super[i][j])
        return coin_remaining, respin_win_info, ball_count

    def do_respin(self, bet, item_list, respin_count, bonus_level, prize, map_info, hv=0):
        respin_start = copy.deepcopy(item_list)     # 初始化respin进场牌面
        respin_board = copy.deepcopy(item_list)     # 初始化respin牌面用作后续处理， 并传入respin list给前段展示
        ball_count = 0                              # 记录获得的coin个数
        respin_time = 0                             # 记录respin次数，用作respin的while循环中做送奖处理
        respin_list_len = copy.deepcopy(respin_count) * 2   # 用作respin的while循环，决定循环次数
        recover_item_list = []                      # 记录respin断线重连回来后的恢复牌面，需要持续添加coin_remaining每次最终牌面
        respin_win_list = []                        # respin中每次spin的赢钱显示，注意包括了JP的尾数，在progressive_mark和jp_mark处有处理，便于game字段中添加尾数
        spin_win_list = []                          # respin中额外spin的coin赢取信息
        multi_win_list = []                         # respin中倍乘coin的赢取信息
        respin_jp_list = []                         # respin中倍乘coin的赢取信息
        progressive_mark = []                       # 记录获得JP（解锁）的位置，便于game文件内处理尾数
        prize_flag = np.random.randint(2, 4)        # 送奖flag，用于控制在第几次respin送出目标coin
        win_flag = np.random.randint(2, respin_list_len)    # 送奖flag，用于控制在第几次respin获得赢钱
        coin_miss = {}                              # 用于后续记录整个respin中均未消除的coin，方式为每个coin分配一个id，做强力teasing
        super_coin_miss = {}                        # 用于后续记录super board中均未消除的coin，方式为每个coin分配一个id，做强力teasing
        recovery_miss = {}
        coin_id_board = copy.deepcopy(item_list)    # coin id的respin记录，便于后续寻找哪些coin未消除
        coin_del_num = 0                            # badge使用
        coin_del_list = []
        coin_id_list = []
        start_coin_id = []
        del_flag = 0

        for i in range(5):                          # 此处将respin_board，respin_start中普通symbol置为0，并计算coin个数
            for j in range(3):
                if 20 <= respin_board[i][j] or respin_board[i][j] == 15:
                    ball_count += 1
                    coin_id_board[i][j] = ball_count
                    coin_miss[ball_count] = [[respin_time, [i, j]]]
                    start_coin_id.append(ball_count)
                else:
                    respin_board[i][j] = 0
                    respin_start[i][j] = 0
                    coin_id_board[i][j] = 0

        # 初始化respin的赢钱信息，其中super_board仅用于super中，格式较为特殊，仅包含中间三列落下的coin信息，且先落下的coin在list前位
        respin_win_info = {'jp_win': [], 'jp_win_temp': [], 'jp_total_win': 0, 'total_win': 0, 'coin_del_num': coin_del_num,
                           'add_times': 0, 'add_delta': 0, 'jp_mark': [], 'jp_mark_temp': [], 'coin_del_list': [],
                           'respin_multi': 0, 'super_board': [], 'respin_list': [copy.deepcopy(respin_board)]}
        # 处理进场时coin下落赢钱的信息，但不负责处理coin生成的信息
        coin_remaining, respin_win_info, ball_count = self.coin_fall(bet, ball_count, respin_time, respin_board,
                                                                     bonus_level, prize, map_info, respin_win_info,
                                                                     coin_miss, super_coin_miss, recovery_miss,
                                                                     coin_id_board)
        recover_item_list.append(coin_remaining)    # 将当次下落并消除后的respin牌面传入，用于断线重连
        for i in range(5):
            for j in range(3):
                if coin_id_board[i][j]:
                    if coin_id_board[i][j] in recovery_miss:
                        recovery_miss[coin_id_board[i][j]].append([respin_time, [i, j]])
                    else:
                        recovery_miss[coin_id_board[i][j]] = [[respin_time, [i, j]]]
        respin_win_list.append(respin_win_info['jp_total_win'] + respin_win_info['total_win'])  # 包括JP的当此spin累计的全部赢钱，注意累计
        spin_win_list.append(respin_win_info['add_delta'])      # 这里仅传出当此spin的额外spin次数，不累计
        multi_win_list.append(respin_win_info['respin_multi'])  # 这里仅传出当此spin的额外倍乘系数，不累计
        progressive_mark.append(respin_win_info['jp_mark'])     # 这里添加获得JP的信息，mark一下位置
        respin_jp_list.append(respin_win_info['jp_mark_temp'])  # 这里添加获得JP的信息，mark一下位置
        coin_del_list.append(respin_win_info['coin_del_list'])
        coin_id_list.append(copy.deepcopy(coin_id_board))
        while respin_list_len:          # respin的循环，视情况而定是否加入次数限制，由于我很自信，所以没加限制
            respin_list_len -= 1
            respin_time += 1
            respin_board = copy.deepcopy(coin_remaining)    # 先根据处理后coin信息生成当次spin牌面，添加新出的coin后返给前段展示
            empty_reel_list = [0, 1, 2, 3, 4]
            for i in range(5):          # 更新coin id board的全新位置，并且将其赋值入coin miss中，便于后续teasing中替换
                for j in range(3):
                    if coin_id_board[i][j]:
                        coin_miss[coin_id_board[i][j]].append([respin_time, [i, j]])
                    if respin_board[i][j] and i in empty_reel_list:
                        empty_reel_list.remove(i)
            if map_info['is_super']:
                if hv:
                    get_empty_reel = rand_with_weight([5, len(empty_reel_list)]) if empty_reel_list else 0
                else:
                    get_empty_reel = rand_with_weight([3, len(empty_reel_list)]) if empty_reel_list else 0
            else:
                if hv:
                    get_empty_reel = rand_with_weight([3, len(empty_reel_list)]) if empty_reel_list else 0
                else:
                    get_empty_reel = rand_with_weight([1, len(empty_reel_list)]) if empty_reel_list else 0
            empty_reel = empty_reel_list[np.random.randint(len(empty_reel_list))] + 1 if get_empty_reel else 0
            coin_win_flag = []                              # 此处先处理coin_win_flag是否送奖，或者是否触发保底
            if (respin_time == win_flag and respin_win_info['total_win'] == 0) or del_flag >= 4:
                coin_win_flag = [x for x in range(5) if respin_board[x] == [0, 0, 0]]
                del_flag = 0
            prize_pos = [0, 0, 0, 0, 0]
            if respin_list_len <= 1 and rand_with_weight([2, 1]):
                lucky_coin_flag = [x for x in range(5) if respin_board[x] == [0, 0, 0]]
                for i in lucky_coin_flag:
                    prize_pos[i] = np.random.randint(3) + 1
            for j in range(5):
                for k in range(3):
                    if respin_board[j][k] == 0:
                        if respin_list_len >= 11:                # 这里控制生成coin
                            coin_value = self.respin_coin.spin(0 + 10 * hv) if j != empty_reel - 1 else 0
                        elif respin_list_len >= 8:
                            coin_value = self.respin_coin.spin(1 + 10 * hv) if j != empty_reel - 1 else 0
                        elif respin_list_len >= 4:
                            coin_value = self.respin_coin.spin(2 + 10 * hv) if j != empty_reel - 1 else 0
                        elif respin_list_len >= 2:
                            coin_value = self.respin_coin.spin(3 + 10 * hv) if j != empty_reel - 1 else 0
                        elif respin_list_len >= 0:
                            coin_value = self.respin_coin.spin(4 + 10 * hv) if j != empty_reel - 1 else 0
                        else:
                            coin_value = self.respin_coin.spin(5 + 10 * hv)
                        if prize == 202 and prize_flag and respin_time == prize_flag:       # 作弊送额外次数
                            coin_value = [41, 42, 43][rand_with_weight([9, 3, 1])]
                            prize_flag = 0
                        if prize == 203 and prize_flag and respin_time == prize_flag:       # 作弊送倍乘
                            coin_value = [51, 52, 53][rand_with_weight([9, 3, 1])]
                            prize_flag = 0
                        if prize in [204, 205, 206, 207, 208] and prize_flag and respin_time == prize_flag:   # 作弊送JP
                            coin_value = [39, 38, 37, 36, 35][prize - 204]
                            prize_flag = 0
                        if prize == 209 and prize_flag and respin_time == prize_flag:       # 作弊送多个JP
                            coin_value = [39, 38, 37, 36, 35][rand_with_weight([9, 9, 6, 3, 1])]
                            if prize_flag < respin_list_len - 1:
                                prize_flag = [0, np.random.randint(prize_flag + 1, respin_list_len)]
                            else:
                                prize_flag = 0
                        if map_info['first_respin'] and prize_flag and respin_time == prize_flag:
                            coin_value = 35
                            prize_flag = 0
                        if j in coin_win_flag:              # 这里控制送奖coin出现，可以加入随机量控制送奖位置和个数，目前未添加
                            coin_value = self.respin_coin.spin(9)
                            coin_win_flag.remove(j)
                        if prize_pos[j] and k == prize_pos[j] - 1:
                            coin_value = self.respin_coin.spin(8)
                        if map_info['is_super'] and coin_value:     # 此处对super respin中新出的coin id处理，便于后续算钱用avg bet或前端显示
                            coin_value += 100
                        if coin_value:
                            ball_count += 1
                            respin_board[j][k] = coin_value
                            coin_miss[ball_count] = [[respin_time, [j, k]]]     # 为出现的coin分配一个id，用于后续处理
                            coin_id_board[j][k] = ball_count
                            ball_count += 1
            respin_win_info['respin_list'].append(copy.deepcopy(respin_board))  # 当此spin牌面生成结束，返给前端
            # 生成牌面后再次送入coin fall方法中处理掉落及赢钱信息
            coin_remaining, respin_win_info, ball_count = self.coin_fall(bet, ball_count, respin_time, respin_board,
                                                                         bonus_level, prize, map_info, respin_win_info,
                                                                         coin_miss, super_coin_miss, recovery_miss,
                                                                         coin_id_board)
            recover_item_list.append(coin_remaining)        # 这里更新当次spin的各种信息，同进场时处理
            for i in range(5):
                for j in range(3):
                    if coin_id_board[i][j]:
                        if coin_id_board[i][j] in recovery_miss:
                            recovery_miss[coin_id_board[i][j]].append([respin_time, [i, j]])
                        else:
                            recovery_miss[coin_id_board[i][j]] = [[respin_time, [i, j]]]
            if respin_win_info['jp_total_win'] + respin_win_info['total_win'] == respin_win_list[-1]:
                del_flag += 1
            else:
                del_flag = 0
            respin_win_list.append(respin_win_info['jp_total_win'] + respin_win_info['total_win'])
            spin_win_list.append(respin_win_info['add_delta'])
            multi_win_list.append(respin_win_info['respin_multi'])
            progressive_mark.append(respin_win_info['jp_mark'])
            respin_jp_list.append(respin_win_info['jp_mark_temp'])
            coin_del_list.append(respin_win_info['coin_del_list'])
            coin_id_list.append(copy.deepcopy(coin_id_board))
            if respin_win_info['add_delta']:                # 更新respin_list_len，用于while循环
                respin_list_len += respin_win_info['add_delta']
        for i in range(5):          # 更新coin id board的全新位置，并且将其赋值入coin miss中，便于后续teasing中替换
            for j in range(3):
                if coin_id_board[i][j]:
                    coin_miss[coin_id_board[i][j]].append([respin_time + 1, [i, j]])
        origin_jp_win = copy.deepcopy(respin_win_info['jp_win'])
        origin_jp_win_temp = copy.deepcopy(respin_win_info['jp_win_temp'])

        # 结束while循环
        if multi_win_list:     # 处理倍乘赢钱
            respin_win_info['total_win'] *= sum(multi_win_list) + 1
            respin_win_info['jp_total_win'] *= sum(multi_win_list) + 1
            if respin_win_info['jp_win']:       # 解锁或未解锁的jp均需要做倍乘处理
                for i in respin_win_info['jp_win']:
                    i['jp_win'] *= sum(multi_win_list) + 1
            if respin_win_info['jp_win_temp']:
                for i in respin_win_info['jp_win_temp']:
                    i['jp_win'] *= sum(multi_win_list) + 1

        if coin_miss:                           # 处理teasing，将respin中未消除的coin替换成更大面额的coin
            for i in start_coin_id:
                if i in coin_miss:
                    coin_miss.pop(i)

            for key in super_coin_miss:
                if super_coin_miss[key][0] == 0 and key in coin_miss:
                    coin_miss.pop(key)

            for key in coin_miss:               # 可以根据key的值来做teasing强度的控制，key的值越小，表示coin出现的靠前，用来做teasing的效果就越好
                is_super = 1 if map_info['is_super'] else 0
                if len(coin_miss[key]) >= 3:
                    super_teasing_coin = self.respin_coin.spin(7)
                else:
                    super_teasing_coin = self.respin_coin.spin(8)

                if key in super_coin_miss:
                    coin_miss[key].pop(0)
                    if coin_miss[key]:
                        for i in coin_miss[key]:
                            if i[0] < len(respin_win_info['respin_list']):
                                respin_win_info['respin_list'][i[0]][i[1][0]][i[1][1]] = super_teasing_coin + is_super * 100
                else:
                    coin_miss[key].pop(-1)
                    for i in coin_miss[key]:
                        respin_win_info['respin_list'][i[0]][i[1][0]][i[1][1]] = super_teasing_coin + is_super * 100
                if key in super_coin_miss:
                    respin_win_info['super_board'][super_coin_miss[key][0]][super_coin_miss[key][1]][super_coin_miss[key][2]] = super_teasing_coin + is_super * 100
                for i in recovery_miss[key]:
                    recover_item_list[i[0]][i[1][0]][i[1][1]] = super_teasing_coin + is_super * 100

        return {
            'theme_respin': respin_win_info['respin_list'],
            'super_board': respin_win_info['super_board'],
            'respin_times': respin_count * 2,           # 此处给前端返回的respin次数为进场时的次数
            'respin_multi': sum(multi_win_list) + 1,
            'add_times': respin_win_info['add_times'],  # 此处给前段返回的增加spin次数为增加的所有额外次数之和
            'respin_start': respin_start,
            'respin_jp_total_win': respin_win_info['jp_total_win'],
            'respin_total_win': respin_win_info['total_win'],
            'jp_win': origin_jp_win,
            'jp_win_temp': origin_jp_win_temp,
            'cal_jp_win': respin_win_info['jp_win'],
            'cal_jp_win_temp': respin_win_info['jp_win_temp'],
            'recover_item_list': recover_item_list,
            'respin_win_list': respin_win_list,
            'item_list': item_list,
            'spin_win_list': spin_win_list,
            'multi_win_list': multi_win_list,
            'progressive_mark': progressive_mark,
            'coin_del_num': respin_win_info['coin_del_num'],
            'respin_jp_list': respin_jp_list,
            'coin_del_list': coin_del_list,
            # 'coin_miss': coin_miss,
            # 'super_coin_miss': super_coin_miss,
            'recovery_miss': recovery_miss,
        }

    def calculate_base_win(self, item_list, bet, index=0):
        win_info = self.evaluate_reel(item_list, index=index)
        base_win = win_info['total_win'] * (bet / BASE_BET)
        return {
            'base_win': base_win,
            'win_scatters': win_info['win_scatters'],
            'win_lines': win_info['win_lines'],
            'win_pos_list': win_info['win_pos_list'],
        }

    def evaluate(self, reel_info, bet, bonus_level, is_fg, map_info, prize=0, fg_info={}, hv=0, snm=0):
        base_win = 0
        total_win = 0
        jp_total_win = 0
        win_jp = []
        win_bonus = {}
        badge_info = [0, 0, 0, 0, 0, 0]

        reel_info, item_list_cal, coin_num, scatter_count = self.post_spin(bet, reel_info, prize, fg_info, is_fg, map_info, snm)

        # 计算line win
        win_info = self.calculate_base_win(item_list_cal, bet, index=0)
        base_win += win_info['base_win']
        total_win += base_win

        # 判断是否触发fg
        win_fg_info = self.check_trigger_fg(scatter_count, bet)
        win_free = win_fg_info['win_free']
        base_win += win_fg_info['base_win']
        total_win += win_fg_info['base_win']
        if win_free and win_free['free_spins'] >= 16:
            badge_info[5] = 1

        # 判断是否触发BG
        if coin_num >= 6:
            if bonus_level >= 3:
                map_info['map_level'] += 1
                if map_info['map_level'] > 5:
                    map_info['is_super'] = 1
                    badge_info[0] = 1
            respin_info = self.do_respin(bet, reel_info['item_list'], coin_num, bonus_level, prize, map_info, hv=hv)
            respin_info['bet'] = bet
            respin_info['avg_bet'] = map_info['avg_bet']
            jp_total_win += respin_info['respin_jp_total_win']
            total_win += respin_info['respin_total_win']
            win_jp = respin_info['cal_jp_win']
            win_jp_temp = respin_info['cal_jp_win_temp']
            win_bonus = respin_info
            badge_info[2] = respin_info['coin_del_num'] / 5
            badge_info[3] = respin_info['add_times']
            badge_info[4] = len(respin_info['jp_win'])

        if is_fg:   # 处理free game的sticky wild，注意sticky wild的次数对于fg的期望影响较大，可以很方便控制rtp（或做高低波动性处理）
            if fg_info['sticky_wild']:  # 由于给前端返回数据中POS数据从1开始，所以需要注意每个pos中[i, j]的取值，看是否需要做-1处理
                sticky_wild_pos = [[i[0] - 1, i[1] - 1] for i in fg_info['sticky_wild']]
            else:
                sticky_wild_pos = []
            for i in range(5):
                for j in range(3):
                    if reel_info['item_list'][i][j] == W:
                        badge_info[1] += 1
                        if [i, j] in sticky_wild_pos:
                            for m in fg_info['sticky_wild']:    # 需要注意m[0]，m[1]的取值，看是否需要做-1处理
                                if i == m[0] - 1 and j == m[1] - 1:
                                    m[2] += rand_with_weight([0, 6, 3, 1]) if hv else rand_with_weight([0, 4, 3, 1])# wild叠加后角标增加的次数
                        else:
                            if hv:
                                fg_info['sticky_wild'].append([i + 1, j + 1, rand_with_weight([0, 4, 2, 4])])   # wild生成时角标增加的次数
                            else:
                                fg_info['sticky_wild'].append([i + 1, j + 1, rand_with_weight([0, 3, 4, 5])])

        if (win_bonus or win_free) and rand_with_weight([5, 5]):
            special_type = 1
        else:
            special_type = 0

        lock_progressive = [0, 0, 0, 0, 0]
        for i in range(5):
            if bonus_level >= [6, 5, 4, 2, 1][i]:
                lock_progressive[i] = 1

        ret = {
            # Reel
            'item_list': reel_info['item_list'],
            'item_list_up': reel_info['up'],
            'item_list_down': reel_info['down'],
            'reel_info': reel_info,
            # base win
            'base_win': base_win,
            'win_lines': win_info['win_lines'],
            'win_pos_list': win_info['win_pos_list'],
            # FG
            'win_free': win_free,
            # JP
            'jp_win': win_jp,
            'jp_total_win': jp_total_win,
            # BG
            'win_bonus': win_bonus,
            'lock_progressive': lock_progressive,
            # Total WIN
            'total_win': total_win,
            # Map
            'map_info': map_info,
            'fg_info': fg_info,
            'special_type': special_type,
            'badge_info': badge_info,
            'bonus_level': bonus_level,
            'trigger_bw': 1 if (total_win + jp_total_win) >= 10 * bet else 0
        }
        return ret

    def get_ac_reel_info(self, remote_prize, fg_info, is_fg, reels=[], snm=0):
        if remote_prize < 5:
            remote_prize = self.prize.spin(index=remote_prize - 1)
        elif remote_prize in [10, 11]:
            remote_prize = self.portfolio.spin(index = remote_prize - 10)

        if remote_prize == 0:
            if snm:
                reel_info = self.gen_reel(0)
            else:
                reel_info = self.spin(reel_index=is_fg)
        elif remote_prize == 9:
            if snm:
                reel_info = get_item_list_str(PRIZE_SNM[np.random.randint(10000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_NM[np.random.randint(10000)], 3)
        elif remote_prize in [100, 101]:
            if snm:
                reel_info = get_item_list_str(PRIZE_SFG[np.random.randint(1000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_FG[np.random.randint(2000)], 3)
        elif remote_prize == 200:
            if snm:
                reel_info = get_item_list_str(PRIZE_SBG[np.random.randint(1000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_BG[np.random.randint(1000)], 3)
        elif remote_prize == 300:
            if snm:
                reel_info = get_item_list_str(PRIZE_SBW[np.random.randint(1000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_BW[np.random.randint(2000)], 3)
        elif remote_prize == 301:
            if snm:
                reel_info = get_item_list_str(PRIZE_SHW[np.random.randint(1000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_HW[np.random.randint(2000)], 3)
        elif remote_prize == 302:
            if snm:
                reel_info = get_item_list_str(PRIZE_SSW[np.random.randint(9000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_SW[np.random.randint(5000)], 3)
        elif remote_prize == 303:
            if snm:
                reel_info = get_item_list_str(PRIZE_SBW[np.random.randint(1000)], 3)
            else:
                reel_info = get_item_list_str(PRIZE_303[np.random.randint(500)], 3)
        else:
            if snm:
                reel_info = self.gen_reel(0)
            else:
                reel_info = self.spin(reel_index=is_fg)
        return reel_info

    def set_prize(self, bet, bonus_level, fg_info, prize, reels, is_fg, map_info, hv=0, snm=0):
        reel_info = self.get_ac_reel_info(prize, fg_info, is_fg, reels=reels, snm=snm)
        win_info = self.evaluate(reel_info, bet, bonus_level, is_fg, map_info, prize, fg_info, hv=hv, snm=snm)
        return win_info

    def get_test_reel_info(self, remote_prize, fg_info, is_fg, reels=[], snm=0):
        if remote_prize == 999:
            reel_info = self.spin()
            reel_info['item_list'] = reels
        else:
            if remote_prize == 101:
                if snm:
                    reel_info = get_item_list_str(PRIZE_SFG[np.random.randint(1000)], 3)
                else:
                    reel_info = get_item_list_str(PRIZE_FG[np.random.randint(2000)], 3)
            elif 200 < remote_prize < 300:
                if snm:
                    reel_info = get_item_list_str(PRIZE_SBG[np.random.randint(1000)], 3)
                else:
                    reel_info = get_item_list_str(PRIZE_BG[np.random.randint(1000)], 3)
            else:
                if snm:
                    reel_info = self.gen_reel(0)
                else:
                    reel_info = self.spin(reel_index=is_fg)
        return reel_info

    def set_test_prize(self, bet, bonus_level, fg_info, prize, reels, is_fg, map_info, hv=0, snm=0):
        reel_info = self.get_test_reel_info(prize, fg_info, is_fg, reels=reels, snm=snm)
        win_info = self.evaluate(reel_info, bet, bonus_level, is_fg, map_info, prize, fg_info, hv=hv, snm=snm)
        return win_info

    def near_miss(self, win_info, is_fg=0, snm=0):
        if win_info['total_win'] == 0 and not win_info['jp_win'] and not win_info['win_free']:
            if is_fg:
                pass
            else:
                if snm:
                    reel_info = get_item_list_str(PRIZE_SNM[np.random.randint(10000)], 3)
                else:
                    reel_info = get_item_list_str(PRIZE_NM[np.random.randint(10000)], 3)
                win_info['item_list_up'] = reel_info['up']
                win_info['item_list'] = reel_info['item_list']
                win_info['item_list_down'] = reel_info['down']
                win_info['reel_info'] = reel_info
        elif not win_info['jp_win'] and not win_info['win_free'] and not win_info['win_bonus']:
            if is_fg:
                pass
            else:
                pass
        return win_info

    def gen_reel(self, is_fg):
        if is_fg:
            reel_info = self.spin(reel_index=0)
        else:
            reel_type = rand_with_weight([137, 700, 350, 9, 10, 3, 4])
            if reel_type == 1:
                reel_info = get_item_list_str(PRIZE_SNM[np.random.randint(10000)], 3)
            elif reel_type == 2:
                reel_info = get_item_list_str(PRIZE_SSW[np.random.randint(9000)], 3)
            elif reel_type == 3:
                reel_info = get_item_list_str(PRIZE_SFG[np.random.randint(1000)], 3)
            elif reel_type == 4:
                reel_info = get_item_list_str(PRIZE_SBG[np.random.randint(1000)], 3)
            elif reel_type == 5:
                reel_info = get_item_list_str(PRIZE_SBW[np.random.randint(1000)], 3)
            elif reel_type == 6:
                reel_info = get_item_list_str(PRIZE_SHW[np.random.randint(1000)], 3)
            else:
                reel_info = self.spin(reel_index=2)
                middle_weight = [0, 0, 1, 1, 1, 1, 3, 3]
                major_symbol = rand_with_weight([0, 0, 3, 3, 3, 3, 3, 3])
                middle_weight[major_symbol] = 0
                middle_symbol = rand_with_weight(middle_weight)
                minor_symbol = [J, K, L, M][rand_with_weight([1, 1, 1, 1])]
                middle_num = rand_with_weight([0, 2, 2, 1])
                middle_reel = list(np.random.choice([0, 1, 2, 3, 4], middle_num, None))
                for i in range(5):
                    for k in ['item_list', 'up', 'down']:
                        for j in range(len(reel_info[k][i])):
                            if reel_info[k][i][j] == A and i in middle_reel:
                                reel_info[k][i][j] = middle_symbol
                            elif reel_info[k][i][j] == A and i in [4, 5]:
                                reel_info[k][i][j] = major_symbol if rand_with_weight([1, 1]) else W
                            elif reel_info[k][i][j] == A:
                                reel_info[k][i][j] = major_symbol
                            elif reel_info[k][i][j] == B:
                                reel_info[k][i][j] = minor_symbol
            # print reel_info['item_list']
        return reel_info

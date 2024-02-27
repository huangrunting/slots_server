# # -*- coding: utf-8 -*-
__author__ = 'Weihua(vv)'
__version__ = '4.0.0'

from cash_frenzy.util import *
from cash_frenzy.artificial_control import *
import const
from const import *
from math import ThemeMath  # 记得改import的ThemeMath类
from slots_game.c_system.jackpot_tickets import JackpotTicketManager
from slots_game import daily_config
from math_configs.reel_config import FG_INFO_SET
from math_configs.reel_config import MAP_INFO_INI
from math_configs.prize_nm import PRIZE_NM
from slots_math.util import get_item_list_str
import numpy as np
m = ThemeMath()


def bet_group(ctx, tid):  #从lobby进主题时选bet界面中的bet列表
    pkg = ctx.user.package
    lv = ctx.user.level
    base_bet = config.get_theme_config(pkg, tid)['base_bet']
    game_type = config.get_theme_config(pkg, tid)['type']
    bet_list = config.get_bet_list_by_lv(ctx, tid, lv, game_type)
    bet_group = []
    if game_type == 'high' or lv >= 15:
        bet_group = [
            {'bet': bet_list[1 + get_bonus_level_increment(ctx)], 'lock': 0},
            {'bet': bet_list[(len(bet_list) - 2) / 3 + get_bonus_level_increment(ctx)], 'lock': 0},
            {'bet': bet_list[(len(bet_list) - 2) / 3 + 3 + get_bonus_level_increment(ctx)], 'lock': 0},
            {'bet': bet_list[-2], 'lock': 0}
        ]
    else:
        bet_multi_list = [1, 2, 3, 5]
        for i in range(4):
            bet = bet_multi_list[i] * base_bet * ctx.user.inflation_coef
            bet_group.append({
                'bet': bet,
                'lock': 0 if bet in bet_list else 1
            })
    return bet_group


def get_bonus_level_bet(ctx):
    if config.get_theme_config(ctx.user.package, ctx.theme.theme_id)['type'] == 'high':
        return [10000, 10000, 10000, 10000, 10000, 10000]
    elif ctx.user.level <= 15:
        return [10000, 10000, 10000, 10000, 10000, 10000]
    else:
        bet_list = config.get_bet_list_by_lv(ctx, ctx.theme.theme_id, ctx.user.level, 'normal',
                                             ctx.property.is_admin)
        return [bet_list[(len(bet_list) - 2) / 5 + 1 + get_bonus_level_increment(ctx)],  # mini
                bet_list[(len(bet_list) - 2) / 3 + get_bonus_level_increment(ctx)],      # minor
                bet_list[(len(bet_list) - 2) / 3 + 1 + get_bonus_level_increment(ctx)],  # Map
                bet_list[(len(bet_list) - 2) / 3 + 2 + get_bonus_level_increment(ctx)],  # major
                bet_list[(len(bet_list) - 2) / 3 + 3 + get_bonus_level_increment(ctx)],  # maxi
                bet_list[(len(bet_list) - 2) / 3 + 5 + get_bonus_level_increment(ctx)]]  # grand


def do_enter_theme(ctx, ret, req):   # 在玩家enter_theme之后 如果game.py里写了do_enter_theme 方法，会进入该方法，目的是对不同主题有个性化的enter_theme操作
    ret['bonus_level'] = get_bonus_level_bet(ctx)  # 例如将bonus_level信息return给前端
    if 'fg_info' not in ctx.theme.data:
        ctx.theme.data['fg_info'] = copy.deepcopy(FG_INFO_SET)
    if 'map_info' not in ctx.theme.data:
        ctx.theme.data['map_info'] = copy.deepcopy(MAP_INFO_INI)
    if 'first_respin' not in ctx.theme.data['map_info']:
        ctx.theme.data['map_info']['first_respin'] = 1
    if 'badge_info' not in ctx.theme.data:
        ctx.theme.data['badge_info'] = [0, 0, 0, 0, 0, 0]
    if "snm" not in ctx.theme.data:
        ctx.theme.data['snm'] = 0
    if K_THEME_INFO not in ret:
        ret[K_THEME_INFO] = {}
    ret[K_THEME_INFO]['base_init_list'] = get_item_list_str(PRIZE_NM[np.random.randint(1000)], 3)['item_list']
    ret[K_THEME_INFO]['sticky_wild'] = ctx.theme.data['fg_info']['sticky_wild']
    ret['map_info'] = ctx.theme.data['map_info']
    # 错误数据修复
    if K_SPIN_BONUS_GAME in ctx.theme.data and ctx.theme.data['map_info']['is_super']:
        min_len = min(3 - ctx.theme.data[K_SPIN_BONUS_GAME]['theme_respin'][0][0].count(0),
                      3 - ctx.theme.data[K_SPIN_BONUS_GAME]['theme_respin'][0][4].count(0))
        if min_len:
            for i in range(3):
                for j in range(min_len):
                    if ctx.theme.data[K_SPIN_BONUS_GAME]['super_board'][0][i][j] in [35, 36, 37, 38, 39, 135, 136, 137, 138, 139]:
                        jp_win_fix = JP_RESET[39 - (ctx.theme.data[K_SPIN_BONUS_GAME]['super_board'][0][i][j] % 100)] * \
                                                    ctx.theme.data['map_info']['avg_bet']
                        jp_win_type_fix = 39 - (ctx.theme.data[K_SPIN_BONUS_GAME]['super_board'][0][i][j] % 100)
                        ctx.theme.data[K_SPIN_BONUS_GAME]['jp_win_temp'].append({'jp_win': jp_win_fix,
                                                                                 'jp_win_type': jp_win_type_fix})
                        ctx.theme.data[K_SPIN_BONUS_GAME]['respin_total_win'] += jp_win_fix
                        ctx.theme.data[K_SPIN_BONUS_GAME]['total_win'] += jp_win_fix


def do_level_up(ctx, ret):    # 该方法会在玩家每次升级之后进行
    ret['bonus_level'] = get_bonus_level_bet(ctx)  # 例如将新的bonus_level返回给前端

def special_theme_rtp_control(ctx):
    return daily_config.AC_CONFIG['super_nm_control']['theme_242']

def do_spin(ctx, req):   # 玩家batch_spin会进入该方法
    bet = ctx.bet        # 获得bet
    game_type = config.get_theme_config(ctx.user.package, ctx.theme.theme_id)['type']  # 获得游戏类型 例如 normal high quest

    if 'bonus_level' in req and ctx.property.is_admin:  # 更改bonus_level内容配合解锁JP，Shopping等
        bonus_level = int(req['bonus_level'])
    else:
        bonus_level = -1
        for ii, i_value in enumerate(sorted(get_bonus_level_bet(ctx))):
            if bet < i_value:
                bonus_level = ii
                break
        if bonus_level == -1 or game_type == 'high':
            bonus_level = 6

    vola_flag = 0
    bet_index = get_bet_index(ctx, game_type)
    vola_ratio = bet_index / float(24)

    prize_id = get_prize(ctx, const.ARTIFICIAL_CONTROL_BONUS, game_type)  # 获得送奖id  (在数学包里叫remote_prize)
    if prize_id == 999:      # prize_id == 999 时，为较特殊的作弊牌面送奖
        cheat = np.array(ctx.cheat).reshape(5, 3).tolist()
    else:
        cheat = ctx.cheat
    if prize_id in [400, 401]:
        prize_id -= 196

    jp_ticket_info = JackpotTicketManager.get_tickets_activity_info(ctx, 242)
    if jp_ticket_info and jp_ticket_info.get('242', {}).get('ticket') == 0 and jp_ticket_info.get('242', {}).get('il') > 0:
        if random.randint(1, 30) == 1:
            prize_id = 200

    fg_info = ctx.theme.data['fg_info']
    map_info = ctx.theme.data['map_info']
    if prize_id == 201:
        map_info['map_level'] = 5
        prize_id = 200

    if ctx.user.id == 100:
        if 'bonus_level' in req:
            bonus_level = req['bonus_level']
        if 'prize' in req:
            prize_id = req['prize']
        if 'hv' in req:
            vola_flag = req['hv']
        if 'bet' in req:
            bet = req['bet']

    ctx.theme.data['snm'] = special_theme_rtp_control(ctx)
    if ctx.user.id % 5 != 0:
        ctx.theme.data['snm'] = 0
    snm_control = ctx.theme.data['snm']
    # if ctx.user.id == 13178:
    #     snm_control = ctx.theme.data['snm'] = 1

    if ctx.theme.free_spins > 0:
        ctx.theme.data['fg_info']['spin_remaining'] = ctx.theme.free_spins
        spin = m.fg_spin(bet, bonus_level, fg_info, map_info, remote_prize=prize_id, debug_reels=cheat, hv=vola_flag)
    else:
        spin = m.ng_spin(bet, bonus_level, fg_info, map_info, remote_prize=prize_id, debug_reels=cheat, hv=vola_flag, snm=snm_control)

    ctx.reset_prize()
    return get_spin_info(spin, ctx)   # 该方法用于处理spin传出的信息 （也就是数学包里的win_info）


def get_spin_info(spin, ctx):
    ret = {K_THEME_INFO: {}}
    tid = ctx.theme.theme_id

    ret[K_THEME_INFO]['snm'] = ctx.theme.data['snm']

    if spin['map_info']:
        ret[K_THEME_INFO]['map_info'] = spin['map_info']

    if 'trigger_bw' in spin and spin['trigger_bw']:
        ret[K_THEME_INFO]['trigger_bw'] = spin['trigger_bw']

    if spin['special_type']:
        ret[K_THEME_INFO]['special_type'] = spin['special_type']

    if spin['win_free']:
        ret[K_SPIN_FREE_SPINS] = spin['win_free']['free_spins']
        ret[K_SPIN_FREE_GAME] = spin['win_free']

    if spin['badge_info']:
        ret[K_THEME_INFO]['badge_info'] = spin['badge_info']
        for i in range(6):
            ctx.theme.data['badge_info'][i] += spin['badge_info'][i]

    if ctx.theme.free_spins:
        ctx.theme.data['fg_info']['sticky_wild'] = spin['fg_info']['sticky_wild']
        ctx.theme.data['fg_info']['win_box'] += spin['total_win'] + spin['jp_total_win']
        ret[K_THEME_INFO]['sticky_wild'] = spin['fg_info']['sticky_wild']
    else:
        if not spin['map_info']['is_super'] and spin['bonus_level'] >= 3:
            ctx.theme.data['map_info']['wager'] += ctx.bet
            ctx.theme.data['map_info']['wager_count'] += 1
            ctx.theme.data['map_info']['avg_bet'] = (ctx.theme.data['map_info']['wager'] / ctx.theme.data['map_info']['wager_count'] / 10000) * 10000 if ctx.theme.data['map_info']['wager_count'] else 1000
            if ctx.theme.data['map_info']['avg_bet'] <= 10000:
                ctx.theme.data['map_info']['avg_bet'] = 10000

    if spin['win_bonus'] and ctx.theme.data['map_info']['is_super']:
        ret['jp_avg_bet'] = ctx.theme.data['map_info']['avg_bet']

    if spin['win_bonus']:
        ret[K_SPIN_BONUS_GAME] = spin['win_bonus']    # 将bonus信息封装起来放入 bonus_game字段 返回前端
        ret[K_SPIN_BONUS_GAME]['avg_bet'] = ctx.theme.data['map_info']['avg_bet']
        if ctx.theme.data['map_info']['is_super']:
            ctx.bet = ctx.theme.data['map_info']['avg_bet']
        progressive_list = copy.deepcopy(get_progressive_list(ctx, const.JP_MAP))
        ret[K_SPIN_BONUS_GAME]['progressive_list'] = copy.deepcopy(progressive_list)
        ret[K_SPIN_BONUS_GAME]['item_list_up'] = spin['item_list_up']
        ret[K_SPIN_BONUS_GAME]['item_list_down'] = spin['item_list_down']
        for i in range(5):
            if spin['lock_progressive'][i] == 0:
                ret[K_SPIN_BONUS_GAME]['progressive_list'][i] = 0
        progressive_flag = [1, 1, 1, 1, 1]
        if spin['jp_win']:
            jp_ticket_info = JackpotTicketManager.get_tickets_activity_info(ctx, 242)
            if jp_ticket_info:
                JackpotTicketManager.add_tickets(ctx, 242, len(spin['jp_win']))
            for i_index, i in enumerate(spin['win_bonus']['jp_win_temp']):
                if progressive_flag[i['jp_win_type']] and spin['lock_progressive'][i['jp_win_type']]:
                    i['jp_win'] += progressive_list[i['jp_win_type']]
                    spin['win_bonus']['respin_jp_total_win'] += progressive_list[i['jp_win_type']]
                    for j_index, j in enumerate(spin['win_bonus']['progressive_mark']):
                        if j and i['jp_win_type'] in j and progressive_flag[i['jp_win_type']]:
                            for k in range(j_index, len(spin['win_bonus']['respin_win_list'])):
                                spin['win_bonus']['respin_win_list'][k] += progressive_list[i['jp_win_type']]
                            progressive_flag[i['jp_win_type']] = 0
                    progressive_flag[i['jp_win_type']] = 0

    if spin['map_info']:
        ctx.theme.data['map_info'] = spin['map_info']

    ret.update(get_basic_info(spin, const, tid, ctx.user.package))  # 通用逻辑 处理base_win total_win 等永远存在的信息
    return ret


def update_complex_data(ctx, ret):  # 不用管这个
    if K_SPIN_JP_WIN in ret:
        if ctx.theme.free_spins > 0:
            ctx.theme.data[K_SPIN_FREE_GAME][K_SPIN_JP_WIN] = ret[K_SPIN_JP_WIN]


def get_map_progress(ctx):
    if 'map_info' in ctx.theme.data:
        return ctx.theme.data['map_info']['map_level'] / 6.0 if ctx.theme.data['map_info']['map_level'] <= 6 else 0
    else:
        return 0


def do_check_win_legitimacy(bet, win, game_type):
    win_multi = win / bet
    if win_multi > LEGITIMACY_CHECK.get(game_type, 9999999999):
        return True
    return False


def do_collect(ctx, req, ret):  # 在前端发送collect_coin请求之后的个性化处理
    if req['type'] == 0:
        ctx.theme.data['fg_info']['sticky_wild'] = []
        ctx.theme.data['fg_info']['win_box'] = 0
        ctx.theme.data['fg_info']['first_fg'] = 0
        ctx.theme.data['fg_info']['spin_remaining'] = 0
        ctx.theme.data['badge_info'][1] = 0
        ctx.theme.data['badge_info'][5] = 0
    elif req['type'] == 1:
        ctx.theme.data['map_info']['first_respin'] = 0
        if ctx.theme.data['map_info']['map_level'] >= 6:
            ctx.theme.data['map_info']['map_level'] = 0
            ctx.theme.data['map_info']['wager'] = ctx.theme.data['map_info']['avg_bet']
            ctx.theme.data['map_info']['wager_count'] = 1
            ctx.theme.data['map_info']['is_super'] = 0
        ctx.theme.data['badge_info'][0] = 0
        ctx.theme.data['badge_info'][2] = 0
        ctx.theme.data['badge_info'][3] = 0
        ctx.theme.data['badge_info'][4] = 0


def update_badge_task(ctx, ret, task_type, win, game_type):
    # BADGE:
    # 1：完成一次super respin
    # 2：累计在free game中获得300个sticky wild
    # 3：在一次respin中消除7行(描述中是固定的7行)
    # 4：累计在respin中获得XX个extra spin
    # 5：在一次respin中获得5个JP(描述中是固定的5个)
    # 6：触发一次5个scatter的free game
    delta_current = 0
    if 2421 == task_type and game_type == 'bonus' and ctx.theme.data['badge_info'][0]:
        delta_current += 1
    elif 2422 == task_type and K_THEME_INFO in ret and 'badge_info' in ret[K_THEME_INFO]:
        delta_current += ret[K_THEME_INFO]['badge_info'][1]
    elif 2423 == task_type and game_type == 'bonus' and ctx.theme.data['badge_info'][2]:
        if ctx.theme.data['badge_info'][2] >= 7:
            delta_current += 1
    elif 2424 == task_type and game_type == 'bonus' and ctx.theme.data['badge_info'][3]:
        delta_current += ctx.theme.data['badge_info'][3]
    elif 2425 == task_type and game_type == 'bonus' and ctx.theme.data['badge_info'][4] >= 3:
        delta_current += 1
    elif 2426 == task_type and game_type == 'free' and ctx.theme.data['badge_info'][5]:
        delta_current += 1
    return delta_current


def update_mansion_quest(ctx, ret, mansion_quest_type, is_free_spin, game_type, **kwargs):
    delta_current = 0
    if mansion_quest_type == 1060 and game_type == 'bonus' and K_SPIN_BONUS_GAME in ctx.theme.data and \
            'coin_del_num' in ctx.theme.data[K_SPIN_BONUS_GAME]:
        delta_current += ctx.theme.data[K_SPIN_BONUS_GAME]['coin_del_num']
    elif mansion_quest_type == 2060 and game_type == 'free':
        delta_current += ctx.theme.data['fg_info']['win_box']
    elif mansion_quest_type == 105:
        if K_SPIN_THEME_INFO in ret and 'trigger_bw' in ret[K_SPIN_THEME_INFO]:
            delta_current += ret[K_SPIN_THEME_INFO]['trigger_bw']
    else:
        delta_current += 0
    return delta_current


# def update_quest(ctx, ret):    # 用于完成quest任务

# def update_quest_in_bonus_collect(ctx,ret):

# def update_quest_in_free_collect(ctx,ret):


import copy
import time

from math import ThemeMath
from slots_math.simulation import Simulation
from math_configs.reel_config import *
import os
import random

path = os.path.dirname(os.path.abspath(__file__))

BET = 100000
COUNT = 10000000
# OUTPUT = [path, "prize_ssw", 10000]
OUTPUT = []
DECIMAL = 3
PRIZE = 0
PRINT_COUNT = 2500
BONUS_LEVEL = 6
HIGH_VOLATILITY = 0
SUPER_NEAR_MISS = 0


class ThemeSimulation(Simulation):
    def simulate(self, bet, n, prize=PRIZE):
        # <editor-fold desc='parameter'>
        a = time.time()
        statistics = {}
        rec = {
            'ng': {
                'wins': [0, 0],
                'jkpt': [0, 0],
                'hits': 0,
                'fgtr': [0, 0],
                'resp': [0, 0],
            },
            'fg': {
                'wins': [0, 0],
                'jkpt': [0, 0],
                'hits': 0,
                'fgtr': [0, 0],
                'resp': [0, 0],
            },
            'bets': 0,
            'wins': 0
        }
        vola_info = {
            'curr_balance': 60 * bet,
            'bet': bet,
            'vola_list': [],
            'spin_count': 0,
            'rec_win': 0
        }
        free_spins = 0
        fg_info = copy.deepcopy(FG_INFO_SET)
        map_info = copy.deepcopy(MAP_INFO_INI)
        bw_count = 1
        hw_count = 1
        mw_count = 1
        bad_fg = 0
        nice_fg = 0
        big_line_win = [0, 0]
        huge_line_win = [0, 0]
        anti_count = 0
        jp_count = [0, 0, 0, 0, 0]
        badge_list = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        map_count = [0, 0, 0]
        respin_count = [[0, 0], [0, 0]]
        mansion_log = [0, 0]
        # </editor-fold desc='parameter'>

        for i in xrange(n):
            rec['bets'] += bet
            # reel = [ [ 38, 53, 1 ], [ 36, 1, 1 ], [ 41, 1, 1 ], [ 52, 43, 1 ], [ 22, 37, 1 ] ]
            win_info = self.theme.ng_spin(bet, BONUS_LEVEL, fg_info, map_info, remote_prize=prize, hv=HIGH_VOLATILITY, snm=SUPER_NEAR_MISS)
            fg_info = win_info['fg_info']
            map_info = win_info['map_info']
            map_info['wager'] += bet
            map_info['wager_count'] += 1
            map_info['avg_bet'] = map_info['wager']  / map_info['wager_count']
            if win_info['jp_total_win']:
                # self.output(win_info)
                for j in win_info['jp_win']:
                    jp_count[j['jp_win_type']] += 1
                self.update_record(rec, [1, win_info['jp_total_win']], 'ng', 'jkpt')
            fg_win = 0
            if win_info['win_free']:
                # self.output(win_info)
                free_spins += win_info['win_free']['free_spins']
                fg_win += win_info['total_win'] + win_info['jp_total_win']
                if win_info['badge_info'][5]:
                    badge_list[5][0] += 1
                self.update_record(rec, [1, win_info['win_free']['free_spins']], 'ng', 'fgtr')
            if win_info['win_bonus']:
                # self.output(win_info)
                self.update_record(rec, [1, win_info['win_bonus']['respin_total_win']], 'ng', 'resp')
                respin_count[map_info['is_super']][0] += 1
                respin_count[map_info['is_super']][1] += win_info['total_win'] + win_info['jp_total_win']
                map_info['first_respin'] = 0
                if map_info['map_level'] > 5:
                    map_info['map_level'] = 0
                    map_info['is_super'] = 0
                    badge_list[0][0] += 1
                if win_info['badge_info'][2] >= 7:
                    badge_list[2][0] += 1
                badge_list[3][1] += win_info['badge_info'][3]
                if badge_list[3][1] >= 100:
                    badge_list[3][0] += 1
                    badge_list[3][1] = 0
                if win_info['badge_info'][4] >= 5:
                    badge_list[4][0] += 1
                mansion_log[0] += 1
                mansion_log[1] += win_info['badge_info'][2] * 5
            if win_info['base_win']:
                if win_info['base_win'] >= 10 * bet:
                    huge_line_win[0] += 1
                    huge_line_win[1] += win_info['base_win']
                elif 10 * bet > win_info['base_win'] >= 5 * bet:
                    # print len(win_info['win_lines'])
                    big_line_win[0] += 1
                    big_line_win[1] += win_info['base_win']
                self.update_record(rec, [1, win_info['base_win']], 'ng', 'wins')
            if win_info['total_win'] or win_info['jp_total_win'] or win_info['win_free']:
                self.update_record(rec, [1], 'ng', 'hits')

            # if not win_info['win_bonus'] and not win_info['win_free'] and win_info['base_win']:
            #     if 0.5 * bet  >=  win_info['base_win'] > 0 * bet:
            #     #     self.output(win_info)
            #         symbol_count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            #         coin_count = 0
            #         scatter_count = 0
            #         for mm in range(5):
            #             for nn in range(3):
            #                 if win_info['item_list'][mm][nn] < 12:
            #                     symbol_count[win_info['item_list'][mm][nn]] += 1
            #                 elif win_info['item_list'][mm][nn] == 13:
            #                     scatter_count += 1
            #                 elif win_info['item_list'][mm][nn] >= 20:
            #                     coin_count += 1
            #         if max(symbol_count) >= 8 or (coin_count == 5 and max(symbol_count) >= 5):
            #             # print win_info['base_win']
            #             self.output(win_info)
                # self.output(win_info)
            # else:
            #     self.output(win_info)

            self.update_record(rec, [win_info['total_win'] + win_info['jp_total_win']], 'wins')
            self.update_volatility_list(vola_info, rec['wins'])

            if 10 * bet <= win_info['total_win'] + win_info['jp_total_win'] < 25 * bet:
                bw_count += 1
            if 25 * bet <= win_info['total_win'] + win_info['jp_total_win'] < 50 * bet:
                hw_count += 1
            if win_info['total_win'] + win_info['jp_total_win'] >= 50 * bet:
                mw_count += 1

            while free_spins > 0:
                win_info = self.theme.fg_spin(bet, BONUS_LEVEL, fg_info, map_info)
                badge_list[1][1] += win_info['badge_info'][1]
                if badge_list[1][1] >= 300:
                    badge_list[1][0] += 1
                    badge_list[1][1] = 0
                fg_info = win_info['fg_info']
                if win_info['jp_total_win']:
                    for j in win_info['jp_win']:
                        jp_count[j['jp_win_type']] += 1
                    self.update_record(rec, [1, win_info['jp_total_win']], 'fg', 'jkpt')
                if win_info['win_bonus']:
                    # self.output(win_info)
                    respin_count[map_info['is_super']][0] += 1
                    respin_count[map_info['is_super']][1] += win_info['total_win'] + win_info['jp_total_win']
                    map_info['first_respin'] = 0
                    if map_info['map_level'] > 5:
                        map_info['map_level'] = 0
                        map_info['is_super'] = 0
                        badge_list[0][0] += 1
                    if win_info['badge_info'][2] >= 7:
                        badge_list[2][0] += 1
                    badge_list[3][1] += win_info['badge_info'][3]
                    if badge_list[3][1] >= 100:
                        badge_list[3][0] += 1
                        badge_list[3][1] = 0
                    if win_info['badge_info'][4] >= 5:
                        badge_list[4][0] += 1
                    mansion_log[0] += 1
                    mansion_log[1] += win_info['badge_info'][2] * 5
                    self.update_record(rec, [1, win_info['win_bonus']['respin_total_win']], 'fg', 'resp')
                if win_info['win_free']:
                    # self.output(win_info)
                    free_spins += win_info['win_free']['free_spins']
                    self.update_record(rec, [1, win_info['win_free']['free_spins']], 'fg', 'fgtr')
                if win_info['base_win']:
                    # if 10 * bet >= win_info['base_win'] >= 5 * bet and fg_info['row_count'] == 3:
                    #     self.output(win_info)
                    self.update_record(rec, [1, win_info['base_win']], 'fg', 'wins')
                if win_info['total_win'] or win_info['jp_total_win'] or win_info['win_free']:
                    rec['fg']['hits'] += 1
                    self.update_record(rec, [1], 'fg', 'hits')
                # else:
                #     self.output(win_info)
                fg_win += win_info['total_win'] + win_info['jp_total_win']

                self.update_record(rec, [win_info['total_win'] + win_info['jp_total_win']], 'wins')
                self.update_volatility_list(vola_info, rec['wins'])

                if 10 * bet <= win_info['total_win'] + win_info['jp_total_win'] < 25 * bet:
                    bw_count += 1
                if 25 * bet <= win_info['total_win'] + win_info['jp_total_win'] < 50 * bet:
                    hw_count += 1
                if win_info['total_win'] + win_info['jp_total_win'] >= 50 * bet:
                    mw_count += 1

                free_spins -= 1
                if free_spins == 0:
                    fg_info['win_box'] = 0
                    fg_info['sticky_wild'] = []
                    fg_info['first_fg'] = 0
                    if fg_win < 5 * bet:
                        bad_fg += 1
                    if fg_win >= 25 * bet:
                        nice_fg += 1

            if i % PRINT_COUNT == 0:
                b = time.time()
                per_spin_sec = i / (b - a) if b - a > 0 else 0
                if i > 0:
                    count = float(i)
                    fg_count = float(rec['ng']['fgtr'][1]+rec['fg']['fgtr'][1]) if rec['ng']['fgtr'][1]+rec['fg']['fgtr'][1]>0 else 1

                    ###############################################
                    # RTP
                    ###############################################
                    data = self.calculate_standard_result(rec, count)

                    ###############################################
                    # HITS & FREQ
                    ###############################################
                    hits_ratio = (rec['ng']['hits'] + rec['fg']['hits']) / count

                    ng_base_hits_ratio = rec['ng']['wins'][0] / count
                    fg_base_hits_ratio = rec['fg']['wins'][0] / fg_count
                    base_hits_ratio = (rec['ng']['wins'][0] + rec['fg']['wins'][0]) / count

                    ###############################################
                    # AVG FREE SPINS
                    ###############################################
                    ng_fgtr_spins = rec['ng']['fgtr'][1] / float(rec['ng']['fgtr'][0]) if float(rec['ng']['fgtr'][0]) > 0 else 0
                    fgtr_spins = fg_count / float(rec['ng']['fgtr'][0]) if float(rec['ng']['fgtr'][0]) > 0 else 0

                    bw_freq = count / float(bw_count)
                    hw_freq = count / float(hw_count)
                    mw_freq = count / float(mw_count)

                    anti_freq = count / float(anti_count) if anti_count else 0
                    anti_pec = anti_count / float(rec['ng']['fgtr'][0]) if float(rec['ng']['fgtr'][0]) else 0

                    bad_fg_pec = bad_fg / float(rec['ng']['fgtr'][0]) if float(rec['ng']['fgtr'][0]) else 0
                    nice_fg_pec = nice_fg / float(rec['ng']['fgtr'][0]) if float(rec['ng']['fgtr'][0]) else 0

                    jp_freq = [0, 0, 0, 0, 0]
                    for j in range(5):
                        jp_freq[j] = count / float(jp_count[j]) if jp_count[j] else 0

                    normal_respin_ev = respin_count[0][1] / float(respin_count[0][0] * bet) if respin_count[0][0] else 0
                    super_respin_ev = respin_count[1][1] / float(respin_count[1][0] * map_info['avg_bet']) if respin_count[1][0] else 0

                    big_line_freq = count / float(big_line_win[0]) if float(big_line_win[0]) else 0
                    big_line_ev = float(big_line_win[1]) / bet / float(big_line_win[0]) if float(big_line_win[0]) else 0

                    huge_line_freq = count / float(huge_line_win[0]) if float(huge_line_win[0]) else 0
                    huge_line_ev = float(huge_line_win[1]) / bet / float(huge_line_win[0]) if float(
                        huge_line_win[0]) else 0

                    if vola_info['vola_list']:
                        volatility_rate = sorted(vola_info['vola_list'])[len(vola_info['vola_list']) / 2 - 1]
                    else:
                        volatility_rate = 0

                    badge_freq = [0, 0, 0, 0, 0, 0]
                    for j in range(6):
                        badge_freq[j] = count / badge_list[j][0] if badge_list[j][0] > 0 else 0

                    mansion_freq = count / float(mansion_log[0])
                    mansion_ev = mansion_log[1] / float(mansion_log[0])

                    statistics = [
                        ['Overall', [
                            [[data['rtp'], data['rtp_check'], hits_ratio], 'RTP'],
                            [[data['wins_rtp'], base_hits_ratio], 'Lines'],
                            [[bw_freq], 'Big Win'],
                            [[hw_freq], 'Huge Win'],
                            [[mw_freq], 'Massive Win'],
                            [[jp_freq[4]], 'JP Mini'],
                            [[jp_freq[3]], 'JP Minor'],
                            [[jp_freq[2]], 'JP Major'],
                            [[jp_freq[1]], 'JP Mega'],
                            [[jp_freq[0]], 'JP Grand'],
                            [[per_spin_sec], 'Spins Per Sec'],
                            [[volatility_rate], ['Low Volatility', 'High Volatility'][HIGH_VOLATILITY]],
                        ]],
                        ['Normal Game', [
                            [[data['ng_rtp'], data['ng_hits_ratio']], 'RTP'],
                            [[data['ng_wins_rtp'], ng_base_hits_ratio], 'Lines'],
                            [[big_line_ev, big_line_freq], '5-10 Line Win'],
                            [[huge_line_ev, huge_line_freq], '> 10 Line Win'],
                            [[data['ng_jkpt_rtp'], data['ng_jkpt_freq']], 'Jackpot'],
                            [[data['ng_resp_rtp'], data['ng_resp_freq']], 'Respin'],
                            [[normal_respin_ev], 'Normal Respin EV'],
                            [[super_respin_ev], 'Super Respin EV'],
                            [[ng_fgtr_spins, data['ng_fgtr_freq']], 'FG Trigger'],
                            [[anti_freq, anti_pec], 'Anti'],
                            [[mansion_freq, mansion_ev], 'Mansion'],
                        ]],
                        ['Free Game', [
                            [[data['fg_rtp'], data['fg_hits_ratio']], 'RTP'],
                            [[data['fg_wins_rtp'], fg_base_hits_ratio], 'Lines'],
                            [[data['fg_jkpt_rtp'], data['fg_jkpt_freq']], 'Jackpot'],
                            [[data['fg_resp_rtp'], data['fg_resp_freq']], 'Respin'],
                            [[bad_fg_pec], 'Bad FG Pec'],
                            [[nice_fg_pec], 'HUGE FG Pec'],
                        ]],
                        ['Badge', [
                            [[badge_freq[0]], [-1], 'Badge 1'],
                            [[badge_freq[1]], [-1], 'Badge 2'],
                            [[badge_freq[2]], [-1], 'Badge 3'],
                            [[badge_freq[3]], [-1], 'Badge 4'],
                            [[badge_freq[4]], [-1], 'Badge 5'],
                            [[badge_freq[5]], [-1], 'Badge 6'],
                        ]]
                    ]
                    self.print_statistics(statistics, i, n)
        self.print_statistics(statistics, n, n)
        if n >= 1000000:
            self.report_statistics(statistics, 102, n,prize)


def run(pay_tree_path):
    s = ThemeSimulation(ThemeMath(pay_tree_path), decimal=DECIMAL, tolerance=0.05, output_config=OUTPUT)
    s.simulate(BET, COUNT, prize=PRIZE)
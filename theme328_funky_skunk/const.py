# -*- coding: utf-8 -*-
THEME_NAME = "Oriental Fortune"  # 主题名
DEFAULT_RTP = 95
THEME_ID = 242            # 主题id
THEME_TYPE = "Line"       # "Line"
ROWS = 3                  # 行数
REELS = 5                 # 列数
BET_BASE = 10000          # BaseBet
MAX_LINE = 50             # Line数量（选填）
PRIZE = [
    [
        [100, 'Free Game'],
        [101, 'Free Game (Retrigger)'],
    ],
    [
        [200, 'Bonus'],
        [201, 'Super Bonus'],
        [202, 'Bonus add respin'],
        [203, 'Bonus multi win'],
        [204, 'Bonus Grand'],
        [205, 'Bonus Maxi'],
        [206, 'Bonus Major'],
        [207, 'Bonus Minor'],
        [208, 'Bonus Mini'],
        [209, 'Bonus JPs'],
        [210, 'Checkout SNM'],
    ],
    [
        [300, 'Big Win'],
        [301, 'Huge Win'],
        [302, 'small Win'],
        [303, 'Middle Win']
    ],
    [
        [1, '1.5 RTP'],
        [2, '2.0 RTP'],
        [3, '2.5 RTP'],
        [4, '3.0 RTP'],
        [9, 'Near Miss'],
        [10, '0.5 RTP'],
        [11, '0.75 RTP'],
    ],
    [
        [400, 'Bonus Grand'],
        [401, 'Bonus Maxi']
    ],
]


JP_RESET = [1000, 100, 50, 25, 10]


JP_MAP = {    # 对应三个主题ID分别是 1xx 6xx 11xx 普通房 高级房 quest
    '242': [717, 718, 719, 720, 721],
    '742': [717, 718, 719, 720, 721],
    '1235': []
}

ARTIFICIAL_CONTROL_BONUS = [200]  # 不用管


LEGITIMACY_CHECK = {
    'base': 200,
    'free': 1000,
    'bonus': 2000,
}

USER_INPUT = [  # 用于在网站中选择bonus_level
    ['bonus_level',
     'Bonus Level',
     'ALL',
     [[0, 'All Lock'],
      [1, 'Unlock Mini'],
      [2, 'Unlock Minor'],
      [3, 'Unlock Map'],
      [4, 'Unlock Major'],
      [5, 'Unlock Maxi'],
      [6, 'Unlock Grand']]]
]

# 课程数据:经典程序化练习法 —— 看局面、自己想、对答案,反复识别杀王模式形成直觉。
# 所有棋题均经过 python-chess 引擎逐一校验(见 backend/scripts/validate_curriculum.py)。
#
# 本文件由 backend/scripts/convert_curriculum.sh 生成;修改请直接编辑本文件,
# 改完必须跑校验:.venv/bin/python backend/scripts/validate_curriculum.py

CHAPTERS = [{'id': 'warmup',
  'badge': {'zh': '热身站', 'en': 'Warm-up'},
  'title': {'zh': '认识棋子朋友', 'en': 'Meet the Pieces'},
  'intro': {'zh': '先和六个棋子朋友打个招呼,学会它们怎么走。',
            'en': 'Say hi to the six piece friends and learn how they move.'},
  'color': '#8C6D3F',
  'soft': '#F3E7CE',
  'levels': [{'id': 'w1',
              'title': {'zh': '棋子走法小课堂', 'en': 'How the Pieces Move'},
              'goal': {'zh': '学会六种棋子的走法', 'en': 'Learn how all six pieces move'},
              'skill': {'zh': '六种棋子走法', 'en': 'Moves of all six pieces'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '直走与斜走:车、象、后',
                                   'en': 'Straight and Diagonal: Rook, Bishop, Queen'},
                         'text': [{'zh': '车走直线,横竖都行;象走斜线,像滑滑梯;后最厉害,直线斜线都会。',
                                   'en': 'The rook moves in straight lines; the bishop slides '
                                         'diagonally; the queen does both — she is the strongest!'},
                                  {'zh': '注意:它们都不能跳过别的棋子。下面挨个试一试!',
                                   'en': "Careful: they can't jump over other pieces. Now try each "
                                         'one below!'}],
                         'fen': '4k3/8/8/8/8/8/8/R2QK2B w - - 0 1',
                         'arrows': [['a1', 'a5'], ['d1', 'h5'], ['h1', 'c6']]},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/8/8/8/R3K3 w - - 0 1',
                         'prompt': {'zh': '车走直线:把车从 a1 走到 a5!',
                                    'en': 'The rook moves straight: move it from a1 to a5!'},
                         'accepted': ['a1a5'],
                         'hint': {'zh': '先点车,再点同一条竖线上的 a5。',
                                  'en': 'Tap the rook, then tap a5 on the same file.'},
                         'successText': {'zh': '车直直地走上了 a5。',
                                         'en': 'The rook zoomed straight to a5.'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/8/8/8/2B1K3 w - - 0 1',
                         'prompt': {'zh': '象走斜线:把象从 c1 滑到 g5!',
                                    'en': 'The bishop moves diagonally: slide it from c1 to g5!'},
                         'accepted': ['c1g5'],
                         'hint': {'zh': '找斜线:c1-d2-e3-f4-g5。',
                                  'en': 'Follow the diagonal: c1-d2-e3-f4-g5.'},
                         'successText': {'zh': '象沿着斜线滑到了 g5。', 'en': 'The bishop slid to g5.'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/8/8/8/3QK3 w - - 0 1',
                         'prompt': {'zh': '后两样都会:让皇后从 d1 斜走到 h5!',
                                    'en': 'The queen does both: move her from d1 to h5!'},
                         'accepted': ['d1h5'],
                         'hint': {'zh': '斜线:d1-e2-f3-g4-h5。', 'en': 'Diagonal: d1-e2-f3-g4-h5.'},
                         'successText': {'zh': '皇后驾到 h5!', 'en': 'The queen arrives on h5!'}},
                        {'type': 'teach',
                         'title': {'zh': '特殊走法:马、兵、王', 'en': 'Special Moves: Knight, Pawn, King'},
                         'text': [{'zh': '马跳“日”字,还能跳过别的棋子;兵只许向前,第一步可冲两格,吃子要斜着吃;王每次只走一格,但八个方向都行。',
                                   'en': 'The knight jumps in an L-shape and can hop over pieces; '
                                         'pawns only go forward — two squares on their first move '
                                         '— but capture diagonally; the king moves one square in '
                                         'any direction.'},
                                  {'zh': '王是最宝贵的:王被吃掉(将死)就输啦!',
                                   'en': 'The king is the most precious: if he is checkmated, you '
                                         'lose!'}],
                         'fen': '4k3/8/8/8/8/8/4P3/1N2K3 w - - 0 1',
                         'arrows': [['b1', 'c3'], ['e2', 'e4'], ['e1', 'e2']]},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/8/8/8/1N2K3 w - - 0 1',
                         'prompt': {'zh': '马跳“日”字:从 b1 跳到 c3!',
                                    'en': 'The knight jumps in an L: hop from b1 to c3!'},
                         'accepted': ['b1c3'],
                         'hint': {'zh': '先直走两格,再拐一格。',
                                  'en': 'Two squares straight, then one to the side.'},
                         'successText': {'zh': '马蹄哒哒,跳到 c3。',
                                         'en': 'Clip-clop! The knight lands on c3.'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/8/8/4P3/4K3 w - - 0 1',
                         'prompt': {'zh': '小兵冲锋:从 e2 冲到 e4!',
                                    'en': 'Pawn charge: rush from e2 to e4!'},
                         'accepted': ['e2e4'],
                         'hint': {'zh': '小兵第一步可以冲两格。',
                                  'en': 'A pawn may dash two squares on its first move.'},
                         'successText': {'zh': '小兵冲到 e4。', 'en': 'The pawn charges to e4.'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/8/8/8/4K3 w - - 0 1',
                         'prompt': {'zh': '王慢慢走:从 e1 走到 e2!',
                                    'en': 'The king strolls: step from e1 to e2!'},
                         'accepted': ['e1e2'],
                         'hint': {'zh': '王一次只走一格。',
                                  'en': 'The king moves just one square at a time.'},
                         'successText': {'zh': '六个棋子朋友都学会啦!',
                                         'en': 'You know all six piece friends now!'}}]},
             {'id': 'w-special',
              'title': {'zh': '三种特殊走法', 'en': 'Three Special Moves'},
              'goal': {'zh': '学会王车易位、兵的升变、吃过路兵', 'en': 'Learn castling, promotion, and en passant'},
              'skill': {'zh': '特殊走法', 'en': 'Special moves'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '书上的三个“例外规则”', 'en': 'Three Exception Rules'},
                         'text': [{'zh': '国际象棋有三种不走寻常路的特殊走法,一个一个来看:',
                                   'en': 'Chess has three special moves that break the usual '
                                         'rules. Let us see them one by one:'},
                                  {'zh': '① 王车易位:王和车一起跳,让王躲到安全角落;',
                                   'en': '1. Castling: the king and rook jump together to tuck the '
                                         'king into a safe corner.'},
                                  {'zh': '② 兵的升变:小兵冲到底线,变身成皇后;',
                                   'en': '2. Promotion: a pawn that reaches the last rank turns '
                                         'into a queen!'},
                                  {'zh': '③ 吃过路兵:对方小兵冲两格路过你旁边,你可以斜着吃掉它。',
                                   'en': '3. En passant: if an enemy pawn dashes two squares past '
                                         'yours, you may capture it diagonally.'},
                                  {'zh': '下面一个一个来试!', 'en': 'Now try each one!'}]},
                        {'type': 'move',
                         'fen': 'r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1',
                         'prompt': {'zh': '① 王车易位:把白王从 e1 走到 g1,看看会发生什么神奇的事!',
                                    'en': '1. Castling: move the white king from e1 to g1 and '
                                          'watch the magic!'},
                         'accepted': ['e1g1'],
                         'hint': {'zh': '点王,再点 g1(跳过 f1)——车会自动跳到王旁边!',
                                  'en': 'Tap the king, then g1 (skipping f1) — the rook hops over '
                                        'by itself!'},
                         'successText': {'zh': '王车易位完成!记住三个条件:王和车都没动过、中间没有棋子、王没被将军也不经过受攻击的格子。',
                                         'en': 'Castled! Remember the three rules: king and rook '
                                               'never moved, nothing between them, and the king is '
                                               'not in check nor passes through an attacked '
                                               'square.'}},
                        {'type': 'move',
                         'fen': '7k/P7/8/8/8/8/8/K7 w - - 0 1',
                         'prompt': {'zh': '② 兵的升变:小兵冲到对面底线就能变身!让 a7 的小兵冲到底线!',
                                    'en': '2. Promotion: a pawn reaching the far rank transforms! '
                                          'Push the a7 pawn to the last rank!'},
                         'accepted': ['a7a8', 'a7a8q'],
                         'hint': {'zh': '点小兵,再点 a8——它会变成皇后!',
                                  'en': 'Tap the pawn, then a8 — it becomes a queen!'},
                         'successText': {'zh': '升变成功!a8 皇后诞生,还顺便将军!(残局篇还会专门练这个)',
                                         'en': 'Promoted! A queen is born on a8 — with check! (The '
                                               'endgame chapter practices this more.)'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2',
                         'prompt': {'zh': '③ 吃过路兵:黑兵刚从 d7 冲两格到 d5,想从白兵身边溜过去!白兵可以斜走一格到 d6,把它吃掉。试试!',
                                    'en': '3. En passant: the black pawn just dashed from d7 to '
                                          'd5, sneaking past your pawn! Capture it by moving your '
                                          'pawn diagonally to d6. Try it!'},
                         'accepted': ['e5d6'],
                         'hint': {'zh': '点 e5 的白兵,再点 d6(黑兵右前方的空格)。',
                                  'en': 'Tap your e5 pawn, then d6 (the empty square beside the '
                                        'black pawn).'},
                         'successText': {'zh': '吃过路兵!白兵斜到 d6,d5 的黑兵被吃掉了。记住:只能趁它刚冲两格的下一回合吃!',
                                         'en': 'En passant! Your pawn lands on d6 and the d5 pawn '
                                               'is gone. Remember: you can only do this right '
                                               'after the enemy pawn dashes two squares!'}}]},
             {'id': 'w2',
              'title': {'zh': '第一次“将死”', 'en': 'Your First Checkmate'},
              'goal': {'zh': '体验把对方王“将死”',
                       'en': 'Feel what it is like to checkmate the enemy king'},
              'skill': {'zh': '将军与将死的直觉', 'en': 'Instinct for check and mate'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '将军与将死', 'en': 'Check and Checkmate'},
                         'text': [{'zh': '你的棋子攻击对方的王,叫“将军”——拉响警报!',
                                   'en': 'When your piece attacks the enemy king, that is "check" '
                                         '— the alarm rings!'},
                                  {'zh': '如果王怎么都逃不掉,就叫“将死”,你就赢了。',
                                   'en': 'If the king cannot escape at all, that is "checkmate" — '
                                         'you win!'},
                                  {'zh': '记住:学棋先学将死,赢棋的感觉最棒!',
                                   'en': 'Remember: learn checkmate first — winning feels the '
                                         'best!'}],
                         'fen': '6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1'},
                        {'type': 'mate',
                         'fen': '6k1/5ppp/8/8/8/8/8/4R1K1 w - - 0 1',
                         'prompt': {'zh': '白棋先走,一步把黑王将死!',
                                    'en': 'White to move — checkmate in one!'},
                         'hint': {'zh': '黑王身后被自己的小兵堵死了。把车开到底线去!',
                                  'en': 'The black king is boxed in by its own pawns. Drive the '
                                        'rook to the back rank!'},
                         'successText': {'zh': '将死!这就是著名的“底线杀”。',
                                         'en': 'Checkmate! This is the famous "back-rank mate".'}},
                        {'type': 'mate',
                         'fen': '7k/6pp/8/8/8/8/8/R5K1 w - - 0 1',
                         'prompt': {'zh': '黑王躲进了角落 h8,还能一步将死吗?',
                                    'en': 'The black king hides in the corner on h8. Can you still '
                                          'mate in one?'},
                         'hint': {'zh': '角落里更没有退路。车冲到底线!',
                                  'en': 'The corner has even fewer escapes. Rook to the back '
                                        'rank!'},
                         'successText': {'zh': 'Ra8 将死!角落也不是避风港。',
                                         'en': 'Ra8 mate! The corner is no safe harbor '
                                               'either.'}}]}]},
 {'id': 'endgame',
  'badge': {'zh': '第一章', 'en': 'Chapter 1'},
  'title': {'zh': '终局实验室', 'en': 'Endgame Lab'},
  'intro': {'zh': '单车、单后、单马、单象、单兵——谁能杀死光杆王？怎么杀？这是每个棋手的第一课。',
            'en': 'Rook, queen, knight, bishop, pawn — which can mate a bare king, and how? This '
                  'is every chess player’s first lesson.'},
  'color': '#2E7D52',
  'soft': '#DFF0E5',
  'levels': [{'id': 'e1',
              'title': {'zh': '单车能杀单王吗？', 'en': 'Can a lone rook mate a bare king?'},
              'goal': {'zh': '答案：能！但必须王车配合',
                       'en': 'Answer: yes! But king and rook must work together'},
              'skill': {'zh': '单车杀王', 'en': 'Rook mate'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '车一个人做不到', 'en': "The rook can't do it alone"},
                         'text': [{'zh': '单车能杀死光杆王吗？能——但光靠车自己做不到！',
                                   'en': 'Can a lone rook mate a bare king? Yes — but not by '
                                         'itself!'},
                                  {'zh': '秘诀是“王车配合”：白王负责把黑王赶到棋盘边，车负责切断退路。',
                                   'en': 'The secret is teamwork: the white king herds the black '
                                         'king to the edge while the rook cuts off escapes.'},
                                  {'zh': '记住：杀王永远是团队工作，王也是战斗力！',
                                   'en': 'Remember: mating is always teamwork — the king is a '
                                         'fighting piece too!'}],
                         'fen': '8/8/8/4k3/8/8/8/R6K w - - 0 1'},
                        {'type': 'mate',
                         'fen': '6k1/8/6K1/8/8/8/8/R7 w - - 0 1',
                         'prompt': {'zh': '白王已经到位，封死了黑王向下的逃路。该车了：一步将死！',
                                    'en': "The white king is in place, sealing the black king's "
                                          "way down. The rook's turn: mate in one!"},
                         'hint': {'zh': '黑王下不去，也吃不了远处的车——冲到底线！',
                                  'en': "The king can't go down or reach the faraway rook — charge "
                                        'to the back rank!'},
                         'successText': {'zh': 'Ra8 将死！王封路、车砍杀，配合成功。',
                                         'en': 'Ra8 mate! King blocks, rook strikes — teamwork '
                                               'succeeds.'}},
                        {'type': 'mate',
                         'fen': 'k7/8/1K6/8/8/8/8/7R w - - 0 1',
                         'prompt': {'zh': '黑王被逼到 a8 角落，白王看着它。车在哪里出手？',
                                    'en': 'The black king is cornered on a8 with the white king '
                                          'watching. Where should the rook strike?'},
                         'hint': {'zh': '车沿 h 线冲到底线 h8！', 'en': 'Rook down the h-file to h8!'},
                         'successText': {'zh': 'Rh8 将死！角落里的王被王车夹击杀。',
                                         'en': 'Rh8 mate! The cornered king falls to the king-rook '
                                               'sandwich.'}},
                        {'type': 'line',
                         'fen': 'k7/8/8/K7/8/8/8/7R w - - 0 1',
                         'script': ['a5b6', 'a8b8', 'h1h8'],
                         'prompts': [{'zh': '这次黑王还没被逼到边！第一步：白王压到 b6，封住黑王的逃路（注意：这步不将军）。',
                                      'en': "This time the black king isn't on the edge yet! "
                                            'First: the white king presses to b6, sealing the '
                                            'escape squares (note: no check this move).'},
                                     {'zh': '黑王只剩 b8 可走……最后一击交给车：',
                                      'en': 'The black king has only b8 left… let the rook deliver '
                                            'the final blow:'}],
                         'hint': {'zh': '杀王顺序：先王逼，再车杀。别急着将军！',
                                  'en': 'Mating order: the king herds first, the rook mates last. '
                                        "Don't rush the check!"},
                         'successText': {'zh': 'Kb6! Kb8，Rh8 将死！你学会了“先逼后杀”。',
                                         'en': "Kb6! Kb8, Rh8 mate! You learned 'herd first, mate "
                                               "second'."}}]},
             {'id': 'e2',
              'title': {'zh': '单后能杀单王吗？', 'en': 'Can a lone queen mate a bare king?'},
              'goal': {'zh': '答案：能！而且最快', 'en': "Answer: yes — and it's the fastest"},
              'skill': {'zh': '单后杀王', 'en': 'Queen mate'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '皇后也要带“保镖”', 'en': 'Even the queen needs a bodyguard'},
                         'text': [{'zh': '单后杀单王，比单车还容易——但皇后同样需要自己的王配合！',
                                   'en': 'Mating with a queen is even easier than with a rook — '
                                         "but she still needs her king's help!"},
                                  {'zh': '最常用的杀法叫“贴脸杀”：皇后躲在自己王的保护圈里，',
                                   'en': "The classic finish is the 'face-to-face mate': the queen "
                                         "stays inside her own king's protection,"},
                                  {'zh': '贴到黑王旁边将军。黑王想吃她？有王保护，不敢！',
                                   'en': 'then checks right next to the black king. Capture her? '
                                         'The king is guarding — no way!'}],
                         'fen': '7k/8/6QK/8/8/8/8/8 w - - 0 1',
                         'arrows': [['g6', 'g7']]},
                        {'type': 'mate',
                         'fen': 'k7/8/2K5/8/8/8/8/1Q6 w - - 0 1',
                         'prompt': {'zh': '黑王困在 a8。皇后贴上去——但要留在白王的保护里！',
                                    'en': 'The black king is stuck on a8. Bring the queen close — '
                                          'but stay protected by the white king!'},
                         'hint': {'zh': '皇后走到 b7，白王在 c6 给她撑腰。',
                                  'en': 'Queen to b7; the white king on c6 has her back.'},
                         'successText': {'zh': 'Qb7 将死！有王保护，黑王不敢吃皇后。',
                                         'en': "Qb7 mate! Protected by the king, the queen can't "
                                               'be taken.'}},
                        {'type': 'mate',
                         'fen': 'k7/6Q1/1K6/8/8/8/8/8 w - - 0 1',
                         'prompt': {'zh': '皇后在 g7。平移一格，贴脸杀！',
                                    'en': 'The queen is on g7. Slide one square for the '
                                          'face-to-face mate!'},
                         'hint': {'zh': '滑到 a7：既贴住黑王，又在 b6 白王的保护圈里。',
                                  'en': 'Slide to a7: touching the black king while guarded by the '
                                        'b6 king.'},
                         'successText': {'zh': 'Qa7 将死！平移也能杀。',
                                         'en': 'Qa7 mate! Sideways works too.'}},
                        {'type': 'mate',
                         'fen': '7k/8/6QK/8/8/8/8/8 w - - 0 1',
                         'prompt': {'zh': '黑王在角落 h8，白王在 h6。皇后贴脸杀！',
                                    'en': 'Black king cornered on h8, white king on h6. Queen: '
                                          'face-to-face mate!'},
                         'hint': {'zh': '皇后走到 g7，紧挨着自己的王。',
                                  'en': 'Queen to g7, right beside her own king.'},
                         'successText': {'zh': 'Qg7 将死！贴脸杀完成。',
                                         'en': 'Qg7 mate! Face-to-face finish complete.'}},
                        {'type': 'line',
                         'fen': '7k/8/5K2/8/8/8/8/Q7 w - - 0 1',
                         'script': ['f6g6', 'h8g8', 'a1a8'],
                         'prompts': [{'zh': '皇后在 a1 睡大觉，先别管她！第一步：白王走到 g6，把黑王往角落里逼。',
                                      'en': 'The queen is napping on a1 — leave her! First: the '
                                            'white king walks to g6, herding the black king toward '
                                            'the corner.'},
                                     {'zh': '黑王只能躲到 g8……皇后沿 a 线冲上去收官：',
                                      'en': 'The black king can only hide on g8… now the queen '
                                            'charges up the a-file to finish:'}],
                         'hint': {'zh': '和单车杀王一个道理：先王逼，再后杀。',
                                  'en': 'Same idea as the rook mate: king herds first, queen mates '
                                        'last.'},
                         'successText': {'zh': 'Kg6! Kg8，Qa8 将死！王和后也是好搭档。',
                                         'en': 'Kg6! Kg8, Qa8 mate! King and queen are great '
                                               'partners too.'}}]},
             {'id': 'e3',
              'title': {'zh': '单马、单象能杀单王吗？', 'en': 'Can a lone knight or bishop mate a bare king?'},
              'goal': {'zh': '答案：不能！子力不足', 'en': 'Answer: no! Insufficient material'},
              'skill': {'zh': '子力评估（杀不了的棋）', 'en': "Material evaluation (mates that can't work)"},
              'steps': [{'type': 'teach',
                         'title': {'zh': '杀不了的棋，叫“子力不足”',
                                   'en': 'When mating is impossible: insufficient material'},
                         'text': [{'zh': '马和象力气太小，叫“轻子”。哪怕加上自己的王帮忙，',
                                   'en': "Knights and bishops are 'minor pieces' — not strong "
                                         'enough. Even with your own king helping,'},
                                  {'zh': '单马或单象也永远杀不死光杆王——直接判和棋！',
                                   'en': 'a lone knight or bishop can never mate a bare king — the '
                                         'game is an automatic draw!'},
                                  {'zh': '所以残局里要留心：别把棋子兑到只剩一个马或一个象。',
                                   'en': "So watch out in endgames: don't trade down to just a "
                                         'knight or a bishop.'}],
                         'fen': '8/8/8/4k3/8/8/3N4/4K3 w - - 0 1'},
                        {'type': 'move',
                         'fen': '8/8/8/4k3/8/8/3N4/4K3 w - - 0 1',
                         'prompt': {'zh': '虽然杀不死，将军还是会的：用马将军一次！（跳到 f3）',
                                    'en': "It can't mate, but it can check: check with the knight! "
                                          '(Jump to f3)'},
                         'accepted': ['d2f3'],
                         'hint': {'zh': '马从 d2 跳“日”字到 f3，正好踢到 e5 的王。',
                                  'en': 'The knight hops from d2 to f3, kicking the king on e5.'},
                         'successText': {'zh': 'Nf3+ 将军！但黑王一躲，你永远追不上将死——这就是子力不足。',
                                         'en': 'Nf3+ check! But the king steps away and you can '
                                               "never catch mate — that's insufficient material."}},
                        {'type': 'move',
                         'fen': '8/8/8/4k3/8/8/8/2B1K3 w - - 0 1',
                         'prompt': {'zh': '象也一样：将军一次试试！（走到 f4）',
                                    'en': 'Same with the bishop: give one check! (Go to f4)'},
                         'accepted': ['c1f4'],
                         'hint': {'zh': '象沿斜线 c1-d2-e3-f4。',
                                  'en': 'Bishop along the diagonal c1-d2-e3-f4.'},
                         'successText': {'zh': 'Bf4+ 将军！同样杀不死——单象单马都拿光杆王没办法。',
                                         'en': 'Bf4+ check! Still no mate — a lone bishop or '
                                               'knight can never finish a bare king.'}}]},
             {'id': 'e4',
              'title': {'zh': '单兵能杀单王吗？', 'en': 'Can a lone pawn mate a bare king?'},
              'goal': {'zh': '答案：不能——但兵会变身！', 'en': 'Answer: no — but pawns can transform!'},
              'skill': {'zh': '兵的升变', 'en': 'Pawn promotion'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '小兵的超能力：升变', 'en': "The pawn's superpower: promotion"},
                         'text': [{'zh': '小兵自己杀不了王。但它有一个超能力：冲到底线，就能“升变”——',
                                   'en': "A pawn can't mate a king by itself. But it has a "
                                         "superpower: reach the last rank and 'promote' —"},
                                  {'zh': '变成皇后（也可以变车、象、马）！变了皇后，就能杀王啦。',
                                   'en': 'turning into a queen (or a rook, bishop, or knight)! As '
                                         'a queen, it can mate.'},
                                  {'zh': '所以残局里，小兵是“未来的皇后”，要好好护送它。',
                                   'en': "So in the endgame, a pawn is a 'future queen' — escort "
                                         'it well.'}],
                         'fen': '7k/P7/8/8/8/8/8/K7 w - - 0 1',
                         'arrows': [['a7', 'a8']]},
                        {'type': 'move',
                         'fen': '7k/P7/8/8/8/8/8/K7 w - - 0 1',
                         'prompt': {'zh': 'a7 的小兵只差一步！冲到底线升变吧！',
                                    'en': 'The a7 pawn is one step away! Push to the last rank and '
                                          'promote!'},
                         'accepted': ['a7a8', 'a7a8q'],
                         'hint': {'zh': '点小兵，再点 a8——自动变成皇后。',
                                  'en': 'Tap the pawn, then a8 — it auto-promotes to a queen.'},
                         'successText': {'zh': '升变！a8 皇后诞生，还顺便将军！',
                                         'en': 'Promoted! A queen is born on a8 — with check!'}},
                        {'type': 'mate',
                         'fen': '6k1/1P6/6K1/8/8/8/8/8 w - - 0 1',
                         'prompt': {'zh': '白王封住了黑王向下的路。小兵一步升变——顺便将死！',
                                    'en': "The white king blocks the black king's way down. "
                                          'Promote the pawn — and mate at the same time!'},
                         'hint': {'zh': 'b7 冲 b8 变皇后，正好封死底线。',
                                  'en': 'b7 pushes to b8 as a queen, sealing the back rank.'},
                         'successText': {'zh': 'b8=Q 将死！小兵变身，一锤定音。',
                                         'en': 'b8=Q mate! The pawn transforms and seals the '
                                               'deal.'}},
                        {'type': 'line',
                         'fen': '6k1/8/1P4K1/8/8/8/8/8 w - - 0 1',
                         'script': ['b6b7', 'g8h8', 'b7b8q'],
                         'prompts': [{'zh': '小兵还差两步。第一步：冲到 b7 待命（黑王吓得往角落退）。',
                                      'en': 'The pawn is two steps away. First: advance to b7 and '
                                            'wait (the scared black king retreats to the corner).'},
                                     {'zh': '黑王躲到 h8……冲到底线升变，将死！',
                                      'en': 'The black king hides on h8… push to the last rank, '
                                            'promote, mate!'}],
                         'hint': {'zh': '白王看着第 7 行，黑王跑不掉——放心冲兵。',
                                  'en': "The white king guards the 7th rank — the black king can't "
                                        'escape. Push with confidence.'},
                         'successText': {'zh': 'b7! Kh8，b8=Q 将死！护送小兵任务完成。',
                                         'en': 'b7! Kh8, b8=Q mate! Pawn escort mission '
                                               'complete.'}}]}]},
 {'id': 'middlegame',
  'badge': {'zh': '第二章', 'en': 'Chapter 2'},
  'title': {'zh': '中局战术场', 'en': 'Middlegame Tactics Arena'},
  'intro': {'zh': '棋子多起来了！学会击双、牵制、闪将、得子，再挑战“连续杀”。',
            'en': 'More pieces on the board! Learn forks, pins, discovered checks, and winning '
                  'material — then take on mating streaks.'},
  'color': '#E07B2A',
  'soft': '#FBE8D4',
  'levels': [{'id': 'm1',
              'title': {'zh': '一箭双雕（击双）', 'en': 'Two Birds, One Stone (Forks)'},
              'goal': {'zh': '用一个棋子同时攻击两个目标', 'en': 'Attack two targets with one piece'},
              'skill': {'zh': '击双（马·兵·后）', 'en': 'Forks (knight · pawn · queen)'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '同时踢两个', 'en': 'Kick Two at Once'},
                         'text': [{'zh': '一个棋子同时攻击两个目标，叫“击双”。对方只能救一个！',
                                   'en': 'Attacking two targets with one piece is called a "fork". '
                                         'Your opponent can only save one!'},
                                  {'zh': '最厉害的是：一边将军，一边攻击皇后——对方只能先救王。',
                                   'en': 'The best kind: check the king AND attack the queen — '
                                         'they must save the king first.'},
                                  {'zh': '马、兵、后，都会击双。',
                                   'en': 'Knights, pawns, and queens can all fork.'}],
                         'fen': 'q3k3/8/8/3N4/8/8/8/4K3 w - - 0 1',
                         'arrows': [['d5', 'c7']]},
                        {'type': 'move',
                         'fen': 'q3k3/8/8/3N4/8/8/8/4K3 w - - 0 1',
                         'prompt': {'zh': '白马跳到 c7：将军的同时，吃掉 a8 的皇后！',
                                    'en': 'Jump the knight to c7: check the king AND gobble the '
                                          'queen on a8!'},
                         'accepted': ['d5c7'],
                         'hint': {'zh': '马从 d5 跳“日”字到 c7。', 'en': 'The knight hops from d5 to c7.'},
                         'successText': {'zh': 'Nc7+ 击双！黑王必须躲，皇后跑不掉啦。',
                                         'en': "Nc7+ fork! The king must run, and the queen can't "
                                               'escape.'}},
                        {'type': 'line',
                         'fen': 'r3k3/1p6/2n5/1B2N3/8/8/8/4K3 w - - 0 1',
                         'script': ['e5c6', 'b7c6', 'b5c6'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '新花样 · 换子再击双:先用 e5 的马吃掉 c6 的黑马!(马换马,不亏)',
                                      'en': 'New trick · trade then fork: first take the c6 knight '
                                            'with your e5 knight! (An even trade — no loss.)'},
                                     {'zh': '黑兵把马吃回去了……白象再吃 c6 兵:一边将军,一边瞄准 a8 的车!',
                                      'en': 'The black pawn takes your knight back… now your '
                                            'bishop takes the c6 pawn: check AND aiming at the a8 '
                                            'rook!'}],
                         'hint': {'zh': '先 Nxc6 换马;黑兵吃回后,Bxc6+ 击双。',
                                  'en': 'Trade with Nxc6 first; after the pawn recaptures, Bxc6+ '
                                        'forks.'},
                         'successText': {'zh': 'Nxc6 bxc6 Bxc6+!象将军,黑王只能躲,a8 的车下一步归你——先换子,再击双!',
                                         'en': 'Nxc6 bxc6 Bxc6+! The bishop checks, the king must '
                                               'run, and the a8 rook is yours next — trade first, '
                                               'then fork!'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/3r1r2/8/8/4P3/4K3 w - - 0 1',
                         'prompt': {'zh': '小兵也会击双！冲到哪个格子，能同时吃掉两个黑车？',
                                    'en': 'Pawns can fork too! Push to which square to attack both '
                                          'black rooks?'},
                         'accepted': ['e2e4'],
                         'hint': {'zh': '小兵斜着“吃”——冲到 e4 就同时瞄准 d5 和 f5。',
                                  'en': 'Pawns capture diagonally — push to e4 and you aim at both '
                                        'd5 and f5.'},
                         'successText': {'zh': 'e4！小兵叉着腰，两个车只能逃一个。',
                                         'en': 'e4! The pawn stands proud — only one rook can run '
                                               'away.'}},
                        {'type': 'move',
                         'fen': '4k3/8/8/8/7n/8/8/3QK3 w - - 0 1',
                         'prompt': {'zh': '皇后出击:走到哪里,能斜线将军、同时瞄准 h4 的黑马?(有两个答案哦!)',
                                    'en': 'Queen attack: where can she check diagonally AND aim at '
                                          'the h4 knight? (Two answers work!)'},
                         'accepted': ['d1a4', 'd1h5'],
                         'hint': {'zh': '想想 d1 出发的两条斜线:a4 和 h5 都行。',
                                  'en': 'Think of the two diagonals from d1: a4 and h5 both work.'},
                         'successText': {'zh': '击双!黑王必须躲,黑马跑不掉啦——a4 和 h5 都对,你找到的是哪一个?',
                                         'en': 'Fork! The king must run and the knight is doomed — '
                                               'both a4 and h5 are right. Which one did you '
                                               'find?'}},
                        {'type': 'line',
                         'fen': '4k3/5p2/8/8/2B1q3/5N2/8/6K1 w - - 0 1',
                         'script': ['c4f7', 'e8f7', 'f3g5'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '进阶 · 引诱击双：先送象！吃掉 f7 兵将军，钓黑王出洞。',
                                      'en': 'Advanced · decoy fork: sacrifice the bishop first! '
                                            'Take the f7 pawn with check and lure the king out.'},
                                     {'zh': '黑王贪吃，爬到了 f7……马跳 g5 击双：一边将军，一边踢 e4 的黑后！',
                                      'en': 'The greedy king crawls to f7… knight jumps to g5 with '
                                            'a fork: check AND kick the e4 queen!'}],
                         'hint': {'zh': 'Bxf7+!（送象钓王）→ Ng5+ 击双。',
                                  'en': 'Bxf7+! (sacrifice the bishop to lure the king) → Ng5+ '
                                        'fork.'},
                         'successText': {'zh': 'Bxf7+! Kxf7，Ng5+ 击双！黑王只能躲，e4 的皇后归你了——先引诱，再击双！',
                                         'en': 'Bxf7+! Kxf7, Ng5+ fork! The king must run, and the '
                                               'e4 queen is yours — lure first, then fork!'}}]},
             {'id': 'm2',
              'title': {'zh': '钉子战术（牵制）', 'en': 'The Nail Tactic (Pins)'},
              'goal': {'zh': '把对方棋子“钉”在原地', 'en': 'Pin enemy pieces in place'},
              'skill': {'zh': '牵制', 'en': 'Pins'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '不敢动的棋子', 'en': 'The Piece That Dares Not Move'},
                         'text': [{'zh': '对方的棋子挡在它自己王的前面时，你用象或车瞄住它——它一动，王就暴露，所以它不敢动！',
                                   'en': 'When an enemy piece stands in front of its own king, aim '
                                         'at it with a bishop or rook — if it moves, the king is '
                                         'exposed, so it dares not move!'},
                                  {'zh': '这叫“牵制”，像被钉子钉住一样。钉在“王”前面最牢：绝对牵制。',
                                   'en': 'That is a "pin" — nailed in place. Pinning against the '
                                         'king is the strongest: an absolute pin.'},
                                  {'zh': '被钉住的棋子不但不敢动，连队友都保护不了——接下来全是你的便宜！',
                                   'en': "A pinned piece can't move and can't even defend its "
                                         'teammates — everything becomes yours!'}],
                         'fen': '6k1/5n2/8/8/8/3B4/8/6K1 w - - 0 1',
                         'arrows': [['d3', 'c4']]},
                        {'type': 'move',
                         'fen': '6k1/5n2/8/8/8/3B4/8/6K1 w - - 0 1',
                         'prompt': {'zh': '白象走到 c4，把 f7 的黑马钉在黑王前面！',
                                    'en': 'Move the bishop to c4 and pin the f7 knight against its '
                                          'king!'},
                         'accepted': ['d3c4'],
                         'hint': {'zh': '让象、黑马、黑王排在同一条斜线上。',
                                  'en': 'Line up bishop, knight, and king on one diagonal.'},
                         'successText': {'zh': 'Bc4 牵制！黑马一动，黑王就被将军。',
                                         'en': 'Bc4 pin! If the knight moves, its king is in '
                                               'check.'}},
                        {'type': 'move',
                         'fen': 'k7/b7/8/8/8/8/8/1R5K w - - 0 1',
                         'prompt': {'zh': '白车走到哪里，能把 a7 的黑象钉住？',
                                    'en': 'Where should the white rook go to pin the a7 bishop?'},
                         'accepted': ['b1a1'],
                         'hint': {'zh': '黑王在 a8，黑象在 a7——车也排到 a 线上去。',
                                  'en': 'The king is on a8, the bishop on a7 — join the a-file '
                                        'with your rook.'},
                         'successText': {'zh': 'Ra1 牵制！黑象动弹不得。',
                                         'en': "Ra1 pin! The bishop can't budge."}},
                        {'type': 'move',
                         'fen': '4k3/8/4n3/8/3P4/8/8/4R1K1 w - - 0 1',
                         'prompt': {'zh': 'e6 的黑马被白车钉在黑王前面。小兵上去踢它一脚：冲到 d5！',
                                    'en': 'The e6 knight is pinned against its king by your rook. '
                                          'Send the pawn to kick it: push to d5!'},
                         'accepted': ['d4d5'],
                         'hint': {'zh': 'd4 的小兵向前走一格，踢被钉住的马。',
                                  'en': 'The d4 pawn steps one square forward to kick the pinned '
                                        'knight.'},
                         'successText': {'zh': 'd5！马被钉着不敢动，下一步就被小兵吃掉——牵制 = 白捡子。',
                                         'en': 'd5! The pinned knight dares not move and gets '
                                               'eaten next — pins mean free pieces.'}},
                        {'type': 'move',
                         'fen': '8/2q1k3/5n2/6B1/8/8/8/2R3K1 w - - 0 1',
                         'prompt': {'zh': '黑后被 f6 的马保护？可马被白象钉住了！白车直接吃掉 c7 的黑后！',
                                    'en': 'Is the black queen guarded by the f6 knight? The knight '
                                          'is pinned by your bishop! Take the queen on c7 with '
                                          'your rook!'},
                         'accepted': ['c1c7'],
                         'hint': {'zh': '车沿 c 线冲上去吃皇后——黑马动弹不得，救不了她。',
                                  'en': 'Rook up the c-file to take the queen — the pinned knight '
                                        "can't save her."},
                         'successText': {'zh': 'Rxc7+！吃掉皇后还将军！被钉住的马连队友都保护不了。',
                                         'en': 'Rxc7+! Take the queen with check! A pinned piece '
                                               "can't even protect its friends."}}]},
             {'id': 'm3',
              'title': {'zh': '闪将出击', 'en': 'Discovered Attack!'},
              'goal': {'zh': '学会“闪开”的连环惊喜', 'en': 'Learn the chain surprise of "stepping aside"'},
              'skill': {'zh': '闪将与双将', 'en': 'Discovered and double checks'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '躲在后面的狙击手', 'en': 'The Sniper Hiding Behind'},
                         'text': [{'zh': '车躲在象后面。象一闪开，车就将军！这叫“闪将”。',
                                   'en': 'The rook hides behind the bishop. When the bishop steps '
                                         'aside, the rook gives check! That is a "discovered '
                                         'check".'},
                                  {'zh': '如果象闪开时自己也将军，就是“双将”——对方只能动王，',
                                   'en': 'If the bishop also gives check while stepping aside, '
                                         'that is a "double check" — the opponent can only move '
                                         'the king,'},
                                  {'zh': '根本顾不上别的棋子。高手最爱这种连环惊喜。',
                                   'en': 'and nothing else matters. Masters love this chain of '
                                         'surprises.'}],
                         'fen': 'q3k3/8/8/8/4B3/8/8/4R1K1 w - - 0 1',
                         'arrows': [['e4', 'a8']]},
                        {'type': 'move',
                         'fen': 'q3k3/8/8/8/4B3/8/8/4R1K1 w - - 0 1',
                         'prompt': {'zh': '白象沿大斜线直接吃掉 a8 的黑后！象一闪开，e1 的车同时将军——闪将吃后，一步到位！',
                                    'en': 'The bishop takes the black queen on a8 along the long '
                                          'diagonal! As it steps aside, the e1 rook gives check — '
                                          'discovered check and queen capture in one move!'},
                         'accepted': ['e4a8'],
                         'hint': {'zh': '象沿 e4-d5-c6-b7-a8 一路吃过去。',
                                  'en': 'The bishop goes e4-d5-c6-b7-a8 all the way.'},
                         'successText': {'zh': 'Bxa8+ 闪将吃后！皇后到嘴，黑王还在被将军——黑方两头都顾不上了。',
                                         'en': 'Bxa8+ discovered check! The queen is eaten and the '
                                               "king is still in check — Black can't handle "
                                               'both.'}},
                        {'type': 'line',
                         'fen': '7k/1q2p1Rp/8/8/8/8/1B6/6K1 w - - 0 1',
                         'script': ['g7h7', 'h8g8', 'h7g7', 'g8h8', 'g7e7'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '名局套路 · 风车战术:车吃 h7 兵将军!黑王只能躲去 g8。',
                                      'en': 'Famous-game pattern · the windmill: rook takes the h7 '
                                            'pawn with check! The black king must hide on g8.'},
                                     {'zh': '车回到 g7 将军,黑王又只能回 h8……',
                                      'en': 'The rook returns to g7 with check, and the king must '
                                            'go back to h8…'},
                                     {'zh': '车再吃 e7 兵——这次轮到 b2 的象闪开将军!黑王疲于奔命。',
                                      'en': 'The rook takes the e7 pawn — this time the b2 bishop '
                                            'gives the discovered check! The king is running '
                                            'ragged.'}],
                         'hint': {'zh': 'Rxh7+ → Kg8 → Rg7+ → Kh8 → Rxe7+,车来回转,每次都将军。',
                                  'en': 'Rxh7+ → Kg8 → Rg7+ → Kh8 → Rxe7+ — the rook spins back '
                                        'and forth, checking every time.'},
                         'successText': {'zh': '风车转起来了!连吃两兵还带将。还没完:黑王躲回 g8 后,Rg7+ 再闪,Rxb7 '
                                               '连皇后也收割!这就是托雷打败拉斯克的名局套路。',
                                         'en': 'The windmill is spinning! Two pawns eaten, all '
                                               'with check. And it is not over: after the king '
                                               'returns to g8, Rg7+ uncovers again, and Rxb7 '
                                               'harvests the queen too! This is the famous '
                                               'Torre–Lasker pattern.'}}]},
             {'id': 'm5',
              'title': {'zh': '连续杀（两步杀）', 'en': 'Mating Streaks (Mate in 2)'},
              'goal': {'zh': '想两步，走一步', 'en': 'Think two moves, play one'},
              'skill': {'zh': '连续计算（两步杀）', 'en': 'Calculation (mate in 2)'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '想两步，赢一步', 'en': 'Think Two, Win One'},
                         'text': [{'zh': '高手会想：“我先走这步，对方只能那样应，然后我再……将死！”',
                                   'en': 'A master thinks: "I play this, they must answer that, '
                                         'and then I… checkmate!"'},
                                  {'zh': '这叫“两步杀”，是最难也最过瘾的题。',
                                   'en': 'That is a "mate in two" — the hardest and most '
                                         'satisfying puzzles.'},
                                  {'zh': '四道题四个原理：弃子引开、后象炮台、后马搭档、贪吃蛇。如果你发现了更快的杀法，同样算赢！',
                                   'en': 'Four puzzles, four ideas: decoy sacrifice, queen-bishop '
                                         'battery, queen-knight duo, and the greedy snake. If you '
                                         'find a faster mate, it counts as a win too!'}],
                         'fen': 'r5k1/5ppp/8/8/3Q4/8/8/3R1RK1 w - - 0 1',
                         'arrows': [['d4', 'd8']]},
                        {'type': 'line',
                         'fen': 'r5k1/5ppp/8/8/3Q4/8/8/3R1RK1 w - - 0 1',
                         'script': ['d4d8', 'a8d8', 'd1d8'],
                         'prompts': [{'zh': '第一步：皇后冲上去送吃！（别怕，这是陷阱）',
                                      'en': "First move: the queen offers herself! (Don't be "
                                            "scared — it's a trap.)"},
                                     {'zh': '黑车吃掉了皇后……可是底线空了！轮到你收官：',
                                      'en': 'The black rook takes the queen… but the back rank is '
                                            'empty! Your turn to finish:'}],
                         'hint': {'zh': '皇后冲上 d8 将军，黑车只能吃掉她——然后 d1 的车再吃掉黑车！',
                                  'en': 'The queen checks on d8, the rook must take her — then '
                                        'your d1 rook takes the rook!'},
                         'successText': {'zh': 'Qd8+! Rxd8，Rxd8 将死！皇后舍身引开黑车，太精彩了！',
                                         'en': 'Qd8+! Rxd8, Rxd8 mate! The queen lures the rook '
                                               'away with her life — brilliant!'}},
                        {'type': 'line',
                         'fen': '3q2k1/5ppp/6Q1/4R3/8/8/2B5/7K w - - 0 1',
                         'script': ['g6h7', 'g8f8', 'h7h8'],
                         'prompts': [{'zh': '第二题 · 后象炮台：皇后吃掉 h7 兵将军！（c2 的象沿大斜线远远保护她，王不敢吃）',
                                      'en': 'Puzzle 2 · queen-bishop battery: the queen takes the '
                                            'h7 pawn with check! (The c2 bishop guards her along '
                                            'the long diagonal — the king dares not capture.)'},
                                     {'zh': '黑王逃向 f8。注意 e5 的车封住了 e 线——皇后钻到 h8 收口：',
                                      'en': 'The black king flees to f8. Notice the e5 rook seals '
                                            'the e-file — the queen slips into h8 to finish:'}],
                         'hint': {'zh': 'Qxh7+!（有象保护）→ Qh8 将死。',
                                  'en': 'Qxh7+! (guarded by the bishop) → Qh8 mate.'},
                         'successText': {'zh': 'Qxh7+! Kf8，Qh8 将死！后象炮台发威，车又封死 e 线，黑王插翅难逃。',
                                         'en': 'Qxh7+! Kf8, Qh8 mate! The queen-bishop battery '
                                               'fires, the rook seals the e-file — the king has no '
                                               'wings.'}},
                        {'type': 'line',
                         'fen': '6k1/5ppp/2nN2Q1/8/8/8/B7/7K w - - 0 1',
                         'script': ['g6f7', 'g8h8', 'f7g8'],
                         'prompts': [{'zh': '第三题 · 后马搭档：皇后走到 f7 将军——d6 的马看着她，王不敢吃。',
                                      'en': 'Puzzle 3 · queen-knight duo: the queen checks from f7 '
                                            "— the d6 knight watches over her, so the king can't "
                                            'take.'},
                                     {'zh': '黑王躲到 h8。皇后贴脸 g8 收口（a2 的象在超远斜线上保护她）：',
                                      'en': 'The black king hides on h8. The queen finishes '
                                            'face-to-face on g8 (the a2 bishop guards her from the '
                                            'super-long diagonal):'}],
                         'hint': {'zh': 'Qf7+! → Qg8 将死。', 'en': 'Qf7+! → Qg8 mate.'},
                         'successText': {'zh': 'Qf7+! Kh8，Qg8 将死！马封逃路、象保皇后，配合天衣无缝。',
                                         'en': 'Qf7+! Kh8, Qg8 mate! Knight seals the escape, '
                                               'bishop guards the queen — flawless teamwork.'}},
                        {'type': 'line',
                         'fen': '1n2r1k1/Q4ppp/8/N2B4/8/8/8/7K w - - 0 1',
                         'script': ['a7f7', 'g8h8', 'f7e8'],
                         'prompts': [{'zh': '第四题 · 贪吃蛇皇后：皇后吃掉 f7 兵将军！（d5 的象保护她）',
                                      'en': 'Puzzle 4 · the greedy-snake queen: the queen takes '
                                            'the f7 pawn with check! (The d5 bishop guards her.)'},
                                     {'zh': '黑王躲到 h8。皇后转头吃掉 e8 的黑车——将死！b8 的黑马睡大觉，来不及救：',
                                      'en': 'The black king hides on h8. The queen turns and eats '
                                            'the e8 rook — mate! The b8 knight is fast asleep, too '
                                            'late to help:'}],
                         'hint': {'zh': 'Qxf7+! → Qxe8 将死。', 'en': 'Qxf7+! → Qxe8 mate.'},
                         'successText': {'zh': 'Qxf7+! Kh8，Qxe8 将死！皇后一路吃过去，小兵、黑车全进肚子。',
                                         'en': 'Qxf7+! Kh8, Qxe8 mate! The queen eats her way '
                                               'through — pawn and rook all swallowed.'}}]},
             {'id': 'm5b',
              'title': {'zh': '三步杀大师', 'en': 'Mate in 3 Master'},
              'goal': {'zh': '最多三步内将死——步数越少越厉害',
                       'en': 'Mate within three moves — fewer moves, more impressive'},
              'skill': {'zh': '连续计算（三步杀）', 'en': 'Calculation (mate in 3)'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '最多三步，将死！', 'en': 'Mate in Three Moves!'},
                         'text': [{'zh': '这一关的每个局面，白棋都能在三步之内将死黑王。',
                                   'en': 'In every position of this level, White can mate the '
                                         'black king within three moves.'},
                                  {'zh': '秘诀：步步将军，对方的每一应着都是被迫的；必要时“弃子”为王炸开杀路。',
                                   'en': 'The secret: check every move so every reply is forced; '
                                         'when needed, "sacrifice" a piece to blast open the '
                                         'path.'},
                                  {'zh': '如果你发现了更快的杀法——一步两步就将死——同样算你赢！',
                                   'en': 'If you find a faster mate — in one or two moves — it '
                                         'counts as a win too!'},
                                  {'zh': '后三题更夸张：白棋兵力比黑棋少得多，照样杀。兵力多不等于赢，王死了就全完了。',
                                   'en': 'The last three puzzles are wilder: White has far less '
                                         "material than Black and still mates. More pieces doesn't "
                                         'mean winning — a dead king loses everything.'}],
                         'fen': '1n1q2k1/5ppp/8/8/2Q5/6N1/5R2/7K w - - 0 1'},
                        {'type': 'line',
                         'fen': '1n1q2k1/5ppp/8/8/2Q5/6N1/5R2/7K w - - 0 1',
                         'script': ['c4f7', 'g8h8', 'f7f8', 'd8f8', 'f2f8'],
                         'prompts': [{'zh': '第一题 · 弃后换防：皇后先吃掉 f7 兵将军！',
                                      'en': 'Puzzle 1 · queen sacrifice to trade defenders: the '
                                            'queen takes the f7 pawn with check first!'},
                                     {'zh': '黑王躲到 h8。第二步：皇后再冲上 f8 将军——黑后只能吃掉她……',
                                      'en': 'The black king hides on h8. Second move: the queen '
                                            'charges to f8 with check — the black queen must take '
                                            'her…'},
                                     {'zh': '皇后的牺牲换来了什么？底线没人守了！轮到 f2 的车收官：',
                                      'en': "What did the queen's sacrifice buy? Nobody guards the "
                                            'back rank! The f2 rook finishes:'}],
                         'hint': {'zh': 'Qxf7+ → Qf8+!!（送后）→ Rxf8 将死。',
                                  'en': 'Qxf7+ → Qf8+!! (queen sacrifice) → Rxf8 mate.'},
                         'successText': {'zh': 'Qxf7+ Kh8，Qf8+!! Qxf8，Rxf8 将死！皇后舍身换掉黑后，车沉底线绝杀。',
                                         'en': 'Qxf7+ Kh8, Qf8+!! Qxf8, Rxf8 mate! The queen '
                                               'trades herself for the black queen, and the rook '
                                               'lands the final blow.'}},
                        {'type': 'line',
                         'fen': '3q2k1/5ppp/8/4N3/8/8/QB6/7K w - - 0 1',
                         'script': ['a2f7', 'g8h8', 'e5g6', 'h7g6', 'f7g7'],
                         'prompts': [{'zh': '第二题 · 长斜线炮台：皇后沿大斜线吃 f7 兵将军！',
                                      'en': 'Puzzle 2 · long-diagonal battery: the queen takes the '
                                            'f7 pawn with check along the big diagonal!'},
                                     {'zh': '黑王躲到 h8。第二步：马跳 g6 将军，送给 h7 兵吃！',
                                      'en': 'The black king hides on h8. Second move: the knight '
                                            'jumps to g6 with check — offered to the h7 pawn!'},
                                     {'zh': 'h 兵吃马……皇后贴脸 g7 收口（b2 的象远远保护着她）：',
                                      'en': 'The h-pawn takes the knight… the queen finishes '
                                            'face-to-face on g7 (the b2 bishop guards her from '
                                            'afar):'}],
                         'hint': {'zh': 'Qxf7+ → Ng6+!!（弃马）→ Qg7 将死。',
                                  'en': 'Qxf7+ → Ng6+!! (knight sacrifice) → Qg7 mate.'},
                         'successText': {'zh': 'Qxf7+ Kh8，Ng6+!! hxg6，Qg7 将死！后象占住同一条大斜线，弃马一逼就成了杀。',
                                         'en': 'Qxf7+ Kh8, Ng6+!! hxg6, Qg7 mate! Queen and bishop '
                                               'own the long diagonal; one knight sacrifice forces '
                                               'mate.'}},
                        {'type': 'line',
                         'fen': '3q2k1/5ppp/8/3B1Q2/8/8/7R/7K w - - 0 1',
                         'script': ['f5f7', 'g8h8', 'h2h7', 'h8h7', 'f7h5'],
                         'prompts': [{'zh': '第三题 · 弃车钓王：皇后沿 f 线冲到 f7 将军。',
                                      'en': 'Puzzle 3 · rook sacrifice to lure the king: the queen '
                                            'checks on f7 along the f-file.'},
                                     {'zh': '黑王躲进 h8 角落。第二步：车直接吃 h7 兵将军——送给黑王吃！',
                                      'en': 'The black king hides in the h8 corner. Second move: '
                                            'the rook takes the h7 pawn with check — offered to '
                                            'the king!'},
                                     {'zh': '黑王被“钓”了出来……皇后换个方向收口：',
                                      'en': 'The king is "fished out"… the queen changes direction '
                                            'to finish:'}],
                         'hint': {'zh': 'Qf7+ → Rxh7+!!（弃车钓王）→ Qh5 将死。',
                                  'en': 'Qf7+ → Rxh7+!! (rook sacrifice to lure the king) → Qh5 '
                                        'mate.'},
                         'successText': {'zh': 'Qf7+ Kh8，Rxh7+!! Kxh7，Qh5 将死！王被钓出堡垒，后象联手关门。',
                                         'en': 'Qf7+ Kh8, Rxh7+!! Kxh7, Qh5 mate! The king is '
                                               'fished out of his fortress, and the queen and '
                                               'bishop close the door.'}},
                        {'type': 'line',
                         'fen': '6k1/4Qppp/1nnRq3/r7/8/8/8/7K w - - 0 1',
                         'script': ['d6d8', 'c6d8', 'e7d8', 'e6e8', 'd8e8'],
                         'prompts': [{'zh': '第四题 · 冲破防线（白棋少 9 分）：黑棋两个马一个后守着底线。第一步：车冲 d8 将军，送给马吃！',
                                      'en': 'Puzzle 4 · breaking the defense (White is down 9 '
                                            'points): Black guards the back rank with two knights '
                                            'and a queen. First: the rook checks on d8, offered to '
                                            'the knight!'},
                                     {'zh': '马吃掉了车。第二步：皇后吃回 d8 将军！黑后只能退到 e8 堵枪眼……',
                                      'en': 'The knight takes the rook. Second move: the queen '
                                            'takes back on d8 with check! The black queen must '
                                            'drop back to e8 to block…'},
                                     {'zh': '挡得住吗？皇后连后带王一起收：',
                                      'en': 'Can that stop her? The queen takes both queen and '
                                            "king's fate:"}],
                         'hint': {'zh': 'Rd8+! Nxd8 → Qxd8+! Qe8 → Qxe8 将死。',
                                  'en': 'Rd8+! Nxd8 → Qxd8+! Qe8 → Qxe8 mate.'},
                         'successText': {'zh': 'Rd8+! Nxd8，Qxd8+! Qe8，Qxe8 将死！车当开路先锋，皇后踏平底线。',
                                         'en': 'Rd8+! Nxd8, Qxd8+! Qe8, Qxe8 mate! The rook clears '
                                               'the way and the queen tramples the back rank.'}},
                        {'type': 'line',
                         'fen': '1n1q2k1/5ppp/8/r5N1/8/r7/2Q2R2/7K w - - 0 1',
                         'script': ['c2h7', 'g8f8', 'f2f7', 'f8e8', 'h7h8'],
                         'prompts': [{'zh': '第五题 · 赶王入瓮（白棋少 8 分）：皇后沿大斜线吃掉 h7 兵将军！（有 g5 的马保护）',
                                      'en': 'Puzzle 5 · herding the king (White is down 8 points): '
                                            'the queen takes the h7 pawn with check along the big '
                                            'diagonal! (Guarded by the g5 knight.)'},
                                     {'zh': '黑王逃向 f8。第二步：车冲 f7 将军，继续赶！',
                                      'en': 'The black king flees to f8. Second move: the rook '
                                            'checks on f7 — keep herding!'},
                                     {'zh': '黑王被赶到 e8……皇后沿 h 线兜头一罩：',
                                      'en': 'The king is herded to e8… the queen swoops down the '
                                            'h-file:'}],
                         'hint': {'zh': 'Qxh7+! → Rf7+! → Qh8 将死。',
                                  'en': 'Qxh7+! → Rf7+! → Qh8 mate.'},
                         'successText': {'zh': 'Qxh7+! Kf8，Rf7+! Ke8，Qh8 将死！后有马保、车占七线，黑王被一路赶进死胡同。',
                                         'en': 'Qxh7+! Kf8, Rf7+! Ke8, Qh8 mate! Queen guarded by '
                                               'the knight, rook owning the 7th rank — the king is '
                                               'herded into a dead end.'}},
                        {'type': 'line',
                         'fen': '3q1bk1/Q4ppp/8/r4R2/8/r7/6N1/7K w - - 0 1',
                         'script': ['a7f7', 'g8h8', 'f7f8', 'd8f8', 'f5f8'],
                         'prompts': [{'zh': '第六题 · 以少胜多（白棋少 8 分）：黑棋后象双车俱全。第一步：皇后横冲到 f7 吃兵将军！',
                                      'en': 'Puzzle 6 · winning with less (White is down 8 '
                                            'points): Black has queen, bishop, and both rooks. '
                                            'First: the queen sweeps to f7, taking the pawn with '
                                            'check!'},
                                     {'zh': '黑王躲 h8。第二步：皇后冲上 f8 将军——黑后被迫吃掉她……',
                                      'en': 'The black king hides on h8. Second move: the queen '
                                            'charges to f8 with check — the black queen is forced '
                                            'to take her…'},
                                     {'zh': '底线空了！f5 的车收官：',
                                      'en': 'The back rank is empty! The f5 rook finishes:'}],
                         'hint': {'zh': 'Qxf7+ → Qf8+!!（送后斩后）→ Rxf8 将死。',
                                  'en': 'Qxf7+ → Qf8+!! (sacrifice the queen to remove theirs) → '
                                        'Rxf8 mate.'},
                         'successText': {'zh': 'Qxf7+ Kh8，Qf8+!! Qxf8，Rxf8 将死！黑棋子再多，王没了就全输。',
                                         'en': 'Qxf7+ Kh8, Qf8+!! Qxf8, Rxf8 mate! However many '
                                               'pieces Black has, a dead king loses it all.'}}]},
             {'id': 'm5c',
              'title': {'zh': '四步杀大师', 'en': 'Mate in 4 Master'},
              'goal': {'zh': '想四步，走一步——学会“弃子钓王”',
                       'en': 'Think four moves, play one — learn to "sacrifice to lure the king"'},
              'skill': {'zh': '连续计算（四步杀）', 'en': 'Calculation (mate in 4)'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '最多四步，将死！', 'en': 'Mate in Four Moves!'},
                         'text': [{'zh': '三步杀也拿下了？终极挑战：四步杀！',
                                   'en': 'Mate in three mastered? The ultimate challenge: mate in '
                                         'four!'},
                                  {'zh': '这一关的三个局面有个共同主题：弃子钓王——故意送掉棋子，把黑王从堡垒里钓出来。',
                                   'en': 'All three positions share one theme: sacrifice to lure '
                                         'the king — give up a piece on purpose to fish the black '
                                         'king out of his fortress.'},
                                  {'zh': '黑棋的每一步都是被迫的；你若发现更快的杀法，同样算赢！',
                                   'en': 'Every black move is forced; if you find a faster mate, '
                                         'it counts as a win!'}],
                         'fen': '6k1/4bppp/8/8/Q4B2/8/4R3/7K w - - 0 1'},
                        {'type': 'line',
                         'fen': '6k1/4bppp/8/8/Q4B2/8/4R3/7K w - - 0 1',
                         'script': ['a4e8', 'e7f8', 'e8f8', 'g8f8', 'f4d6', 'f8g8', 'e2e8'],
                         'prompts': [{'zh': '第一题 · 弃后钓王：皇后冲 e8 将军！黑象只能退到 f8 挡。',
                                      'en': 'Puzzle 1 · queen sacrifice to lure the king: the '
                                            'queen checks on e8! The black bishop must drop back '
                                            'to f8 to block.'},
                                     {'zh': '第二步：皇后吃掉 f8 的象将军——送给黑王吃！（别心疼，看后面）',
                                      'en': 'Second move: the queen takes the f8 bishop with check '
                                            "— offered to the king! (Don't cry, watch what "
                                            'follows.)'},
                                     {'zh': '黑王吃掉皇后，被钓到了 f8！第三步：象走 d6 将军，把王往回赶。',
                                      'en': 'The king takes the queen and gets fished to f8! Third '
                                            'move: the bishop checks from d6, herding the king '
                                            'back.'},
                                     {'zh': '黑王退回 g8……e2 的车沉底线收官：',
                                      'en': 'The king retreats to g8… the e2 rook sinks to the '
                                            'back rank to finish:'}],
                         'hint': {'zh': 'Qe8+ → Qxf8+!!（弃后钓王）→ Bd6+ → Re8 将死。',
                                  'en': 'Qe8+ → Qxf8+!! (queen sacrifice to lure the king) → Bd6+ '
                                        '→ Re8 mate.'},
                         'successText': {'zh': 'Qe8+ Bf8，Qxf8+!! Kxf8，Bd6+ Kg8，Re8 将死！皇后换一条王命，值！',
                                         'en': 'Qe8+ Bf8, Qxf8+!! Kxf8, Bd6+ Kg8, Re8 mate! A '
                                               "queen for the king's life — worth it!"}},
                        {'type': 'line',
                         'fen': '5rk1/5ppp/2N5/3Q4/8/2B5/8/7K w - - 0 1',
                         'script': ['c6e7', 'g8h8', 'c3g7', 'h8g7', 'd5g5', 'g7h8', 'g5f6'],
                         'prompts': [{'zh': '第二题 · 弃象钓王：马跳 e7 将军，把黑王逼进 h8 角落。',
                                      'en': 'Puzzle 2 · bishop sacrifice to lure the king: the '
                                            'knight checks on e7, forcing the black king into the '
                                            'h8 corner.'},
                                     {'zh': '第二步：象吃掉 g7 兵将军——送给黑王吃！（这是钓饵）',
                                      'en': 'Second move: the bishop takes the g7 pawn with check '
                                            '— offered to the king! (That is the bait.)'},
                                     {'zh': '黑王中计了！第三步：皇后飞到 g5 将军。',
                                      'en': 'The king takes the bait! Third move: the queen flies '
                                            'to g5 with check.'},
                                     {'zh': '黑王又退回 h8……皇后到 f6 收口（马看着 g8，王逃不掉）：',
                                      'en': 'The king retreats to h8 again… the queen finishes on '
                                            "f6 (the knight watches g8 — the king can't escape):"}],
                         'hint': {'zh': 'Ne7+ → Bxg7+!!（弃象钓王）→ Qg5+ → Qf6 将死。',
                                  'en': 'Ne7+ → Bxg7+!! (bishop sacrifice to lure the king) → Qg5+ '
                                        '→ Qf6 mate.'},
                         'successText': {'zh': 'Ne7+ Kh8，Bxg7+!! Kxg7，Qg5+ Kh8，Qf6 '
                                               '将死！一个象钓出黑王，后马联手收网。',
                                         'en': 'Ne7+ Kh8, Bxg7+!! Kxg7, Qg5+ Kh8, Qf6 mate! One '
                                               'bishop fishes out the king; queen and knight close '
                                               'the net.'}},
                        {'type': 'line',
                         'fen': '5rk1/5ppp/2N5/3r4/4Q3/5R2/8/7K w - - 0 1',
                         'script': ['c6e7', 'g8h8', 'e4h7', 'h8h7', 'f3h3', 'd5h5', 'h3h5'],
                         'prompts': [{'zh': '第三题 · 弃后破门：马跳 e7 将军，逼黑王进角落。',
                                      'en': 'Puzzle 3 · queen sacrifice to break the door: the '
                                            'knight checks on e7, forcing the king into the '
                                            'corner.'},
                                     {'zh': '第二步：皇后吃掉 h7 兵将军——直接送给黑王！',
                                      'en': 'Second move: the queen takes the h7 pawn with check — '
                                            'straight into the king’s mouth!'},
                                     {'zh': '黑王吃掉皇后，h 线大门被撞开了！车冲到 h3 将军。',
                                      'en': 'The king takes the queen, and the h-file door is '
                                            'smashed open! The rook charges to h3 with check.'},
                                     {'zh': '黑车来堵枪眼（h5）……连车带王一起收：',
                                      'en': 'The black rook blocks on h5… take rook and king '
                                            'together:'}],
                         'hint': {'zh': 'Ne7+ → Qxh7+!!（弃后破门）→ Rh3+ → Rxh5 将死。',
                                  'en': 'Ne7+ → Qxh7+!! (queen sacrifice to break the door) → Rh3+ '
                                        '→ Rxh5 mate.'},
                         'successText': {'zh': 'Ne7+ Kh8，Qxh7+!! Kxh7，Rh3+ Rh5，Rxh5 '
                                               '将死！皇后劈开大门，车一冲到底。',
                                         'en': 'Ne7+ Kh8, Qxh7+!! Kxh7, Rh3+ Rh5, Rxh5 mate! The '
                                               'queen splits the door open and the rook charges '
                                               'home.'}}]}]},
 {'id': 'opening',
  'badge': {'zh': '第三章', 'en': 'Chapter 3'},
  'title': {'zh': '开局新天地', 'en': 'Opening Horizons'},
  'intro': {'zh': '学会了杀王和战术，最后学开局：意大利、西班牙、后翼弃兵、西西里、古印度……名开局一网打尽，连“四步杀”攻防都拿下！',
            'en': 'Mates and tactics learned — time for openings: Italian, Spanish, Queen’s '
                  'Gambit, Sicilian, King’s Indian… all the classics, plus the four-move checkmate '
                  'attack and defense!'},
  'color': '#2F6FBA',
  'soft': '#DFEAF8',
  'levels': [{'id': 'o4',
              'title': {'zh': '意大利开局详解', 'en': 'The Italian Game in Detail'},
              'goal': {'zh': '亲手走出 500 岁的经典开局，并看懂它的两种套路',
                       'en': 'Play the 500-year-old classic yourself and understand its two main '
                             'plans'},
              'skill': {'zh': '意大利开局思路', 'en': 'Italian Game ideas'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '500 岁的经典开局', 'en': 'The 500-Year-Old Classic'},
                         'text': [{'zh': '意大利开局已经有 500 多岁了，是最古老也最经典的开局：',
                                   'en': 'The Italian Game is over 500 years old — the oldest and '
                                         'most classic opening:'},
                                  {'zh': '1.e4 e5 2.马f3 马c6 3.象c4——占中心、快出子、瞄弱点，三原则全用上！',
                                   'en': '1.e4 e5 2.Nf3 Nc6 3.Bc4 — center, quick development, aim '
                                         'at the weakness: all three principles at once!'},
                                  {'zh': '前三步先亲手走一遍，然后再看它的两种经典套路。',
                                   'en': 'Play the first three moves yourself, then see its two '
                                         'classic plans.'}],
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'},
                        {'type': 'move',
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                         'prompt': {'zh': '第 1 步：冲兵占中心！',
                                    'en': 'Move 1: push the pawn and take the center!'},
                         'accepted': ['e2e4'],
                         'hint': {'zh': 'e 兵向前两格。', 'en': 'The e-pawn goes two squares forward.'},
                         'successText': {'zh': '1.e4！（黑棋应 e5）', 'en': '1.e4! (Black answers e5)'}},
                        {'type': 'move',
                         'fen': 'rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1',
                         'prompt': {'zh': '第 2 步：跳马出子！', 'en': 'Move 2: develop the knight!'},
                         'accepted': ['g1f3'],
                         'hint': {'zh': 'g1 的马跳到 f3。', 'en': 'The g1 knight jumps to f3.'},
                         'successText': {'zh': '2.Nf3！（黑棋跳马 Nc6 保护 e5 兵）',
                                         'en': '2.Nf3! (Black plays Nc6, defending the e5 pawn)'}},
                        {'type': 'move',
                         'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1',
                         'prompt': {'zh': '第 3 步：象出 c4，意大利开局完成！象瞄准了 f7——黑王身边只有王保护的弱点。',
                                    'en': 'Move 3: bishop to c4 — the Italian Game is complete! '
                                          'The bishop aims at f7, the weakest point near the black '
                                          'king.'},
                         'accepted': ['f1c4'],
                         'hint': {'zh': 'f1 的象斜走到 c4。',
                                  'en': 'The f1 bishop slides diagonally to c4.'},
                         'successText': {'zh': '3.Bc4！象已瞄准 f7。（黑棋正常应着：象 c5）',
                                         'en': '3.Bc4! The bishop already eyes f7. (Black’s normal '
                                               'reply: Bc5)'}},
                        {'type': 'line',
                         'fen': 'r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 '
                                '4',
                         'script': ['c2c3', 'g8f6', 'd2d4', 'e5d4', 'c3d4'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '套路一 · 稳健建中心：白棋先悄悄垫一步 c3——猜它想干嘛？',
                                      'en': 'Plan 1 · build the center quietly: White quietly '
                                            'plays c3 first — guess what it wants?'},
                                     {'zh': '黑马 f6 出子。白棋亮出用意：d4 中心冲锋！',
                                      'en': 'Black develops Nf6. White reveals the idea: d4, the '
                                            'center charge!'},
                                     {'zh': '黑兵吃掉 d4，白兵吃回——看棋盘中心！',
                                      'en': 'Black takes on d4, White takes back — look at the '
                                            'center!'}],
                         'hint': {'zh': '跟着提示走：c3 → d4 → 兵吃回 d4。',
                                  'en': 'Follow the plan: c3 → d4 → pawn recaptures on d4.'},
                         'successText': {'zh': '演变结果：c3 垫一步、再 d4 冲锋，白棋双兵镇中心！这就是意大利开局的标准套路。',
                                         'en': 'Result: c3 prepares, d4 charges, and White’s two '
                                               'pawns rule the center! This is the standard '
                                               'Italian plan.'}},
                        {'type': 'line',
                         'fen': 'r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 '
                                '4',
                         'script': ['b2b4', 'c5b4', 'c2c3', 'b4a5', 'd2d4'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '套路二 · 埃文斯弃兵：同样的局面，白棋直接冲 b4 送兵给黑象吃！',
                                      'en': 'Plan 2 · the Evans Gambit: same position, but White '
                                            'boldly pushes b4, offering a pawn to the bishop!'},
                                     {'zh': '黑象吃兵了。白棋 c3 一赶——',
                                      'en': 'The bishop takes the pawn. White chases with c3 —'},
                                     {'zh': '黑象退 a5，白棋 d4 冲锋！看中心。',
                                      'en': 'The bishop retreats to a5, and White charges d4! Look '
                                            'at the center.'}],
                         'hint': {'zh': '跟着提示走：b4 弃兵 → c3 赶象 → d4 冲锋。',
                                  'en': 'Follow the plan: b4 gambit → c3 chase → d4 charge.'},
                         'successText': {'zh': '演变结果：弃一个兵，换来中心加出子速度！百年前的棋手靠这招赢下无数对局。',
                                         'en': 'Result: give up one pawn for the center plus '
                                               'development speed! Players won countless games '
                                               'with this a century ago.'}}]},
             {'id': 'o4b',
              'title': {'zh': '西班牙开局详解', 'en': 'The Spanish Game in Detail'},
              'goal': {'zh': '用五步演变看懂：象 b5 压马 vs 象 c4 盯兵',
                       'en': 'See in five-move lines: bishop to b5 pressuring the knight vs bishop '
                             'to c4 eyeing the pawn'},
              'skill': {'zh': '西班牙开局思路', 'en': 'Spanish Game ideas'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '象，到底去哪？', 'en': 'Where Should the Bishop Go?'},
                         'text': [{'zh': '1.e4 e5 2.马f3 马c6 之后，白象有两个热门去处：',
                                   'en': 'After 1.e4 e5 2.Nf3 Nc6, White’s bishop has two popular '
                                         'squares:'},
                                  {'zh': '去 c4 盯住 f7 兵（意大利开局），或去 b5 压住 c6 马（西班牙开局）。',
                                   'en': 'c4 to eye the f7 pawn (Italian), or b5 to pressure the '
                                         'c6 knight (Spanish).'},
                                  {'zh': '哪个好？光讲道理没用——我们把两种走法各演变五步，比比看！',
                                   'en': 'Which is better? Talking won’t tell — let’s play out '
                                         'both for five moves and compare!'}],
                         'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3'},
                        {'type': 'line',
                         'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
                         'script': ['f1b5', 'a7a6', 'b5c6', 'd7c6', 'f3e5'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '演变一 · 西班牙：白象走 b5，压住 c6 马。',
                                      'en': 'Line 1 · Spanish: the bishop goes to b5, pressuring '
                                            'the c6 knight.'},
                                     {'zh': '黑棋 a6 赶象？白象不逃——直接把马吃掉！',
                                      'en': 'Black plays a6 to chase the bishop? The bishop '
                                            'doesn’t run — it takes the knight!'},
                                     {'zh': '黑兵只好吃回象。注意：e5 兵的保镖没了！白马动手：',
                                      'en': 'Black must recapture the bishop. Notice: the e5 '
                                            'pawn’s bodyguard is gone! White’s knight strikes:'}],
                         'hint': {'zh': '跟着提示走：象b5 → 象吃马 → 马吃 e5 兵。',
                                  'en': 'Follow the plan: Bb5 → bishop takes knight → knight takes '
                                        'the e5 pawn.'},
                         'successText': {'zh': '演变结果：白棋白赚一个兵！Bb5 的算盘——吃掉 e5 中心兵的保镖，再夺兵。',
                                         'en': 'Result: White wins a pawn for free! The idea of '
                                               'Bb5 — remove the center pawn’s guard, then take '
                                               'it.'}},
                        {'type': 'line',
                         'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
                         'script': ['f1c4', 'g8f6', 'f3g5', 'd7d5', 'e4d5'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '演变二 · 意大利：同样的局面，白象改走 c4 盯 f7 兵。',
                                      'en': 'Line 2 · Italian: same position, but the bishop goes '
                                            'to c4, eyeing the f7 pawn.'},
                                     {'zh': '黑马 f6 正常防守。白再跳马 g5——双攻 f7 弱点！',
                                      'en': 'Black defends normally with Nf6. White jumps Ng5 — '
                                            'double attack on the f7 weakness!'},
                                     {'zh': '黑棋不硬保 f7，反而冲 d5 反击中心！白兵吃掉 d5：',
                                      'en': 'Black doesn’t cling to f7 — instead d5 counterattacks '
                                            'the center! White takes on d5:'}],
                         'hint': {'zh': '跟着提示走：象c4 → 马g5 → 兵吃 d5。',
                                  'en': 'Follow the plan: Bc4 → Ng5 → pawn takes d5.'},
                         'successText': {'zh': '演变结果：Bc4 攻 f7 见效快，但黑 d5 一反击，象的斜线被兵挡住，攻势缓和了。',
                                         'en': 'Result: Bc4 attacks f7 quickly, but Black’s d5 '
                                               'counter blocks the bishop’s diagonal and cools the '
                                               'attack.'}}]},
             {'id': 'o4d',
              'title': {'zh': '后翼弃兵详解', 'en': 'The Queen’s Gambit in Detail'},
              'goal': {'zh': '用三步演变看懂：弃兵为什么能夺中心',
                       'en': 'See in a three-move line why the gambit wins the center'},
              'skill': {'zh': '后翼弃兵思路', 'en': 'Queen’s Gambit ideas'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '白送的兵，有诈！', 'en': 'A Free Pawn? It’s a Trap!'},
                         'text': [{'zh': '1.d4 d5 之后，白棋明明已经占着中心，却还要把 c 兵“送”给黑方吃——',
                                   'en': 'After 1.d4 d5, White already owns the center — yet still '
                                         '"offers" the c-pawn to Black—'},
                                  {'zh': '这不是大方，是陷阱！直接冲 e4 会被 dxe4 白吃一兵（d5 兵守着 e4 格），',
                                   'en': 'That’s not generosity, it’s a trap! Charging e4 directly '
                                         'loses a pawn to dxe4 (the d5 pawn guards e4),'},
                                  {'zh': '所以先用 c4 把黑兵从中心“钓”走。走三步演变，你就看明白了。',
                                   'en': 'so c4 first fishes the black pawn away from the center. '
                                         'Play the three-move line and you’ll see.'}],
                         'fen': 'rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 2'},
                        {'type': 'line',
                         'fen': 'rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq d6 0 2',
                         'script': ['c2c4', 'd5c4', 'e2e4'],
                         'endsWithMate': False,
                         'prompts': [{'zh': '白棋冲 c4，把兵送到黑兵嘴边（弃兵！）。',
                                      'en': 'White pushes c4, dangling the pawn in front of the '
                                            'black pawn (the gambit!).'},
                                     {'zh': '黑兵贪吃了：离开 d5 中心，吃掉 c4。白棋立刻冲 e 兵：',
                                      'en': 'Black gets greedy: leaves the d5 center to take c4. '
                                            'White immediately pushes the e-pawn:'}],
                         'hint': {'zh': '跟着提示走：c4 弃兵 → 黑吃 → e4 冲中。',
                                  'en': 'Follow the plan: c4 gambit → Black takes → e4 into the '
                                        'center.'},
                         'successText': {'zh': '看清了吗？黑兵离开中心去贪吃，白棋 d4+e4 双兵镇中心——弃一个边兵，换来整个中心！',
                                         'en': 'See it now? The black pawn left the center to '
                                               'snack, and White’s d4+e4 pawns rule the center — '
                                               'trade a flank pawn for the whole center!'}},
                        {'type': 'move',
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                         'prompt': {'zh': '同一个思路的另一种玩法——英国式开局：第一步直接冲 c 兵到 c4！',
                                    'en': 'The same idea, another flavor — the English Opening: '
                                          'push the c-pawn to c4 on move one!'},
                         'accepted': ['c2c4'],
                         'hint': {'zh': 'c 兵向前两格。', 'en': 'The c-pawn goes two squares forward.'},
                         'successText': {'zh': '1.c4！英国式开局：c 兵从侧面瞄准中心 d5 格，又不暴露计划——和后翼弃兵异曲同工。',
                                         'en': '1.c4! The English Opening: the c-pawn aims at d5 '
                                               'from the side without revealing the plan — same '
                                               'spirit as the Queen’s Gambit.'}}]},
             {'id': 'o4c',
              'title': {'zh': '世界名开局（黑棋篇）', 'en': 'Famous Openings (Black’s Side)'},
              'goal': {'zh': '认识西西里防御、古印度防御',
                       'en': 'Meet the Sicilian Defense and the King’s Indian Defense'},
              'skill': {'zh': '经典开局（黑）', 'en': 'Classic openings (Black)'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '黑棋的名开局，叫“防御”',
                                   'en': 'Black’s Famous Openings Are Called "Defenses"'},
                         'text': [{'zh': '执黑后手不用怕！黑棋也有响当当的经典开局，名字叫“防御”。',
                                   'en': 'Don’t fear playing Black! Black has famous classic '
                                         'openings too, called "defenses".'},
                                  {'zh': '执黑的两大经典武器：对白兵 e4 用西西里防御（不对称抢地盘、对攻反击），',
                                   'en': 'Black’s two classic weapons: against e4, the Sicilian '
                                         'Defense (asymmetric counterattack),'},
                                  {'zh': '对白兵 d4 用古印度防御（先让出中心，架好堡垒象再反击）。',
                                   'en': 'and against d4, the King’s Indian Defense (yield the '
                                         'center first, set up the fortress bishop, then strike '
                                         'back).'},
                                  {'zh': '这次棋盘会调转方向——你来执黑棋！',
                                   'en': 'This time the board flips — you play Black!'}]},
                        {'type': 'move',
                         'fen': 'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1',
                         'prompt': {'zh': '西西里防御：白棋冲 e4 占中心，你不跟他对称——冲 c 兵到 c5 应战！',
                                    'en': 'Sicilian Defense: White pushes e4 for the center — '
                                          'don’t copy symmetrically; answer with the c-pawn to '
                                          'c5!'},
                         'accepted': ['c7c5'],
                         'hint': {'zh': '黑方 c 兵向前两格（从下往上冲）。',
                                  'en': 'Black’s c-pawn goes two squares forward (upward from your '
                                        'side).'},
                         'successText': {'zh': '1...c5！西西里防御。不对称战斗开始：你抢 c 线地盘，对攻到底！',
                                         'en': '1...c5! The Sicilian Defense. The asymmetric '
                                               'battle begins: you grab c-file ground and fight '
                                               'back!'},
                         'orientation': 'black'},
                        {'type': 'move',
                         'fen': 'rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1',
                         'prompt': {'zh': '古印度防御：白棋冲 d4，你跳马 g8 到 f6 应战！',
                                    'en': 'King’s Indian Defense: White pushes d4 — answer with '
                                          'the g8 knight to f6!'},
                         'accepted': ['g8f6'],
                         'hint': {'zh': '黑方 g8 的马跳到 f6。', 'en': 'Black’s g8 knight jumps to f6.'},
                         'successText': {'zh': '1...Nf6！古印度防御第一步。接下来黑棋会走 g6、象 g7 架起“堡垒象”，再反击中心！',
                                         'en': '1...Nf6! The first move of the King’s Indian. Next '
                                               'Black plays g6 and Bg7 to set up the "fortress '
                                               'bishop", then counterattacks the center!'},
                         'orientation': 'black'}]}]},
 {'id': 'battle',
  'badge': {'zh': '实战篇', 'en': 'Battle'},
  'title': {'zh': '实战演练场', 'en': 'The Battlefield'},
  'intro': {'zh': '学会了本领，就要真刀真枪地下棋！和电脑对战，把学到的全用出来。',
            'en': 'Skills learned — time for real games! Play the computer and use everything you '
                  'learned.'},
  'color': '#7C4DA0',
  'soft': '#EDE6F6',
  'levels': [{'id': 'b1',
              'title': {'zh': '初战电脑宝宝', 'en': 'First Game vs Baby Bot'},
              'goal': {'zh': '和随意走棋的电脑下一盘', 'en': 'Play a full game against the careless computer'},
              'skill': {'zh': '完整对局经验', 'en': 'A full game of experience'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '真刀真枪第一盘', 'en': 'Your First Real Game'},
                         'text': [{'zh': '电脑宝宝会随便走棋，正好让你练手。',
                                   'en': 'The baby bot moves randomly — perfect for practice.'},
                                  {'zh': '目标：将死它的王，或者吃掉它的皇后，就算你赢！',
                                   'en': 'Goal: checkmate its king, or capture its queen — either '
                                         'wins!'},
                                  {'zh': '记得用上你的本领：占中心、快出子、找机会底线杀。',
                                   'en': 'Use your skills: take the center, develop fast, and look '
                                         'for a back-rank mate.'}],
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'},
                        {'type': 'play',
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                         'bot': 'random',
                         'win': 'mateOrQueen',
                         'prompt': {'zh': '你执白棋先走。将死黑王，或吃掉黑后，就获胜！',
                                    'en': 'You are White and move first. Mate the black king or '
                                          'capture the black queen to win!'},
                         'hint': {'zh': '电脑宝宝乱走棋，很容易露出没人保护的棋子——数数保护，大胆吃！',
                                  'en': 'The baby bot moves randomly and leaves pieces unprotected '
                                        '— count defenders and capture boldly!'},
                         'successText': {'zh': '你赢了第一盘真棋！', 'en': 'You won your first real game!'},
                         'failText': {'zh': '被将死了，没关系，再来一盘！',
                                      'en': 'Checkmated? No worries — play again!'},
                         'drawText': {'zh': '和棋了！差一点点，再来一盘吧。',
                                      'en': 'A draw! So close — play one more.'}}]},
             {'id': 'b2',
              'title': {'zh': '大战贪吃鬼', 'en': 'Battle the Greedy Bot'},
              'goal': {'zh': '战胜会吃子、会将军的电脑', 'en': 'Beat the computer that captures and checks'},
              'skill': {'zh': '实战攻防', 'en': 'Attack and defense in real games'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '这个对手会吃子！', 'en': 'This Opponent Captures!'},
                         'text': [{'zh': '“贪吃鬼”电脑会吃掉你没保护的棋子，还会找机会将军。',
                                   'en': 'The "greedy" bot eats your unprotected pieces and looks '
                                         'for checks.'},
                                  {'zh': '所以：走每一步之前，先看看自己的棋子有没有保护！',
                                   'en': 'So before every move, check whether your pieces are '
                                         'protected!'},
                                  {'zh': '目标不变：将死它，或吃掉它的皇后。',
                                   'en': 'Same goal: mate it, or take its queen.'}],
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'},
                        {'type': 'play',
                         'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                         'bot': 'greedy',
                         'win': 'mateOrQueen',
                         'prompt': {'zh': '你执白棋先走。小心：它会吃掉你没保护的棋子！',
                                    'en': 'You are White and move first. Careful: it will eat any '
                                          'unprotected piece!'},
                         'hint': {'zh': '故意放个没人保护的小兵当诱饵，等它贪吃时，看看能不能惩罚它！',
                                  'en': 'Try leaving a pawn unprotected as bait — when it gets '
                                        'greedy, see if you can punish it!'},
                         'successText': {'zh': '战胜了贪吃鬼！你的棋子都有保护意识了。',
                                         'en': 'You beat the greedy bot! Your pieces all have '
                                               'bodyguards now.'},
                         'failText': {'zh': '被将死了……检查一下哪步棋把子送掉啦？再来！',
                                      'en': 'Checkmated… check which move gave a piece away. '
                                            'Again!'},
                         'drawText': {'zh': '和棋！稳稳的，再来一盘争取赢。',
                                      'en': 'A draw! Solid — one more game, go for the win.'}}]},
             {'id': 'b3',
              'title': {'zh': '车王杀王实操', 'en': 'Rook-and-King Mate for Real'},
              'goal': {'zh': '用“车+王”将死活王——真本事！',
                       'en': 'Mate a living king with rook and king — real skill!'},
              'skill': {'zh': '车王杀单王', 'en': 'Rook-and-king mate'},
              'steps': [{'type': 'teach',
                         'title': {'zh': '把学到的用出来', 'en': 'Use What You Learned'},
                         'text': [{'zh': '实战里最常见的终局：你剩车和王，对方只剩光杆王。',
                                   'en': 'The most common endgame in real games: you have rook and '
                                         'king; they have a bare king.'},
                                  {'zh': '秘诀：车负责“砍格子”，把黑王的活动范围越切越小，逼到棋盘边再将死。',
                                   'en': 'The secret: the rook "cuts squares", shrinking the black '
                                         'king’s space smaller and smaller, then mates at the '
                                         'edge.'},
                                  {'zh': '这次没有固定答案——电脑会真的躲，你要真的追！',
                                   'en': 'No fixed answer this time — the computer really dodges, '
                                         'and you really chase!'}],
                         'fen': '6k1/8/8/8/8/8/8/R5K1 w - - 0 1',
                         'arrows': [['a1', 'a8']]},
                        {'type': 'play',
                         'fen': '6k1/8/8/8/8/8/8/R5K1 w - - 0 1',
                         'bot': 'smart',
                         'win': 'mate',
                         'prompt': {'zh': '你执白棋先走：用车把黑王逼到棋盘边，将死它！',
                                    'en': 'You are White: use the rook to drive the black king to '
                                          'the edge and mate it!'},
                         'hint': {'zh': '车先把黑王切成两半，王再慢慢靠上来帮忙。别把王逼成“逼和”（没棋走但没被将军）哦！',
                                  'en': 'Cut the king in half with the rook first, then bring your '
                                        'king up slowly. Careful not to stalemate (no moves but '
                                        'not in check)!'},
                         'successText': {'zh': '真的将死了活王！这是货真价实的棋力。',
                                         'en': 'You really mated a living king! That is genuine '
                                               'chess strength.'},
                         'failText': {'zh': '被它反杀了？不可能——再来一次！',
                                      'en': 'It mated YOU? Impossible — one more time!'},
                         'drawText': {'zh': '逼和了！黑王没棋走但没被将军算和棋。下次将军前，给它留个格子。',
                                      'en': 'Stalemate! The black king has no moves but isn’t in '
                                            'check — that’s a draw. Next time, leave it one square '
                                            'before checking.'}}]}]}]

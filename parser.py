import shogi
import shogi.KIF
import re
import sys


def place_board(md, board, board_number=None, last_move=None, caption=None):
    '''
    add board's caption to .md file

    Parameters:
        md(list()) : list
        board(shogi.Board()) : boards
    '''
    # set caption
    if caption == None:
        caption = str()

        # board number
        if board_number != None:
            caption += '【第' + str(board_number) + '図】'

        # move number and last move
        if board.move_number != 1:
            caption += str(board.move_number - 1) + '手目'
            caption += last_move
            caption += "まで"
        else:
            caption += "初期局面"
    
    last = str()
    last += '手数＝' + str(board.move_number - 1) + '　'
    if board.move_number != 1:
        last += '▲△'[board.move_number % 2] + last_move[1:] + '　まで'

    html = [
        '<figure class="zumen">',
        '<figcaption>' + caption + '</figcaption>',
        '<pre class="shogizumen">',
        board.kif_str(),
        last,
        '</pre>',
        '</figure><br>'
    ]
    md.extend(html)
    return


def bold(s):
    return "<b>" + s + "</b>"


def colored_red(s):
    return '<span style ="color: red">' + bold(s) + '</span>'


def kif_to_md(path):
    '''
    convert .kif file to .md file

    Parameters:
        path(str) : path of (.kif | .kifu) file

    Returns:
        str: data of .md file
    '''

    # set encoding
    if re.search(".kif\Z", path):
        charset = "cp932"
    elif re.search(".kifu\Z", path):
        charset = "utf-8"
    else:
        print("extansion error")
        raise RuntimeError

    # open file
    fp = open(path, mode='r', encoding=charset)
    raw_kif = fp.readlines()

    # see: https://github.com/gunyarakun/python-shogi/blob/master/shogi/KIF.py
    # kif.['sfen'] ... initial board
    # kif.['moves'] ... move
    kif = shogi.KIF.Parser.parse_str(''.join(raw_kif))[0]
    # output file (list containing str)
    md = list()
    # board
    board = shogi.Board(kif['sfen'])
    # number of board (【第〇図】)
    board_number = 1
    # last move
    last_moves = list()
    # last comment
    last_comment = list()
    # move number
    move_number = 1

    # wrapper of place_board
    def board_push(caption=None):
        last_move = None if len(last_moves) == 0 else last_moves[-1]
        place_board(md, board, board_number, last_move, caption)

    def caption_push(caption=None):
        # detail
        detail = "<br><br>\n "
        detail += bold("【第" + str(board_number - 1) + "図からの指し手】")+"\n"
        md.append(detail)
        # moves
        for i in range(0, len(last_moves), 4):
            moves = ''.join(last_moves[i:min(i+4, len(last_moves))])
            md.append(colored_red(moves) + '\n')
        md.append(bold("（第" + str(board_number) + "図）"))
        # board
        board_push(caption if len(caption) > 0 else None)
        # comment
        md.extend(last_comment)
        # reset value
        return [board_number+1, list(), list()]

    # push initial board
    board_push()
    board_number += 1

    for line in raw_kif:
        # move
        lst = line.split()
        if len(lst) == 0:
            continue
        if lst[0] == str(move_number):
            # move
            if len(kif['moves']) < move_number:
                # resign, terminate, draw, ...etc
                break
            # move board
            board.push_usi(kif['moves'][move_number - 1])
            # push moves
            move = '☖☗'[move_number % 2] + lst[1].rstrip('123456789()')
            last_moves.append(move)
            move_number += 1
        elif lst[0][0] == '*':
            if lst[0] == '*cap':
                # push data
                caption = line[4:].lstrip().rstrip()
                caption = None if len(caption) == 0 else caption
                board_number, last_moves, last_comment = caption_push(caption)
            else:
                # comment
                comment = line[1:].lstrip().rstrip()
                last_comment.append(comment + '\n')
            pass
        elif lst[0][0] == '&':
            # push data
            caption = line[1:].lstrip().rstrip()
            board_number, last_moves, last_comment = caption_push(caption)

    # return
    return '\n'.join(md)


# unit test
if __name__ == '__main__':
    path = "test.kif"
    with open("output.md", mode='w', encoding='utf-8') as f:
        f.write(kif_to_md(path))

import svgwrite
from private_colleges import private


private = private.split()

NULL_MARK = -200 # 学校缺席
BLANK_MARK = 0 # 不缺席但分数空白
ZOOM = 3 # svg size x 3

LI = True # 理科
SHOW_PRIVATE = True
SHOW_VOID = True
SHOW_HIGH = True
SHOW_LOW_OR_EQUAL = True

ROUNDS = 4
MAX_MARKS = 600
svg_size_width = ((ROUNDS - 1) * 100 + 10) * ZOOM
svg_size_height = MAX_MARKS * ZOOM

# collect marks:
marks = {}
for r in range(0, ROUNDS):
    with open('erben%d.json'%r, 'r') as f:
        a = eval(f.read())
    for i in a:
        try:
            x = int(i['FIELD3'])
        except:
            x = BLANK_MARK
        try:
            y = int(i['FIELD4'])
        except:
            y = BLANK_MARK
        if int(i['FIELD1']) not in marks:
            marks[int(i['FIELD1'])] = {
                    'name': i['FIELD2'],
                    'wen%d'%r: x,
                    'li%d'%r: y,
                }
        else:
            marks[int(i['FIELD1'])]['wen%d'%r] = x
            marks[int(i['FIELD1'])]['li%d'%r] = y
def main():
    # generate file name:
    filename_subfix = ''
    if SHOW_HIGH:
        filename_subfix += '升'
    if SHOW_LOW_OR_EQUAL:
        filename_subfix += '降'
    if SHOW_VOID:
        filename_subfix += '空'
    if SHOW_PRIVATE:
        filename_subfix += '私'

    if LI:
        filename = '理科映射-%s.svg'%filename_subfix
    else:
        filename = '文科映射-%s.svg'%filename_subfix

    # create canvas:
    dwg = svgwrite.Drawing(filename, (svg_size_width, svg_size_height), profile='tiny')
    g = svgwrite.container.Group(transform='scale(1,-1)')
    h = svgwrite.container.Group(transform='translate(2,%d)'%svg_size_height)
    h.add(g)
    dwg.add(h)


    # white background:
    temp = g.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill='rgb(255,255,255)'))
    # draw horizontal line:
    for r in range(0, ROUNDS):
        temp = g.add(dwg.line((r * 100 * ZOOM, 0), (r * 100 * ZOOM, 750 * ZOOM), stroke=svgwrite.rgb(10, 10, 10, '%')))

    # devide school lines into groups:
    # marks increased.
    # private colleage:
    high_group_private = svgwrite.container.Group()
    high_group_private_color = svgwrite.rgb(0, 0, 100, '%') # blue
    # pre or after mark is null:
    high_group_no = svgwrite.container.Group()
    high_group_no_color = svgwrite.rgb(50, 50, 50, '%') # gray
    # not the 2 abouve:
    high_group_other = svgwrite.container.Group()
    high_group_other_color = svgwrite.rgb(90, 0, 0, '%') # red

    low_group_private = svgwrite.container.Group()
    low_group_private_color = svgwrite.rgb(0, 0, 100, '%') # blue
    low_group_no = svgwrite.container.Group()
    low_group_no_color = svgwrite.rgb(50, 50, 50, '%') # gray
    low_group_other = svgwrite.container.Group()
    low_group_other_color = svgwrite.rgb(0, 0, 0, '%') # black


    # add to groups:
    for r in range(0, ROUNDS - 1):
        for key in marks:
            if LI:
                prefix = 'li'
            else:
                prefix = 'wen'
            try:
                prev = marks[key][prefix+'%d'%r]
            except:
                prev = NULL_MARK
            try:
                after = marks[key][prefix+'%d'%(r + 1)]
            except:
                after = NULL_MARK

            start_point = (r * 100 * ZOOM, prev * ZOOM)
            end_point = ((r + 1) * 100 * ZOOM, after * ZOOM)
            if '大学' in marks[key]['name'] and '学院' in marks[key]['name'] or \
                marks[key]['name'].count('学院') >=2 or marks[key]['name'] in private:
                if after > prev:
                    high_group_private.add(dwg.line(start_point, end_point, stroke=high_group_private_color))
                else:
                    low_group_private.add(dwg.line(start_point, end_point, stroke=low_group_private_color))
                    

            elif after in (NULL_MARK, BLANK_MARK) or prev in (NULL_MARK, BLANK_MARK):
                if after > prev:
                    high_group_no.add(dwg.line(start_point, end_point, stroke=high_group_no_color))
                else:
                    low_group_no.add(dwg.line(start_point, end_point, stroke=low_group_no_color))

            else:
                if after > prev:
                    high_group_other.add(dwg.line(start_point, end_point, stroke=high_group_other_color))
                else:
                    low_group_other.add(dwg.line(start_point, end_point, stroke=low_group_other_color))
                    if prev - after > 10:
                        print('降分', prev, after, prev - after, key, marks[key]['name'])


    # draw on canvas:
    if SHOW_PRIVATE:
        if SHOW_HIGH:
            g.add(high_group_private)
        if SHOW_LOW_OR_EQUAL:
            g.add(low_group_private)

    if SHOW_VOID:
        if SHOW_HIGH:
            g.add(high_group_no)
        if SHOW_LOW_OR_EQUAL:
            g.add(low_group_no)

    if SHOW_HIGH:
        g.add(high_group_other)
    if SHOW_LOW_OR_EQUAL:
        g.add(low_group_other)


    # draw horizontal ruler:
    for i in range(0, MAX_MARKS, 10):
        temp = h.add(dwg.line((0, -i * ZOOM), ((ROUNDS - 1) * 100 * ZOOM, -i * ZOOM), stroke=svgwrite.rgb(0, 100, 0, '%')))
        temp = h.add(dwg.text(i, insert=((ROUNDS - 1) * 100 * ZOOM, -i * ZOOM), fill=svgwrite.rgb(0, 80, 0, '%')))

    temp = h.add(dwg.text('二本投档', insert=(0, -16), fill='black'))
    temp = h.add(dwg.text('二本一补', insert=(100 * ZOOM, -16), fill='black'))

    temp = h.add(dwg.text('空白', insert=(0, -BLANK_MARK * ZOOM - 4), fill='red'))
    temp = h.add(dwg.text('缺席', insert=(70 * ZOOM, -BLANK_MARK * ZOOM - 4), fill='red'))
    temp = h.add(dwg.text('空白', insert=(100 * ZOOM, -BLANK_MARK * ZOOM - 4), fill='red'))
    # temp = h.add(dwg.text('Test', insert=(0, 14), fill='red'))
    dwg.save()

    print('已生成 %s 于当前文件夹下.'%filename)

main()
answer = input('是否全部生成? y|Y ')
if answer in ('y', 'Y'):
    for li in (True, False):
        LI = li

        # 显示全部
        SHOW_PRIVATE = True
        SHOW_VOID = True
        SHOW_HIGH = True
        SHOW_LOW_OR_EQUAL = True
        main()

        # 减去私校和空白
        SHOW_PRIVATE = False
        SHOW_VOID = False
        main()

        # 只显示高
        SHOW_HIGH = True
        SHOW_LOW_OR_EQUAL = False
        main()

        # 只显示低
        SHOW_HIGH = False
        SHOW_LOW_OR_EQUAL = True
        main()

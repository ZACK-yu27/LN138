while True:
    info = input('请依次输入鸡和兔的总数、腿的总数，以英文逗号隔开：')
    info_list = info.split(',')
    sum = int(info_list[0])
    feet = int(info_list[1])

    if sum <= 0:
        print('数据有误，请重新输入\n')
        continue

    else:
        feet_0 = sum * 4
        sum_rab = (feet_0 - feet) / 2
        sum_chick = sum - sum_rab
        
        if int(sum_rab) != sum_rab or int(sum_chick) != sum_chick or sum_rab <= 0 or sum_chick <=0:
            print('数据有误，请重新输入\n')

        else:
            print(f'鸡有{sum_chick}只，兔有{sum_rab}只')
            break
        
        continue
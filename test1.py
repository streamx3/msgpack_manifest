import mp_manifest
import logging


def status2str(status):
    rv = 'FAIL'
    if type(status) == bool and status is True:
        rv = ' OK '
    return rv


def test_mapdepth():
    test_str1 = 'a{b{c}d}e'
    test_rsp1 = [0, 1, 1, 2, 2, 2, 1, 1, 0]
    status = (test_rsp1 == mp_manifest.__map_depth(test_str1))
    print('[' + status2str(status) + '] Test mapdepth 1')

    test_str2 = 'asd{asASDASD{{ASD{asd{asd}asd}ASD{ASD{}asdasd{{ASD{}as}as}as}ad}}234}1'
    #            0001111111112333344445555544443334444554444445666677666555444333211110
    test_rsp2 = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 4, 4,
                 4, 4, 3, 3, 3, 4, 4, 4, 4, 5, 5, 4, 4, 4, 4, 4, 4, 5, 6, 6, 6, 6, 7, 7, 6, 6, 6, 5,
                 5, 5, 4, 4, 4, 3, 3, 3, 2, 1, 1, 1, 1, 0]

    status = (test_rsp2 == mp_manifest.__map_depth(test_str2))
    print('[' + status2str(status) + '] Test mapdepth 2')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_mapdepth()
    mp_manifest.readf("1.mpsch")

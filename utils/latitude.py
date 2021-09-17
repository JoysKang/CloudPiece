import re


class Degree(object):
    def __init__(self):
        pass

    @staticmethod
    def dd_to_dms(dd):
        """
        十进制度转为度分秒
        Paramaters:
            dd : 十进制度
        Return:
            dms : 度分秒
        """
        degree = int(float(dd))
        minute = int((float(dd) - degree) * 60)
        second = round((float(dd) - degree - float(minute) / 60) * 3600, 2)
        dms = str(degree) + '°' + str(minute) + '\'' + str(second) + "\""
        return dms

    @staticmethod
    def dms_to_dd(degree, minute, second):
        """
        度分秒转为十进制度
        Paramater:
            degree : 度
            minute : 分
            second : 秒
        Return:
            dd : 十进制度
        """
        dd = degree + minute / 60 + second / 60 / 60
        return dd

    @staticmethod
    def parse_dms(dms):
        """
        解析度分秒字符串
        Paramater:
            dms : 度分秒字符串
        Returns:
            degree : 度
            minute : 分
            second : 秒
        """
        parts = re.split('[°′″]', dms)
        degree = float(parts[0])
        minute = float(parts[1])
        second = float(parts[2])
        return {"degree": degree, "minute": minute, "second": second}


if __name__ == '__main__':
    print(Degree.dd_to_dms(36.129698))

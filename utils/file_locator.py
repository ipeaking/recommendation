import os
from sys import argv


# -------------------------------- prettifier

def prettify_dir(adir: str) -> str:
    """
    美化文件夹路径.
    
    输入: "..\\A\\B\\C"
    输出: "../A/B/C/"
    """
    if '\\' in adir:
        adir = adir.replace('\\', '/')
    if adir[-1] != '/':
        adir += '/'
    return adir


def prettify_file(afile: str) -> str:
    """
    美化文件路径.
    
    输入: "A\\B\\C.txt"
    输出: "A/B/C.txt"
    """
    if '\\' in afile:
        afile = afile.replace('\\', '/')
    return afile


# -------------------------------- basic path locator

def get_launch_path():
    """
    获得启动模块的绝对路径
    
    输入:
        sys.argv[0]
            e.g. 'D:\\workspace\\my_project\\A.py'
    输出:
        'D:/workspace/my_project/A.py'
    """
    path = os.path.abspath(argv[0])
    return prettify_file(path)


def find_project_dir(apath='', recursive_times=0):
    """
    获得当前项目的根目录的绝对路径.
    已知 afile = "D:/workspace/my_project/A/B/C/D.py", 求哪一个目录是该项目的根路径?

    提示:
        1. 项目路径下面有 ".idea" 文件夹, 这是一个判断特征
        2. os.listdir() 是一个可迭代对象, 使用 `iter(os.listdir())` 可将其转换为迭代器
        2. 使用迭代器, 可以大幅减少遍历文件树花费的时间

    原理:
        假设我们知道启动文件的绝对路径是 "D:/workspace/my_project/A/B/C/D.py", 我们以此
        为观察点, 不断向上查找 (递归), 看哪一层能够找到 ".idea" 文件夹, 当找到时, 就认为这
        是项目的根路径.

    输入:
        启动文件的绝对路径
            示例: "D:/workspace/my_project/A/B/C/D.py"
    输出:
        "D:/workspace/my_project/"

    注意:
        1. 本设计有一个缺陷, 假如我的项目结构为:
            D:/workspace/main_project/
                |- .idea
                |- sub_project
                    |- .idea
                    |- B.py
                |- A.py
            此时我打算从 main_project 项目启动并运行 B.py, 则本函数会误认为 sub_project
            是项目根路径.
            要避免此错误, 请这样做 (方法二选一):
                1. 删除 sub_project 下的 .idea 文件夹
                2. 新建一个 D:/workspace/main_project/C.py 引用 B.py 启动, 而不要直接
                从 B.py 启动

    """
    if not apath:
        apath = get_launch_path()
        # 第一次查找时, 获取启动文件的绝对路径
    if recursive_times > 10:
        # 预防机制: 当启动文件路径过深时 (默认深度为10层), 本函数会报错
        raise AttributeError

    d = os.path.dirname(apath)  # d is the abbr of directory
    p = iter(os.listdir(d))  # p is the abbr of paths

    while True:
        sd = p.__next__()  # sd is the abbr of sub-directory
        if sd[0] == '.':

            if sd == '.idea':
                # lk.prt('the project path is {}'.format(d))
                return prettify_dir(d)  # 返回项目根目录
            else:
                # 可能遇到了 '.abc', '.git', ... 文件夹
                continue
        elif sd in ['scheduler','cold_start', 'constant']:
            return prettify_dir(d)  # 返回项目根目录
        else:
            break

    return find_project_dir(d, recursive_times + 1)  # 递归查找


# --------------------------------

root = find_project_dir(get_launch_path())


def getfile(path):
    return root + path


if __name__ == '__main__':
    res = getfile(r'util')
    print(res)

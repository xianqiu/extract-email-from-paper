from data import Loader
from reader import BatchReader, Reader, EmailParser


def run():
    directories = [
        '/Users/xianqiu/Downloads/Conference/APMC2021_Proceedings',
        '/Users/xianqiu/Downloads/Conference/APMC2022_Proceedings/pdf/oral',
        '/Users/xianqiu/Downloads/Conference/APMC2022_Proceedings/pdf/vif',
        '/Users/xianqiu/Downloads/Conference/APMC2023_Proceedings',
        '/Users/xianqiu/Downloads/Conference/EuCAP2024_Proceedings/papers',
        '/Users/xianqiu/Downloads/Conference/EuMW2020_Proceedings',
        '/Users/xianqiu/Downloads/Conference/EuMW2021_Proceedings',
        '/Users/xianqiu/Downloads/Conference/EuMW2022_Proceedings',
        '/Users/xianqiu/Downloads/Conference/EuMW2023_Proceedings',
        '/Users/xianqiu/Downloads/Conference/IEEE WPTCE2023 Proceedings',
        '/Users/xianqiu/Downloads/Conference/IEEE WPTCE2024 Proceedings',
        '/Users/xianqiu/Downloads/Conference/IEEE WPW2020 Proceedings',
        '/Users/xianqiu/Downloads/Conference/IEEE WPW2021 Proceedings',
        '/Users/xianqiu/Downloads/Conference/IEEE WPW2022 Proceedings'
    ]
    jobs = Loader(directories).jobs()
    br = BatchReader(jobs)
    br.read().save()
    br.save_fail_jobs()


def check_fail_job(job_id):
    jobs = Loader.load_fail_jobs()
    text = Reader(jobs[job_id]).read()
    print("==== Text ====")
    print(text)
    res = EmailParser(text).parse()
    print("==== Result ====")
    print(res)


def check_success_job(job_id):
    jobs = Loader.load_success_jobs()
    text = Reader(jobs[job_id]).read()
    print("==== Text ====")
    print(text)
    res = EmailParser(text).parse()
    print("==== Result ====")
    print(res)


if __name__ == '__main__':
    run()
    #check_fail_job(0)


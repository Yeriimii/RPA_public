import os
import pickle

def save_data(data: str, filename: str = None, path: str = None) -> None:
    if path is None:
        path = './datafile/wb/'  # 개발용 path
    os.chdir(path)
    with open(f'{filename}.p', 'wb') as f:
        pickle.dump(data, f)

def get_data(filename, path: str = None) -> dict:
    if path is None:
        path = './datafile/wb/'  # 개발용 path
    os.chdir(path)
    try:
        with open(f'{filename}', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError as e:
        raise e


if __name__ == '__main__':
    ...
    # save_data(data, filename='')
    # data = get_data('')

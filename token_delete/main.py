import os
import logging
from datetime import datetime

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'file_deletion.log')),
        logging.StreamHandler()
    ]
)

def delete_specific_files(file_paths):
    """
    指定されたファイルを削除する
    
    Args:
        file_paths (list): 削除するファイルのフルパスのリスト
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f'ファイルを削除しました: {file_path}')
                else:
                    logging.warning(f'指定されたパスはファイルではありません: {file_path}')
            else:
                logging.warning(f'ファイルが存在しません: {file_path}')
                
        except PermissionError:
            logging.error(f'権限エラー - ファイルにアクセスできません: {file_path}')
        except Exception as e:
            logging.error(f'エラーが発生しました - {file_path}: {str(e)}')

if __name__ == "__main__":
    # 削除するファイルのパスをリストで指定
    FILES_TO_DELETE = [
        r"C:\Users\Yu\Documents\Codes\Trello_Automation\token.pickle",
    ]
    
    # ファイル削除の実行
    delete_specific_files(FILES_TO_DELETE)
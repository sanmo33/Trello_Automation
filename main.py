import os
import sys
import logging
from typing import List, Dict
import configparser
import datetime
import io
from trello import TrelloClient
from trello.exceptions import ResourceUnavailable

# ログエンコーディングを明示的に設定
def setup_logging():
    """
    ログ設定を行う関数
    UTF-8エンコーディングとコンソール出力に対応
    """
    # ログディレクトリ作成
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # ログファイルのパス
    log_file_path = os.path.join(log_dir, 'trello_todo.log')
    
    # ロガーの設定
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            # ファイルハンドラ
            logging.FileHandler(log_file_path, encoding='utf-8'),
            # コンソールハンドラ
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 文字化け防止のためのエンコーディング設定
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ログ設定を最初に呼び出し
setup_logging()
logger = logging.getLogger(__name__)

class TrelloTodoManager:
    def __init__(self, config_path='config.ini'):
        """
        Trelloボード管理クラスの初期化
        
        :param config_path: 設定ファイルのパス
        """
        try:
            # 設定ファイルの読み込み
            self.config = self._load_config(config_path)
            
            # 環境変数の設定
            self._set_environment_variables()
            
            # Trelloクライアントの初期化
            self.client = self._initialize_trello_client()
            
            # ボードとリストの取得
            self.board = self._get_board()
            self.todo_list = self.board.list_lists()[0]
            self.done_list = self.board.list_lists()[1]
            
            # 定義済みのTODOリスト
            self.everyday_todo = [
                '読書', 
                '筋トレ or ランニング',
                '技術に触れる',
                'プロテイン1',
                'プロテイン2',
                '朝のサプリ',
                '夜のサプリ',
                'pao1',
                'pao2',
                'くすり',
                '歯磨き',
                'ワセリン',
            ]
            
            self.classes = {
                "Mon": [],
                "Tue": [],
                "Wed": [],
                "Thu": [],
                "Fri": ['Workday', 'CATS'],
                "Sat": ['トイレ掃除'],
                "Sun": ['Skin Care'],
            }
        
        except (configparser.Error, KeyError) as e:
            logger.error(f"設定の読み込みに失敗しました: {e}")
            raise
        except ResourceUnavailable as e:
            logger.error(f"Trelloへの接続に失敗しました: {e}")
            raise

    def _load_config(self, config_path: str) -> configparser.ConfigParser:
        """
        設定ファイルを安全に読み込む
        
        :param config_path: 設定ファイルのパス
        :return: 設定オブジェクト
        """
        config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            logger.error(f"設定ファイル {config_path} が見つかりません")
            raise FileNotFoundError(f"設定ファイル {config_path} が存在しません")
        
        config.read(config_path, encoding='utf-8')
        return config

    def _set_environment_variables(self):
        """環境変数を安全に設定する"""
        try:
            login_section = self.config['login']
            env_vars = {
                'trello_key': login_section['api_key'],
                'trello_secret': login_section['trello_secret'],
                'id_board': login_section['bd_id'],
                'token': login_section['token']
            }
            
            for key, value in env_vars.items():
                os.environ[key] = value
        
        except KeyError as e:
            logger.error(f"設定ファイルに必要な項目が不足しています: {e}")
            raise

    def _initialize_trello_client(self) -> TrelloClient:
        """
        Trelloクライアントを初期化する
        
        :return: Trelloクライアント
        """
        try:
            return TrelloClient(
                api_secret=os.environ["trello_secret"],
                api_key=os.environ["trello_key"],
                token=os.environ["token"]  # トークンを追加
            )
        except Exception as e:
            logger.error(f"Trelloクライアントの初期化に失敗しました: {e}")
            raise

    def _get_board(self):
        """
        Trelloボードを取得する
        
        :return: Trelloボード
        """
        try:
            return self.client.get_board(os.environ["id_board"])
        except ResourceUnavailable as e:
            logger.error(f"ボードの取得に失敗しました: {e}")
            raise

    def manage_daily_todos(self):
        """
        日々のTODOを管理する
        """
        try:
            # 前日のTODOリストが空の場合、Doneリストをアーカイブ
            if not self.todo_list.list_cards():
                logger.info("TODOリストが空のため、Doneリストをアーカイブします")
                self.done_list.archive_all_cards()
            
            # 現在のTODOリストをアーカイブ
            self.todo_list.archive_all_cards()

            # 毎日のTODOを追加
            for todo in self.everyday_todo:
                self.todo_list.add_card(todo)

            # 曜日ごとのTODOを追加
            current_day = datetime.datetime.now().strftime('%a')
            self.add_day_specific_todos(current_day)

        except Exception as e:
            logger.error(f"日々のTODO管理中にエラーが発生しました: {e}")
            raise

    def add_day_specific_todos(self, day: str):
        """
        曜日固有のTODOを追加する
        
        :param day: 曜日の略称
        """
        try:
            day_todos = self.classes.get(day, [])
            for todo in day_todos:
                self.todo_list.add_card(todo)
        except Exception as e:
            logger.error(f"{day}の固有TODOの追加に失敗しました: {e}")

    def add_schedule_todos(self, schedule: List[str]):
        """
        スケジュールからTODOを追加する
        
        :param schedule: スケジュールのリスト
        """
        try:
            for event in schedule:
                self.todo_list.add_card(event)
        except Exception as e:
            logger.error(f"スケジュールTODOの追加に失敗しました: {e}")

def main():
    """
    メインエントリーポイント
    """
    try:
        # カスタム関数のインポートは既存の関数を想定
        from function import todays_event

        # TODOマネージャーの初期化
        todo_manager = TrelloTodoManager()
        
        # 日々のTODO管理
        todo_manager.manage_daily_todos()
        
        # 本日のスケジュールを取得して追加
        today_schedule = todays_event()
        todo_manager.add_schedule_todos(today_schedule)
        
        logger.info("TODOリストの更新が正常に完了しました")
    
    except Exception as e:
        logger.error(f"メイン処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
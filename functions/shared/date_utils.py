from datetime import datetime, timezone, timedelta


def get_jst_now() -> datetime:
    """現在のJST時刻を取得"""
    return datetime.now(timezone(timedelta(hours=9)))


def get_yesterday_jst() -> datetime:
    """昨日のJST時刻を取得"""
    return get_jst_now() - timedelta(days=1)

# QuoteToPaid

QuoteToPaid は、フリーランス向けの「見積 -> 請求 -> 入金確認 -> 催促」業務を一つの流れで管理するための Django + PostgreSQL アプリです。

## 使用技術

- Python 3.14
- Django
- PostgreSQL
- Pipenv
- Tailwind CSS
- ReportLab
- pytest

## ローカル開発手順

1. `.env.example` を `.env` にコピーし、PostgreSQL の接続情報を更新します。
2. 依存関係を `pipenv install` でインストールします。
3. `.env` に合わせて PostgreSQL のデータベースを作成します。
4. `pipenv run python manage.py migrate` でマイグレーションを適用します。
5. Tailwind 監視を `pipenv run python manage.py tailwind start` で起動します。
6. Django 開発サーバーを `pipenv run python manage.py runserver` で起動します。

## アプリ構成

- `billing/views/`: クラスベースビューのみを配置します。
- `billing/forms/`: `Form` と `ModelForm` を配置します。
- `billing/services/`: 業務ロジック用のサービスクラスを配置します。
- `billing/models/`: ドメインモデルを配置します。
- `billing/tests/`: 機能単位のテストモジュールを配置します。
- `templates/`: 共通テンプレートを配置します。
- `templates/billing/`: billing アプリ用テンプレートを配置します。

## 主要ルート

- `/`: ダッシュボードを表示します。
- `/health/`: JSON のヘルスチェックを返します。
- `/pdf/preview/`: 日本語の請求書プレビュー PDF を返します。
- `/admin/`: Django 管理画面です。

## テスト実行

- `pipenv run pytest --ds=config.settings`

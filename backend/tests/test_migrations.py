"""Alembic migration tests, including 006–009 schema revisions."""

import os

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from werkzeug.security import check_password_hash, generate_password_hash

from backend.models.user import User

REVISION_BEFORE_PASSWORD_HASH_WIDEN = '005'
PASSWORD_HASH_WIDEN_REVISION = '006'
HEAD_REVISION = '009'
RATE_LIMIT_COUNTERS_REVISION = '007'
TOKEN_VERSION_REVISION = '008'
REFRESH_TOKENS_REVISION = '009'
PASSWORD_HASH_WIDENED_LENGTH = 255

_USER_COLUMNS = (
    'id',
    'username',
    'password_hash',
    'email',
    'oauth_provider',
    'oauth_id',
    'is_active',
)


def _alembic_cfg() -> Config:
    """Return the project Alembic config (URL comes from DATABASE_URI)."""
    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    return Config(os.path.join(backend_dir, 'alembic.ini'))


def _configure_tmp_db(tmp_path, monkeypatch):
    """Point Alembic at a disposable SQLite file and return path/cfg/engine."""
    db_path = tmp_path / 'migrate_test.db'
    monkeypatch.setenv('DATABASE_URI', f'sqlite:///{db_path}')
    engine = create_engine(f'sqlite:///{db_path}')
    return db_path, _alembic_cfg(), engine


def _current_revision(engine) -> str | None:
    """Return the Alembic revision stored in the given database."""
    with engine.connect() as conn:
        return MigrationContext.configure(conn).get_current_revision()


def _fetch_users(engine) -> list[dict]:
    """Return every users row as a dict, ordered by id."""
    cols = ', '.join(_USER_COLUMNS)
    with engine.connect() as conn:
        rows = (
            conn.execute(text(f'SELECT {cols} FROM users ORDER BY id')).mappings().all()
        )
    return [dict(row) for row in rows]


def _unique_column_sets(inspector, table: str = 'users') -> set[tuple[str, ...]]:
    """Return unique constraint/index column sets for a table."""
    sets: set[tuple[str, ...]] = set()
    for unique in inspector.get_unique_constraints(table):
        sets.add(tuple(unique['column_names']))
    for index in inspector.get_indexes(table):
        if index.get('unique'):
            sets.add(tuple(index['column_names']))
    return sets


def _users_schema(engine) -> dict:
    """Snapshot users indexes, unique constraints, and column defaults."""
    inspector = inspect(engine)
    columns = {column['name']: column for column in inspector.get_columns('users')}
    return {
        'column_names': list(columns),
        'nullable': {name: column['nullable'] for name, column in columns.items()},
        'defaults': {name: column['default'] for name, column in columns.items()},
        'uniques': _unique_column_sets(inspector),
        'unique_names': {
            unique['name']
            for unique in inspector.get_unique_constraints('users')
            if unique['name']
        },
        'indexes': [
            (tuple(index['column_names']), bool(index.get('unique')))
            for index in inspector.get_indexes('users')
        ],
        'pk': inspector.get_pk_constraint('users')['constrained_columns'],
        'tables': set(inspector.get_table_names()),
        'password_hash_length': columns['password_hash']['type'].length,
    }


def _insert_user(engine, **values) -> None:
    """Insert one users row via SQL so tests do not depend on the ORM model."""
    columns = ', '.join(values)
    params = ', '.join(f':{name}' for name in values)
    with engine.begin() as conn:
        conn.execute(
            text(f'INSERT INTO users ({columns}) VALUES ({params})'),
            values,
        )


def test_alembic_upgrade_head(tmp_path, monkeypatch):
    db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, 'head')

    tables = inspect(engine).get_table_names()
    assert 'users' in tables
    assert 'rate_limit_counters' in tables
    assert 'refresh_tokens' in tables
    assert 'alembic_version' in tables
    assert _current_revision(engine) == HEAD_REVISION


def test_password_hash_column_fits_werkzeug_hash():
    """Model length must hold Werkzeug's default scrypt hash (~162 chars)."""
    sample = generate_password_hash('x')
    length = User.__table__.c.password_hash.type.length
    assert len(sample) > 128
    assert length >= len(sample)
    assert length == PASSWORD_HASH_WIDENED_LENGTH


def test_migration_006_preserves_rows_and_password_hashes(tmp_path, monkeypatch):
    """Upgrade 005 → 006 keeps every users value and hash verification."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, REVISION_BEFORE_PASSWORD_HASH_WIDEN)
    assert _current_revision(engine) == REVISION_BEFORE_PASSWORD_HASH_WIDEN

    schema_before = _users_schema(engine)
    assert schema_before['password_hash_length'] == 128

    scrypt_password = 'scrypt-secret-17a'
    pbkdf2_password = 'pbkdf2-secret-17a'
    scrypt_hash = generate_password_hash(scrypt_password)
    pbkdf2_hash = generate_password_hash(pbkdf2_password, method='pbkdf2:sha256')
    assert len(scrypt_hash) == 162
    assert len(pbkdf2_hash) < 128

    _insert_user(
        engine,
        username='scrypt_user',
        password_hash=scrypt_hash,
        email='scrypt@example.com',
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )
    _insert_user(
        engine,
        username='pbkdf2_user',
        password_hash=pbkdf2_hash,
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )
    _insert_user(
        engine,
        username='oauth_only',
        password_hash=None,
        email='oauth@example.com',
        oauth_provider='google',
        oauth_id='oauth-sub-1',
        is_active=1,
    )
    _insert_user(
        engine,
        username='inactive_user',
        password_hash=pbkdf2_hash,
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=0,
    )

    rows_before = _fetch_users(engine)
    assert len(rows_before) == 4

    command.upgrade(alembic_cfg, PASSWORD_HASH_WIDEN_REVISION)
    assert _current_revision(engine) == PASSWORD_HASH_WIDEN_REVISION

    rows_after = _fetch_users(engine)
    assert rows_after == rows_before
    assert check_password_hash(rows_after[0]['password_hash'], scrypt_password)
    assert check_password_hash(rows_after[1]['password_hash'], pbkdf2_password)
    assert rows_after[2]['password_hash'] is None
    assert check_password_hash(rows_after[3]['password_hash'], pbkdf2_password)

    schema_after = _users_schema(engine)
    assert schema_after['password_hash_length'] == PASSWORD_HASH_WIDENED_LENGTH
    assert schema_after['column_names'] == schema_before['column_names']
    assert schema_after['nullable'] == schema_before['nullable']
    assert schema_after['defaults'] == schema_before['defaults']
    assert schema_after['uniques'] == schema_before['uniques']
    assert schema_after['unique_names'] == schema_before['unique_names']
    assert schema_after['indexes'] == schema_before['indexes']
    assert schema_after['pk'] == schema_before['pk']
    assert schema_after['tables'] == schema_before['tables']
    assert schema_after['uniques'] == {
        ('username',),
        ('oauth_provider', 'oauth_id'),
    }
    assert 'uq_oauth' in schema_after['unique_names']
    assert schema_after['defaults']['is_active'] == "'1'"


def test_upgrade_head_is_idempotent(tmp_path, monkeypatch):
    """A second alembic upgrade head is a no-op: same revision, same rows."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, REVISION_BEFORE_PASSWORD_HASH_WIDEN)
    password = 'idempotent-secret'
    password_hash = generate_password_hash(password)
    _insert_user(
        engine,
        username='once',
        password_hash=password_hash,
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )
    command.upgrade(alembic_cfg, 'head')
    rows_first = _fetch_users(engine)
    revision_first = _current_revision(engine)

    command.upgrade(alembic_cfg, 'head')
    assert _current_revision(engine) == revision_first == HEAD_REVISION
    assert _fetch_users(engine) == rows_first
    assert check_password_hash(rows_first[0]['password_hash'], password)


def test_widened_column_round_trips_hash_longer_than_128(tmp_path, monkeypatch):
    """After 006 the inspected type is 255 and a 162-char hash round-trips."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, 'head')

    inspector = inspect(engine)
    password_hash_col = next(
        column
        for column in inspector.get_columns('users')
        if column['name'] == 'password_hash'
    )
    assert password_hash_col['type'].length == PASSWORD_HASH_WIDENED_LENGTH

    password = 'round-trip-secret'
    long_hash = generate_password_hash(password)
    assert len(long_hash) > 128
    _insert_user(
        engine,
        username='longhash',
        password_hash=long_hash,
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )
    stored = _fetch_users(engine)[0]['password_hash']
    assert stored == long_hash
    assert len(stored) == len(long_hash)
    assert check_password_hash(stored, password)


def test_downgrade_005_and_upgrade_again_on_short_hash_data(tmp_path, monkeypatch):
    """Downgrade 006 → 005 → head works when stored hashes fit in 128 chars.

    Downgrade can fail on Postgres/MySQL if a hash longer than 128 exists;
    this case only uses a short pbkdf2 hash.
    """
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, 'head')
    password = 'short-enough'
    short_hash = generate_password_hash(password, method='pbkdf2:sha256')
    assert len(short_hash) < 128
    _insert_user(
        engine,
        username='short_user',
        password_hash=short_hash,
        email='short@example.com',
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )
    rows_at_head = _fetch_users(engine)

    command.downgrade(alembic_cfg, REVISION_BEFORE_PASSWORD_HASH_WIDEN)
    assert _current_revision(engine) == REVISION_BEFORE_PASSWORD_HASH_WIDEN
    assert _users_schema(engine)['password_hash_length'] == 128
    assert _fetch_users(engine) == rows_at_head
    assert check_password_hash(rows_at_head[0]['password_hash'], password)

    command.upgrade(alembic_cfg, 'head')
    assert _current_revision(engine) == HEAD_REVISION
    assert _users_schema(engine)['password_hash_length'] == PASSWORD_HASH_WIDENED_LENGTH
    assert _fetch_users(engine) == rows_at_head
    assert check_password_hash(rows_at_head[0]['password_hash'], password)


def test_migration_007_rate_limit_counters_round_trip(tmp_path, monkeypatch):
    """007 creates rate_limit_counters; downgrade drops it; upgrade is back."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, PASSWORD_HASH_WIDEN_REVISION)
    assert 'rate_limit_counters' not in inspect(engine).get_table_names()

    command.upgrade(alembic_cfg, RATE_LIMIT_COUNTERS_REVISION)
    inspector = inspect(engine)
    assert 'rate_limit_counters' in inspector.get_table_names()
    columns = {
        column['name'] for column in inspector.get_columns('rate_limit_counters')
    }
    assert columns == {'scope', 'key', 'window_start', 'hit_count', 'expires_at'}
    pk = inspector.get_pk_constraint('rate_limit_counters')['constrained_columns']
    assert pk == ['scope', 'key', 'window_start']

    with engine.begin() as conn:
        conn.execute(
            text(
                'INSERT INTO rate_limit_counters '
                '(scope, key, window_start, hit_count, expires_at) '
                "VALUES ('auth_ip', '192.0.2.1', 100, 3, 160)"
            )
        )

    command.downgrade(alembic_cfg, PASSWORD_HASH_WIDEN_REVISION)
    assert _current_revision(engine) == PASSWORD_HASH_WIDEN_REVISION
    assert 'rate_limit_counters' not in inspect(engine).get_table_names()
    assert 'users' in inspect(engine).get_table_names()

    command.upgrade(alembic_cfg, 'head')
    assert _current_revision(engine) == HEAD_REVISION
    assert 'rate_limit_counters' in inspect(engine).get_table_names()
    with engine.connect() as conn:
        remaining = conn.execute(
            text('SELECT COUNT(*) FROM rate_limit_counters')
        ).scalar()
    assert remaining == 0


def test_migration_008_adds_token_version_for_existing_users(tmp_path, monkeypatch):
    """008 backfills token_version=0 on existing users; downgrade drops it."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, RATE_LIMIT_COUNTERS_REVISION)
    assert _current_revision(engine) == RATE_LIMIT_COUNTERS_REVISION
    users_columns = {column['name'] for column in inspect(engine).get_columns('users')}
    assert 'token_version' not in users_columns

    _insert_user(
        engine,
        username='pre_tv',
        password_hash=generate_password_hash('existing-user'),
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )

    command.upgrade(alembic_cfg, TOKEN_VERSION_REVISION)
    assert _current_revision(engine) == TOKEN_VERSION_REVISION
    inspector = inspect(engine)
    token_col = next(
        column
        for column in inspector.get_columns('users')
        if column['name'] == 'token_version'
    )
    assert token_col['nullable'] is False
    with engine.connect() as conn:
        versions = conn.execute(
            text('SELECT username, token_version FROM users ORDER BY id')
        ).all()
    assert versions == [('pre_tv', 0)]

    _insert_user(
        engine,
        username='post_tv',
        password_hash=generate_password_hash('new-user'),
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )
    with engine.connect() as conn:
        new_version = conn.execute(
            text("SELECT token_version FROM users WHERE username = 'post_tv'")
        ).scalar()
    assert new_version == 0

    command.downgrade(alembic_cfg, RATE_LIMIT_COUNTERS_REVISION)
    assert _current_revision(engine) == RATE_LIMIT_COUNTERS_REVISION
    assert 'token_version' not in {
        column['name'] for column in inspect(engine).get_columns('users')
    }
    with engine.connect() as conn:
        remaining = (
            conn.execute(text('SELECT username FROM users ORDER BY id')).scalars().all()
        )
    assert remaining == ['pre_tv', 'post_tv']

    command.upgrade(alembic_cfg, 'head')
    assert _current_revision(engine) == HEAD_REVISION
    with engine.connect() as conn:
        versions = conn.execute(
            text('SELECT username, token_version FROM users ORDER BY id')
        ).all()
    assert versions == [('pre_tv', 0), ('post_tv', 0)]


def test_migration_009_adds_refresh_tokens_for_existing_users(tmp_path, monkeypatch):
    """009 creates refresh_tokens; existing users stay; downgrade drops it."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, TOKEN_VERSION_REVISION)
    assert _current_revision(engine) == TOKEN_VERSION_REVISION
    assert 'refresh_tokens' not in inspect(engine).get_table_names()

    _insert_user(
        engine,
        username='pre_refresh',
        password_hash=generate_password_hash('existing-user'),
        email=None,
        oauth_provider=None,
        oauth_id=None,
        is_active=1,
    )

    command.upgrade(alembic_cfg, REFRESH_TOKENS_REVISION)
    assert _current_revision(engine) == REFRESH_TOKENS_REVISION
    inspector = inspect(engine)
    assert 'refresh_tokens' in inspector.get_table_names()
    columns = {column['name'] for column in inspector.get_columns('refresh_tokens')}
    assert columns == {
        'id',
        'user_id',
        'family_id',
        'token_hash',
        'token_version',
        'created_at',
        'expires_at',
        'family_expires_at',
        'used_at',
        'revoked_at',
        'user_agent',
    }
    with engine.connect() as conn:
        remaining = conn.execute(text('SELECT COUNT(*) FROM users')).scalar()
        tokens = conn.execute(text('SELECT COUNT(*) FROM refresh_tokens')).scalar()
    assert remaining == 1
    assert tokens == 0

    command.downgrade(alembic_cfg, TOKEN_VERSION_REVISION)
    assert _current_revision(engine) == TOKEN_VERSION_REVISION
    assert 'refresh_tokens' not in inspect(engine).get_table_names()
    with engine.connect() as conn:
        users = conn.execute(text('SELECT username FROM users')).scalars().all()
    assert users == ['pre_refresh']

    command.upgrade(alembic_cfg, 'head')
    assert _current_revision(engine) == HEAD_REVISION
    assert 'refresh_tokens' in inspect(engine).get_table_names()
    with engine.connect() as conn:
        versions = conn.execute(text('SELECT username, token_version FROM users')).all()
    assert versions == [('pre_refresh', 0)]


def test_alembic_check_reports_no_model_drift(tmp_path, monkeypatch):
    """alembic check is a no-op once head matches the SQLAlchemy models."""
    _db_path, alembic_cfg, engine = _configure_tmp_db(tmp_path, monkeypatch)
    command.upgrade(alembic_cfg, 'head')
    command.check(alembic_cfg)
    assert _current_revision(engine) == HEAD_REVISION

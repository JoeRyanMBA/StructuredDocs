import argparse
import os

import psycopg2


def fetch_enums(database_url: str) -> None:
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute('SELECT enumtypid, enumlabel FROM pg_enum ORDER BY enumtypid, enumsortorder;')
            enums = cursor.fetchall()
            print('All enum values in database:')
            for enum in enums:
                print(f'  {enum}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Inspect enum values in the connected PostgreSQL database.')
    parser.add_argument('--url', default=os.environ.get('DATABASE_URL'), help='PostgreSQL connection URL (defaults to DATABASE_URL env variable).')
    args = parser.parse_args()

    if not args.url:
        print('❌ No database URL provided. Set DATABASE_URL or pass --url.')
        return 1

    fetch_enums(args.url)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

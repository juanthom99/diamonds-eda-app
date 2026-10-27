"""Load the public Diamonds dataset from Supabase, with an offline fallback."""
import os
from pathlib import Path

import pandas as pd

COLUMNS = ['carat', 'cut', 'color', 'clarity', 'depth', 'table', 'price', 'x', 'y', 'z']


def load_diamonds(*, url=None, key=None, client_factory=None, csv_path=None):
    url = url if url is not None else os.environ.get('SUPABASE_URL')
    key = key if key is not None else os.environ.get('SUPABASE_KEY')
    csv_path = Path(csv_path) if csv_path else Path(__file__).parent / 'data' / 'diamonds.csv'
    if url and key:
        try:
            if client_factory is None:
                from supabase import create_client
                client_factory = create_client
            client = client_factory(url, key)
            records = []
            for start in range(0, 100_000, 1000):
                result = (client.table('diamonds').select(','.join(COLUMNS))
                          .order('id').range(start, start + 999).execute())
                records.extend(result.data)
                if len(result.data) < 1000:
                    break
            frame = pd.DataFrame(records)
            if frame.empty or not set(COLUMNS).issubset(frame.columns):
                raise ValueError('The remote dataset is empty or incomplete.')
            return frame[COLUMNS], 'Supabase'
        except Exception:
            # A database outage should not expose a traceback to public visitors.
            return pd.read_csv(csv_path)[COLUMNS], 'Bundled CSV (Supabase unavailable)'
    return pd.read_csv(csv_path)[COLUMNS], 'Bundled CSV'

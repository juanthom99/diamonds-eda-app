import unittest
from pathlib import Path
from types import SimpleNamespace
from data_source import load_diamonds,COLUMNS

class SourceTests(unittest.TestCase):
 def test_snapshot_has_full_dataset(self):
  frame,source=load_diamonds(url='',key='')
  self.assertEqual(len(frame),53940)
  self.assertEqual(list(frame.columns),COLUMNS)
  self.assertEqual(source,'Bundled CSV')

 def test_connection_failure_is_labeled(self):
  def unavailable(*args): raise ConnectionError('offline')
  frame,source=load_diamonds(url='https://example.test',key='test',client_factory=unavailable)
  self.assertEqual(len(frame),53940)
  self.assertIn('Supabase unavailable',source)

 def test_database_pagination_does_not_stop_at_1000(self):
  class Client:
   def table(self,*args): return self
   def select(self,*args): return self
   def order(self,*args): return self
   def range(self,start,end): self.start=start; return self
   def execute(self):
    row=dict(zip(COLUMNS,[1,'Ideal','D','IF',60,55,1000,1,1,1]))
    return SimpleNamespace(data=[row]*(1000 if self.start==0 else 1))
  frame,source=load_diamonds(url='https://example.test',key='test',client_factory=lambda *args:Client())
  self.assertEqual(len(frame),1001)
  self.assertEqual(source,'Supabase')

if __name__=='__main__': unittest.main()

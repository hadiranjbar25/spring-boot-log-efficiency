"""Measurement checks: keep mixed outputs and repeated reads from biasing attribution."""
import unittest
from natural_analyze import classify
from analyze import measure
class ClassificationTest(unittest.TestCase):
 def test_repeated_full_read(self):
  log='[ERROR] unique constraint failure\n'
  row,parts=classify('/bin/zsh -lc "cat failure.log; cat failure.log; cat Defects.java"',log+log+'package com.ai;\n',log)
  self.assertEqual(row['category'],'mixed')
  self.assertEqual(len(parts),2)
  self.assertEqual(row['log_token_lower'],2*measure(log)['tokens'])
 def test_discovery_is_not_reading(self):
  row,_=classify("pwd; rg --files -g 'failure.log' -g 'Defects.java'",'failure.log\nDefects.java\n','log')
  self.assertFalse(row['log_directed']);self.assertEqual(row['category'],'other')
 def test_source_and_status_is_mixed(self):
  row,_=classify("cat Defects.java; git status --short",'code\nstatus','log')
  self.assertEqual(row['category'],'mixed');self.assertFalse(row['log_directed'])
 def test_directory_source_search(self):
  row,_=classify("git status --short; rg -n 'connect' investigation",'Defects.java:17:connect','log')
  self.assertEqual(row['category'],'mixed');self.assertTrue(row['source_directed'])
 def test_source_not_log(self):
  row,_=classify('cat Defects.java','code','log')
  self.assertEqual(row['category'],'source_read');self.assertEqual(row['log_token_lower'],0)
 def test_test_not_inspection(self):
  row,_=classify('./test.sh','test output','log')
  self.assertEqual(row['category'],'test_command');self.assertEqual(row['log_token_lower'],0)
 def test_pure_search(self):
  row,_=classify("rg -n 'ERROR|Caused by' failure.log",'4:[ERROR] failure\n','log')
  self.assertEqual(row['category'],'log_inspection');self.assertGreater(row['log_token_lower'],0)
 def test_unresolved_mixed(self):
  row,_=classify("rg ERROR failure.log; cat Defects.java",'partial and source','log')
  self.assertTrue(row['unallocated_log_mixed']);self.assertEqual(row['log_token_lower'],0)
  self.assertGreater(row['log_token_upper'],0)
 def test_find_in_search_pattern_is_not_command(self):
  row,_=classify("rg 'Could not find a valid Docker environment' /tmp/case09.log",'Docker failure\n','log')
  self.assertEqual(row['category'],'log_inspection')
 def test_redirected_test_then_tail(self):
  row,parts=classify('./test.sh -Dexperiment.case=05 > /tmp/case05.log 2>&1; tail -n 15 /tmp/case05.log','BUILD SUCCESS\n','initial log')
  self.assertEqual(row['category'],'mixed');self.assertEqual(parts,['BUILD SUCCESS\n']);self.assertFalse(row['unallocated_log_mixed'])
 def test_direct_jshell_verification(self):
  row,_=classify('/jdk/bin/jshell --class-path target/test-classes <<EOF\nvar p = new Defects().readyPattern();\nEOF','verified','log')
  self.assertEqual(row['category'],'test_command')
 def test_source_read_and_assertion_is_mixed(self):
  row,_=classify("python3 - <<'PY'\nsource = Path('Defects.java').read_text()\nassert source\nPY",'passed','log')
  self.assertEqual(row['category'],'mixed');self.assertTrue(row['test_execution'])
 def test_literal_slice(self):
  row,parts=classify("sed -n '2,3p' failure.log; cat Defects.java",'two\nthree\ncode','one\ntwo\nthree\nfour\n')
  self.assertEqual(parts,['two\nthree\n']);self.assertFalse(row['unallocated_log_mixed'])
if __name__=='__main__':unittest.main()

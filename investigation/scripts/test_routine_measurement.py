"""Checks for the new initial-log/diff boundary and live-suite endpoint."""
import unittest
from natural_analyze import classify
from analyze import measure
from routine_measurement import normalize_command
class RoutineMeasurementTest(unittest.TestCase):
 def test_log_and_change_diff_remain_separate(self):
  raw='cat change.diff; cat test-output.log'
  log='[INFO] BUILD SUCCESS\n'
  cl,segments=classify(normalize_command(raw),'implementation diff\n'+log,log)
  self.assertEqual(cl['category'],'mixed');self.assertEqual(segments,[log]);self.assertEqual(cl['log_token_lower'],measure(log)['tokens'])
 def test_multi_argument_cat(self):
  raw="/bin/zsh -lc 'cat change.diff test-output.log test.sh'"
  cl,segments=classify(normalize_command(raw),'diff\nBUILD SUCCESS\nscript','BUILD SUCCESS\n')
  self.assertEqual(cl['category'],'mixed');self.assertEqual(segments,['BUILD SUCCESS\n'])
 def test_glob_log_read(self):
  cl,_=classify(normalize_command("cat container-logs/*.log"),'worker ready\n','')
  self.assertEqual(cl['category'],'log_inspection')
 def test_live_suite_is_test_output_not_zero_consumption(self):
  cl,segments=classify('./test.sh','Tests run: 13, Failures: 1\n','')
  self.assertEqual(cl['category'],'test_command');self.assertTrue(cl['test_execution']);self.assertEqual(segments,[])
 def test_repeated_passing_reads_count_twice(self):
  log='BUILD SUCCESS\n'
  cl,segments=classify('cat test-output.log; cat test-output.log; cat change.diff'.replace('test-output.log','failure.log').replace('change.diff','Defects.java'),log+log+'diff',log)
  self.assertEqual(cl['log_token_lower'],2*measure(log)['tokens']);self.assertEqual(len(segments),2)
if __name__=='__main__':unittest.main()

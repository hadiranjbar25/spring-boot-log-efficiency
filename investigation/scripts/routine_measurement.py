"""Routine-specific classification normalization; raw commands remain untouched."""
import re
from natural_analyze import shell_body

def normalize_command(command):
 body=shell_body(command)
 # Only plain literal, option-free cat arguments. Do not rewrite pipes/quoted programs.
 def cats(match):
  names=match.group(1).split()
  if len(names)<2 or any(n.startswith('-') for n in names):return match.group(0)
  return '; '.join('cat '+n for n in names)
 body=re.sub(r'\bcat[ \t]+((?:[\w./-]+[ \t]+)*[\w./-]+)(?=[;\n&|]|$)',cats,body)
 return body.replace('test-output.log','failure.log').replace('change.diff','Defects.java').replace('*.log','capture.log')
